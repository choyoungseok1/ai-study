# Week 23 회고

> 기간: 2026-05-26 (월) ~ 2026-06-01 (일)

---

## 이번 주 산출물

**코드 (8건)**
- `code/week06/CNN_pytorch.ipynb` — CNN MNIST 분류 3단계 실험 (기본 98.91% → BatchNorm+Dropout 99.25% → 증강 99.00%)
- `code/week06/RNN_pytorch.ipynb` — LSTM 텍스트 감성 분류 (vocab 구축 → 정수 인코딩 → Embedding+LSTM)
- `code/week06/pg_lv2_11_순위검색(이진탐색).py` — Lv2 "순위검색" (와일드카드 전처리 + bisect_left)
- `code/week06/pg_lv2_15_dynamicprogramming.py` — Lv2 "2×n 타일링" DP (점화식 + MOD)
- `code/week06/pg_lv2_18_viruspipe(dfs).py` — Lv2 "바이러스 파이프" DFS+BFS 혼합 풀이
- `code/week07/leaf_node_maximize.py` — 트리 리프 노드 최대화 (수학적 모델링)
- `code/week07/crane.py` — Lv2 크레인 문제 풀이
- `code/week07/server_build.py` — 서버 빌드 문제 풀이

**논문 리뷰 (1건)**
- `papers/RWKV_논문리뷰.md` — "RWKV: Reinventing RNNs for the Transformer Era" 리뷰 (선형 어텐션, 학습/추론 이중 모드)

**TIL 작성**
- 5일분 작성 (5/25, 5/26, 5/27, 5/28, 5/31) — 5/29, 5/30 미작성

---

## 배운 핵심 3가지

1. **CNN 정규화 기법 실전 비교** — BatchNorm+Dropout은 항상 성능을 높이지만, Data Augmentation은 데이터가 이미 충분할 때 오히려 성능을 낮출 수 있음 (99.25% → 99.00%). 기법을 맹목적으로 쌓지 않고 실험으로 검증하는 태도 체득
2. **DFS+BFS 혼합 전략 + RWKV 이중 모드** — 알고리즘(DFS로 선택 탐색 + BFS로 시뮬레이션)과 딥러닝(학습 시 병렬/추론 시 순차)에서 동일한 "역할 분리" 패턴 발견. 복잡도를 줄이는 핵심은 한 구조에 두 모드를 부여하는 것
3. **이진탐색·DP 실전 패턴** — "미리 정렬 + bisect_left"로 대량 쿼리 O(log n) 처리, DP에서 제한 조건(n 크기)을 먼저 보고 알고리즘을 선택하는 습관. 완전탐색 → 최적화 사고 흐름 강화

---

## 잘한 점

- **주 6일 학습 실행**: Notion 기준 7개 항목 중 6개 완료(86%) — 전주(57%) 대비 대폭 개선
- **Week 6 → Week 7 전환 완료**: CNN/RNN/DP/이진탐색 마무리 후 NLP(토큰화, Word2Vec, Seq2Seq) 주제로 자연스럽게 진입
- **논문 리뷰 실행**: RWKV 논문을 읽고 핵심 아이디어(선형 어텐션, 이중 모드)를 정리. 전주 미이행했던 논문 읽기 과제를 이번 주에 해결
- **실수 원인 분석 구체화**: bisect_left 입출력 스펙, for문 내 append 위치, nonlocal 키워드 등 반복 실수를 패턴화하여 기록
- **하루 밀림 → 다음 날 회복 패턴 형성**: 5/30 Word2Vec 구현 미완 → 5/31에 "어제 못한 구현 함"으로 당일 복구

---

## 아쉬운 점

- **TIL 미작성일 2일 (5/29, 5/30)**: 코드 활동은 있었지만(leaf_node_maximize.py 등) TIL로 기록하지 않음. 학습 흔적 추적 공백
- **Notion "완료" 표시의 부정확성 지속**: 5/29 "리프 문제 1문제만했음", 5/30 "구현은 X"로 메모했지만 상태는 "완료" — 부분 완료와 완료의 구분이 모호
- **6/1 Transformer 심화 미착수**: 주 마지막 날 학습을 시작하지 못함 — 주말 페이스 다운 패턴 반복
- **Word2Vec 직접 구현 부채**: 5/30 "구현은 X"로 스킵 → 5/31에 Seq2Seq 구현을 했지만 Word2Vec 구현은 여전히 미완
- **5/26 코드 기록 공백**: Notion "완료"이지만 code/에 해당일 새 파일이 없음 (5/27에 몰아서 작성한 것으로 추정)

---

## Notion DB 이번 주 완료/스킵 비율

| 날짜 | 할일 | 주차 | Notion 상태 | 메모 |
|------|------|------|-------------|------|
| 5/26 (월) | DP 문제 2개 + RNN 구현 | Week6 | ✅ 완료 | |
| 5/27 (화) | 알고리즘 복습 (전 유형 문제풀기) + 논문 1편 | Week6 | ✅ 완료 | |
| 5/28 (수) | 버퍼데이 (Week 6 회고 + 밀린 거 처리) | Week6 | ✅ 완료 | |
| 5/29 (목) | 토큰화 개념 (BPE, WordPiece) + Lv2 2문제 | Week 7 | ✅ 완료 | 리프 문제 1문제만했음 |
| 5/30 (금) | Word2Vec/임베딩 개념 + 직접 구현 + Lv2 2문제 | Week 7 | ✅ 완료 | 구현은 X |
| 5/31 (토) | Seq2Seq + Attention 메커니즘 개념 + Lv2 2문제 | Week 7 | ✅ 완료 | 어제 못한 구현 함 |
| 6/1 (일) | Transformer 구조 심화 (Self-Attention, Multi-Head) + Lv2 2문제 | Week 7 | ⏭️ 시작 전 | |

**Notion 기준 완료율: 6/7 ≈ 86%** (전주 57% → 29%p 개선)
**실제 완전 이행률: ~4/7 ≈ 57%** — 부분 완료(문제 수 부족, 구현 스킵)를 고려하면 절반 수준

---

## 다음 주 계획

> Notion DB 다음 주 항목 (Week 7 후반)

| 날짜 | 할일 |
|------|------|
| 6/1 (일) | Transformer 구조 심화 (Self-Attention, Multi-Head) + Lv2 2문제 |
| 6/3 (화) | BERT/GPT 개념 + 논문 1편 + Lv2 2문제 |
| 6/4 (수) | 버퍼데이 (Week 7 회고 + 밀린 거 처리) |

**중점 사항:**
- **미착수 Transformer 심화 우선 소화**: 6/1 항목을 월요일 중 완료
- **Word2Vec 구현 부채 해소**: 버퍼데이(6/4)까지 반드시 구현 코드 작성
- **TIL 작성률 100% 목표**: 이번 주 71%(5/7) → 다음 주는 매일 작성 (짧아도 OK)
- **Notion 상태 정직하게 관리**: 부분 완료 시 "진행 중"으로 두고, 메모에 미완 항목 명시
- **NLP 파이프라인 완성**: Tokenization → Embedding → Seq2Seq → Transformer → BERT/GPT 흐름 마무리
