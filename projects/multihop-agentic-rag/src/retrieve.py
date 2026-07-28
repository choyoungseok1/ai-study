"""
retrieve.py — 검색 + 재정렬 모듈 (멀티홉 Agentic RAG, Phase A)

노트북(03_chroma_index)에서 검증한 2단계 검색을 굳힌 재사용 모듈.
  1단계 bi-encoder(all-MiniLM-L6-v2)로 넓게 검색 → 2단계 cross-encoder
  (bge-reranker-base)로 정밀 재정렬.

검증(HotpotQA dev 서브셋 500, recall@5): 검색만 0.739 → 재정렬후 0.849 (상한 0.869)
"""

import os
import json

from sentence_transformers import SentenceTransformer, CrossEncoder
import chromadb
from dotenv import load_dotenv        # ← 추가 (없으면)
load_dotenv()                          # ← 추가

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_DATA = os.path.join(_ROOT, "data")

# ⚠️ 한글 경로(C:\Users\조영석\...)에서 chroma-hnswlib(C++ 확장)이
#    hnsw 인덱스를 로드하지 못함. ASCII 경로를 .env 의 CHROMA_DIR 로 지정.
_PERSIST_DEFAULT = os.getenv("CHROMA_DIR") or os.path.join(_DATA, "chroma")
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)                 # multihop-agentic-rag/
_DATA = os.path.join(_ROOT, "data")

EMBED_MODEL = "all-MiniLM-L6-v2"
RERANK_MODEL = "BAAI/bge-reranker-base"
COLLECTION = "en_minilm"


class Retriever:
    def __init__(self, corpus_path=None, persist_dir=None):
        self.corpus_path = corpus_path or os.path.join(_DATA, "corpus.json")
        self.persist_dir = persist_dir or _PERSIST_DEFAULT

        self.embedder = SentenceTransformer(EMBED_MODEL)
        self.reranker = CrossEncoder(RERANK_MODEL)

        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.col = self.client.get_or_create_collection(COLLECTION)
        
        self._build_if_empty()

    def _build_if_empty(self):
        if self.col.count() > 0:
            return
        corpus = json.load(open(self.corpus_path, encoding="utf-8"))
        titles = list(corpus.keys())
        docs = list(corpus.values())
        embs = self.embedder.encode(docs, batch_size=64, show_progress_bar=True)
        self.col.add(ids=titles, documents=docs,
                     embeddings=[e.tolist() for e in embs])

    def retrieve(self, query, k=20):
        q = self.embedder.encode([query])[0].tolist()
        res = self.col.query(query_embeddings=[q], n_results=k)
        return res["ids"][0], res["documents"][0]

    def retrieve_and_rerank(self, query, k_retrieve=20, k_final=5, return_docs=False):
        titles, docs = self.retrieve(query, k=k_retrieve)
        scores = self.reranker.predict([(query, d) for d in docs])
        ranked = sorted(zip(scores, titles, docs), key=lambda x: x[0], reverse=True)
        top = ranked[:k_final]
        if return_docs:
            return [(t, d) for _, t, d in top]
        return [t for _, t, _ in top]


if __name__ == "__main__":
    r = Retriever()
    qa = json.load(open(os.path.join(_DATA, "qa.json"), encoding="utf-8"))
    q = qa[0]
    print("Q   :", q["question"])
    print("gold:", q["gold_titles"])
    print("top5:", r.retrieve_and_rerank(q["question"]))
