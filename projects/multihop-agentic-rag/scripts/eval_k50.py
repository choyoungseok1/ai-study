"""
B 실험 — k=50 예산에서 정답률(EM)도 따라잡히는가
2026-08-11 (Week 17)

배경
  recall 곡선에서 bridge는 pure RAG가 k=50에 이르러야 agentic recall에 근접했다.
  그렇다면 "검색이 따라잡힌 지점에서 답도 따라잡히는가"가 남는다.
  recall과 정답률은 다른 축이므로 따로 재야 한다.

설계
  - 대상: bridge, idx 오름차순 앞 22문항
    ⚠️ 22는 TPD 제약에서 나온 수다(질문당 약 7.5k 토큰 × 22 ≈ 165k).
       결과를 보고 문항을 고르면 체리피킹이므로 인덱스 순으로 고정한다.
  - 비교 상대는 v2 평가의 agentic EM (같은 질문, 대응표본)
  - 이어하기 지원. TPD/TPM 으로 죽어도 이어서 채운다

실행: projects/multihop-agentic-rag/ 에서
      python -m scripts.eval_k50
"""
import os
import json
import time
import datetime

from src.agent import (
    eval_pure_budget, load_done, load_records, append_record, _DATA,
)

K = 50
N_TARGET = 22           # TPD 제약. 늘리려면 남은 토큰을 먼저 확인할 것
SLEEP_SEC = 7           # ⚠️ TPM 회피용. TPD와 달리 TPM 은 기다리면 풀린다

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(os.path.dirname(_HERE), "data")
_EVAL_DIR = os.path.join(_DATA, "eval")
OUT = os.path.join(_EVAL_DIR, f"pure_k{K}_bridge.jsonl")


def pick_targets():
    """bridge 질문을 idx 오름차순으로 앞 N_TARGET개.

    ⚠️ idx 는 qa 리스트에서의 위치여야 한다. v2 평가와 같은 기준이라야
       나중에 agentic 결과와 짝을 맞출 수 있다.
    """
    qa = json.load(open(os.path.join(_DATA, "qa.json"), encoding="utf-8"))
    out = []
    for i, item in enumerate(qa[:50]):
        if item.get("type") == "bridge":
            out.append((i, item))
        if len(out) == N_TARGET:
            break
    return out


def main():
    targets = pick_targets()
    done = load_done(OUT)
    if done:
        print(f"이미 완료된 {len(done)}개 건너뜀")

    todo = [(i, x) for i, x in targets if i not in done]
    print(f"대상 {len(targets)}문항 중 {len(todo)}문항 실행 (k={K})\n")

    for n, (i, item) in enumerate(todo, 1):
        rec = {
            "idx": i,
            "question": item["question"],
            "type": item.get("type"),
            "gold_titles": item["gold_titles"],
            "gold_answer": item.get("answer"),
            "k": K,
            "error": None,
            "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        }
        try:
            r = eval_pure_budget(
                item["question"], item["gold_titles"],
                k=K, gold_answer=item.get("answer"),
            )
            rec["pure_k50"] = r
            print(f"[{i}] recall={r['recall']:.2f} em={r['em']:.0f} "
                  f"f1={r.get('f1', 0):.2f}  {item['question'][:45]}")
        except Exception as e:
            rec["error"] = f"{type(e).__name__}: {e}"
            print(f"[{i}] ERROR {rec['error'][:80]}")
            # ⚠️ TPD 소진이면 남은 문항도 전부 실패한다. 즉시 중단이 옳다.
            #    TPM 은 기다리면 풀리므로 구분해서 처리한다.
            if "rate_limit" in rec["error"] and "per day" in rec["error"]:
                append_record(OUT, rec)
                print("\n⚠️ TPD 소진. 남은 문항은 내일 이어하기로 회수한다.")
                break

        append_record(OUT, rec)
        if n < len(todo):
            time.sleep(SLEEP_SEC)

    summarize(load_records(OUT))


def summarize(records):
    ok = [r for r in records if not r.get("error")]
    if not ok:
        print("\n집계할 레코드 없음")
        return

    n = len(ok)
    rec = sum(r["pure_k50"]["recall"] for r in ok) / n
    em = sum(r["pure_k50"]["em"] for r in ok) / n
    f1 = sum(r["pure_k50"].get("f1", 0) for r in ok) / n

    print("\n" + "=" * 55)
    print(f"pure_budget k={K}  (bridge, n={n})")
    print(f"  recall {rec:.3f}   EM {em:.3f}   F1 {f1:.3f}")
    print("\n※ 같은 idx의 agentic 결과와 짝지어 비교할 것.")
    print("  ⚠️ 전체 평균끼리 빼지 말 것 — 대응표본이므로 질문별 차이를 내야")
    print("     신뢰구간이 나온다. n 이 다르면 비교 자체가 성립하지 않는다.")


if __name__ == "__main__":
    main()
