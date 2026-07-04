"""
RAGAS 평가 스크립트 (Week 11)
rag_app.py의 RAG 파이프라인을 RAGAS로 평가.
judge LLM = Groq, 임베딩 = multilingual (둘 다 로컬/무료)
"""

import sys
sys.path.append("code/week09")   # rag_app.py 있는 경로
from rag_app import build_vectorstore, make_rag_chain, TEXTS
from dotenv import load_dotenv
load_dotenv()

# rag_app에서 함수/문서 가져오기 (import해도 __main__ while루프는 안 돌아감)


from ragas import SingleTurnSample, EvaluationDataset, evaluate
from ragas.metrics import faithfulness, answer_relevancy
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings


# ── RAG 준비 (rag_app과 동일) ──
vectorstore = build_vectorstore(TEXTS)
rag_chain = make_rag_chain(vectorstore)


# ── judge LLM + 임베딩 (RAGAS가 OpenAI 대신 Groq 쓰도록 명시) ──
judge_llm = LangchainLLMWrapper(ChatGroq(model="openai/gpt-oss-120b"))
judge_emb = LangchainEmbeddingsWrapper(
    HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
)


# ════════════════════════════════════════════════
# ★★★ 여기가 네가 채울 부분 ★★★
# ════════════════════════════════════════════════

# [채울 칸 1] 질문 3~5개. TEXTS 내용에 답이 있는 질문으로.
questions = [
    # 예: "RAG는 환각을 어떻게 줄이는가?",
    # ...
    'RAG는 환각을 어떻게 줄이는가?',
    "벡터 데이터베이스는 텍스트를 어떻게 검색하는가?",
    '파인튜닝은 무엇인가?'
]

# [채울 칸 2] 각 질문을 RAG에 통과시켜 평가 샘플 모으기
samples = []
for q in questions:
    sources = vectorstore.similarity_search(q, k=2)   # 근거 청크 (Document 리스트)
    contexts = [doc.page_content for doc in sources]                                   # ← sources에서 텍스트만 뽑아 문자열 리스트로
    answer = rag_chain.invoke(q)                                  # ← rag_chain으로 답 생성
    samples.append(SingleTurnSample(
        user_input=q,
        retrieved_contexts=contexts,
        response=answer,
    ))

# ════════════════════════════════════════════════
# ★★★ 여기까지 ★★★
# ════════════════════════════════════════════════


# 확인용 (한 번 찍어보고 제대로 들어갔나 보기)
print("샘플 수:", len(samples))
print("첫 샘플:", samples[0])


# ── 평가 실행 ──
dataset = EvaluationDataset(samples=samples)
result = evaluate(
    dataset=dataset,
    metrics=[faithfulness, answer_relevancy],
    llm=judge_llm,
    embeddings=judge_emb,
)
print("\n=== 평가 결과 ===")
print(result)