# 📚 이번 주 논문 추천 — Week 12 (2026-07-07 ~)

> **현재 학습 주제** (Notion 학습용 캘린더 기준): **Week 12 — "논문 1편 (RAG 평가 / Agentic RAG 계열) + 리뷰 + Lv2 1문제"**
> 캘린더 메모: *"프로젝트 방향에 맞춘 논문 선택. 노션에 4단 양식으로 정리"*
> 직전 주차에는 PEFT 계열(DoRA)을 마쳤고, 이번 주는 **RAG 평가 + Agentic(에이전트형) RAG**가 초점입니다.
>
> **선정 기준**: ① 주제 적합(RAG 평가 / Agentic RAG) · ② 코드 공개 · ③ 최신(2024–2025) · ④ 분량 15p 이내(본문 기준). 아래 3편이 이번 주 메인, 마지막 1편은 심화용(분량 초과)입니다.

---

## ✅ 추천 1 — R1-Searcher: RL로 LLM에 "검색 능력"을 학습시키기
**Agentic RAG · 강화학습 · 코드 공개 · 2025.03**

**초록 요약**
기존 Large Reasoning Model은 수학·코딩 등에서는 강하지만, 내부 지식에만 의존하기 때문에 시의성 있거나 지식 집약적인 질문에서는 부정확·환각(hallucination)이 발생합니다. R1-Searcher는 이를 해결하기 위한 **2단계 outcome-based 강화학습** 기법으로, LLM이 추론 과정 중 **스스로 외부 검색 시스템을 호출**해 지식을 획득하도록 학습시킵니다. process reward나 distillation cold-start 없이 **오직 RL만으로** 동작하며, out-of-domain 데이터로의 일반화와 Base/Instruct 모델 모두를 지원합니다. 실험에서 강력한 기존 RAG 기법은 물론 closed-source GPT-4o-mini까지 능가했습니다.

**추천 이유 (3줄)**
1. "검색을 언제·어떻게 호출할지"를 프롬프트가 아니라 **RL로 학습**시키는 Agentic RAG의 대표 출발점 논문입니다.
2. process reward 없이 **outcome reward만으로** 학습해 구조가 단순 → 리뷰·재현이 쉽고 4단 양식 정리에 적합합니다.
3. 이번 주 뒤 두 편(R1-Searcher++, Search-R1)을 이해하기 위한 **베이스라인**이라 첫 논문으로 최적입니다.

