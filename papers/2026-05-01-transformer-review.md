# Understanding Transformers and Attention Mechanisms

- arxiv: https://arxiv.org/abs/2604.00965
- 저자: Michel Fabrice Serret (Paul Scherrer Institute, Switzerland)
- 날짜: 2026-05-01

## 한 줄 요약

Transformer의 핵심인 Attention 메커니즘이 어떻게 작동하는지, 그리고 KV캐싱/GQA/Latent Attention 등 최신 최적화 기법까지 수학적으로 소개하는 입문 논문.

## 섹션별 정리

### 1. 서론 — 텍스트를 벡터로 바꾸는 과정

Transformer 기반 NLP 모델은 텍스트를 문자열이 아닌 **벡터의 시퀀스**로 처리한다.

1. **토큰화** — 텍스트를 서브스트링(토큰)으로 분할. vocabulary 크기는 의미 정보를 충분히 담으면서도 가능한 작게 유지하는 게 중요 (이상적으로는 형태소 단위)
2. **임베딩** — 토큰의 vocabulary 인덱스를 임베딩 행렬 E에서 해당 행을 꺼내 벡터로 변환. 이 행렬은 사전학습되거나 모델과 함께 학습됨
3. **Positional/Feature 임베딩 추가** — 토큰 임베딩 벡터에 위치 정보(positional)나 문장 정보(feature)를 더해 의미를 풍부하게 함

이 벡터들이 self-attention의 입력이 된다.

### 2. Attention Mechanism

Attention은 Query(질문)-Key(라벨)-Value(정보) 구조로, 토큰 간 의미적 관계를 인코딩하는 메커니즘이다.

#### 2.1 일반 Attention

1. 입력 벡터에 각각 다른 가중치 행렬(W^Q, W^K, W^V)을 곱해 Q, K, V를 생성
2. Q와 K의 내적으로 어텐션 score 계산
3. √dQK로 스케일링 후 softmax로 정규화 → attention weight (합이 1인 확률 분포)
4. attention weight로 V를 가중합 → 최종 출력 Y

- self-attention에서는 Q, K, V 모두 같은 입력에서 나옴 (자기 자신 포함 전체 토큰과 비교)

#### 2.2 Multi-Headed Attention

- 같은 입력에 대해 여러 개의 attention head를 병렬로 돌림
- 각 head가 서로 다른 유형의 관계를 학습
- 각 head의 출력을 concat → W^O로 선형 변환 → 최종 출력

### 3. Transformer Architecture

Transformer는 인코더-디코더 구조로, 원래 기계 번역을 위해 설계됨.

#### 인코더 레이어 구성

- **Multi-Headed Self-Attention** (Q=K=V, 같은 입력)
- **Layer Normalization** (평균 0, 분산 1로 정규화 + 학습 가능한 파라미터)
- **Feed Forward** (비선형 함수 적용, ReLU/GLU 계열)
- **Skip Connection** (각 서브레이어의 입출력을 더함 → 기울기 소실 방지)

#### 디코더 레이어 차이점

- **Masked/Causal Attention** — 미래 토큰을 볼 수 없게 마스킹. Query는 자신과 이전 토큰의 Key만 참조 가능
- **Cross-Attention** — 디코더 상태가 Query, 인코더 출력이 Key/Value. 출력 문장을 입력 문장과 연결

#### Transformer 변형

- **Encoder-only (BERT)** — 정보 추출, 분류 태스크
- **Decoder-only (GPT)** — 텍스트 생성
- 공통: 대량 데이터로 사전학습 → 다른 태스크에 fine-tuning

### 4. KV Caching, 압축, Attention 최적화

새 토큰 생성 시 이전 모든 토큰의 K, V가 필요 → 매번 재계산하면 비효율 → KV캐싱(저장해서 재사용)으로 연산량 감소. 단, 대화가 길어지면 캐시 메모리가 병목.

#### 4.1 Grouped Query Attention (GQA)

- 여러 Query head가 같은 K, V head를 공유
- 저장해야 할 KV head 수 자체를 줄여 메모리 절감
- 극단적으로 KV head 1개만 쓰면 Multi-Query Attention (MQA)

#### 4.2 Latent Attention (MLA)

- 모든 head가 공유하는 저차원 잠재 임베딩 L 하나만 캐시에 저장
- L에서 각 head의 K, V를 생성 → 가중치 행렬 병합으로 연산 효율화
- 한계: Positional embedding(RoPE) 적용 시 완전한 등가성이 깨짐 → non-latent 부분을 별도 추가하여 우회

## 새로 알게 된 것

- Attention이 데이터베이스의 Query-Key-Value 검색과 유사한 구조라는 점
- KV캐싱이 연산량을 줄이지만 메모리 병목을 만든다는 트레이드오프
- GQA와 Latent Attention이 이 메모리 문제를 해결하는 서로 다른 접근법이라는 것

## 이해 안 된 것 / 처음에 잘못 이해했던 것

- **"NLP = self-attention"으로 착각함** → NLP는 넓은 분야이고, self-attention은 Transformer라는 특정 모델 구조의 핵심일 뿐
- **토큰화와 임베딩 순서를 혼동함** → 임베딩을 거쳐야 토큰화가 된다고 생각했지만, 실제로는 토큰화(텍스트 쪼개기) → 임베딩(벡터 변환) 순서
- **Positional/Feature 임베딩을 "임베딩 방식의 종류"로 이해함** → 실제로는 역할이 다른 별도의 정보이며, 토큰 임베딩에 추가로 더해주는 것
- **Attention의 텍스트 설명만으로는 직관적 이해가 어려웠음** → 데이터베이스 검색 비유(Query=질문, Key=라벨, Value=내용)로 이해함
- **self-attention에서 Key가 "자기 자신 제외 나머지"라고 생각함** → 실제로는 자기 자신 포함 전체 토큰이 Key/Value가 됨
- **Value를 "Key의 값"으로 이해함** → Key와 Value는 같은 토큰에서 나오지만 서로 다른 가중치 행렬을 거쳐 역할이 다름 (Key=라벨, Value=전달할 정보)
- **softmax 정규화, √dQK 스케일링의 역할을 처음엔 놓침** → 스케일링은 차원이 클수록 내적값이 커지는 걸 보정, softmax는 확률 분포로 만드는 것
- **KV캐싱 자체가 병목 현상이라고 혼동함** → KV캐싱은 연산 병목의 해결책이지만, 메모리 병목이라는 새로운 문제를 만듦
- **수식 전반** — 행렬 연산, 커널 함수 등 수학적 표현은 대부분 건너뜀. DL/선형대수 학습 후 재독 필요
