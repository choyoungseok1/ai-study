"""
Gold Context 실험 — 검색을 우회한 정답률 상한
2026-08-17 (Week 18)

⚠️ 왜 필요한가
  방어 노트 Q3의 가장 약한 지점이 "생성이 병목"의 근거였다.
  현재 근거는 두 가지뿐인데 둘 다 간접적이다:
    ① recall 0.925인데 EM 0.350 (소거법)
    ② 실패 사례 육안 검수 몇 건
  → 면접에서 "직접 측정 안 하셨네요"가 되는 자리.

  Gold Context 는 그 공백을 직접 메운다.
  **정답 문서만 컨텍스트에 넣고 답을 생성**하면 검색이 완벽할 때의 상한이 나온다.

★ 선행연구
  arXiv 2601.19827 "When Iterative RAG Beats Ideal Evidence" 가
  No Context / Gold Context / Iterative RAG 세 조건을 비교한다.
  이 스크립트는 그중 Gold Context 를 내 파이프라인에 적용한 것.

해석
  | 결과                          | 뜻                                      |
  |------------------------------|----------------------------------------|
  | Gold EM ≈ agentic EM (recall 1.0 구간) | 생성이 천장. 검색 개선으로 안 풀린다     |
  | Gold EM  > agentic EM        | 방해 문서가 해치고 있다 → 정밀도 문제     |
  | Gold EM  < agentic EM        | ⚠️ 반복이 추론을 돕는다. 근거가 '어떻게'  |
  |                              |    도착하는지가 중요하다는 뜻            |

⚠️ 세 번째가 나오면 README 서술을 고쳐야 한다.
   현재 "남은 손실은 여러 문서를 엮어 추론하는 단계에 있다"로 썼는데,
   그 경우 "단계적 탐색 자체가 추론을 돕는다"는 다른 (더 강한) 주장이 된다.

실행: projects/multihop-agentic-rag/ 에서
      python -m scripts.gold_context
"""
import os
import json
import time
import datetime

from src.agent import (
    generate_answer, load_done, load_scored, append_record, _DATA,
)
from src.answer_eval import score_answer

# ⚠️ corpus 는 제목 → 본문 복원용. context_precision.py 와 같은 파일을 쓴다.
#    정의가 다르면 gold 문서 본문이 달라져 비교가 깨진다.
_HERE = os.path.dirname(os.path.abspath(__file__))
_EVAL_DIR = os.path.join(_DATA, "eval")
BASE = os.path.join(_EVAL_DIR, "answer_v2_n50.jsonl")     # 비교 대상 (agentic)
OUT = os.path.join(_EVAL_DIR, "gold_context.jsonl")

SLEEP_SEC = 2
ONLY_TYPE = None          # "bridge" 로 좁히려면 여기서 지정. None = 전체


def load_corpus():
    """제목 → 본문. 지연 로드."""
    path = os.path.join(_DATA, "corpus.json")
    return json.load(open(path, encoding="utf-8"))