- 🔗 **arXiv**: https://arxiv.org/abs/2503.05592
- 💻 **코드**: https://github.com/RUCAIBox/R1-Searcher
- 📝 **한글 해설**: [themoonlight 논문 리뷰](https://www.themoonlight.io/en/review/r1-searcher-incentivizing-the-search-capability-in-llms-via-reinforcement-learning)
- 📄 분량: 본문 약 10p (+부록) — **15p 이내 충족**

---

## ✅ 추천 2 — R1-Searcher++: 내부 지식 + 외부 검색을 "적응적"으로
**Agentic RAG · 검색 효율화 · 코드 공개 · 2025.05**

**초록 요약**
RAG는 외부 정보를 주입해 환각을 줄이지만, 현재 방법들은 (1) 비용이 크거나 (2) 일반화가 약하거나 (3) 모델의 내부 지식을 무시하는 문제가 있습니다. R1-Searcher++는 LLM이 **내부 지식과 외부 검색을 적응적으로 함께 활용**하도록 학습하는 프레임워크입니다. **2단계 전략**(SFT Cold-start → Dynamic Knowledge Acquisition을 위한 RL)을 쓰며, RL 단계에서 내부 지식 활용을 유도하는 reward와 검색 결과를 내부 지식으로 지속 흡수하는 **memorization 메커니즘**을 결합합니다. 결과적으로 성능을 높이면서(예: 최고 vanilla RL 대비 LasJ +4.3%) **평균 검색 횟수를 42.9% 절감**해 "사람처럼 아는 건 먼저 떠올리고, 모를 때만 검색"하는 효율적 RAG를 구현합니다.

**추천 이유 (3줄)**
1. 추천 1의 **직계 후속작**이라 함께 읽으면 "무조건 검색 → 필요할 때만 검색"으로의 발전 흐름이 명확히 보입니다.
2. **검색 횟수(비용) 절감**이라는 실서비스 핵심 지표를 정면으로 다뤄 프로젝트 적용 가치가 큽니다.
3. 내부 지식 재사용 + memorization 아이디어가 신선해 리뷰에서 **비판적 논점(일반화·안정성)**을 잡기 좋습니다.

- 🔗 **arXiv**: https://arxiv.org/abs/2505.17005
- 💻 **코드**: https://github.com/RUCAIBox/R1-Searcher-plus
- 📝 **한글 해설**: [themoonlight 논문 리뷰](https://www.themoonlight.io/en/review/r1-searcher-incentivizing-the-dynamic-knowledge-acquisition-of-llms-via-reinforcement-learning)
- 📄 분량: 본문 약 10p (+부록) — **15p 이내 충족**

---

## ✅ 추천 3 — RAGChecker: RAG를 "세분화 지표"로 진단하는 평가 프레임워크
**RAG 평가 · 진단 지표 · 코드 공개(pip 설치) · NeurIPS 2024**

**초록 요약**
RAG 시스템은 검색(retrieval)과 생성(generation) 모듈이 결합된 구조라 종합 평가가 어렵고, 특히 긴 답변(long-form)의 정확도 측정과 지표 신뢰성이 문제입니다. RAGChecker는 **검색·생성 각 모듈을 세분화해 진단**하는 지표 모음(claim 단위 entailment 기반)을 제공하는 평가 프레임워크입니다. 메타 평가 결과 기존 지표보다 **사람 판단과의 상관관계가 유의하게 높았고**, 이를 이용해 8개 RAG 시스템을 분석하여 설계 선택에 따른 trade-off(예: 검색 품질 vs. 생성 충실도)를 드러냈습니다.

**추천 이유 (3줄)**
1. 이번 주 주제의 다른 축인 **"RAG 평가"**를 정면으로 다루는 대표 논문으로, 방법론(1·2번)과 짝을 이룹니다.
2. `pip install ragchecker`로 **바로 실행 가능** → 본인 프로젝트 RAG에 지표를 붙여보는 실습까지 연결됩니다.
3. retrieval/generation을 분리 진단하는 관점이 **RAG 디버깅 사고 틀**을 잡아줘 실무 가치가 높습니다.

- 🔗 **arXiv**: https://arxiv.org/abs/2408.08067
- 💻 **코드**: https://github.com/amazon-science/RAGChecker
- 📝 **한글 참고**: [RAG 평가 관련 논문 리스트 정리 (velog)](https://velog.io/@cathx618/RAG-%EA%B4%80%EB%A0%A8-%EB%85%BC%EB%AC%B8-%EB%A6%AC%EC%8A%A4%ED%8A%B8-%EC%A0%95%EB%A6%AC) · [VERA — RAG 검증과 평가 (모두의연구소)](https://modulabs.co.kr/blog/vera-rag-%EA%B2%80%EC%A6%9D%EA%B3%BC-%ED%8F%89%EA%B0%80)
- 📄 분량: 본문 약 10p (+부록) — **15p 이내 충족**

> ℹ️ RAGChecker 자체의 한글 단독 리뷰 블로그는 검색되지 않아, 같은 "RAG 평가" 주제의 한글 자료로 대체했습니다.

---

## ⭐ 심화(선택) — Search-R1: 검색 엔진과 상호작용하는 추론을 RL로 학습
**Agentic RAG · 강화학습 · 코드+체크포인트 공개 · 2025.03**

**초록 요약**
Search-R1은 LLM이 단계별 추론 도중 **여러 개의 검색 쿼리를 자율 생성**하고 실시간 검색을 수행하도록 RL로 학습하는 프레임워크입니다. 멀티턴 검색 상호작용으로 추론 궤적을 최적화하며, 안정적 학습을 위한 **retrieved token masking**과 단순한 outcome-based reward를 사용합니다. 7개 QA 데이터셋에서 다양한 RAG 베이스라인 대비 Qwen2.5-7B 41%, 3B 20% 성능 향상을 보였고, RL 최적화 방식·모델 선택·응답 길이 동역학에 대한 실증적 통찰도 제공합니다.

**추천 이유 (3줄)**
1. R1-Searcher와 **동시기·동일 문제의식**의 쌍둥이 논문이라 비교 리뷰로 읽으면 이해가 깊어집니다.
2. **코드와 모델 체크포인트가 모두 공개**되어 재현·실습 자료가 가장 풍부합니다.
3. 한글 블로그 리뷰가 여러 편 있어 진입 장벽이 낮습니다.

- 🔗 **arXiv**: https://arxiv.org/abs/2503.09516
- 💻 **코드**: https://github.com/PeterGriffinJin/Search-R1
- 📝 **한글 해설**: [facerain 블로그](https://facerain.me/nonmun-ribyu-search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning/) · [velog 리뷰](https://velog.io/@d4r6j/Search-R1-paper-review)
- ⚠️ 분량: **31p — 15p 초과**. 본문+부록이 길어 이번 주 "1편 정독"보다는 참고/발췌 추천.

---

## 🗺️ 이번 주 추천 읽기 순서
1. **R1-Searcher** (기초 개념 잡기) →
2. **R1-Searcher++** (효율화·발전 흐름) →
3. **RAGChecker** (만든 RAG를 평가·진단하는 법)
4. 여유가 되면 **Search-R1**을 R1-Searcher와 비교 발췌.

> 캘린더 지시대로 "1편만" 고른다면 → **R1-Searcher (추천 1)** 를 정독하고 4단 양식으로 정리하는 것을 권장합니다. 프로젝트가 "RAG 평가"에 더 가깝다면 **RAGChecker (추천 3)** 를 메인으로 잡으세요.

---

### 자동 실행 안내
- 이 목록은 예약 작업으로 **Notion 학습용 캘린더의 Week 12 항목**을 읽어 자동 생성했습니다.
- 검증: 각 arXiv 페이지를 직접 조회해 초록·코드 공개 여부를 확인했습니다. 단, 검색으로 노출된 일부 2026년 arXiv ID(예: A-RAG 등)는 원문 접근이 제한되어 **검증 실패로 제외**했고, 원문을 직접 확인한 논문만 실었습니다.
