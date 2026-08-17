"""
No Context 실험 — 파라메트릭 지식만으로 얼마나 답하나
2026-08-17 (Week 18)

⚠️ 왜 필요한가
  Gold Context 실험에서 bridge EM 0.649 가 나왔다.
  그런데 그 0.649 가 **gold 문서 덕인지 모델이 원래 알던 것인지** 모른다.
  문서를 아예 주지 않았을 때의 EM 을 재야 gold 문서의 기여를 분리할 수 있다.

  분해:
      No Context   →  파라메트릭 지식만
      Gold Context →  파라메트릭 + 완벽한 근거
      차이         =  **gold 문서가 실제로 기여한 몫**

★ 두 가지를 동시에 닫는다
  ① Gold Context 0.649 의 해석 (위)
  ② 방어 노트 미확정 1번 —
     "bridge 1홉 종료가 암묵적 무검색(A) 경로인가"
     1홉에서 멈춘 17문항이 무검색으로도 잘 답한다면
     그 종료는 "이미 안다"의 신호였다는 뜻이다.
     ⚠️ 기존 근거는 n=5, CI [0.23, 0.88] 로 아무것도 말할 수 없었다.

★ 선행연구
  arXiv 2601.19827 이 No Context / Gold Context / Iterative 세 조건을 쓴다.
  이 스크립트로 세 조건이 모두 채워진다.

⚠️ 주의 — 이 실험은 HotpotQA 가 closed-domain 이라는 전제를 흔든다.
   무검색 EM 이 높게 나오면 "검색 성능 = 정답률" 이라는 가정이 약해지고,
   프로젝트의 recall 중심 서술에 단서를 달아야 한다.
   결과가 불리해도 그대로 기록한다.

실행: projects/multihop-agentic-rag/ 에서
      python -m scripts.no_context
"""
import os
import time
import datetime

from src.agent import load_done, load_scored, append_record, _DATA
from src.answer_eval import score_answer
from src.llm import default_provider

_EVAL_DIR = os.path.join(_DATA, "eval")
BASE = os.path.join(_EVAL_DIR, "answer_v2_n50.jsonl")
GOLD = os.path.join(_EVAL_DIR, "gold_context.jsonl")
OUT = os.path.join(_EVAL_DIR, "no_context.jsonl")

SLEEP_SEC = 2


def answer_without_context(question):
    """문서 없이 질문만 주고 답을 받는다.

    ⚠️ 프롬프트를 generate_answer 와 최대한 맞춘다.
      형식 지시가 다르면 EM 차이가 '지식 차이'가 아니라 '형식 차이'가 된다.
      2026-08-06 실측: 답변 형식 지시만 바꿔도 지표가 움직였다.
    """
    prompt = (
        "Answer the question with a short phrase. "
        "Do not explain. If you do not know, answer with your best guess.\n\n"
        f"Question: {question}\n"
        "Answer:"
    )
    r = default_provider().chat(
        [{"role": "user", "content": prompt}],
        temperature=0,
    )
    return (r.text or "").strip()


