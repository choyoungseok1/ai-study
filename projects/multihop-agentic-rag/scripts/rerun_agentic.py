"""
재현성 실험 — agentic 재실행 간 편차 실측
2026-08-12 (Week 17)

배경
  에이전트의 검색어는 LLM이 생성하고 temperature를 고정하지 않았다.
  따라서 같은 평가를 다시 돌리면 숫자가 움직인다.
  기존 신뢰구간 [0.101, 0.277]은 질문 간 분산만 반영하고
  실행 간 분산은 포함하지 않는다.

  ⚠️ 이 프로젝트는 Adaptive-RAG를 "single run이라 분산 보고가 없다"고
     비판한다. 자기 것도 single run이면 그 비판이 부메랑이 된다.

설계
  - 대상: B 실험과 같은 21문항 (bridge, k=50 평가가 성공한 것)
    ★ 같은 부분집합이라야 agentic run1 / run2 / pure k=50 이
      한 테이블에 들어간다
  - agentic 만 재실행. pure/rerank 는 검색이 결정적이라 재실행 의미 없음
  - 출력 파일을 분리한다 (원본을 건드리지 않는다)

⚠️ 원본 평가 파일에 append 하면 안 된다. load_records 가 나중 것을
   채택하므로 run2 가 run1 을 덮어써 원본이 사라진다.

실행: projects/multihop-agentic-rag/ 에서
      python -m scripts.rerun_agentic
"""
import os
import json
import time
import datetime

from src.agent import (
    eval_agentic, load_done, load_records, append_record, _DATA,
)

RUN = 2
SLEEP_SEC = 3

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(os.path.dirname(_HERE), "data")
_EVAL_DIR = os.path.join(_DATA, "eval")
BASE = os.path.join(_EVAL_DIR, "answer_v2_n50.jsonl")          # run1 (원본)
K50 = os.path.join(_EVAL_DIR, "pure_k50_bridge.jsonl")         # 대상 선정용
OUT = os.path.join(_EVAL_DIR, f"agentic_bridge_run{RUN}.jsonl")


def pick_targets():
    """B 실험이 성공한 21문항과 같은 집합.

    ★ 대상을 코드로 유도한다. 인덱스를 손으로 적으면 B 쪽이 바뀔 때
      조용히 어긋난다.
    """
    idxs = {r["idx"] for r in load_records(K50) if not r.get("error")}
    qa = json.load(open(os.path.join(_DATA, "qa.json"), encoding="utf-8"))
    return [(i, qa[i]) for i in sorted(idxs)]


def main():
    targets = pick_targets()
    done = load_done(OUT)
    if done:
        print(f"이미 완료된 {len(done)}개 건너뜀")

    todo = [(i, x) for i, x in targets if i not in done]
    print(f"대상 {len(targets)}문항 중 {len(todo)}문항 실행 (run{RUN})\n")

    for n, (i, item) in enumerate(todo, 1):
        rec = {
            "idx": i,
            "question": item["question"],
            "type": item.get("type"),
            "gold_titles": item["gold_titles"],
            "gold_answer": item.get("answer"),
            "run": RUN,
            "error": None,
            "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        }
        try:
            r = eval_agentic(item["question"], item["gold_titles"],
                             gold_answer=item.get("answer"))
            rec["agentic"] = r
            uniq = len({t for log in r["search_log"] for t in log["titles"]})
            print(f"[{i}] recall={r['recall']:.2f} em={r['em']:.0f} "
                  f"hops={len(r['search_log'])} uniq={uniq:2}  "
                  f"{item['question'][:40]}")
        except Exception as e:
            rec["error"] = f"{type(e).__name__}: {e}"
            print(f"[{i}] ERROR {rec['error'][:80]}")
            if "rate_limit" in rec["error"] and "per day" in rec["error"]:
                append_record(OUT, rec)
                print("\n⚠️ TPD 소진. 이어하기로 회수한다.")
                break

        append_record(OUT, rec)
        if n < len(todo):
            time.sleep(SLEEP_SEC)

    compare()


def compare():
    """run1 vs run2 대응표본 비교."""
    r1 = {r["idx"]: r["agentic"] for r in load_records(BASE) if not r.get("error")}
    r2 = {r["idx"]: r["agentic"] for r in load_records(OUT) if not r.get("error")}
    idxs = sorted(set(r1) & set(r2))
    if not idxs:
        print("\n비교할 공통 idx 없음")
        return

    n = len(idxs)
    print("\n" + "=" * 60)
    print(f"run1 vs run{RUN}  (bridge, n={n})")

    def uniq_of(a):
        return len({t for log in a["search_log"] for t in log["titles"]})

    rows = []
    for key, get in [("recall", lambda a: a["recall"]),
                     ("em", lambda a: a["em"]),
                     ("hops", lambda a: len(a["search_log"])),
                     ("uniq", uniq_of)]:
        a = sum(get(r1[i]) for i in idxs) / n
        b = sum(get(r2[i]) for i in idxs) / n
        d = [get(r2[i]) - get(r1[i]) for i in idxs]
        md = sum(d) / n
        var = sum((x - md) ** 2 for x in d) / (n - 1) if n > 1 else 0
        se = (var / n) ** 0.5
        changed = sum(1 for x in d if x != 0)
        print(f"  {key:7} run1 {a:6.3f} / run{RUN} {b:6.3f} / 차이 {md:+.3f} "
              f"95% CI [{md-1.96*se:+.3f}, {md+1.96*se:+.3f}]  변동 {changed}/{n}문항")
        rows.append((key, md, se))

    print("\n※ 해석")
    print("  - 차이 CI 가 0을 포함 = 실행 간 편차가 질문 간 편차에 묻힌다")
    print("  - 변동 문항 수가 핵심: 평균이 같아도 개별 질문이 흔들리면")
    print("    그 자체가 비결정성의 크기다")
    print("  ⚠️ n=1 회 재실행이므로 '편차의 상한'이 아니라 '편차가 존재하는지'만 답한다")


if __name__ == "__main__":
    main()
