# Drawing Pandas: A Benchmark for LLMs in Generating Plotting Code
- arxiv: https://arxiv.org/abs/2412.02764
- 날짜: 2026-05-06

## 한 줄 요약
LLM이 자연어 지시문으로 Pandas DataFrame 시각화 코드를 얼마나 잘 생성하는지 평가하는 벤치마크 PandasPlotBench(175개 합성 태스크)를 제안하고, 모델/라이브러리/태스크 길이 3가지 축에서 LLM의 강점과 한계를 분석한 논문.

---

## 섹션별 정리

### I. Introduction

1. **데이터 시각화의 중요성**: 데이터 분석에서 시각화는 패턴과 트렌드를 발견하는 핵심 수단이며, 그 중요성이 계속 커지고 있음.

2. **LLM의 등장과 한계**: LLM이 시각화 코드 생성을 자동화할 수 있는 잠재력을 보였지만, 복잡한 태스크에서 실행 가능한 코드를 만드는 데 한계가 있음.

3. **기존 벤치마크의 부족함**:
   - 실제 DataFrame/CSV 기반 시각화 벤치마크는 MatPlotBench 1개뿐 (그마저 25개 데이터 포인트로 제한적)
   - 기존 벤치마크들은 **태스크 표현 방식이나 라이브러리 선택이 성능에 어떤 영향을 주는지 깊이 있게 분석하지 못함**

4. **PandasPlotBench 제안**: 175개의 인간이 검수한 태스크로 구성된 벤치마크. **합성 데이터**로 만들어 data leakage(LLM이 학습 데이터에서 답을 본 적 있는 문제)를 방지함.

5. **주요 실험 결과 (Introduction에서 미리 공개)**:
   - **태스크 압축 실험**: 자세한 태스크를 한 문장으로 줄여도 성능 저하가 거의 없음 → 사용자가 짧게 입력하는 UI 설계 가능
   - **라이브러리별 차이**: Matplotlib과 Seaborn은 잘하지만, Plotly는 LLM이 약함
   - **모델 비교**: GPT-4o, Claude 3.5 Sonnet 등 주요 LLM과 Llama 시리즈를 평가

6. **기여**: 연구자들이 시각화 분야의 LLM 활용을 개선할 수 있도록 **확장 가능한 평가 프레임워크**를 제공.

---

### II. PandasPlotBench

#### A. 데이터 수집 및 가공
- Matplotlib gallery의 **501개 스크립트**를 출발점으로 함
- 가공 단계:
  1. 실행 가능한 것만 → 307개
  2. GPT-4로 "데이터 생성 코드"와 "그리기 코드" 분리
  3. 수동 검증 후 → 201개
  4. 최종 검증 → **175개 데이터 포인트**
- 태스크 프롬프트는 **GPT-4V**로 자동 생성 (코드 + 그래프 이미지를 보고 자연어 지시문 작성)

#### B. 데이터 구성
**각 데이터 포인트 = 다음 5가지를 묶은 패키지:**
1. CSV 파일 (시각화할 데이터)
2. 데이터 로딩 스크립트
3. Ground truth plot (정답 그래프)
4. Ground truth code (정답 Matplotlib 코드)
5. 태스크 프롬프트 **3가지 길이 버전**:
   - 자세한 버전 (Plot description + Plot style description)
   - 2-3문장 압축 버전
   - 한 문장 압축 버전

→ 이 3가지 길이가 Section III-C 실험(태스크 길이 영향)의 기반이 됨.

#### C. 평가 지표
**메인 평가 (GPT-4o가 Judge 역할):**
- **Visual Scoring**: 생성된 그래프 ↔ 정답 그래프 비교 (0~100점)
- **Task-based Scoring**: 생성된 그래프 ↔ 태스크 설명 부합도 (0~100점)
- 두 점수의 Pearson 상관계수 0.58 → 둘 다 보는 게 의미 있음
- 저자들은 **Task-based를 더 신뢰** (LLM이 정답보다 더 잘 그릴 때도 있어서, "정답과의 유사도"보다 "지시 부합도"가 공정)

**검증용 (메인 평가 방식의 신뢰성을 점검):**
- CodeBERT Score: 시도했으나 시각/태스크 점수와 **상관관계 없어서 폐기**
- Human scoring (저자 1명, Python 5년차):
  - Task-based score와 상관계수 **0.85** → 강한 일치 → GPT-4o judge 신뢰 가능
  - Visual score와는 0.66 → 중간 정도

---

### III. Experiments

#### 사전 세팅: DataFrame Description 방식
본 실험에 앞서 "DataFrame을 어떻게 프롬프트에 넣을까"를 결정.
→ **`head(5)` + 컬럼명/타입**이 가장 효과적.

#### A. 모델 비교
- **GPT-4o ≈ Claude 3.5 Sonnet** (점수 비슷)
- Sonnet은 응답 길이 때문에 20% 느림 → **이후 실험은 GPT-4o 사용**
- **오픈 모델 Llama 3.1 70B/405B**도 proprietary 급 성능
- 작은 Llama(1B, 3B)는 코드 자체가 자주 실패
- 관찰: **Claude 계열은 짧게 쓰라고 해도 응답이 길다**