def main():
    records = load_scored(BASE)
    targets = [r for r in records if not r.get("error") and r.get("gold_answer")]

    done = load_done(OUT)
    if done:
        print(f"이미 완료된 {len(done)}개 건너뜀")
    todo = [r for r in targets if r["idx"] not in done]
    print(f"대상 {len(targets)}문항 중 {len(todo)}문항 실행\n")

    for n, src in enumerate(todo, 1):
        i = src["idx"]
        rec = {
            "idx": i,
            "question": src["question"],
            "type": src.get("type"),
            "gold_answer": src["gold_answer"],
            "error": None,
            "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        }
        try:
            pred = answer_without_context(src["question"])
            out = {"answer": pred}
            out.update(score_answer(pred, src["gold_answer"]))
            rec["no_ctx"] = out
            print(f"[{i}] em={out['em']:.0f} f1={out.get('f1', 0):.2f}  "
                  f"pred={pred[:28]:30} gold={src['gold_answer'][:20]}")
        except Exception as e:
            rec["error"] = f"{type(e).__name__}: {e}"
            print(f"[{i}] ERROR {rec['error'][:80]}")
            if "per day" in rec["error"]:
                append_record(OUT, rec)
                print("\n⚠️ TPD 소진. 이어하기로 회수한다.")
                break

        append_record(OUT, rec)
        if n < len(todo):
            time.sleep(SLEEP_SEC)

    compare()


def compare():
    # ⚠️ load_scored: 저장된 em/f1 을 버리고 현재 정규화로 재채점한다.
    no = {r["idx"]: r["no_ctx"] for r in load_scored(OUT) if not r.get("error")}
    base = {r["idx"]: r for r in load_scored(BASE) if not r.get("error")}
    gold = {}
    if os.path.exists(GOLD):
        gold = {r["idx"]: r["gold_ctx"] for r in load_scored(GOLD) if not r.get("error")}

    idxs = sorted(set(no) & set(base))
    if not idxs:
        print("\n비교할 공통 idx 없음")
        return

    print("\n" + "=" * 70)

    def ci(diffs):
        n = len(diffs)
        m = sum(diffs) / n
        var = sum((x - m) ** 2 for x in diffs) / (n - 1) if n > 1 else 0
        se = (var / n) ** 0.5
        return m, m - 1.96 * se, m + 1.96 * se

    def block(label, sel):
        ids = [i for i in idxs if sel(base[i])]
        if not ids:
            return
        n = len(ids)
        nc = sum(no[i]["em"] for i in ids) / n
        pu = sum(base[i]["pure"]["em"] for i in ids) / n
        ag = sum(base[i]["agentic"]["em"] for i in ids) / n
        print(f"\n{label} (n={n})")
        print(f"  no context   {nc:.3f}   ← 파라메트릭 지식만")
        print(f"  pure         {pu:.3f}")
        print(f"  agentic      {ag:.3f}")
        gi = [i for i in ids if i in gold]
        if gi:
            gc = sum(gold[i]["em"] for i in gi) / len(gi)
            print(f"  gold context {gc:.3f}   ← 완벽한 근거 (n={len(gi)})")
            d = [gold[i]["em"] - no[i]["em"] for i in gi]
            m, lo, hi = ci(d)
            print(f"  ★ gold − no ctx = {m:+.3f} 95% CI [{lo:+.3f}, {hi:+.3f}]")
            print(f"    = gold 문서가 실제로 기여한 몫")
        d = [base[i]["agentic"]["em"] - no[i]["em"] for i in ids]
        m, lo, hi = ci(d)
        print(f"  agentic − no ctx = {m:+.3f} 95% CI [{lo:+.3f}, {hi:+.3f}]")

    block("전체", lambda r: True)
    block("bridge", lambda r: r.get("type") == "bridge")
    block("comparison", lambda r: r.get("type") == "comparison")

    # ★★ 방어 노트 미확정 1번 — 1홉 종료가 암묵적 무검색 경로인가
    print("\n" + "=" * 70)
    print("★ bridge 홉 수별 — 1홉 종료가 '이미 안다'의 신호인가\n")
    for label, sel in [
        ("1홉 종료", lambda r: len(r["agentic"]["search_log"]) == 1),
        ("2홉 이상", lambda r: len(r["agentic"]["search_log"]) >= 2),
    ]:
        ids = [i for i in idxs
               if base[i].get("type") == "bridge" and sel(base[i])]
        if not ids:
            continue
        n = len(ids)
        nc = sum(no[i]["em"] for i in ids) / n
        ag = sum(base[i]["agentic"]["em"] for i in ids) / n
        print(f"  {label:9} n={n:2}  no ctx EM {nc:.3f}   agentic EM {ag:.3f}   "
              f"차이 {ag-nc:+.3f}")

    print("\n  해석")
    print("    1홉 구간의 no ctx EM 이 2홉+ 구간보다 **높으면**")
    print("    → 에이전트는 '이미 아는 질문'에서 1홉에 멈춘다 = 암묵적 무검색 경로")
    print("    비슷하면 → 1홉 종료는 지식 여부와 무관하다")
    print("  ⚠️ 관찰이지 인과가 아니다. 종료 시점에 무엇을 근거로 멈췄는지는")
    print("     이 실험으로 알 수 없다.")


if __name__ == "__main__":
    main()
