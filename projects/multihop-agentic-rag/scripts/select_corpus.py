"""
Phase B Step 1-2 — 후보 124편에서 코퍼스 40편 선별
2026-08-18 (Week 18)

선별 기준 (우선순위 순)
  1. **인용 가능성** — 서로 인용하는 클러스터여야 bridge 질문이 만들어진다.
     주제가 비슷한 것과 서로 인용하는 것은 다르다.
  2. **내가 아는 논문 우선** — QA쌍 정답 검증이 빠르고 정확해진다.
  3. **Phase B 주제 직결** — 질의 재작성 논문을 두껍게 넣었다.
     선행연구 확인과 bridge 재료가 동시에 된다.
  4. **고전 포함** — 2022~2023 논문은 이후 논문들이 인용하므로
     허브 노드가 된다. 최신 논문만 모으면 인용이 희박하다.

제외한 것
  - Raga(인도 고전음악) 오탐 2편
  - DoRA — 읽은 논문이지만 파인튜닝 주제라 RAG 클러스터와 인용 관계 없음
  - cs.CV / cs.CR / cs.SE / 법률 / 금융 도메인
  - 워크숍 참가 보고서 (SemEval, TREC, CheckThat, COLIEE, iKAT)
  - R-Bot — "query rewrite"지만 DB 쿼리라 검색 질의가 아니다

실행: projects/multihop-agentic-rag/ 에서
      python -m scripts.select_corpus
"""
import os
import json

import arxiv

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(os.path.dirname(_HERE), "data")
ARXIV_DIR = os.path.join(_DATA, "arxiv")
CANDIDATES = os.path.join(ARXIV_DIR, "candidates.json")
OUT = os.path.join(ARXIV_DIR, "selected.json")

# ─────────────────────────────────────────────
# 후보 목록에서 고른 번호 (1-indexed, 출력 순서 기준)
# ─────────────────────────────────────────────
GROUPS = {
    "핵심": {
        "why": "선행연구 + 이 프로젝트가 직접 인용하는 논문. 클러스터의 허브",
        "picks": [4, 5, 6, 9, 61, 75],
        # 4 Self-RAG / 5 ReAct / 6 RAGAS / 9 Best Practices
        # 61 Dissecting Agentic RAG (선행연구) / 75 When Iterative RAG Beats Ideal Evidence (선행연구)
    },
    "멀티홉·반복검색": {
        "why": "Phase A 주제. agentic 루프의 직접 비교 대상들",
        "picks": [13, 20, 22, 23, 24, 28, 29, 56, 65, 66, 68, 70],
    },
    "질의 재작성": {
        "why": "★ Phase B 중심 실험 주제. 두껍게 넣어 선행연구 확인과 bridge 재료를 겸한다",
        "picks": [38, 40, 42, 43, 45, 51, 78, 123],
    },
    "적응형 검색": {
        "why": "Adaptive-RAG 계열. 유형/난이도 분기 논의의 배경",
        "picks": [2, 52, 53, 55],
    },
    "평가·벤치마크": {
        "why": "RAGAS/ARES 계열. 지표 설계 논의에 필요하고 서로 조밀하게 인용한다",
        "picks": [95, 97, 98, 99, 104, 107, 109],
    },
    "청킹·문헌검색": {
        "why": "★ Phase B Step 2 직결. HiChunk 은 청킹 정책, LitSearch 는 과학 문헌 검색 벤치마크",
        "picks": [106, 122],
    },
}

# ⚠️ 시드 중 검색으로 못 잡은 원 논문은 ID 로 직접 확보한다.
#   ti:"Adaptive-RAG" 가 하이픈 때문에 실패했다 (2026-08-17).
EXTRA_IDS = ["2403.14403"]      # Adaptive-RAG (Jeong et al.)


def main():
    cands = json.load(open(CANDIDATES, encoding="utf-8"))
    print(f"후보 {len(cands)}편 로드\n")

    picked, seen = [], set()
    for group, info in GROUPS.items():
        print(f"[{group}] {info['why']}")
        for i in info["picks"]:
            if not (1 <= i <= len(cands)):
                print(f"  ⚠️ 범위 밖: {i}")
                continue
            rec = cands[i - 1]
            key = rec["arxiv_id"].split("v")[0]
            if key in seen:
                print(f"  (중복) {rec['title'][:60]}")
                continue
            seen.add(key)
            rec["group"] = group
            picked.append(rec)
            print(f"  {key:12} {rec['title'][:62]}")
        print()

    # ── 검색으로 못 잡은 논문 보충 ──────────────
    if EXTRA_IDS:
        print("[보충] ID 직접 조회")
        client = arxiv.Client()
        todo = [i for i in EXTRA_IDS if i not in seen]
        if todo:
            for r in client.results(arxiv.Search(id_list=todo)):
                rec = {
                    "arxiv_id": r.entry_id.rsplit("/", 1)[-1],
                    "title": r.title.strip().replace("\n", " "),
                    "authors": [a.name for a in r.authors][:6],
                    "published": r.published.date().isoformat(),
                    "categories": list(r.categories),
                    "abstract": r.summary.strip().replace("\n", " "),
                    "pdf_url": r.pdf_url,
                    "group": "핵심",
                }
                seen.add(rec["arxiv_id"].split("v")[0])
                picked.append(rec)
                print(f"  {rec['arxiv_id']:12} {rec['title'][:62]}")
        print()

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(picked, f, ensure_ascii=False, indent=2)

    # ── 요약 ────────────────────────────────────
    print("=" * 74)
    print(f"선별 {len(picked)}편  →  {OUT}\n")

    from collections import Counter
    by_group = Counter(r["group"] for r in picked)
    for g, c in by_group.items():
        print(f"  {g:14} {c:2}편")

    years = Counter(r["published"][:4] for r in picked)
    print("\n연도 분포:")
    for y in sorted(years):
        print(f"  {y}  {'█' * years[y]} {years[y]}")

    print("\n⚠️ 확인할 것")
    print("  1. 제목을 훑어 모르는 논문이 몇 편인지 센다.")
    print("     너무 많으면 QA쌍 작성 시 정답 검증이 느려진다")
    print("  2. 2022~2023 논문이 충분한가 — 이후 논문들이 인용하는 허브 노드다")
    print("  3. 빠진 시드가 없는지 (Adaptive-RAG 는 ID 로 보충함)")


if __name__ == "__main__":
    main()
