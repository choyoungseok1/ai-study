"""
프로그래머스 Lv2 - 당구 연습  (Day 68)
https://school.programmers.co.kr/learn/courses/30/lessons/169198

[문제 요약]
가로 m, 세로 n 당구대. 시작 공 (startX, startY)에서 각 목표 공을
'원쿠션'(벽에 최소 1번 맞고)으로 맞힐 때, 굴러간 최소 거리의 '제곱'을 반환.

[핵심 아이디어 - 반사(거울상) 법]
"벽에 튕겨 목표를 맞힌다"  ==  "목표를 벽 너머로 반사시키면 경로가 직선이 된다".
=> 시작점에서 '거울상 목표'까지의 직선거리(²) = 그 벽으로 원쿠션 친 거리(²).
정렬 여부와 무관하게 동일하게 적용되는 게 핵심 -> x,y가 다 다른 일반 케이스가
오히려 제일 단순(4개 거울상 중 min).

목표 (a, b)의 벽별 거울상:
  좌 (x=0):  (-a,    b)   -> (startX + a)²       + (startY - b)²
  우 (x=m):  (2m-a,  b)   -> (2m - startX - a)²   + (startY - b)²
  상 (y=n):  (a,  2n-b)   -> (startX - a)²        + (2n - startY - b)²
  하 (y=0):  (a,   -b)    -> (startX - a)²        + (startY + b)²

[원쿠션 예외 - 무효 거울상]
시작점과 목표가 '같은 줄'(같은 x 또는 같은 y)이면, "목표가 있는 방향"의 벽은
벽에 닿기 전에 목표를 먼저 맞으므로 무효 -> 그 거울상 '하나'만 빼고 나머지 min.
정렬은 한 축에서만 가능하므로(둘 다 같으면 시작점과 겹침=입력 없음) 무효 거울상은
항상 최대 1개.

[복잡도] 공 1개당 O(1), 전체 O(len(balls)). (제곱 그대로 쓰므로 sqrt 불필요)
"""


def solution(m, n, startX, startY, balls):  # m = 가로(x축), n = 세로(y축)
    answer = []
    for finalX, finalY in balls:
        # 4개 벽 거울상까지의 직선거리(제곱)
        udist = (startX - finalX) ** 2 + (2 * n - startY - finalY) ** 2  # 상 (y=n)
        ddist = (startX - finalX) ** 2 + (startY + finalY) ** 2          # 하 (y=0)
        rdist = (startY - finalY) ** 2 + (2 * m - startX - finalX) ** 2  # 우 (x=m)
        ldist = (startY - finalY) ** 2 + (startX + finalX) ** 2          # 좌 (x=0)

        if startX == finalX and startY > finalY:     # 같은 열, 목표가 아래  -> 하(ddist) 무효
            answer.append(min(udist, rdist, ldist))
        elif startX == finalX and startY < finalY:   # 같은 열, 목표가 위    -> 상(udist) 무효
            answer.append(min(ddist, rdist, ldist))
        elif startY == finalY and startX > finalX:   # 같은 행, 목표가 왼쪽  -> 좌(ldist) 무효
            answer.append(min(udist, ddist, rdist))
        elif startY == finalY and startX < finalX:   # 같은 행, 목표가 오른쪽 -> 우(rdist) 무효
            answer.append(min(udist, ddist, ldist))
        else:                                         # 정렬 안 됨 -> 4개 모두 유효
            answer.append(min(udist, ddist, rdist, ldist))
    return answer


if __name__ == "__main__":
    print(solution(10, 10, 3, 7, [[7, 7], [2, 7], [7, 3]]))  # [52, 37, 116]
    print(solution(10, 10, 5, 9, [[5, 8]]))                  # [9]  (정렬: 반대쪽 벽이 정답)


"""
====================================================================
[피드백 - Day 68]
====================================================================

● 잘한 점
- 반사(거울상) 아이디어를 스스로 발견. 처음 same-y/same-x 공식에서 쓴
  '벽까지 갔다 반으로 쪼갠다'가 사실 거울상 법의 특수 형태였음.
- "same-x에서 좌우가 항상 best는 아니지 않냐"는 질문이 핵심 통찰.
  -> 정렬 케이스에서도 '특정 한 쌍의 벽'만 보면 안 되고, 무효 1개만 빼고
     나머지 전부 min 해야 한다는 정답 구조로 이어짐. (반례로 직접 확인)
- 코드 전에 시간복잡도 O(1)/공 을 의식하고 접근.

● 일반화의 열쇠 (이번에 얻은 것)
- 거울상 법: "튕겨서 맞힌다" -> "목표를 반사하면 직선거리". 정렬이든 아니든
  동일하게 적용 -> x,y 다른 일반 케이스가 오히려 제일 단순(4개 중 min).
- 무효 거울상은 항상 최대 1개 (정렬은 한 축에서만 가능하므로).

● 디버깅에서 잡은 버그 (모두 단골 패턴)
  1. 오타: fianlY -> finalY                         (변수명 오타)
  2. startY == startY -> startY == finalY           (항상 True, 분기 무력화)
  3. ldist 공식: (startY+finalY) -> (startX+finalX)  (ddist의 y패턴을 복붙;
                                                      좌벽은 x를 반사해야 함)
  4. 분기 조건 부등호 4개 전부 반대                  (무효 = 목표가 그 방향에 있을 때)

  ★ 반복 패턴 주의: 1~4 모두 '비슷한 줄을 빠르게 쓰다가' 나온 변수/방향 혼동
    (복붙 드리프트). 반복 코드일수록 한 줄씩 검토.
    대안: 무효 거울상을 float('inf')로 두고 min을 한 번만 호출하면, 분기 반복이
    사라져서 오타 위험이 줄어듦.

● 검증
  - 공식 예제 통과: [52, 37, 116]
  - 게시판 까다로운 정렬 케이스 통과: solution(10,10,5,9,[[5,8]]) -> [9]
    (목표가 바로 아래면 좌우(101)가 아니라 '반대쪽 위 벽'(9)이 정답)
  - 독립 레퍼런스 구현과 랜덤 20,000개 입력 비교 -> 전부 일치.
"""
