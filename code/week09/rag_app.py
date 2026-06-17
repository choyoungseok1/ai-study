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
    "LLM은 이전 토큰들을 보고 다음 토큰의 확률을 예측하는 모델이다.",
    "RAG는 관련 문서를 검색해 프롬프트에 넣어줌으로써 환각을 줄이고 최신 정보를 답에 반영한다.",
    "임베딩은 텍스트를 의미를 담은 고차원 벡터로 바꾼 것이다.",
    "벡터 데이터베이스는 임베딩을 저장하고 코사인 유사도로 가까운 것을 빠르게 검색한다.",
    "파인튜닝은 사전학습된 모델의 가중치를 특정 데이터로 추가 학습해 행동을 바꾸는 것이다.",
    "청크 크기가 너무 작으면 문장이 토막나 검색 품질이 떨어지고, 너무 크면 잡내용이 섞여 흐려진다.",
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
    llm = ChatGroq(model="llama-3.3-70b-versatile")

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