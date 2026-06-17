"""
프로그래머스 - 미로 탈출 (Lv2)
================================

[문제]
1x1 칸으로 이루어진 직사각형 격자 미로. 각 칸은 통로 또는 벽이다.
시작(S)에서 출발해 레버(L)를 당긴 뒤, 출구(E)로 가야 탈출할 수 있다.
- 출구는 레버를 당기기 전에도 '지나갈' 수 있다 (그냥 통로처럼).
- 모든 통로/출구/레버/시작점은 여러 번 지나갈 수 있다.
- 한 칸 이동에 1초. 최소 시간을 구하고, 탈출 불가면 -1을 반환.

maps[i] 구성 문자: S(시작), E(출구), L(레버), O(통로), X(벽). S/E/L은 각 1개씩.


[핵심 아이디어 - 여정을 두 개의 독립적인 최단경로로 분해]
"S에서 L 들렀다가 E로" 라는 하나의 여정을 한 번의 BFS로 풀려고 하면
visited가 꼬인다 (레버 당기고 돌아오는 길에 이미 밟은 칸을 또 지나야 할 수 있음).

해법: 두 개의 독립적인 BFS로 쪼갠다.
    d1 = 최단거리(S -> L)
    d2 = 최단거리(L -> E)
    답 = (둘 중 하나라도 도달 불가면 -1) 아니면 d1 + d2

이렇게 나누면 각 BFS가 자기만의 visited를 새로 가지므로 서로 간섭하지 않는다.
- S->L 탐색에서 E는 그냥 지나가도 되는 통로일 뿐 (특별 취급 X).
- 벽(X)만 막고 나머지(S/E/L/O)는 전부 통행 가능.
"""

from collections import deque


def solution(maps):
    n = len(maps)
    m = len(maps[0])

    # 1. S, L, E 좌표를 미리 한 번만 찾아둔다 (BFS 밖에서)
    start, lever, escape = None, None, None
    for i in range(n):
        for j in range(m):
            if maps[i][j] == 'S':
                start = (i, j)
            elif maps[i][j] == 'L':
                lever = (i, j)
            elif maps[i][j] == 'E':
                escape = (i, j)

    # 상·하·좌·우 이동 방향
    dx = [-1, 1, 0, 0]
    dy = [0, 0, -1, 1]

    # 2. start_pos -> dest_pos 최단거리를 구하는 BFS. 도달 불가면 -1.
    def bfs(start_pos, dest_pos):
        sx, sy = start_pos
        ex, ey = dest_pos

        # visited 배열이 '거리 저장 + 방문 체크'를 겸한다.
        # -1 = 미방문, 0 이상 = 거기까지의 최단거리.
        visited = [[-1] * m for _ in range(n)]
        queue = deque([(sx, sy)])
        visited[sx][sy] = 0

        while queue:
            x, y = queue.popleft()

            # 목적지를 꺼낸 순간이 곧 최단거리 (BFS는 거리 순으로 퍼지므로)
            if x == ex and y == ey:
                return visited[x][y]

            for i in range(4):
                nx, ny = x + dx[i], y + dy[i]
                # 격자 범위 안 + 벽이 아님 + 아직 미방문
                if 0 <= nx < n and 0 <= ny < m:
                    if maps[nx][ny] != 'X' and visited[nx][ny] == -1:
                        visited[nx][ny] = visited[x][y] + 1
                        queue.append((nx, ny))

        # 큐가 다 비도록 목적지를 못 밟음 -> 도달 불가
        return -1

    # 3. 두 구간을 따로 구해서 합친다
    d1 = bfs(start, lever)   # S -> L
    d2 = bfs(lever, escape)  # L -> E

    if d1 == -1 or d2 == -1:
        return -1
    return d1 + d2


# =============================================================
# 피드백 (대화 전체 흐름 기준)
# =============================================================
#
# [핵심 교훈 - 이번 문제의 본질]
#   "상태가 바뀌는 여정"(레버 당기기 전/후)을 한 번의 BFS + 한 개의 visited로
#   풀려다 막혔다. 막힌 지점을 정확히 스스로 진단함:
#     "S->E->L->E 가 될 수도 있어서 visited 한 개로는 안 될 것 같아"  ← 옳은 관찰.
#   해법은 여정을 '독립적인 하위 문제 둘'(S->L, L->E)로 쪼개는 재구성.
#   → 복잡한 경로 문제는 단계로 분해하면 visited 충돌이 사라진다.
#   (참고: 다른 정석 해법은 '좌표 + 레버여부'를 상태로 묶는 3D-visited BFS.
#    이번엔 단계 분해 방식을 썼고, 둘 다 알아두면 좋다.)
#
# [잘한 점]
#  - visited 배열을 '거리 저장'과 '방문 체크'로 겸용 (-1 초기화 패턴). 깔끔.
#  - S/L/E 좌표 탐색을 BFS 밖에서 한 번만 수행 (반복 호출에서 재계산 안 함).
#  - BFS 본체가 정석: 범위 체크 -> 벽/방문 체크 -> 거리 갱신 + enqueue,
#    pop 시점에 목적지 확인 (BFS 최단거리 보장).
#  - 도달 불가(-1)를 별도 연결성 검사 없이 BFS의 자연스러운 결과로 처리.
#
# [성장 포인트 = 빠르게 짤 때의 잔실수]
#  - 초기 골격에 Python 2 문법(매개변수 튜플 언패킹: def f(a, (b,c)))과
#    할당문 끝 콜론(n,m = ...:) 두 개의 SyntaxError가 있었음. 바로 수정.
#    → 함수 시그니처/할당문은 "이게 Python 3 문법 맞나" 한 번 점검하는 습관.
#
# [검증]
#  공식 예제 2개(16, -1) 정답 + 랜덤 격자 30,000개를 상태공간 BFS(독립 구현)와
#  전수 비교 -> 불일치 0개. 모든 케이스에서 정답.
