# rag_pipeline.py
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("BAAI/bge-reranker-base")
def rerank(question, docs, top_k=3):
    # 1. 질문이랑 각 문서를 '쌍'으로 묶기
    pairs = [(question,doc) for doc in docs]                          # [(질문, 문서1), (질문, 문서2), ...]
    # 2. 각 쌍의 관련도 점수 매기기
    scores = reranker.predict(pairs)     # 점수 배열
    # 3. 점수 높은 순으로 문서 정렬 → 상위 top_k개 반환
    scored = list(zip(scores, docs))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in scored[:top_k]]



from rag_app import build_vectorstore, TEXTS

vectorstore = build_vectorstore(TEXTS)

def retrieve_and_rerank(question, first_k=20, top_k=5):
    # 1. 검색: 후보를 넉넉히 (first_k개)
    candidates = vectorstore.similarity_search(question, k=first_k)   # Document 리스트
    # 2. 재정렬: candidates에서 상위 top_k로 좁히기
    texts = [d.page_content for d in candidates]
    reranked = rerank(question, texts, top_k)
    return reranked


vectorstore.delete_collection()      # 옛 컬렉션 삭제
# 또는 persist 폴더 통째로: import shutil; shutil.rmtree("경로", ignore_errors=True)
vectorstore = build_vectorstore(TEXTS)   # 깨끗하게 재빌드
print(vectorstore._collection.count())   # 이제 26 나와야 정상
from rag_app import TEXTS
import rag_app, inspect

print("1) len(TEXTS):", len(TEXTS))
print("2) TEXTS 샘플:", TEXTS[:2])
print("3) collection count:", vectorstore._collection.count())
print("4) build_vectorstore:\n", inspect.getsource(rag_app.build_vectorstore))
q = "RAG는 환각을 어떻게 줄이는가?"

# 재정렬 전 (그냥 검색 순서)
before = [d.page_content for d in vectorstore.similarity_search(q, k=5)]
# 재정렬 후
after = retrieve_and_rerank(q, first_k=20, top_k=3)

print("=== 검색 순서 (before) ===")
for i, t in enumerate(before, 1):
    print(f"{i}. {t}")
print("\n=== 재정렬 후 (after) ===")
for i, t in enumerate(after, 1):
    print(f"{i}. {t}")
q = "RAG는 환각을 어떻게 줄이는가?"
cands = [d.page_content for d in vectorstore.similarity_search(q, k=20)]
scores = reranker.predict([(q, d) for d in cands])
for s, d in sorted(zip(scores, cands), key=lambda x: x[0], reverse=True)[:8]:
    print(f"{s:8.3f}  {d[:45]}")
test_qs = [
    "적은 메모리로 큰 모델을 학습시키려면?",          # 정답 QLoRA("4비트+VRAM") / 질문은 '메모리'·'학습' → 단어 어긋남
    "긴 문서를 어떻게 잘라야 검색이 잘 되나?",          # 정답 청킹/overlap / '자르다'vs'청크' 단어 어긋남
    "답변이 근거 있는지 어떻게 확인하나?",              # 정답 faithfulness / '근거 확인'vs'faithfulness' 어긋남
    "두 문장이 의미가 비슷한지 어떻게 판단하나?",        # 정답 임베딩/코사인 / 단어 다름
    "빠른 검색이랑 정확한 검색을 둘 다 잡으려면?",        # 정답 2단계 검색 / 단어 어긋남
]

for q in test_qs:
    before = [d.page_content for d in vectorstore.similarity_search(q, k=5)]
    after  = retrieve_and_rerank(q, first_k=20, top_k=3)
    moved = before[0] != after[0]          # 1위가 바뀌었나
    print(f"\n{'★ 순위변동' if moved else '  변동없음'}  | Q: {q}")
    print(f"  before 1위: {before[0][:40]}")
    print(f"  after  1위: {after[0][:40]}")
q = "답변이 근거 있는지 어떻게 확인하나?"
before = [d.page_content for d in vectorstore.similarity_search(q, k=5)]
after  = retrieve_and_rerank(q, first_k=20, top_k=3)
print("=== before (bi-encoder) ===")
for i,t in enumerate(before,1): print(f"{i}. {t}")
print("\n=== after (re-ranked) ===")
for i,t in enumerate(after,1):  print(f"{i}. {t}")
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

llm = ChatGroq(model="openai/gpt-oss-120b")   # 생성용 (또는 gpt-oss-120b)
prompt = ChatPromptTemplate.from_template(
    """아래 컨텍스트를 근거로만 질문에 답하라. 없으면 없다고 답하라. 한국어로 답하라.

컨텍스트:
{context}

질문: {question}

답변:"""
)

def generate_answer(question, reranked_docs):
    context = "\n\n".join(reranked_docs)   # 재정렬된 문서들을 하나의 문자열로
    messages = prompt.format_messages(context=context, question=question)
    response = llm.invoke(messages)
    return response.content
def rag_pipeline(question):
    reranked = retrieve_and_rerank(question, first_k=20, top_k=3)   # 검색+재정렬
    answer = generate_answer(question, reranked)                    # 생성
    return answer, reranked   # 답 + 근거(평가에 쓸 거)
q = "RAG는 환각을 어떻게 줄이는가?"
answer, docs = rag_pipeline(q)
print("답:", answer)
print("근거:", docs)
from ragas import SingleTurnSample, EvaluationDataset, evaluate
from ragas.metrics import faithfulness
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

# judge (gpt-oss-120b로!)
judge_llm = LangchainLLMWrapper(ChatGroq(model="openai/gpt-oss-120b"))
judge_emb = LangchainEmbeddingsWrapper(
    HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
)


from ragas import SingleTurnSample, EvaluationDataset, evaluate
from ragas.metrics import faithfulness   # TODO: context_precision 계열 추가
# judge_llm, judge_emb 는 위 셀에서 이미 정의됨 (재사용)
from ragas.metrics import faithfulness, LLMContextPrecisionWithoutReference

metrics = [faithfulness, LLMContextPrecisionWithoutReference()]

questions = [
    "답변이 근거 있는지 어떻게 확인하나?",
    "빠른 검색이랑 정확한 검색을 둘 다 잡으려면?",
    "긴 문서를 어떻게 잘라야 검색이 잘 되나?",
    "15년은 몇 일인가?",
]

def rag_no_rerank(question, k=3):
    docs = [d.page_content for d in vectorstore.similarity_search(question, k=k)]
    answer = generate_answer(question, docs)
    return answer, docs

def build_dataset(pipeline_fn):
    samples = []
    for q in questions:
        answer, docs = pipeline_fn(q)
        samples.append(SingleTurnSample(
            user_input=q, retrieved_contexts=docs, response=answer,
        ))
    return EvaluationDataset(samples=samples)

res_off = evaluate(dataset=build_dataset(rag_no_rerank), metrics=metrics, llm=judge_llm, embeddings=judge_emb)
res_on  = evaluate(dataset=build_dataset(rag_pipeline),  metrics=metrics, llm=judge_llm, embeddings=judge_emb)
print("재정렬 OFF:", res_off)
print("재정렬 ON :", res_on)
