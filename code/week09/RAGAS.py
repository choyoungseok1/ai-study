from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()
llm = ChatGroq(model="llama-3.3-70b-versatile")

def extract_claims(answer: str) -> list[str]:
    """답을 '독립적으로 검증 가능한 원자적 주장' 리스트로 분해."""
    prompt = f"""주어진 답을 독립적으로 검증 가능한 원자적 주장들로 나눠라. 각 주장을 한 줄에 하나씩, 설명·번호·군더더기 없이 주장 문장만 출력0.
    
    답:
    {answer}
    """          # TODO ① 네가 작성
    resp = llm.invoke(prompt).content
    # '한 줄에 하나'로 시켰다는 가정의 파싱 — 프롬프트 형식 바꾸면 여기도 맞춰
    return [c.strip("-•* ").strip() for c in resp.splitlines() if c.strip()]

def is_supported(claim: str, context: str) -> bool:
    """claim이 context로 뒷받침되는지 yes/no 판정."""
    prompt = f"""주어진 context만 근거로 이 주장이 사실인지 판단해라. context에 직접/암시적으로 뒷받침되면 yes, 아니면 no. 다른 말 없이 yes 또는 no 한 단어만
    
    context:
    {context}

    주장:
    {claim}
    """          # TODO ② 네가 작성
    verdict = llm.invoke(prompt).content.strip().lower()
    return verdict.startswith("yes")

def faithfulness(answer: str, context: str) -> float:
    claims = extract_claims(answer)
    if not claims:
        return 0.0
    supported = sum(is_supported(c, context) for c in claims)
    print(f"  주장 {len(claims)}개 중 {supported}개 뒷받침")   # 디버깅용
    return supported / len(claims)

# 테스트 (일부러 환각 한 줄 섞음)
context = "RAG는 관련 문서를 검색해 프롬프트에 넣고, 그것을 근거로 답을 생성한다."
answer  = "RAG는 문서를 검색해 근거로 답을 만든다. 그리고 GPT-4보다 항상 정확하다."
print(faithfulness(answer, context))   # 두 번째 주장은 context에 없음 → 0.5 근처 기대