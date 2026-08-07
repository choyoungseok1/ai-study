"""
recall_curve.py — k에 따른 pure RAG recall 곡선
경로: projects/multihop-agentic-rag/scripts/recall_curve.py

실행: python -m scripts.recall_curve

────────────────────────────────────────────────────────────
[무엇을 보이려는 것인가]

"k를 늘리면 agentic을 따라잡는 것 아니냐"는 반박에 답한다.
단 답의 형태에 주의해야 한다. recall 은 k 에 단조 증가하고
k=4928 이면 반드시 1.0 이므로, "절대 못 따라잡는다"는 틀린 주장이다.

★ 옳은 질문: agentic recall 에 도달하려면 k 가 얼마여야 하고,
  그때 컨텍스트 비용이 몇 배인가.
  agentic 은 고유 문서 평균 7.5개로 그 값에 도달했다.

★ 곡선의 기울기가 0 으로 수렴하는 것을 보이면,
  "따라잡으려면 비현실적인 k 가 필요하다"가 그래프로 증명된다.

⚠️ agentic 은 k 가 없다(홉마다 5개씩). 수평선이 아니라
  점 하나(x=고유문서수 평균, y=recall)로 찍는다.
  수평선은 "모든 k 에서 그 값"이라는 오해를 준다.
────────────────────────────────────────────────────────────
"""

import json
import os

from src.retrieve import Retriever
from src.agent import recall_at_k

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(os.path.dirname(_HERE), "data")
_EVAL_DIR = os.path.join(_DATA, "eval")

K_LIST = [5, 8, 10, 15, 20, 30, 50, 75, 100]

# ⚠️ 곡선용 질문 집합을 평가 결과와 맞춰야 한다.
#   재실행에서 성공한 idx 만 써야 agentic 점과 같은 모집단이 된다.
EVAL_PATH = os.path.join(_EVAL_DIR, "answer_v2_n50.jsonl")


def load_eval_subset():
    """평가에서 성공한 레코드만 반환. agentic 점의 모집단과 일치시킨다."""
    if not os.path.exists(EVAL_PATH):
        raise FileNotFoundError(
            f"{EVAL_PATH} 없음. 평가를 먼저 돌리거나 EVAL_PATH 를 고칠 것"
        )
    recs = [json.loads(l) for l in open(EVAL_PATH, encoding="utf-8") if l.strip()]
    return [r for r in recs if not r["error"]]


def main():
    ok = load_eval_subset()
    print(f"모집단: n={len(ok)} (평가 성공분만)")

    r = Retriever()

    # ── pure 곡선 ──────────────────────────────────────
    rows = []
    for k in K_LIST:
        by_type = {"bridge": [], "comparison": []}
        for rec in ok:
            titles, _ = r.retrieve(rec["question"], k=k)
            score = recall_at_k(rec["gold_titles"], titles)
            by_type[rec["type"]].append(score)

        allv = by_type["bridge"] + by_type["comparison"]
        rows.append({
            "k": k,
            "bridge": sum(by_type["bridge"]) / len(by_type["bridge"]),
            "comparison": sum(by_type["comparison"]) / len(by_type["comparison"]),
            "all": sum(allv) / len(allv),
        })
        print(f"  k={k:3}  bridge={rows[-1]['bridge']:.3f} "
              f"comparison={rows[-1]['comparison']:.3f} all={rows[-1]['all']:.3f}")

    # ── 기준점: agentic / rerank ───────────────────────
    def avg(rs, mode, key="recall"):
        return sum(x[mode][key] for x in rs) / len(rs) if rs else 0

    def uniq_docs(rec):
        return len({t for h in rec["agentic"]["search_log"] for t in h["titles"]})

    print("\n기준점 (곡선 위에 점으로 찍을 것)")
    for t in ("bridge", "comparison", None):
        rs = ok if t is None else [x for x in ok if x["type"] == t]
        if not rs:
            continue
        ud = sum(uniq_docs(x) for x in rs) / len(rs)
        print(f"  {t or '전체':10} agentic: x={ud:.1f}(고유문서) y={avg(rs,'agentic'):.3f}"
              f"   |  rerank k=5: y={avg(rs,'rerank'):.3f}")

    # ── ★ 핵심 판독: agentic recall 에 닿는 k ──────────
    print("\n★ pure 가 agentic recall 에 도달하는 k")
    for t in ("bridge", "comparison", None):
        rs = ok if t is None else [x for x in ok if x["type"] == t]
        if not rs:
            continue
        target = avg(rs, "agentic")
        key = t or "all"
        hit = next((row["k"] for row in rows if row[key] >= target), None)
        ud = sum(uniq_docs(x) for x in rs) / len(rs)
        if hit:
            print(f"  {t or '전체':10} target={target:.3f} → k={hit} "
                  f"(agentic {ud:.1f}개 대비 {hit/ud:.1f}배)")
        else:
            print(f"  {t or '전체':10} target={target:.3f} → k={K_LIST[-1]} 에서도 미달 "
                  f"({rows[-1][key]:.3f})  ← 더 강한 결과")

    # ── 기울기: 포화 확인 ──────────────────────────────
    print("\n기울기 (k 1개 늘릴 때 recall 증가분, bridge)")
    for a, b in zip(rows, rows[1:]):
        slope = (b["bridge"] - a["bridge"]) / (b["k"] - a["k"])
        print(f"  k {a['k']:3}→{b['k']:3}: {slope:+.5f}/doc")

    out = os.path.join(_EVAL_DIR, "recall_curve.json")
    json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\n저장: {out}")


if __name__ == "__main__":
    main()
