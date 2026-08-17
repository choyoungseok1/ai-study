"""
EM/F1 재채점 — 정규화 수정 후 기존 로그 재평가
2026-08-17 (Week 18)

⚠️ 왜 필요한가
  모델이 U+2011(NON-BREAKING HYPHEN)을 출력하는데 기존 정규화가
  `string.punctuation` 만 제거해서 이 문자를 놓쳤다.

    pred "Jang Hyun‑seung"  → 'jang hyun‑seung'   (하이픈 남음)
    gold "Jang Hyun-seung"  → 'jang hyunseung'    (하이픈 제거)
    → 정답인데 EM=0

  ⚠️ 즉 지금까지의 **모든 EM 수치가 과소평가돼 있을 수 있다.**
     Phase A 결과 포함.

★ LLM 호출 0회. 저장된 answer 필드로 다시 채점만 한다.
  (지침: 원본만 저장하고 파생값은 분석 시점에 계산 — 이 설계 덕에 재채점이 가능)

실행: projects/multihop-agentic-rag/ 에서
      python -m scripts.rescore
"""
import os
import json

from src.agent import _DATA
from src.answer_eval import score_answer          # ★ 수정된 정규화가 적용된 것

_EVAL_DIR = os.path.join(_DATA, "eval")

# (파일, 모드별 접근 경로) — answer 가 들어 있는 위치가 파일마다 다르다
FILES = [
    ("answer_v2_n50.jsonl",   ["pure", "rerank", "agentic"]),
    ("pure_k50_bridge.jsonl", ["pure_k50"]),
    ("agentic_bridge_run2.jsonl", ["agentic"]),
    ("gold_context.jsonl",    ["gold_ctx"]),
    ("no_context.jsonl",      ["no_ctx"]),
]


def load_lines(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                out.append(json.loads(line))
    return out


def merge(recs):
    """idx당 1건 — 나중 것이 이긴다 (load_records 와 같은 규칙)."""
    d = {}
    for r in recs:
        d[r["idx"]] = r
    return list(d.values())


def main():
    grand = []

    for fname, modes in FILES:
        path = os.path.join(_EVAL_DIR, fname)
        if not os.path.exists(path):
            print(f"⚠️ 없음: {fname}")
            continue

        recs = merge(load_lines(path))
        ok = [r for r in recs if not r.get("error")]
        print(f"\n=== {fname}  (n={len(ok)}) ===")

        for mode in modes:
            changed = []
            old_em = new_em = 0
            cnt = 0
            for r in ok:
                blk = r.get(mode)
                if not blk or "answer" not in blk:
                    continue
                gold = r.get("gold_answer")
                if gold is None:
                    continue
                cnt += 1
                before = blk.get("em", 0)
                after = score_answer(blk["answer"], gold)
                old_em += before
                new_em += after["em"]
                if after["em"] != before:
                    changed.append((r["idx"], blk["answer"][:32], gold[:24],
                                    before, after["em"]))

            if cnt == 0:
                print(f"  {mode:10} answer 필드 없음 — 건너뜀")
                continue

            print(f"  {mode:10} EM {old_em/cnt:.3f} → {new_em/cnt:.3f}"
                  f"   ({old_em:.0f}/{cnt} → {new_em:.0f}/{cnt})"
                  f"   변동 {len(changed)}건")
            for idx, pred, gold, b, a in changed:
                print(f"      [{idx}] {b:.0f}→{a:.0f}  pred={pred!r}  gold={gold!r}")

            grand.append((fname, mode, cnt, old_em, new_em))

    # ── 요약 ────────────────────────────────
    print("\n" + "=" * 68)
    tot_c = sum(x[2] for x in grand)
    tot_o = sum(x[3] for x in grand)
    tot_n = sum(x[4] for x in grand)
    print(f"전체 채점 {tot_c}건 중 {tot_n - tot_o:+.0f}건 변동")
    if tot_n != tot_o:
        print("\n⚠️ 수치가 바뀌었다. 다음을 전부 갱신할 것:")
        print("   - README 정답률·비용 섹션의 EM")
        print("   - 방어 노트의 EM 관련 답변")
        print("   - 지침의 실측 기록")
        print("   ⚠️ 홉 수별 분해(1홉 0.706 / 2홉+ 0.350)도 다시 계산해야 한다")
    else:
        print("\n변동 없음 — 기존 수치 유지")

    print("\n⚠️ 이 스크립트는 파일을 수정하지 않는다.")
    print("   저장된 em 값은 옛 정규화 기준이므로, 이후 분석 스크립트는")
    print("   저장값을 쓰지 말고 score_answer 로 다시 계산해야 한다.")
    print("   → eval_stats.py / compare_k50.py / gold_context.py 확인 필요")


if __name__ == "__main__":
    main()
