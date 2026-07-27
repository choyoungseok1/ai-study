# 이번 주 논문 추천 (2026-07-27, Week 15)

> 자동 실행 결과. Notion 「학습용 캘린더」 확인 → 현재 진행 중인 **멀티홉 Agentic RAG 시스템 (Phase A · W3)** 주제에 맞춰 선별.
> 이번 주 작업: 평가 실행(비교군 3종 × 50~100문항) → 결과 분석/표 → **정체(stuck) 감지** 과제 도출. 7/28(화)이 논문 리뷰일이라 여기서 1편 골라 4단 양식으로 정리하면 됩니다.
>
> **선별 기준**: 본문 15쪽 이내 · 코드 공개 · 프로젝트 W3(라우팅/멀티홉/평가/정체 감지)와 직접 연결 · 가능한 한 최신.
> **자동 판단 메모**: 딱 맞는 후보였던 Self-RAG(2310.11511)는 전체 30쪽이라 15쪽 제한으로 제외. 대신 라우팅·멀티홉·평가·최신 RL 4축으로 1편씩 골랐습니다.

---

## 우선순위 요약

| # | 논문 | 왜 이번 주에 딱인가 | 코드 | 최신도 |
|---|------|--------------------|------|--------|
| 1 | **Adaptive-RAG** | "복잡도 분기기" 방어 카드의 원조 논문 | ✅ | NAACL 2024 |
| 2 | **RAGAS** | W3-2/W3-3에서 지금 쓰는 평가 프레임워크 그 자체 | ✅ | EACL 2024 |
| 3 | **IRCoT** | ReAct 루프·멀티홉 검색의 직계 선행연구 | ✅ | ACL 2023 |
| 4 | **Search-R1** | 정체 감지→다음 검색어 생성을 RL로 학습(최신) | ✅ | 2025 |

**7/28 리뷰 1편만 고른다면 → ①Adaptive-RAG** (모의면접 "왜 Agentic / 복잡도 분기" 방어와 직결, 본문 짧고 코드 명확).

---

## 1. Adaptive-RAG: Learning to Adapt Retrieval-Augmented LLMs through Question Complexity

- **arXiv**: https://arxiv.org/abs/2403.14403  (NAACL 2024, 본문 ~9쪽 / 15쪽 이내 ✅)
- **코드**: https://github.com/starsuzi/Adaptive-RAG ✅
- **한글 해설**:
  - velog 논문 리뷰 — https://velog.io/@yeomsee97/Adaptive-RAG-Learning-to-Adapt-Retrieval-Augmented-Large-Language-Models-through-Question-Complexity
  - 모두의연구소 「한단계 진화한 Adaptive RAG」 — https://modulabs.co.kr/community/momos/8/feeds/344

**초록(요약)**: 질문마다 필요한 검색 전략이 다르다는 관찰에서 출발한다. 단순 질문에 반복 검색을 쓰면 낭비이고, 복잡한 멀티홉 질문에 단일 검색이나 무검색을 쓰면 정답을 놓친다. 저자들은 작은 분류기(smaller LM)를 학습시켜 들어오는 질문의 복잡도를 예측하고, 그 결과에 따라 **무검색 / 단일 검색 / 반복(iterative) 검색** 중 최적 전략으로 동적 라우팅한다. 복잡도 라벨은 모델의 실제 예측 성공/실패와 데이터셋 편향에서 자동 수집한다. 오픈도메인 QA 전반에서 효율과 정확도의 균형을 크게 개선.

**추천 이유 (3줄)**
1. 프로젝트의 "복잡도 분기기"·"순수 RAG vs Agentic 라우팅"이 바로 이 논문의 핵심 — 모의면접 방어 카드의 이론적 근거.
2. 단일/반복 검색을 질문 복잡도로 가르는 분류기 설계가 곧바로 내 코드에 이식 가능(경량 LM 라우터).
3. 본문이 짧고 코드가 깔끔해 7/28 4단 양식 리뷰 + Lv2 병행에 부담 없음.

---

## 2. RAGAS: Automated Evaluation of Retrieval Augmented Generation

- **arXiv**: https://arxiv.org/abs/2309.15217  (EACL 2024 demo, 본문 ~5쪽 / 15쪽 이내 ✅)
- **코드**: https://github.com/explodinggradients/ragas ✅
- **한글 해설**:
  - velog 「우아한 스터디: RAGAS 평가 프레임워크」 — https://velog.io/@judy_choi/우아한-스터디-RAGAS-RAG-파이프라인-평가-프레임워크
  - 랭체인 노트(wikidocs) RAGAS 평가 — https://wikidocs.net/259205
  - SK DevOcean Faithfulness 해설 — https://devocean.sk.com/community/detail.do?ID=166209&boardType=DEVOCEAN_STUDY

