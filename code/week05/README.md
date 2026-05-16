# 유방암 분류 최적 모델 실험

sklearn 내장 유방암 데이터셋으로 전처리 → 모델 비교 → 하이퍼파라미터 튜닝 → 평가까지의 ML 파이프라인을 구성한 프로젝트입니다.

## 데이터셋

- **출처**: `sklearn.datasets.load_breast_cancer()`
- **크기**: 569개 샘플, 30개 피처 + 1개 타겟
- **타겟**: 악성(0) 212개 / 양성(1) 357개
- **피처**: mean radius, mean texture, mean perimeter, mean area, mean smoothness, mean compactness, mean concavity, mean concave points, mean symmetry, mean fractal dimension 등 30개 (mean, error, worst 각 10개씩)

## 과정

### 1. EDA
데이터 로드 후 `shape`, `describe()`, `value_counts()`로 기본 분포 확인.

### 2. 전처리
- `train_test_split`으로 train/test 8:2 분리 (stratify 적용)
- `StandardScaler`로 피처 스케일링 (train에 fit, test는 transform만)

### 3. 모델 비교
세 가지 모델을 학습하고 `cross_val_score(cv=5)`로 비교:

| 모델 | 교차검증 평균 |
|------|-------------|
| LogisticRegression | ~0.980 |
| KNeighborsClassifier | ~0.967 |
| DecisionTreeClassifier | ~0.930 |

### 4. 하이퍼파라미터 튜닝
교차검증 1위인 LogisticRegression을 `GridSearchCV`로 튜닝:
- 탐색 범위: `C=[0.01, 0.1, 1, 10, 100]`, `solver=['lbfgs', 'liblinear']`
- **최적 파라미터**: `C=0.1, solver=lbfgs`
- **최적 교차검증 점수**: 0.987

### 5. 최종 평가

```
Confusion Matrix:
[[40  2]
 [ 1 71]]

              precision    recall  f1-score
악성(0)          0.98      0.95      0.96
양성(1)          0.97      0.99      0.98
accuracy                             0.97
```

114개 테스트 샘플 중 3개만 오분류. 악성을 놓친 케이스(FN)가 1건뿐으로 의료 데이터 관점에서도 양호한 결과.

## 배운 점

- **Bunch 객체 구조**: sklearn 내장 데이터셋은 DataFrame이 아니라 `data`, `target`이 분리된 Bunch 객체라서 직접 합쳐야 한다.
- **스케일링의 중요성**: StandardScaler 적용 전후로 GridSearchCV 점수가 0.958 → 0.987로 크게 차이났다. 피처 스케일이 다르면 모델 성능에 직접적인 영향을 준다.
- **train에만 fit**: Scaler를 train에 fit하고 test는 transform만 해야 데이터 누수(data leakage)를 방지할 수 있다.
- **교차검증 vs 단일 split**: 단일 split의 score(0.982)보다 교차검증 평균(0.980)이 더 신뢰할 수 있는 지표다.


## 실행 환경

- Python 3.12
- scikit-learn, pandas, numpy, matplotlib
