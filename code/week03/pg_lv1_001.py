# 문제 설명
# 어떤 도로에 차량 신호등이 n개 있습니다. 모든 신호등은 항상 초록불 → 노란불 → 빨간불 순서로 반복되며, 각 신호의 지속 시간은 신호등마다 다릅니다. 시간은 1초부터 시작하며, 각 신호등은 처음에는 초록불 상태로 시작합니다.

# 이 도로에서는 가끔 정전이 일어나는데, 모든 신호등이 모두 노란불이 되면 정전이 발생한다는 사실이 밝혀졌습니다.

# 예를 들어 신호등이 2개이고, 각 신호등의 주기가 다음과 같다고 가정해 보겠습니다.

# 신호등	초록불	노란불	빨간불
# 1번	2초	1초	2초
# 2번	5초	1초	1초
# 신호등-1.drawio.png

# 위 그림과 같이 13초에 처음으로 두 신호등이 모두 노란불이 됩니다.

# 신호등 n개의 신호 주기를 담은 2차원 정수 배열 signals가 매개변수로 주어집니다. 모든 신호등이 노란불이 되는 가장 빠른 시각(초)을 return 하도록 solution 함수를 완성해 주세요. 만약 모든 신호등이 노란불이 되는 경우가 존재하지 않는다면 -1을 return 해주세요.

# 제한사항
# 2 ≤ signals의 길이 = n ≤ 5
# signals의 원소는 [G, Y, R] 형태의 길이가 3인 정수 배열입니다. 순서대로 초록불, 노란불, 빨간불의 지속 시간을 의미합니다.
# 1 ≤ G, Y, R ≤ 18
# 3 ≤ G + Y + R ≤ 20


def solution(signals):
    answer = 0
    period = 0
    period_save = []
    for row_id, row in enumerate(signals):
        for col_id,col in enumerate(row):
            period += col
        period_save.append(period)
        period = 0    

    for t in range(1, 2000000):
        if all(signals[i][0] <= (t-1) % period_save[i] < signals[i][0] + signals[i][1] for i in range(len(signals))):
            return t
    return -1
# 최종 코드:
# python
def solution(signals):
    period_save = [sum(s) for s in signals]
    for t in range(1, 2000000):
        if all(signals[i][0] <= (t-1) % period_save[i] < signals[i][0] + signals[i][1] for i in range(len(signals))):
            return t
    return -1
# 잘한 점:

# 문제의 핵심 구조(주기, 노란불 구간, 교집합)를 정확하게 파악했음
# set 교집합 접근이 안 됐을 때 완전탐색 방식으로 전환한 판단이 좋았음
# (t-1) % 주기로 현재 신호 상태를 판단하는 로직을 스스로 이해하고 적용함

# 반복된 실수 (다음에 주의):

# 변수명 혼동 — period와 period_save, signal과 signals를 여러 번 헷갈림. 변수명을 지을 때 역할을 명확히 구분하고, 쓰기 전에 "이게 int인지 list인지" 항상 확인하기
# 덮어쓰기 vs 누적 — =으로 할당하면 이전 값이 사라진다는 걸 여러 번 놓침. append, update 등 누적 메서드와 구분하는 습관 필요
# 들여쓰기 위치 — for문 안에 넣어야 할 것과 밖에 넣어야 할 것을 혼동. 코드 쓰기 전에 "이 줄이 몇 번 실행되어야 하는가"를 먼저 생각하기
# 탐색 범위 산정 — 제한사항에서 최악의 경우를 계산하는 습관이 부족. LCM이 100만을 넘을 수 있다는 걸 놓침

# 배운 것:

# all() + generator expression으로 "모든 조건 만족" 체크를 한 줄로 쓸 수 있음
# (t-1) % 주기로 주기적 이벤트의 현재 상태를 판단할 수 있음
# set 교집합 방식보다 완전탐색이 코드가 더 단순하고 디버깅이 쉬운 경우가 있음
# 탐색 범위는 "감"이 아니라 수학적 근거(LCM)로 잡아야 함