"""
context_precision.py — 검색 품질 지표 직접 구현 (W3-2)

왜 직접 구현?
  - RAGAS 0.4.x는 API가 갈아엎어졌고 자료가 적어 오늘 안에 안정화가 불확실
  - judge 호출을 직접 통제해야 Groq n=1 제약 / rate limit 을 회피 가능
  - context_precision 로직 자체가 단순 → 표준 라이브러리보다 "완전히 설명 가능한" 파이프라인
  ⚠️ 면접 방어: "RAGAS 못 써서 도망친 것"이 아니라 "통제를 위한 선택"

지표 정의 (가장 단순한 버전 — 순위 가중치 없음):
    context_precision = (gold 근거로 판정된 문서 수) / (검색된 전체 문서 수)
  각 문서에 대해 judge 한테 "이 문서가 이 질문의 정답과 관련 있나? yes/no" → yes 비율.

  faithfulness 와의 차이:
    - faithfulness : 답을 주장으로 쪼개 각 주장이 '컨텍스트에 있나' (답 기준, 환각 측정)
    - context_precision : 문서 하나하나가 '정답의 근거인가' (문서 기준, 검색 품질 측정)
      → 쓰레기 문서가 많으면 precision 하락 → "많이 긁어오기"에 벌점
"""

import os
import json
import time
from src.llm import OpenAICompatProvider
from dotenv import load_dotenv

load_dotenv()

# ⚠️ llama-3.3-70b 는 2026-06 단종. 현재 주력 모델로 교체.
_MODEL = "openai/gpt-oss-120b"

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_DATA = os.path.join(_ROOT, "data")


# ─────────────────────────────────────────────
# corpus 로드 — 제목 → 본문 복원용
# ─────────────────────────────────────────────
# W3-1 레코드엔 제목만 저장됨. judge 엔 본문이 필요하므로 corpus 에서 복원.
_corpus = json.load(open(os.path.join(_DATA, "corpus.json"), encoding="utf-8"))


def titles_to_contexts(titles):
    """제목 리스트 → 본문 리스트. corpus 에 없는 제목은 건너뜀(방어)."""
    return [(t, _corpus[t]) for t in titles if t in _corpus]


# ─────────────────────────────────────────────
# judge — 문서 1개가 질문/정답과 관련 있는지
# ─────────────────────────────────────────────
_judge = None


def _get_judge():
    """judge provider — 지연 생성 + 모델 고정.

    ★ default_provider() 를 쓰지 않는다.
      judge 는 측정 도구이고 에이전트는 측정 대상이다.
      에이전트 provider 를 바꿨을 때 judge 까지 따라 바뀌면
      지표 변화의 원인을 가를 수 없다.
    ★ import 시점에 만들지 않는다 (llm.py 와 같은 이유).
    """
    global _judge
    if _judge is None:
        load_dotenv()
        _judge = OpenAICompatProvider(
            api_key=os.environ["GROQ_API_KEY"],
            model=_MODEL,
            base_url="https://api.groq.com/openai/v1",
        )
    return _judge
def _call(prompt, max_retries=5):
    """rate limit 대비 재시도 래퍼. 실패하면 예외를 위로 던짐."""
    for attempt in range(max_retries):
        try:
            return _get_judge().chat(
                [{"role": "user", "content": prompt}],
                temperature=0,
            ).text.strip()
        except Exception as e:
            # Groq rate limit(429) 등 → 지수 백오프
            wait = 2 ** attempt
            print(f"    [retry {attempt+1}/{max_retries}] {type(e).__name__}, {wait}s 대기")
            time.sleep(wait)
    raise RuntimeError(f"judge 호출 {max_retries}회 실패")
# 30~31줄 대체

def is_relevant(question: str, document: str, gold_answer: str = None) -> bool:
    """이 document 가 question 의 정답에 관련 있는 근거인지 yes/no.
    
      - question 과 document 를 주고, 이 문서가 질문에 답하는 데
        유용한 정보를 담고 있으면 yes, 무관하면 no
      - gold_answer 를 줄지 말지 결정 (아래 설계 질문 참고)
      - "yes 또는 no 한 단어만" 으로 출력 강제
    """
    prompt = f"""You are evaluating whether a retrieved document is useful for answering a question.

    Question: {question}

    Document: {document}

    Does this document contain information useful for answering the question? Answer with only "yes" or "no", nothing else."""

    verdict = _call(prompt).lower()
    return verdict.startswith("yes")


