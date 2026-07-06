from fastapi import FastAPI
from pydantic import BaseModel
from rag_pipeline import rag_pipeline   # ← 방금 만든 모듈 재사용!

app = FastAPI()

# 1) 요청 스키마 (받을 데이터) — Week 11 Pydantic 그대로
class AskRequest(BaseModel):
    question: str

# 2) 엔드포인트
@app.post("/ask")
def ask(req: AskRequest):
    answer, sources = rag_pipeline(req.question)
    return {"answer": answer, "sources": sources}