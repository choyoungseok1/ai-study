"""
rag_pipeline.py
================================
검색 → 재정렬 → 생성 → (평가) RAG 파이프라인 모듈.

이 파일은 import해서 쓰는 '모듈'이다.
  from rag_pipeline import rag_pipeline, retrieve_and_rerank
→ 이때 아래 정의(함수/객체)만 로드되고,
  맨 아래 if __name__ == "__main__" 블록은 실행되지 않는다.
  (테스트/평가 코드를 그 안에 넣은 이유: import 시 무거운 작업이 안 돌게 하려고)

직접 실행(python rag_pipeline.py)하면 if __name__ 블록의 데모가 돈다.
"""

from dotenv import load_dotenv
load_dotenv()

from sentence_transformers import CrossEncoder
from rag_app import build_vectorstore, TEXTS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate


# ── 모델/벡터스토어 (import 시 1회 생성) ──
# 주의: vectorstore 생성은 26개 임베딩이라 import가 살짝 느려짐.
#       서빙에선 서버 시작 시 1회만 로드되므로 OK.
reranker = CrossEncoder("BAAI/bge-reranker-base")
vectorstore = build_vectorstore(TEXTS)


# ── 재정렬 (cross-encoder) ──
def rerank(question, docs, top_k=3):
    pairs = [(question, doc) for doc in docs]      # (질문, 문서) 쌍
    scores = reranker.predict(pairs)               # 관련도 점수
    scored = list(zip(scores, docs))
    scored.sort(key=lambda x: x[0], reverse=True)  # 점수 내림차순
    return [doc for score, doc in scored[:top_k]]


# ── 검색 + 재정렬 (2단계) ──
def retrieve_and_rerank(question, first_k=20, top_k=3):
    candidates = vectorstore.similarity_search(question, k=first_k)  # 넓게
    texts = [d.page_content for d in candidates]
    reranked = rerank(question, texts, top_k)                        # 정밀
    return reranked


# ── 생성 ──
llm = ChatGroq(model="openai/gpt-oss-120b")
prompt = ChatPromptTemplate.from_template(
    """아래 컨텍스트를 근거로만 질문에 답하라. 없으면 없다고 답하라. 한국어로 답하라.

컨텍스트:
{context}

질문: {question}

답변:"""
)

def generate_answer(question, reranked_docs):
    context = "\n\n".join(reranked_docs)
    messages = prompt.format_messages(context=context, question=question)
    response = llm.invoke(messages)
    return response.content


# ── 전체 파이프라인 ──
def rag_pipeline(question):
    reranked = retrieve_and_rerank(question, first_k=20, top_k=3)  # 검색+재정렬
    answer = generate_answer(question, reranked)                    # 생성
    return answer, reranked   # (답, 근거)


# ============================================================
# 아래는 직접 실행할 때만 도는 데모/테스트 (import 시엔 안 돌아감)
# ============================================================
if __name__ == "__main__":
    q = "RAG는 환각을 어떻게 줄이는가?"
    answer, docs = rag_pipeline(q)
    print("답:", answer)
    print("근거:", docs)
