"""
Phase B Step 1 — arXiv 후보 논문 수집
2026-08-17 (Week 18)

목적
  RAG/에이전트 논문 약 40편의 코퍼스를 만든다.
  ⚠️ 이 스크립트는 **후보를 모아 목록으로 뽑는 것**까지만 한다.
     최종 40편은 사람이 고른다.

왜 자동 확정하지 않나
  코퍼스가 **서로 인용하는 클러스터**여야 bridge 질문이 만들어진다.
  키워드 검색만으로는 주제가 비슷하지만 서로 무관한 논문이 섞이고,
  그러면 "A를 읽어야 B를 안다"는 구조가 성립하지 않는다.
  → 아는 논문을 시드로 두고, 후보를 넓게 받아 눈으로 고른다.

산출물
  data/arxiv/candidates.json   후보 메타데이터
  콘솔에 번호 붙은 목록 (고를 때 사용)

실행: projects/multihop-agentic-rag/ 에서
      python -m scripts.fetch_arxiv
"""
import os
import json
import time

import arxiv

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(os.path.dirname(_HERE), "data")
OUT_DIR = os.path.join(_DATA, "arxiv")
OUT = os.path.join(OUT_DIR, "candidates.json")

# ─────────────────────────────────────────────
# 시드 — 이미 읽은 논문 (제목으로 찾는다)
# ─────────────────────────────────────────────
# ⚠️ arXiv ID를 하드코딩하지 않는다. 기억에 의존한 ID는 틀릴 수 있고,
#    틀리면 엉뚱한 논문이 조용히 들어온다. 제목으로 찾아 눈으로 확인한다.
SEED_TITLES = [
    "Adaptive-RAG",
    "Self-RAG",
    "ReAct: Synergizing Reasoning and Acting in Language Models",
    "RAGAS",
    "Searching for Best Practices in Retrieval-Augmented Generation",
    "DoRA: Weight-Decomposed Low-Rank Adaptation",
]

# ─────────────────────────────────────────────
# 후보 확장 — 키워드 검색
# ─────────────────────────────────────────────
QUERIES = [
    'abs:"retrieval-augmented generation" AND abs:"multi-hop"',
    'abs:"multi-hop question answering" AND abs:retrieval',
    'abs:"query rewriting" AND abs:retrieval AND cat:cs.CL',
    'abs:"adaptive retrieval" AND cat:cs.CL',
    'abs:"iterative retrieval" AND abs:"language model"',
    'abs:"tool use" AND abs:"language model" AND abs:agent',
    'abs:"RAG evaluation" OR abs:"retrieval evaluation" AND cat:cs.CL',
    'abs:"dense retrieval" AND abs:reranking',
]
PER_QUERY = 15


def _to_record(r):
    """arxiv Result → 저장용 dict.

    ⚠️ 본문은 저장하지 않는다. 여기서는 메타데이터만.
       메타데이터는 CC0이고 본문은 저작권이 있다.
    """
    return {
        "arxiv_id": r.entry_id.rsplit("/", 1)[-1],   # 예: 2403.14403v2
        "title": r.title.strip().replace("\n", " "),
        "authors": [a.name for a in r.authors][:6],
        "published": r.published.date().isoformat() if r.published else None,
        "categories": list(r.categories),
        "abstract": r.summary.strip().replace("\n", " "),
        "pdf_url": r.pdf_url,
    }


def fetch(client, query=None, id_list=None, n=10):
    """검색 1회. arxiv 패키지가 요청 간 지연을 알아서 넣는다(초당 3요청 제한)."""
    kwargs = {"max_results": n}
    if query:
        kwargs["query"] = query
    if id_list:
        kwargs["id_list"] = id_list
    search = arxiv.Search(**kwargs)
    try:
        return list(client.results(search))
    except Exception as e:
        print(f"  ⚠️ 실패 ({type(e).__name__}): {str(e)[:80]}")
        return []


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    client = arxiv.Client(page_size=50, delay_seconds=3.0, num_retries=3)

    found = {}          # arxiv_id(버전 제외) → record
    source = {}         # arxiv_id → 어디서 왔나

    def add(recs, tag):
        new = 0
        for r in recs:
            rec = _to_record(r)
            key = rec["arxiv_id"].split("v")[0]
            if key not in found:
                found[key] = rec
                source[key] = tag
                new += 1
        return new

    # ── 시드 ────────────────────────────────────
    print("[시드] 제목으로 검색\n")
    for t in SEED_TITLES:
        recs = fetch(client, query=f'ti:"{t}"', n=3)
        if not recs:                                  # 제목 완전일치 실패 시 완화
            recs = fetch(client, query=t, n=3)
        n = add(recs, "seed")
        mark = "✅" if recs else "❌"
        print(f"  {mark} {t[:50]:52} → {len(recs)}건 (신규 {n})")
        for r in recs[:2]:
            print(f"        {r.entry_id.rsplit('/',1)[-1]}  {r.title[:60]}")
        print()

    # ── 키워드 확장 ─────────────────────────────
    print("\n[확장] 키워드 검색\n")
    for q in QUERIES:
        recs = fetch(client, query=q, n=PER_QUERY)
        n = add(recs, "keyword")
        print(f"  {len(recs):2}건 (신규 {n:2})  {q[:70]}")

    # ── 저장 ────────────────────────────────────
    records = list(found.values())
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    # ── 고르기용 목록 ───────────────────────────
    print("\n" + "=" * 78)
    print(f"후보 {len(records)}편  →  {OUT}\n")
    for i, (key, rec) in enumerate(found.items(), 1):
        tag = "★" if source[key] == "seed" else " "
        cat = rec["categories"][0] if rec["categories"] else "?"
        print(f"{i:3}.{tag} [{rec['published']}] {cat:10} {rec['title'][:58]}")

    print("\n" + "=" * 78)
    print("다음 단계")
    print("  1. 위 목록에서 약 40편을 고른다")
    print("     ⚠️ 기준: 서로 인용할 만한 클러스터인가 (주제 유사성이 아니라 인용 가능성)")
    print("     ⚠️ 아는 논문을 우선 — QA쌍 정답 검증이 빨라진다")
    print("  2. 고른 arxiv_id 를 data/arxiv/selected.json 에 리스트로 저장")
    print("  3. Step 2: 본문 수집 + 섹션 분할 + 청킹")


if __name__ == "__main__":
    main()
