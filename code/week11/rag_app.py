"""
RAG 미니앱 통합 (Week 9 정리)
================================
Day 65에서 만든 LangChain RAG 파이프라인을 하나로 묶은 실행용 미니앱.
- 인덱싱: 문서 → split → embed → Chroma
- 생성:   retriever | prompt | ChatGroq | StrOutputParser  (LCEL 체인)
- 루프:   질문 입력 → 근거(출처) + 답변 출력

실행: python rag_app.py   (로컬, 기존 GROQ_API_KEY .env 사용)
필요 패키지(이미 설치돼 있음): langchain, langchain-groq, langchain-huggingface,
                              langchain-chroma, langchain-text-splitters, python-dotenv
"""

from dotenv import load_dotenv
load_dotenv()  # .env 의 GROQ_API_KEY 로드 (ChatGroq가 자동으로 집어감)

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


# ── 문서 (네가 쓰던 샘플. 나중에 네 실제 문서/말뭉치로 교체하면 됨) ──
TEXTS = [
    # --- RAG 기초 (환각/검색) ---
    "RAG는 관련 문서를 검색해 프롬프트에 넣어줌으로써 환각을 줄이고 최신 정보를 답에 반영한다.",
    "환각(hallucination)은 모델이 학습하지 않았거나 근거 없는 내용을 사실인 것처럼 그럴듯하게 지어내는 현상이다.",   # near-miss: '환각' 정의일 뿐
    "RAG에서 검색 품질이 나쁘면 엉뚱한 문서가 프롬프트에 들어가 오히려 환각이 늘 수 있다.",                          # near-miss: RAG+환각인데 반대 각도
    "RAG는 모델 가중치를 바꾸지 않고 외부 지식을 주입하므로 지식 갱신이 잦은 도메인에 적합하다.",
    # --- 임베딩 ---
    "임베딩은 텍스트를 의미를 담은 고차원 벡터로 바꾼 것이다.",
    "의미가 비슷한 문장은 임베딩 공간에서 가까이, 무관한 문장은 멀리 위치한다.",
    "다국어 임베딩 모델은 서로 다른 언어의 같은 의미 문장을 비슷한 벡터로 매핑한다.",
    # --- 벡터DB / 검색 ---
    "벡터 데이터베이스는 임베딩을 저장하고 코사인 유사도로 가까운 것을 빠르게 검색한다.",
    "코사인 유사도는 두 벡터의 방향(각도)만 보고 크기는 무시한다.",
    "Chroma는 로컬에서 가볍게 돌릴 수 있는 임베딩 기반 벡터 저장소다.",
    # --- 청킹 ---
    "청크 크기가 너무 작으면 문장이 토막나 검색 품질이 떨어지고, 너무 크면 잡내용이 섞여 흐려진다.",
    "청크를 나눌 때 일부를 겹치게(overlap) 하면 경계에서 잘린 문맥 손실을 줄일 수 있다.",
    # --- 재정렬 (bi vs cross) ---
    "bi-encoder는 질문과 문서를 각각 따로 임베딩해 유사도를 재므로 빠르지만 상호작용을 못 본다.",
    "cross-encoder는 질문과 문서를 함께 입력해 상호작용을 보고 관련도를 매기므로 정확하지만 느리다.",
    "2단계 검색은 bi-encoder로 후보를 넓게 뽑고 cross-encoder로 정밀하게 재정렬해 속도와 정확도를 절충한다.",
    # --- 파인튜닝 ---
    "파인튜닝은 사전학습된 모델의 가중치를 특정 데이터로 추가 학습해 행동을 바꾸는 것이다.",
    "LoRA는 원래 가중치는 얼리고 작은 저랭크 행렬만 학습해 파인튜닝 비용을 크게 줄인다.",
    "QLoRA는 모델을 4비트로 양자화한 뒤 LoRA를 얹어 적은 VRAM으로도 학습할 수 있게 한다.",
    "파인튜닝은 지식 주입보다 말투·형식·도메인 적응에 강하고, 최신 사실 반영에는 RAG가 낫다.",
    # --- 생성 / 프롬프트 ---
    "temperature가 높을수록 생성이 다양해지고 낮을수록 결정적(deterministic)이 된다.",
    "프롬프트에 '컨텍스트에 없으면 없다고 답하라'는 지시를 넣으면 근거 없는 답을 줄일 수 있다.",
    # --- 평가 ---
    "RAGAS의 faithfulness는 생성된 답이 검색된 컨텍스트에 근거하는지를 측정한다.",
    "context precision은 검색된 문서가 질문에 실제로 관련 있는지를 측정해 검색·재정렬 품질을 본다.",
    "answer relevancy는 답변이 질문에 얼마나 잘 대응하는지를 측정한다.",
    # --- 원거리 주제 (far distractor: RAG 질문엔 낮게 깔려야 정상) ---
    "어텐션은 시퀀스의 각 토큰이 다른 토큰들을 얼마나 참고할지 가중치로 정한다.",
    "토큰화는 텍스트를 모델이 처리할 수 있는 작은 단위(토큰)로 쪼개는 과정이다.",
]


# ── 1. 인덱싱: 문서 → split → embed → Chroma  (Day 65~66) ──
def build_vectorstore(texts):
    documents = [Document(page_content=t) for t in texts]

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    # 한국어 문서라 multilingual 임베딩 (English 전용 X)
    embeddings = HuggingFaceEmbeddings(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,          # 파라미터명은 embedding (단수)
        collection_name="rag_app",
    )
    return vectorstore


# ── 2. RAG 체인: retriever | prompt | llm | parser  (Day 65 LCEL) ──
def make_rag_chain(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    llm = ChatGroq(model="openai/gpt-oss-120b")
    prompt = ChatPromptTemplate.from_template(
        """당신은 AI 전문가이다. 아래 컨텍스트를 근거로만 질문에 답하라.
너가 가진 정보에 없으면 없다고 솔직하게 답해라.
항상 한글과 한국어만을 사용한다.

컨텍스트:
{context}

질문: {question}

답변:"""
    )

    # retriever는 Document 객체 리스트를 주는데 프롬프트 {context}는 문자열이 필요 → 변환
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain


# ── 3. 질문 루프 (이 글루가 '통합'의 핵심 — 새로 짠 부분) ──
if __name__ == "__main__":
    print("인덱싱 중...")
    vectorstore = build_vectorstore(TEXTS)
    rag_chain = make_rag_chain(vectorstore)
    print(f"준비 완료 (문서 {len(TEXTS)}개). 질문해봐.\n")

    while True:
        q = input("질문 (종료하려면 q): ").strip()
        if q.lower() == "q":
            print("종료.")
            break
        if not q:
            continue

        # 근거로 검색된 청크 (왜 그렇게 답했는지 보여주기)
        sources = vectorstore.similarity_search(q, k=2)
        # 검색 결과 기반 답변 생성
        answer = rag_chain.invoke(q)

        print("\n[답변]")
        print(answer)
        print("\n[근거 청크]")
        for i, d in enumerate(sources, 1):
            print(f"  {i}. {d.page_content}")
        print()