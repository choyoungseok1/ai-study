"""
응답시간 재측정 — 생성을 포함한 공정 비교
2026-08-13 (Week 17)

⚠️ 왜 다시 재는가
  기존 수치(pure 0.3초 / rerank 5초 / agentic 13.4초, 44.7배)는
  **분모에 생성이 빠져 있었다.** pure·rerank 는 검색만 재고
  agentic 은 LLM 호출까지 포함해 잰 값이라 비교 자체가 성립하지 않는다.
  분모를 가볍게 재놓고 "우리가 N배 비싸다"고 말하는 셈이다.

설계
  - 세 모드 모두 **검색 + 생성** 전 구간을 잰다 (사용자가 답을 받기까지)
  - 검색 구간과 생성 구간을 나눠 기록한다 → 어디서 시간이 드는지 보인다
  - agentic 은 홉 수를 함께 남긴다. 평균만 내면 오해를 부른다
  - 워밍업 1회는 버린다 (모델 로딩·인덱스 최초 접근 포함)

⚠️ 응답시간은 무료 티어 API 대기열에 크게 좌우된다.
   절대값이 아니라 **모드 간 상대 비교**로만 쓴다.

실행: projects/multihop-agentic-rag/ 에서
      python -m scripts.latency
"""
import os
import json
import time
import statistics

from src.agent import (
    _default_retriever, run_agent, generate_answer, _DATA,
)

N = 6                # 워밍업 1 + 측정 5
K = 5


def _timed(fn):
    t = time.perf_counter()
    out = fn()
    return out, time.perf_counter() - t


def measure_pure(q):
    (titles, docs), t_ret = _timed(lambda: _default_retriever().retrieve(q, k=K))
    _, t_gen = _timed(lambda: generate_answer(q, list(zip(titles, docs))))
    return {"retrieve": t_ret, "generate": t_gen, "total": t_ret + t_gen, "hops": 1}


def measure_rerank(q):
    pairs, t_ret = _timed(
        lambda: _default_retriever().retrieve_and_rerank(q, k_final=K, return_docs=True))
    _, t_gen = _timed(lambda: generate_answer(q, pairs))
    return {"retrieve": t_ret, "generate": t_gen, "total": t_ret + t_gen, "hops": 1}


def measure_agentic(q):
    """⚠️ agentic 은 검색과 생성이 루프 안에서 섞여 분리 불가.
    total 만 기록하고 retrieve/generate 는 None 으로 둔다.
    ★ 억지로 나누면 정의가 다른 수치를 같은 열에 넣게 된다.
    """
    res, t = _timed(lambda: run_agent(q, trace=True))
    return {"retrieve": None, "generate": None, "total": t,
            "hops": len(res["search_log"])}


def main():
    qa = json.load(open(os.path.join(_DATA, "qa.json"), encoding="utf-8"))
    qs = [x["question"] for x in qa[:50] if x.get("type") == "bridge"][:N]

    modes = [("pure", measure_pure), ("rerank", measure_rerank),
             ("agentic", measure_agentic)]
    acc = {name: [] for name, _ in modes}

    for i, q in enumerate(qs):
        warm = (i == 0)
        tag = "워밍업" if warm else f"{i}"
        for name, fn in modes:
            try:
                r = fn(q)
            except Exception as e:
                print(f"  [{tag}] {name}: ERROR {type(e).__name__}")
                continue
            if not warm:
                acc[name].append(r)
            ret = f"{r['retrieve']:.2f}" if r["retrieve"] is not None else "  - "
            gen = f"{r['generate']:.2f}" if r["generate"] is not None else "  - "
            print(f"  [{tag}] {name:8} 검색 {ret}  생성 {gen}  "
                  f"합계 {r['total']:6.2f}s  hops={r['hops']}")
        print()
        time.sleep(2)

    print("=" * 58)
    print(f"응답시간 (워밍업 제외, n={len(acc['pure'])})\n")
    base = None
    for name, _ in modes:
        rows = acc[name]
        if not rows:
            continue
        tot = [r["total"] for r in rows]
        med = statistics.median(tot)
        if base is None:
            base = med
        ret = [r["retrieve"] for r in rows if r["retrieve"] is not None]
        gen = [r["generate"] for r in rows if r["generate"] is not None]
        hop = statistics.mean(r["hops"] for r in rows)
        parts = ""
        if ret:
            parts = (f"  (검색 {statistics.median(ret):.2f} + "
                     f"생성 {statistics.median(gen):.2f})")
        print(f"  {name:8} 중앙값 {med:6.2f}s  [{min(tot):.2f}–{max(tot):.2f}]"
              f"  {med/base:5.2f}배{parts}  평균 홉 {hop:.1f}")

    print("\n※ 중앙값을 쓴다 — 무료 티어 대기열로 이상값이 섞인다")
    print("⚠️ 절대값은 API 대기열에 좌우되므로 모드 간 상대 비교로만 사용")


if __name__ == "__main__":
    main()
