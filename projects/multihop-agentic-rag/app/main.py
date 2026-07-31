"""
멀티홉 Agentic RAG 서빙 API
경로: projects/multihop-agentic-rag/app/main.py

실행 (프로젝트 루트에서):
    uvicorn app.main:app --reload
    → http://127.0.0.1:8000/docs

⚠️ 반드시 프로젝트 루트에서 실행할 것.
   `python app/main.py` 로 직접 실행하면 sys.path[0]이 app/ 이 되어
   `from src.retrieve import ...` 가 깨진다. (지침: -m 실행 vs 파일 직접 실행)
"""

import os
import time
from contextlib import asynccontextmanager
from typing import Literal, Optional

from dotenv import load_dotenv

# ★ src.retrieve import 보다 먼저. CHROMA_DIR 를 못 읽으면
#   한글 경로로 떨어져서 'Error loading hnsw index' 재현된다.
load_dotenv()

from fastapi import FastAPI, HTTPException          # noqa: E402
from pydantic import BaseModel, Field               # noqa: E402


# ============================================================
# 모델 로딩 (프로세스당 1회)
# ============================================================
STATE = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ⚠️ 요청마다 로드하면 첫 응답이 수십 초. 여기서 1회만.
    print(f"[startup] CHROMA_DIR = {os.getenv('CHROMA_DIR')}")

    from src.retrieve import Retriever
    STATE["retriever"] = Retriever()

    try:
        _ = STATE["retriever"].retrieve("warmup", k=1)
        print("[startup] retriever OK")
    except Exception as e:
        print(f"[startup] retriever FAILED: {e}")
        raise

    yield
    STATE.clear()


app = FastAPI(title="Multi-hop Agentic RAG", lifespan=lifespan)


# ============================================================
# 스키마
# ============================================================
Mode = Literal["pure", "rerank", "agentic"]


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    mode: Mode = "rerank"
    k: int = Field(5, ge=1, le=50)


class AskResponse(BaseModel):
    question: str
    mode: Mode
    answer: Optional[str] = None          # pure/rerank 는 아직 None (검색만)
    retrieved_titles: list[str]
    hops: int = 1
    search_log: list[dict] = []           # agentic 에서 홉별 기록
    elapsed_ms: int


# ============================================================
# 엔드포인트
# ============================================================
@app.get("/health")
def health():
    return {"status": "ok", "chroma_dir": os.getenv("CHROMA_DIR")}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    t0 = time.perf_counter()
    if req.mode == "pure":
        titles, _ = STATE["retriever"].retrieve(req.question, k=req.k)
        answer, hops, log = None, 1, []

    elif req.mode == "rerank":
        titles = STATE["retriever"].retrieve_and_rerank(req.question, k_final=req.k)
        answer, hops, log = None, 1, []
    else:  # agentic
        # TODO(8/1): LLMProvider 어댑터 붙인 뒤 연결
        raise HTTPException(status_code=501, detail="agentic mode not wired yet")

    return AskResponse(
        question=req.question,
        mode=req.mode,
        answer=answer,
        retrieved_titles=titles,
        hops=hops,
        search_log=log,
        elapsed_ms=int((time.perf_counter() - t0) * 1000),
    )


# ============================================================
# 남은 것 (네가 채울 부분)
# ============================================================
# 1. src/retrieve.py 의 실제 함수 시그니처 확인 → 위 TODO 두 줄 수정
#    (본문·제목 튜플로 반환하는지, k 인자명이 뭔지)
#
# 2. src/llm.py — LLMProvider 인터페이스 (8/1)
#      ChatResult(text, tool_calls, raw)   ← ★ raw 필수.
#      ToolCall(id, name, args:dict)
#      OpenAICompatProvider(base_url, api_key, model)
#    되붙일 때 raw 를 쓴다. thought_signature 같은 provider 고유 필드 보존.
#
# 3. agent.py 의 messages.append(msg) / json.loads(...arguments) 를
#    우리 타입으로 교체 → /ask 의 agentic 분기 연결
#
# 4. 비교 데모용 GET /compare?question=... (세 mode 나란히)
#    — 이 프로젝트의 셀링포인트가 평가라서 값어치 있음. 여유 있으면.
