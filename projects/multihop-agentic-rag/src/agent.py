"""
agent.py — ReAct 멀티홉 Agentic RAG (Phase A, W4)

retrieve.py의 2단계 검색을 도구로 등록하고,
ReAct 루프(Thought→Action→Observation 반복)로 멀티홉 질문을 분해한다.

[W3 변경점]
  1. search()가 (본문 문자열, 제목 리스트) 둘 다 반환 → TOOL_MAP 경로 부활 (중복 경로 제거)
  2. run_agent이 stopped("final" / "max_iters") 를 함께 반환
  3. eval_* 3종이 recall만이 아니라 titles / search_log 까지 반환
  4. 질문별 레코드를 JSONL로 append 저장 + 재실행 시 이어하기 (rate limit 대비)

[W4 변경점 — 2026-08-03]
  5. ★ retriever 의존성 주입: run_agent(..., retriever=None)
     - 이유: 서빙(app/main.py)이 agent를 import하면 Retriever 인스턴스가 2개가 된다
       (cross-encoder 두 벌 + Chroma 커넥션 두 개, RAM 13GB에 부담)
     - 세터(set_retriever) 방식을 기각한 이유: 전역을 갈아끼우면
       "누가 무엇을 쓰는지"가 호출 시점의 전역 상태에 달리게 된다.
       run_agent(q)만 봐서는 어떤 retriever를 쓰는지 알 수 없고,
       동시 요청 중 교체되면 에러 없이 조용히 어긋난다.
       주입은 호출부만 보면 답이 나온다.
  6. search를 make_search(retriever) 팩토리로 변경
     - tool 스키마에는 query 하나뿐이라 LLM이 retriever를 채워줄 수 없다
       → 클로저로 미리 묶어 넣는다
"""

import os
import json
import datetime

from src.retrieve import Retriever

# 검색기는 무거우니(임베딩+리랭커+Chroma 로드) 모듈 로드 시 1회만 생성해 재사용
# ⚠️ 이건 노트북·배치 평가용 기본값. 서빙은 자기 인스턴스를 주입한다.
# 검색기는 무거우니(임베딩+리랭커+Chroma 로드) 재사용한다.
# ★ 지연 생성: import 시점에 만들지 않는다.
#   서빙(app/main.py)이 이 모듈을 import할 때 두 번째 인스턴스가 생기는 걸 막는다.
#   주입은 '쓰는 쪽'만 고친 것이고, '만드는 쪽'도 같이 고쳐야 완성된다.
_retriever = None


def _default_retriever():
    """배치 평가·노트북용 기본 인스턴스. 처음 필요할 때만 만든다."""
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever
_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(os.path.dirname(_HERE), "data")
_EVAL_DIR = os.path.join(_DATA, "eval")


# ─────────────────────────────────────────────
# [A] 도구 실행부 — search 래퍼 (팩토리)
# ─────────────────────────────────────────────
def make_search(retriever):
    """retriever를 캡처한 search 도구를 만든다.

    ★ 왜 팩토리인가: tool 스키마에는 query 하나뿐이라
      LLM이 retriever를 채워줄 수 없다. 클로저로 미리 묶어 넣는다.
    """

    def search(query: str):
        """query로 관련 문단을 찾아 (LLM이 읽을 문자열, 제목 리스트) 를 반환.

        ★ 제목 리스트를 같이 내보낸다.
          이전에는 ReAct 루프가 titles를 얻으려고 retriever를 직접 호출해서
          '같은 일을 하는 경로'가 두 개였다. 이제 루프는 tool_map만 쓴다.
        """
        pairs = retriever.retrieve_and_rerank(query, return_docs=True)
        # pairs = [(제목, 본문), ...]  최대 5개

        if not pairs:
            return "No results found.", []

        text = "\n\n".join(f"[{t}] {d}" for t, d in pairs)
        titles = [t for t, _ in pairs]
        return text, titles

    return search


# ─────────────────────────────────────────────
# [B] 도구 스키마 — Groq function calling 포맷
# ─────────────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search",              # 실제 함수명과 일치해야 함
            "description": "Search the Wikipedia corpus for paragraphs relevant to the query. "
                           "Returns the top passages, each as '[title] text'. "
                           "Use this to look up facts about a specific entity, event, or topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query (keywords or a natural-language question).",
                    }
                },
                "required": ["query"],
            },
        },
    }
]

# ⚠️ 모듈 레벨 TOOL_MAP 제거됨 (W4).
#    search가 retriever를 캡처하게 되면서 매핑을 run_agent 안에서 만든다.

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
_client = Groq()
_MODEL = "openai/gpt-oss-120b"


SYSTEM_PROMPT = """You are a research assistant answering multi-hop questions using a search tool over a Wikipedia corpus.

Strategy:
- Break the question into single-fact steps. Search for ONE entity or fact at a time.
- Use the result of one search to inform the next. For example, first find a person's name, then search for that person to get further details.
- Do not put the entire multi-part question into one search. Search the specific sub-fact you need next.
- When you have gathered enough information to answer, respond with the final answer directly and do NOT call the tool.

Answer concisely — the answer is usually a short phrase, name, date, or number."""


