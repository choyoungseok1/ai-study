"""
agent.py — ReAct 멀티홉 Agentic RAG (Phase A, W2)

retrieve.py의 2단계 검색을 도구로 등록하고,
ReAct 루프(Thought→Action→Observation 반복)로 멀티홉 질문을 분해한다.
"""

import os
import json

from src.retrieve import Retriever

# 검색기는 무거우니(임베딩+리랭커+Chroma 로드) 모듈 로드 시 1회만 생성해 재사용
_retriever = Retriever()
_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(os.path.dirname(_HERE), "data")

# ─────────────────────────────────────────────
# [A] 도구 실행부 — search 래퍼
# ─────────────────────────────────────────────
def search(query: str) -> str:
    """query로 관련 문단을 찾아 LLM이 읽을 하나의 문자열로 반환."""
    results = _retriever.retrieve_and_rerank(query, return_docs=True)
    # results = [(제목, 본문), ...]  최대 5개

    # TODO(너): results를 하나의 문자열로 포맷
    #   - 각 문단을 "[제목] 본문" 형태로
    #   - 문단끼리 "\n\n" 로 구분
    #   - (선택) 결과 비면 "No results found." 가드
    if not results: return "No results found."
    results = [f"[{t}] {d}" for t,d in results]
    
    return "\n\n".join(results)


# ─────────────────────────────────────────────
# [B] 도구 스키마 — Groq function calling 포맷  (다음 단계)
# ─────────────────────────────────────────────
# TOOLS = [
#     {
#         "type": "function",
#         "function": {
#             "name": "search",
#             "description": "...",          # LLM이 언제 쓸지 판단하는 근거
#             "parameters": { ... },          # query: str 하나
#         },
#     }
# ]
#
# TOOL_MAP = {"search": search}   # 이름→실제 함수 매핑
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
                        "description": "The search query (keywords or a natural-language question)."
                    }
                },
                "required": ["query"],
            },
        },
    }
]

TOOL_MAP = {"search": search}   # 이름 → 실제 함수. 나중에 루프에서 이걸로 실행
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
# [C] ReAct 루프  (다음 단계)
# ─────────────────────────────────────────────
def run_agent(question: str, max_iters: int = 6,trace: bool = False) -> str:
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
            print(f"[step {step}] FINAL")
            if trace:
                return {"answer": msg.content, "search_log": search_log}
            return msg.content

        # 도구 부름 = 실행하고 결과 다시 넣기
        messages.append(msg)                    # assistant tool_call 먼저 (순서 중요)
        for tc in msg.tool_calls:
            query = json.loads(tc.function.arguments)["query"]
            pairs = _retriever.retrieve_and_rerank(query, return_docs=True)
            titles = [t for t, d in pairs]
            result = "\n\n".join(f"[{t}] {d}" for t, d in pairs)
            print(f"[step {step}] search({query})")
            search_log.append({"hop": step, "query": query, "titles": titles})
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
    if trace:
            return {"answer": "[max iterations reached]", "search_log": search_log}
    return "[max iterations reached]"
def recall_at_k(gold_titles, retrieved_titles):
    """gold 중 retrieved에 잡힌 비율."""
    gold = set(gold_titles)            # ← 중복 제거 (아까 발견한 gold 중복 문제!)
    retrieved = set(retrieved_titles)
    
    if len(gold) == 0:
        return 0
    return len(gold.intersection(retrieved))/len(gold)
def eval_pure_rag(question, gold, k=5):
    titles, docs = _retriever.retrieve(question, k=k)   # bi-encoder top-k
    return recall_at_k(gold, titles)
def eval_rerank_rag(question, gold, k_final=5):
    titles = _retriever.retrieve_and_rerank(question, k_final=k_final)  # 제목만 (return_docs=False 기본)
    return recall_at_k(gold, titles)
def eval_agentic(question, gold):
    result = run_agent(question, trace=True)
    # TODO: result["search_log"]의 모든 hop에서 titles를 다 모아 합집합
    #   - search_log = [{"hop":0, "query":..., "titles":[...]}, {"hop":1, ...}]
    #   - 모든 titles를 하나의 리스트/set으로
    
    all_titles = set([t for log in result["search_log"] for t in log["titles"]])
    return recall_at_k(gold, all_titles)

# ─────────────────────────────────────────────
# 손 테스트
# ─────────────────────────────────────────────

if __name__ == "__main__":
    qa = json.load(open(os.path.join(_DATA, "qa.json"), encoding="utf-8"))
    subset = qa[:10]          # 먼저 10개만

    pure_scores, rerank_scores, agentic_scores = [], [], []
    for i, item in enumerate(subset):
        q = item["question"]
        gold = item["gold_titles"]
        p = eval_pure_rag(q, gold)
        r = eval_rerank_rag(q, gold)
        a = eval_agentic(q, gold)
        pure_scores.append(p)
        rerank_scores.append(r)
        agentic_scores.append(a)
        print(f"[{i}] pure={p:.2f} rerank={r:.2f} agentic={a:.2f}  {q[:50]}")

    n = len(subset)
    print("=" * 50)
    print(f"평균 recall (n={n})")
    print(f"  순수 RAG   : {sum(pure_scores)/n:.3f}")
    print(f"  재정렬 RAG : {sum(rerank_scores)/n:.3f}")
    print(f"  Agentic    : {sum(agentic_scores)/n:.3f}")