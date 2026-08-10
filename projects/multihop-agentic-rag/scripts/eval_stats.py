"""
평가 로그 통계 — LLM 호출 0회, 파일만 읽는다.
2026-08-10 (Week 17)

두 가지를 분리해서 센다:
  (가) 시도 통계   = 파일의 모든 줄 (중복 포함) → 시스템 안정성
  (나) 최종 상태   = load_records 결과          → 평가 완결성

⚠️ 홉 수·고유 문서 수는 반드시 (나) 기준.
   (가)로 세면 재시도된 idx가 두 번 들어가 평균이 오염된다.

실행: projects/multihop-agentic-rag/ 에서
      python -m scripts.eval_stats
"""
import os
import json
from collections import Counter

from src.agent import load_records

# ─────────────────────────────────────────────
# [경로] ⚠️ scripts/recall_curve.py 의 _EVAL_DIR 정의를 그대로 복사해 올 것.
#        여기만 다르게 잡으면 나중에 폴더를 옮길 때 한쪽만 깨진다.
_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(os.path.dirname(_HERE), "data")
_EVAL_DIR = os.path.join(_DATA, "eval")
EVAL_PATH = os.path.join(_EVAL_DIR, "answer_v2_n50.jsonl")
LIMIT = 50

# ═════════════════════════════════════════════
# (가) 시도 통계 — 모든 줄, 중복 포함
# ═════════════════════════════════════════════
def attempt_stats(path):
    """파일의 전 줄을 그대로 읽어 시도 횟수와 실패를 센다.

    반환: (총 시도 수, 실패 수, 원인별 Counter)

    TODO
      1. 줄 단위로 읽어 json.loads (⚠️ encoding="utf-8")
      2. rec["error"] 가 None 이 아니면 실패
      3. error 문자열은 f"{type(e).__name__}: {e}" 형태다.
         → 원인별로 쪼개려면 무엇을 기준으로 자를지 정해라.
         ⚠️ rate limit(내 TPD 제약)과 tool call 에러(모델 결함)는
            성격이 완전히 달라서 한 숫자로 합치면 둘 다 못 쓴다.
    """

    total = 0
    causes = Counter()

    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                total += 1                    # 줄이 곧 시도
                err = rec.get("error")
                if err:
                    causes["인프라 거부" if "RateLimit" in err else "모델 결함"] += 1          # ← 여기만 네가 정함

    return total, causes

# ═════════════════════════════════════════════
# (나) 최종 상태 — idx당 1건
# ═════════════════════════════════════════════

def final_stats(records):
    """이어하기 병합 후 최종 상태.

    반환: (건수, 남은 error 수, 결측 idx 리스트)
    """
    n = len(records)
    remaining_err = sum(1 for r in records if r.get("error"))

    # ⚠️ 결측 기준은 파일이 아니라 원본 qa 길이여야 한다.
    #    len(records)를 기준 삼으면 순환이다 — 빠진 걸 찾으려는데
    #    빠진 채로 센 개수를 기준으로 쓰는 꼴.
    have = {r["idx"] for r in records}
    missing = sorted(set(range(LIMIT)) - have)

    return n, remaining_err, missing

# ═════════════════════════════════════════════
# 유형별 비용 — 오늘의 핵심
# ═════════════════════════════════════════════
def cost_by_type(records):
    """bridge / comparison 별 agentic 비용."""
    out = {}
    for t in ("bridge", "comparison"):
        rs = [r for r in records if r.get("type") == t and not r.get("error")]
        if not rs:
            continue
        hops = [len(r["agentic"]["search_log"]) for r in rs]
        uniq = [len({x for log in r["agentic"]["search_log"] for x in log["titles"]})
                for r in rs]
        out[t] = {
            "n": len(rs),
            "hops": sum(hops) / len(rs),
            "uniq": sum(uniq) / len(rs),
            "hop1_ratio": sum(h == 1 for h in hops) / len(rs),
        }
        
    return out
def bridge_by_hops(records):
    """bridge를 홉 1회 / 2회 이상으로 갈라 agentic recall 비교."""
    rs = [r for r in records if r.get("type") == "bridge" and not r.get("error")]
    groups = {"1홉": [], "2홉+": []}
    for r in rs:
        h = len(r["agentic"]["search_log"])
        groups["1홉" if h == 1 else "2홉+"].append(r)

    for label, g in groups.items():
        if not g:
            continue
        rec = sum(x["agentic"]["recall"] for x in g) / len(g)
        em = sum(x["agentic"]["em"] for x in g) / len(g)
        pb = sum(x["pure"]["recall"] for x in g) / len(g)
        print(f"  {label:5} n={len(g):2}  agentic recall={rec:.3f}  em={em:.3f}  (pure recall={pb:.3f})")

def bridge_hop1_cross(records):
    """bridge 1홉 그룹에서 recall × EM 교차표."""
    rs = [r for r in records
          if r.get("type") == "bridge" and not r.get("error")
          and len(r["agentic"]["search_log"]) == 1]

    tab = Counter()
    for r in rs:
        a = r["agentic"]
        tab[(a["recall"], a["em"])] += 1

    print(f"  n={len(rs)}")
    for rec in (1.0, 0.5, 0.0):
        row = [tab[(rec, em)] for em in (1, 0)]
        if sum(row):
            print(f"  recall {rec:.1f}: 정답 {row[0]:2}  오답 {row[1]:2}  "
                  f"(정답률 {row[0]/sum(row):.2f})")
# ═════════════════════════════════════════════
def main():
    print(f"파일: {EVAL_PATH}\n")

    # ── (가) 시도 ────────────────────────────
    total, causes = attempt_stats(EVAL_PATH)
    infra = causes["인프라 거부"]
    model = causes["모델 결함"]
    attempted = total - infra

    print(f"[시도 통계] 총 {total}줄")
    print(f"  실제 실행된 시도: {attempted}")
    print(f"  - 모델 결함(tool call): {model}건")
    print(f"  → tool call 성공률 {(attempted - model) / attempted:.1%}")
    print(f"  TPD 소진 거부: {infra}회 (평가 운영 비용, 시스템 품질 아님)\n")

    # ── (나) 최종 ────────────────────────────
    records = load_records(EVAL_PATH)
    n, remaining_err, missing = final_stats(records)
    print(f"[최종 상태] n={n} / error {remaining_err}건 / 결측 idx {missing or '없음'}\n")

    # ── 유형별 ──────────────────────────────
    stats = cost_by_type(records)
    print(f"{'':16}", end="")
    for t in stats:
        print(f"{t + f'({stats[t][chr(110)]})':>16}", end="")
    print()
    for key, label in [("hops", "평균 홉 수"),
                       ("uniq", "평균 고유 문서"),
                       ("hop1_ratio", "홉 1회 비율")]:
        print(f"{label:16}", end="")
        for t in stats:
            print(f"{stats[t][key]:>16.2f}", end="")
        print()
    print("\n[bridge — 홉 수별 분해]")
    bridge_by_hops(records)
    print("\n[bridge 1홉 — recall × EM]")
    bridge_hop1_cross(records)

if __name__ == "__main__":
    main()