**초록(요약)**: RAG 파이프라인을 **정답 주석(ground truth) 없이** 평가하는 참조-프리 프레임워크. 검색·생성 각 모듈을 세 축 — Faithfulness(답변이 컨텍스트에 근거하는가), Answer Relevance(질문에 적절한가), Context Relevance(검색 문맥이 초점을 맞췄는가) — 으로 나눠 측정한다. LLM 자체를 평가자(judge)로 써서 진술(statement) 단위로 근거 여부를 채점하므로 사람 라벨링 비용을 없앤다.

**추천 이유 (3줄)**
1. W3-2(RAGAS 안정화)·W3-3(평가 실행)에서 지금 바로 돌리는 도구의 원 논문 — 지표 정의를 원전으로 이해하면 judge 모델/RunConfig 선택 근거가 단단해짐.
2. "recall ≠ answer accuracy" 문제(qa[18]) 대응으로 도입 중인 context_precision·faithfulness의 계산 논리를 정확히 파악 가능.
3. answer_relevancy가 Groq n=1 제약으로 NaN 나는 이유(지표의 샘플링 전제)를 논문에서 확인 → 제외 문서화 근거로 인용.

---

## 3. IRCoT: Interleaving Retrieval with Chain-of-Thought Reasoning for Multi-Step Questions

- **arXiv**: https://arxiv.org/abs/2212.10509  (ACL 2023, 본문 ~12쪽 / 15쪽 이내 ✅)
- **코드**: https://github.com/StonyBrookNLP/ircot ✅
- **한글 해설**: 완전한 한글 리뷰는 미발견. 대안 — 영문 정리(themoonlight/alphaXiv) 또는 arXiv HTML(https://arxiv.org/html/2212.10509v2). *리뷰 시 본인이 한글 요약을 남기면 첫 한글 자료가 됩니다.*

**초록(요약)**: 멀티홉 질문에서는 "다음에 무엇을 검색할지"가 "지금까지 추론한 내용"에 달려 있다. IRCoT는 검색과 CoT 추론을 **번갈아(interleave)** 수행한다 — CoT 한 문장을 생성해 다음 검색을 안내하고, 검색 결과로 다시 CoT를 이어간다. HotpotQA·2WikiMultihopQA·MuSiQue·IIRC에서 검색 최대 +21점, QA 최대 +15점. 소형 모델·OOD에서도 이득, 환각 감소.

**추천 이유 (3줄)**
1. 내 ReAct 루프(Thought→Action→Observation)의 직계 선행연구 — "직전 Observation에서 다음 검색어를 만든다"는 프로젝트 핵심 서사와 정확히 일치.
2. bridge entity가 질문에 없어 단일 검색이 gold 절반을 놓치는 문제를 IRCoT가 어떻게 회수하는지, 내 recall 0.50→1.00 결과와 대조 분석 가능.
3. 평가 데이터셋(HotpotQA 등)이 내 벤치마크와 겹쳐, W3-4 결과표 해석에 바로 참고.

---

## 4. Search-R1: Training LLMs to Reason and Leverage Search Engines with RL

- **arXiv**: https://arxiv.org/abs/2503.09516  (2025, 본문 ~12쪽 / 15쪽 이내 ✅ · **가장 최신**)
- **코드**: https://github.com/PeterGriffinJin/Search-R1 ✅
- **한글 해설**: facerain.me 논문 리뷰 — https://facerain.me/nonmun-ribyu-search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning/

**초록(요약)**: 프롬프트/휴리스틱으로 검색 시점을 정하는 대신, LLM이 **강화학습(결과 기반 보상)** 으로 다단계 추론 중 언제·무엇을 검색할지 스스로 학습한다. 검색으로 삽입된 토큰은 손실 마스킹해 정책 그래디언트가 모델 생성 토큰에만 적용되도록 안정화. 7개 QA 데이터셋에서 RAG 베이스라인 대비 Qwen2.5-7B +41%, 3B +20%.

**추천 이유 (3줄)**
1. 이번 주 도출한 **정체(stuck) 감지** 과제 — "언제 검색을 멈추고 전환할지"를 규칙 대신 학습으로 푸는 최신 접근으로, 다음 스텝의 방향타.
2. multi-turn 검색·retrieved token masking 설계는 내 에이전트 루프를 RL로 확장할 때의 구체적 레시피.
3. 2025년 논문이라 이력서/포트폴리오 "최신 동향 추적" 항목으로도 활용 가치가 큼(Phase B 이후 확장 후보).

---

### 리뷰 순서 제안
- **7/28 (필수 1편)**: ①Adaptive-RAG — 방어 카드 직결 + 본문 짧음.
- **여유 시**: ②RAGAS(지금 쓰는 도구라 즉시 실전 도움) → ③IRCoT(서사 보강) → ④Search-R1(다음 방향).

_출처: Notion 「학습용 캘린더」·「멀티홉 Agentic RAG 시스템」 프로젝트 페이지, arXiv, 각 논문 공식 GitHub._