# ─────────────────────────────────────────────
# [C] ReAct 루프
# ─────────────────────────────────────────────
def run_agent(question: str, max_iters: int = 6, trace: bool = False,
              verbose: bool = False, retriever=None):
    """멀티홉 질문에 답한다.

    trace=False → 최종 답 문자열만 반환
    trace=True  → {"answer", "search_log", "stopped"} 딕셔너리 반환

    stopped: "final"     = LLM이 도구를 그만 부르고 답을 냄 (정상 종료)
             "max_iters" = 반복 한도에 걸림 (정체 의심 케이스)

    retriever: None이면 모듈 전역 _retriever 사용 (기존 호출부 호환).
               서빙은 자기 인스턴스를 넘겨 이중 로드를 피한다.
    """
    retriever = retriever or _retriever
    tool_map = {"search": make_search(retriever)}

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    search_log = []

    for step in range(max_iters):
        resp = _client.chat.completions.create(
            model=_MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        msg = resp.choices[0].message

        # 도구 안 부름 = 최종 답 → 루프 종료
        if not msg.tool_calls:
            if verbose:
                print(f"[step {step}] FINAL")
            if trace:
                return {"answer": msg.content, "search_log": search_log, "stopped": "final"}
            return msg.content

        # 도구 부름 = 실행하고 결과 다시 넣기
        messages.append(msg)                    # assistant tool_call 먼저 (순서 중요)
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            fn = tool_map[tc.function.name]     # ★ tool_map 경로 사용 (직접 호출 제거)
            result, titles = fn(**args)

            if verbose:
                print(f"[step {step}] search({args.get('query')})")

            search_log.append({"hop": step, "query": args.get("query"), "titles": titles})
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    # 반복 한도 도달
    if trace:
        return {"answer": "[max iterations reached]", "search_log": search_log, "stopped": "max_iters"}
    return "[max iterations reached]"


# ─────────────────────────────────────────────
# [D] 평가 — 비교군 3종
# ─────────────────────────────────────────────
def recall_at_k(gold_titles, retrieved_titles):
    """gold 중 retrieved에 잡힌 비율."""
    gold = set(gold_titles)            # ← 중복 제거 (gold 중복 문제)
    retrieved = set(retrieved_titles)

    if len(gold) == 0:
        return 0
    return len(gold.intersection(retrieved)) / len(gold)


def eval_pure_rag(question, gold, k=5):
    """bi-encoder top-k 만. 반환: {"titles", "recall"}"""
    titles, docs = _default_retriever().retrieve(question, k=k)
    return {"titles": titles, "recall": recall_at_k(gold, titles)}


def eval_rerank_rag(question, gold, k_final=5):
    """20개 뽑아 5개로 재정렬. 반환: {"titles", "recall"}"""
    titles = _default_retriever().retrieve_and_rerank(question, k_final=k_final)
    return {"titles": titles, "recall": recall_at_k(gold, titles)}


def eval_agentic(question, gold):
    """ReAct 멀티홉. 반환: {"answer", "recall", "stopped", "search_log"}

    ★ 변경: search_log를 통째로 내보낸다.
      이전에는 여기서 recall 하나만 짜내고 나머지를 버렸다.
      홉 수·고유 문서 수·정체 여부는 전부 search_log에서 나온다.
    """
    result = run_agent(question, trace=True)

    # 모든 홉의 titles 합집합 = 에이전트가 실제로 본 고유 문서
    all_titles = {t for log in result["search_log"] for t in log["titles"]}

    return {
        "answer": result["answer"],
        "recall": recall_at_k(gold, all_titles),
        "stopped": result["stopped"],
        "search_log": result["search_log"],
    }


def eval_pure_budget(question, gold, k):
    """예산 통제 순수 RAG — k를 외부에서 지정"""
    titles, docs = _default_retriever().retrieve(question, k=k)
    return {"titles": titles, "recall": recall_at_k(gold, titles), "k": k}


# ─────────────────────────────────────────────
# [E] 결과 저장 — JSONL append + 이어하기
# ─────────────────────────────────────────────
def append_record(path, rec):
    """레코드 한 줄 append. 중간에 죽어도 여기까지는 남는다."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:     # ← utf-8 필수 (Windows cp949 함정)
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        f.flush()


def load_done(path):
    """이미 끝난 idx 집합 → 재실행 시 건너뛰기 (rate limit 대비)"""
    if not os.path.exists(path):
        return set()
    done = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                done.add(json.loads(line)["idx"])
    return done


def load_records(path):
    """저장된 레코드 전부 읽기 (분석용)"""
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def run_eval(qa, out_path, limit=None):
    """비교군 3종을 돌려 질문별 레코드를 JSONL로 저장.

    - 이미 끝난 idx는 건너뜀 (이어하기)
    - 질문 하나가 실패해도 error 필드에 남기고 다음으로 진행
    - 파생값(홉 수, 고유 문서 수)은 저장하지 않는다 → search_log에서 언제든 재계산
    """
    subset = qa[:limit] if limit else qa
    done = load_done(out_path)
    if done:
        print(f"이미 완료된 {len(done)}개 건너뜀")

    for i, item in enumerate(subset):
        if i in done:
            continue

        q = item["question"]
        gold = item["gold_titles"]

        rec = {
            "idx": i,
            "question": q,
            "type": item.get("type"),
            "gold_titles": gold,
            "error": None,
            "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        }

        try:
            rec["pure"] = eval_pure_rag(q, gold)
            rec["rerank"] = eval_rerank_rag(q, gold)
            rec["agentic"] = eval_agentic(q, gold)
            print(f"[{i}] pure={rec['pure']['recall']:.2f} "
                  f"rerank={rec['rerank']['recall']:.2f} "
                  f"agentic={rec['agentic']['recall']:.2f} "
                  f"hops={len(rec['agentic']['search_log'])}  {q[:45]}")
        except Exception as e:
            rec["error"] = f"{type(e).__name__}: {e}"
            print(f"[{i}] ERROR {rec['error']}")

        append_record(out_path, rec)

    return load_records(out_path)


# ─────────────────────────────────────────────
# [F] 요약 — 기본 집계만 (타입별 분해는 W3-4에서)
# ─────────────────────────────────────────────
def summarize(records):
    ok = [r for r in records if r["error"] is None]
    n = len(ok)
    if n == 0:
        print("집계할 레코드 없음")
        return

    def avg(vals):
        return sum(vals) / len(vals)

    pure = avg([r["pure"]["recall"] for r in ok])
    rerank = avg([r["rerank"]["recall"] for r in ok])
    agentic = avg([r["agentic"]["recall"] for r in ok])

    hops = [len(r["agentic"]["search_log"]) for r in ok]
    uniq = [len({t for log in r["agentic"]["search_log"] for t in log["titles"]}) for r in ok]
    stuck = sum(1 for r in ok if r["agentic"]["stopped"] == "max_iters")

    print("=" * 55)
    print(f"평균 recall (n={n}, 실패 {len(records) - n}건 제외)")
    print(f"  순수 RAG   : {pure:.3f}   (컨텍스트 문서 5개 고정)")
    print(f"  재정렬 RAG : {rerank:.3f}   (컨텍스트 문서 5개 고정)")
    print(f"  Agentic    : {agentic:.3f}")
    print("-" * 55)
    print("Agentic 예산 실측")
    print(f"  검색 횟수    평균 {avg(hops):.2f}  (최소 {min(hops)} / 최대 {max(hops)})")
    print(f"  고유 문서 수 평균 {avg(uniq):.2f}  (최소 {min(uniq)} / 최대 {max(uniq)})")
    print(f"  중복 제거 효과: 홉×5 = {avg(hops) * 5:.2f} → 실제 {avg(uniq):.2f}")
    print(f"  max_iters 도달(정체 의심): {stuck}건")
    print("=" * 55)


# ─────────────────────────────────────────────
# 실행
# ─────────────────────────────────────────────
if __name__ == "__main__":
    qa = json.load(open(os.path.join(_DATA, "qa.json"), encoding="utf-8"))
    OUT = os.path.join(_EVAL_DIR, "eval_n50.jsonl")

    records = run_eval(qa, OUT, limit=50)

    rows = []
    for rec in records:
        if rec["error"]:
            continue
        uniq = len({t for log in rec["agentic"]["search_log"] for t in log["titles"]})
        pb = eval_pure_budget(rec["question"], rec["gold_titles"], k=uniq)
        rows.append({
            "idx": rec["idx"], "type": rec["type"], "k": uniq,
            "pure": rec["pure"]["recall"],
            "rerank": rec["rerank"]["recall"],
            "pure_budget": pb["recall"],
            "agentic": rec["agentic"]["recall"],
        })
        r = rows[-1]
        print(f"[{r['idx']}] {r['type']:11} k={uniq:2}  "
              f"pure={r['pure']:.2f} rerank={r['rerank']:.2f} "
              f"pure_b={r['pure_budget']:.2f} agentic={r['agentic']:.2f}")

    def avg(rs, key):
        return sum(x[key] for x in rs) / len(rs) if rs else 0

    print("\n" + "=" * 55)
    for t in ("bridge", "comparison", None):
        rs = rows if t is None else [x for x in rows if x["type"] == t]
        if not rs:
            continue
        print(f"\n{t or '전체'} (n={len(rs)}, 평균 k={avg(rs,'k'):.1f})")
        for key in ("pure", "rerank", "pure_budget", "agentic"):
            print(f"  {key:12}: {avg(rs, key):.3f}")