# ─────────────────────────────────────────────
# 지표 계산
# ─────────────────────────────────────────────
def context_precision(question, titles, gold_titles, verbose=False):
    """검색된 문서 중 관련 문서 비율.
    gold 문서는 라벨을 신뢰해 자동 relevant. gold 아닌 문서만 LLM judge.
    (judge가 gold를 오판하는 걸 육안 검수로 발견 → gold는 judge에 안 맡김)
    """
    contexts = titles_to_contexts(titles)
    if not contexts:
        return 0.0

    gold = set(gold_titles)
    relevant = 0
    for title, doc in contexts:
        if title in gold:
            r = True                          # ★ gold는 자동 relevant
        else:
            r = is_relevant(question, doc)    # gold 아닌 것만 judge
        relevant += r
        if verbose:
            mark = "★" if title in gold else " "
            print(f"    [{'O' if r else 'X'}]{mark} {title[:40]}")

    score = relevant / len(contexts)
    if verbose:
        print(f"  → {relevant}/{len(contexts)} = {score:.3f}")
    return score


# ─────────────────────────────────────────────
# W3-1 레코드에 먹이기
# ─────────────────────────────────────────────
def score_record(record, which="agentic"):
    q = record["question"]
    gold_titles = record["gold_titles"]        # ★ 추가

    if which == "agentic":
        titles = list({t for log in record["agentic"]["search_log"] for t in log["titles"]})
    else:
        titles = record[which]["titles"]

    return context_precision(q, titles, gold_titles)   # ★ gold 넘김

# ─────────────────────────────────────────────
# 소규모 테스트 — 먼저 레코드 2~3개로
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # [1] 자족 테스트 — judge 자체가 되나 (2콜)
    q = "What country is the singer from who duets with Elton John on 'Don't Go Breaking My Heart'?"
    good = "Kiki Dee is a British singer who recorded the duet with Elton John."
    junk = "The Great Barrier Reef is the world's largest coral reef system off Australia."
    print("관련 문서:", is_relevant(q, good))
    print("무관 문서:", is_relevant(q, junk))

    # [2] 10개 표 + 타입별 평균
    records = [json.loads(l) for l in open(os.path.join(_DATA, "eval", "eval_n10.jsonl"), encoding="utf-8")]
    results = []
    for rec in records:
        if rec["error"]:
            continue
        row = {"idx": rec["idx"], "type": rec["type"]}
        for w in ("pure", "rerank", "agentic"):
            row[w] = score_record(rec, w)
        results.append(row)
        print(f"[{rec['idx']}] {rec['type']:11} pure={row['pure']:.3f} rerank={row['rerank']:.3f} agentic={row['agentic']:.3f}")

    for t in ("bridge", "comparison"):
        rows = [r for r in results if r["type"] == t]
        if rows:
            print(f"\n{t} (n={len(rows)})")
            for w in ("pure", "rerank", "agentic"):
                print(f"  {w}: {sum(r[w] for r in rows)/len(rows):.3f}")

    # [3] judge 육안 검수 — idx=2 (bridge)
    print("\n" + "=" * 60)
    print("judge 육안 검수 (idx=2 bridge)")
    print("=" * 60)
    rec = next(r for r in records if r["idx"] == 2)
    q2 = rec["question"]
    print("Q:", q2)
    print("gold:", rec["gold_titles"])
    titles = list({t for log in rec["agentic"]["search_log"] for t in log["titles"]})
    for title in titles:
        if title not in _corpus:
            print(f"\n[없음] {title}")
            continue
        doc = _corpus[title]
        doc = _corpus[title]
        if title in rec["gold_titles"]:
            verdict = True                      # gold 고정 (표와 동일 로직)
        else:
            verdict = is_relevant(q2, doc)
        gold_mark = "  ★gold" if title in rec["gold_titles"] else ""
        print(f"\n[{'O' if verdict else 'X'}] {title}{gold_mark}")
        print(f"    {doc[:200]}...")
