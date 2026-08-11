import os, json
from src.agent import load_records
from scripts.eval_k50 import OUT as K50_OUT
from scripts.eval_stats import EVAL_PATH   # v2 n=50

k50 = {r["idx"]: r for r in load_records(K50_OUT) if not r.get("error")}
v2  = {r["idx"]: r for r in load_records(EVAL_PATH) if not r.get("error")}
idxs = sorted(set(k50) & set(v2))

rows = [(i, k50[i]["pure_k50"], v2[i]["agentic"]) for i in idxs]
n = len(rows)
for key in ("recall", "em"):
    a = sum(p[key] for _, p, _ in rows) / n      # pure k=50
    b = sum(g[key] for _, _, g in rows) / n      # agentic
    d = [g[key] - p[key] for _, p, g in rows]
    md = sum(d) / n
    var = sum((x - md) ** 2 for x in d) / (n - 1)
    se = (var / n) ** 0.5
    print(f"{key:7} pure_k50 {a:.3f} / agentic {b:.3f} / 차이 {md:+.3f} "
          f"95% CI [{md-1.96*se:.3f}, {md+1.96*se:.3f}]")
print(f"n={n}, 평균 agentic 문서 수 = "
      f"{sum(len({t for l in g['search_log'] for t in l['titles']}) for _,_,g in rows)/n:.1f}")