#### B. 라이브러리 비교 (Matplotlib / Seaborn / Plotly)
- **Plotly가 명확히 약함**: 코드 실패율 22% (Matplotlib 1.8%, Seaborn 5.2%)
- 원인 추정: **학습 데이터에 Plotly 비중이 적음** → LLM은 인기 라이브러리에 편향
- Visual 점수가 Matplotlib에서 높은 건 ground truth 자체가 Matplotlib이기 때문 (저자도 인정 → Task-based 신뢰)

#### C. 태스크 길이 영향
- 자세한 태스크(736자) → 한 문장(154자)로 줄여도 **점수 거의 유지** (89 → 85)
- **태스크 자체를 빼고 generic 지시문으로 대체하면 폭락** (89 → 36)
- 함의: **"태스크 유무"가 중요하지 "태스크 길이"는 덜 중요**
- → 사용자가 짧게 입력해도 OK한 **간결한 UI 설계가 가능**
- 단, DataFrame 설명과 시스템 프롬프트는 자세해야 함 (이쪽이 정보 대부분)

---

### V. Limitations and Future Work

1. **Matplotlib 편향**: Ground truth가 Matplotlib 기반이라 Seaborn/Plotly는 Visual 점수에서 구조적으로 불리. → Task-based 점수를 더 신뢰하는 방식으로 부분 보완.

2. **OpenAI 모델 편향 가능성**: 태스크 생성 시 GPT-4/GPT-4V 사용 → OpenAI 모델 편향 가능. 단, 데이터 자체는 **합성**이라 data leakage는 낮음. 저자들은 이 편향이 미미하다고 주장.

3. **데이터 규모와 다양성**:
   - 175개로 적은 편
   - **출처가 Matplotlib gallery 한 곳**이라 다양성 부족
   - 향후 다른 출처로 확장 필요

4. **DataFrame이 비현실적으로 깔끔함**: 시각화에 필요한 컬럼만 포함되어 있어, **결측치/불필요 컬럼/노이즈가 많은 실제 업무 데이터와 거리 있음**. 더 현실적인 데이터로 augmentation 필요.

5. **Python 한정**: 다른 프로그래밍 언어로 확장 예정.

6. **Human scoring을 1명(저자 본인)만 수행**: 향후 다수의 전문가 검증이 필요함을 인정.

---

## 새로 알게 된 것

### 벤치마크 설계 관점
- **Ground truth**라는 개념: 모델 출력을 채점할 때 비교 기준이 되는 "정답"
- **Data leakage 방지**를 위해 합성 데이터를 만드는 설계 결정
- **LLM judge**로 채점하되, **사람 점수와의 상관관계(0.85)** 로 신뢰성을 검증하는 방식
- CodeBERT Score는 코드 유사도 측정엔 좋지만 **시각화 결과의 좋고 나쁨과는 무관** (그래서 폐기됨)
- 평가 지표를 **Visual(정답과 유사도)** vs **Task-based(지시 부합도)** 로 분리한 발상 → "정답보다 더 잘 그렸을 때"를 공정하게 평가 가능

### LLM 시각화 능력에 대한 발견
- **GPT-4o ≈ Claude 3.5 Sonnet** (성능 비슷, 속도는 GPT-4o가 빠름)
- **오픈 모델 Llama 3.1 70B/405B도 proprietary급** → 비용 민감 환경에서 대안 가능
- **LLM은 라이브러리 인기도에 편향**: Matplotlib/Seaborn은 잘하지만 Plotly는 22% 실패
- **태스크 길이는 거의 무관, 태스크 유무는 결정적** (한 문장 vs 자세한 버전 점수 차이 4점 / 태스크 빠지면 53점 폭락)
- **DataFrame 설명 방식**: `head(5)` + 컬럼명/타입이 가장 효과적

### 실용 인사이트
- 데이터 분석 도구 UI 설계 시 → 사용자는 짧게 입력해도 OK, 단 시스템 측에서 DataFrame 설명을 자세히 제공해야 함
- 면접/실무에서 "어떤 LLM을 쓸까" 질문에 답할 거리 (속도-성능 trade-off, 응답 길이 차이 등)

---

## 이해 안 된 것

<!-- 직접 채우기. 아래는 후보 -->

- (예시) Pearson 상관계수 0.58, 0.85 같은 통계 수치가 "강하다/약하다"의 기준이 어디인지
- (예시) "Judge 모델"이 다른 모델의 출력을 점수 매기는 LLM-as-a-Judge 방식의 한계는?
- (예시) 합성 데이터로 만들면 정말 data leakage가 없다고 할 수 있는가? (LLM이 Matplotlib gallery는 학습했을 텐데)
- (예시) 175개 태스크 수가 통계적으로 의미 있는 결론을 내기에 충분한가?
