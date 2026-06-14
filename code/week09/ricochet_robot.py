"""
프로그래머스 - 리코쳇 로봇
https://school.programmers.co.kr/learn/courses/30/lessons/169199

[핵심 아이디어 - BFS 최단경로]
- "최소 이동 횟수" + 각 이동 비용 동일 → 비가중 그래프 최단경로 → BFS.
- 노드 = 말의 위치 (r, c).  (방향은 상태가 아님 → visited도 위치 기준)
- 트위스트: 한 번의 이동 = 한 칸이 아니라 "벽/장애물('D')까지 쭉 미끄러짐".
    · 한 노드의 이웃 = 4방향으로 각각 미끄러져 "멈춘 지점" 4개.
- 중요한 규칙: G는 장애물이 아니다.
    · 슬라이드는 벽/'D'에서만 멈춤 → G는 빈 칸처럼 그냥 통과한다.
    · 따라서 G 도달 체크는 "슬라이드가 멈춘 지점(= BFS 노드)"에서만 한다.
      (지나가는 중간 칸에서는 체크하지 않음)
- visited(위치 기준)로 사이클 방지. BFS라 어떤 위치에 처음 도달한 순간이 최소 횟수.

[시간복잡도] O(R*C*(R+C))
  - 칸마다 한 번 방문(R*C), 각 칸에서 4방향 슬라이드(각 최대 O(R+C)).
  - 100x100이라 충분히 통과.
"""
from collections import deque


def solution(board):
    R, C = len(board), len(board[0])
    start_x, start_y = 0, 0

    # 시작 위치(R) 찾기
    for r in range(R):
        for c in range(C):
            if board[r][c] == 'R':
                start_x, start_y = r, c
                break

    # 상, 하, 좌, 우
    dx = [-1, 1, 0, 0]
    dy = [0, 0, -1, 1]

    # BFS: 방문한 '정지 위치'를 기록
    queue = deque([(start_x, start_y, 0)])
    visited = [[False] * C for _ in range(R)]
    visited[start_x][start_y] = True

    while queue:
        x, y, count = queue.popleft()

        # 멈춘 위치가 G면 도착 (중간 통과는 여기서 안 잡힘 → 정확)
        if board[x][y] == 'G':
            return count

        # 4방향으로 미끄러지기
        for i in range(4):
            nx, ny = x, y
            # 다음 칸이 판 밖이거나 'D'면 멈춤 (G는 멈춤 조건 아님 → 통과)
            while True:
                mx, my = nx + dx[i], ny + dy[i]
                if not (0 <= mx < R and 0 <= my < C) or board[mx][my] == 'D':
                    break
                nx, ny = mx, my

            # 멈춘 위치를 처음 방문하면 큐에 추가
            if not visited[nx][ny]:
                visited[nx][ny] = True
                queue.append((nx, ny, count + 1))

    return -1   # 큐가 비도록 G에 못 멈췄으면 도달 불가


if __name__ == "__main__":
    tests = [
        (["...D..R", ".D.G...", "....D.D", "D....D.", "..D...."], 7),
        (["R....", ".....", "..G..", ".....", "....."], -1),   # G가 내부라 멈출 수 없음
        (["R...G"], 1),
    ]
    all_pass = True
    for idx, (board, expected) in enumerate(tests, 1):
        got = solution(board)
        ok = got == expected
        all_pass &= ok
        print(f"test {idx}: {'OK ' if ok else 'FAIL'} | got={got} expected={expected}")
    print("=" * 40)
    print("ALL PASS" if all_pass else "SOME FAILED")


# ============================================================
# 피드백 (Day 67 / 6/14 코테)
# ============================================================
# [잘한 것]
# - 문제 타입을 정확히 BFS 최단경로로 잡음 (최소 횟수 + 균일 비용).
# - 대화 중에 핵심 함정 3개를 스스로 질문해서 다 정확히 처리함:
#     1) "방향이 중요한 거 아닌가?" → 방향은 이웃 계산에만 쓰고, 상태(노드)는
#        위치 하나. visited도 위치 기준. (정확)
#     2) "visited 왜 필요?" → 슬라이드 그래프엔 사이클(왔다갔다)이 있어서 필수.
#     3) "중간에 G 있으면?" → G는 멈춤 조건 아님(통과), 도달 체크는 멈춘 지점
#        에서만. 코드에서 정확히 그렇게 구현됨 (슬라이드는 'D'/벽에서만 멈추고,
#        G 체크는 popleft 직후 = 정지 위치).
#   질문으로 모델을 먼저 검증하고 구현한 게 이 풀이의 백미.
# - 슬라이드 내부 루프(다음 칸 검사 후 전진)와 BFS 뼈대를 깔끔하게 분리.
#
# [아주 사소한 것 - 버그 아님]
# - R 찾는 이중 루프의 break는 안쪽 for만 빠져나옴 (바깥 for는 계속 돔).
#   'R'이 한 번만 등장하니 결과엔 지장 없지만, 두 루프를 다 끊고 싶으면
#   flag를 쓰거나 함수로 분리하는 패턴을 기억해둘 것.