def main():
    corpus = load_corpus()
    records = load_scored(BASE)
    targets = [r for r in records
               if not r.get("error")
               and (ONLY_TYPE is None or r.get("type") == ONLY_TYPE)]

    done = load_done(OUT)
    if done:
        print(f"이미 완료된 {len(done)}개 건너뜀")
    todo = [r for r in targets if r["idx"] not in done]
    print(f"대상 {len(targets)}문항 중 {len(todo)}문항 실행\n")

    skipped = []
    for n, src in enumerate(todo, 1):
        i = src["idx"]
        gold_titles = src["gold_titles"]
        gold_answer = src.get("gold_answer")

        # ⚠️ corpus 에 없는 gold 제목이 있으면 그 문항은 제외한다.
        #    일부만 넣고 "gold context"라고 부르면 정의가 깨진다.
        missing = [t for t in gold_titles if t not in corpus]
        if missing or gold_answer is None:
            skipped.append((i, missing or "gold_answer 없음"))
            continue

        rec = {
            "idx": i,
            "question": src["question"],
            "type": src.get("type"),
            "gold_titles": gold_titles,
            "gold_answer": gold_answer,
            "error": None,
            "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        }
        try:
            pairs = [(t, corpus[t]) for t in gold_titles]
            pred = generate_answer(src["question"], pairs)
            out = {"answer": pred, "n_docs": len(pairs)}
            out.update(score_answer(pred, gold_answer))
            rec["gold_ctx"] = out
            print(f"[{i}] em={out['em']:.0f} f1={out.get('f1', 0):.2f}  "
                  f"docs={len(pairs)}  {src['question'][:42]}")
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

    if skipped:
        print(f"\n⚠️ 제외 {len(skipped)}문항 (gold 본문 결측 등)")
        for i, why in skipped[:5]:
            print(f"    idx {i}: {why}")

    compare()


def compare():
    """agentic vs gold context 대응표본."""
    # ⚠️ load_scored: 저장된 em/f1 을 버리고 현재 정규화로 재채점한다.
    #   2026-08-17 U+2011 누락으로 저장값이 낡았다.
    gold = {r["idx"]: r["gold_ctx"] for r in load_scored(OUT) if not r.get("error")}
    base = {r["idx"]: r for r in load_scored(BASE) if not r.get("error")}
    idxs = sorted(set(gold) & set(base))
    if not idxs:
        print("\n비교할 공통 idx 없음")
        return

    print("\n" + "=" * 68)

    def block(label, sel):
        ids = [i for i in idxs if sel(base[i])]
        if not ids:
            return
        n = len(ids)
        g = sum(gold[i]["em"] for i in ids) / n
        a = sum(base[i]["agentic"]["em"] for i in ids) / n
        p = sum(base[i]["pure"]["em"] for i in ids) / n
        d = [gold[i]["em"] - base[i]["agentic"]["em"] for i in ids]
        md = sum(d) / n
        var = sum((x - md) ** 2 for x in d) / (n - 1) if n > 1 else 0
        se = (var / n) ** 0.5
        print(f"\n{label} (n={n})")
        print(f"  pure EM      {p:.3f}")
        print(f"  agentic EM   {a:.3f}")
        print(f"  gold ctx EM  {g:.3f}   ← 검색이 완벽할 때의 상한")
        print(f"  gold − agentic = {md:+.3f}  95% CI [{md-1.96*se:+.3f}, {md+1.96*se:+.3f}]")

    block("전체", lambda r: True)
    block("bridge", lambda r: r.get("type") == "bridge")
    block("comparison", lambda r: r.get("type") == "comparison")

    # ★ 핵심: agentic 이 이미 gold 를 다 찾은 구간
    #   여기서 gold ctx 와 차이가 없으면 "생성이 천장"이 직접 확인된다
    ids = [i for i in idxs if base[i]["agentic"]["recall"] == 1.0]
    if ids:
        n = len(ids)
        g = sum(gold[i]["em"] for i in ids) / n
        a = sum(base[i]["agentic"]["em"] for i in ids) / n
        print(f"\n★ agentic recall=1.0 구간 (n={n})")
        print(f"  agentic EM   {a:.3f}")
        print(f"  gold ctx EM  {g:.3f}")
        print(f"  차이 {g-a:+.3f}")
        print("\n  해석: 같은 gold 문서를 봤는데도 EM 이 다르면 차이는")
        print("        **방해 문서의 존재**에서 온다 (agentic 은 gold + 잡음을 함께 본다).")
        print("        차이가 없으면 잡음이 해롭지 않다는 뜻.")

    print("\n⚠️ 이 실험은 '검색이 완벽하면 어디까지 가나'만 답한다.")
    print("   No Context(무검색) 조건은 별도 실험이 필요하다 —")
    print("   그것 없이는 파라메트릭 지식 기여를 분리할 수 없다.")


if __name__ == "__main__":
    main()
