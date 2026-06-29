"""
프로그래머스 Lv2 - 무인도 여행
=================================================================

[문제 설명]
지도(maps)는 'X'(바다) 또는 1~9 자연수(식량)로 이루어진 직사각형 격자.
상하좌우로 연결된 땅들이 하나의 무인도를 이루며, 그 섬의 숫자 합 = 머물 수 있는 최대 일수.
각 섬에서 머물 수 있는 일수를 오름차순 배열로 return. 섬이 없으면 [-1].

[제한사항]
- 3 <= maps의 길이 <= 100
- 3 <= maps[i]의 길이 <= 100
- maps[i]는 'X' 또는 1~9 자연수로 이루어진 문자열
- 지도는 직사각형

[핵심 발상]
전형적인 flood fill (연결 요소 찾기) 문제.
1. 모든 칸을 순회하며 "아직 안 간 땅" = 새 섬의 시작점을 찾는다 (바깥 루프)
2. 시작점에서 상하좌우로 연결된 땅을 전부 훑으며 식량을 누적 (탐색)
3. 한 번 방문한 칸은 다시 세지 않는다 (방문 체크 ← 핵심 함정)
4. 섬마다 합을 모아서 정렬

[주의 함정]
- maps[r][c]는 문자열('5')이지 숫자(5)가 아니다 → int() 변환 필수
- 문자열은 item 수정 불가 → 덮어쓰기 방식이면 [list(row) for row in maps] 변환 필요
  (안 하면 TypeError: 'str' object does not support item assignment)
- 격자 경계 체크: 0 <= nr < R and 0 <= nc < C
- DFS 재귀는 호출 스택 깊이 한계(기본 1000) → 큰 입력에서 RecursionError
"""

# =================================================================
# 풀이 ④ - DFS(재귀) + 덮어쓰기  ★ 직접 푼 풀이
# =================================================================
# 발상: 재귀 함수가 "현재 칸 식량 + 네 방향 재귀 결과의 합"을 반환.
#       호출 스택 자체가 탐색 스택 역할을 한다 (재귀 = 암묵적 스택).
#       진입하자마자 'X'로 덮어 재방문을 차단하는 게 생명.

import sys
sys.setrecursionlimit(10**6)   # 최악 100x100=10000칸이 한 줄로 이어질 수 있어 넉넉히

def solution(maps):
    grid = [list(row) for row in maps]   # 문자열 → 수정 가능한 리스트
    rows, cols = len(grid), len(grid[0])
    dx = [-1, 1, 0, 0]
    dy = [0, 0, -1, 1]

    def dfs(x, y):
        food = int(grid[x][y])
        grid[x][y] = 'X'            # ★ 호출 전(진입 직후) 방문 표시 → 무한재귀 방지
        for i in range(4):
            nx, ny = x + dx[i], y + dy[i]
            if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] != 'X':
                food += dfs(nx, ny)  # 자기 호출 = 스택에 쌓는 것과 동일
        return food

    answer = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 'X':
                answer.append(dfs(r, c))
    return sorted(answer) if answer else [-1]


# =================================================================
# 비교용 나머지 3가지 케이스
# =================================================================
# flood fill은 골격이 하나, 부품 2개(방문체크: visited/덮어쓰기, 탐색: DFS/BFS)만 갈아끼움.
# 아래 4개를 나란히 보면 "어디만 다른가"가 핵심 수확.

from collections import deque


# ① BFS + visited 배열
def solution_bfs_visited(maps):
    R, C = len(maps), len(maps[0])
    dr, dc = [-1, 1, 0, 0], [0, 0, -1, 1]
    visited = [[False] * C for _ in range(R)]
    answer = []
    for r in range(R):
        for c in range(C):
            if maps[r][c] != 'X' and not visited[r][c]:
                visited[r][c] = True
                food = int(maps[r][c])
                q = deque([(r, c)])
                while q:
                    cr, cc = q.popleft()          # BFS: 큐 앞에서 꺼냄
                    for d in range(4):
                        nr, nc = cr + dr[d], cc + dc[d]
                        if 0 <= nr < R and 0 <= nc < C and maps[nr][nc] != 'X' and not visited[nr][nc]:
                            visited[nr][nc] = True  # 큐에 넣을 때 바로 방문 표시
                            food += int(maps[nr][nc])
                            q.append((nr, nc))
                answer.append(food)
    return sorted(answer) if answer else [-1]


# ② BFS + 덮어쓰기
def solution_bfs_overwrite(maps):
    maps = [list(row) for row in maps]   # 문자열 수정 불가 → 리스트 변환 (빠뜨리면 TypeError)
    R, C = len(maps), len(maps[0])
    dr, dc = [-1, 1, 0, 0], [0, 0, -1, 1]
    answer = []
    for r in range(R):
        for c in range(C):
            if maps[r][c] != 'X':
                food = int(maps[r][c])
                maps[r][c] = 'X'                  # 방문 = 'X'로 덮음
                q = deque([(r, c)])
                while q:
                    cr, cc = q.popleft()
                    for d in range(4):
                        nr, nc = cr + dr[d], cc + dc[d]
                        if 0 <= nr < R and 0 <= nc < C and maps[nr][nc] != 'X':
                            food += int(maps[nr][nc])
                            maps[nr][nc] = 'X'
                            q.append((nr, nc))
                answer.append(food)
    return sorted(answer) if answer else [-1]


# ③ DFS(스택) + visited 배열
def solution_dfs_stack(maps):
    R, C = len(maps), len(maps[0])
    dr, dc = [-1, 1, 0, 0], [0, 0, -1, 1]
    visited = [[False] * C for _ in range(R)]
    answer = []
    for r in range(R):
        for c in range(C):
            if maps[r][c] != 'X' and not visited[r][c]:
                visited[r][c] = True
                food = int(maps[r][c])
                stack = [(r, c)]
                while stack:
                    cr, cc = stack.pop()          # DFS: 스택 뒤에서 꺼냄 (①과 여기만 다름!)
                    for d in range(4):
                        nr, nc = cr + dr[d], cc + dc[d]
                        if 0 <= nr < R and 0 <= nc < C and maps[nr][nc] != 'X' and not visited[nr][nc]:
                            visited[nr][nc] = True
                            food += int(maps[nr][nc])
                            stack.append((nr, nc))
                answer.append(food)
    return sorted(answer) if answer else [-1]


# =================================================================
# 4가지 비교 포인트
# =================================================================
# ①↔③ (BFS↔DFS, visited 고정): 딱 한 줄. q.popleft() ↔ stack.pop().
#                                큐냐 스택이냐 = "다음에 어느 칸을 먼저 펼치냐"의 차이.
# ①↔② (visited↔덮어쓰기, BFS 고정): visited[][]=True/체크 → maps[][]='X'/체크.
#                                  ②는 문자열 수정 불가라 [list(row)...] 변환이 맨 앞에 추가.
# ④만 결이 다름: 나머지 셋은 명시적 큐/스택으로 돌지만, ④는 재귀 호출 스택이 ③의 스택 역할.
#               "재귀 = 암묵적 스택" → ③↔④ 비교하면 확 와닿음.
#               setrecursionlimit을 올려야 하는 이유도 이것(호출 스택도 진짜 스택이라 깊이 한계).
#
# 시간복잡도: 네 버전 모두 O(R×C) — 모든 칸을 한 번씩 방문. DFS/BFS 간 효율 차이 없음.
#            덮어쓰기는 visited 배열 안 써서 공간 O(1) 추가, 대신 원본 maps 훼손(트레이드오프).


# =================================================================
# 대화 기반 피드백 (Day 79)
# =================================================================
"""
[스스로 잘한 것]
- 문제 유형을 바로 정확히 짚음: "flooding" = flood fill(연결 요소). 접근 자체가 정확.
- ★ 재귀가 식량 합을 반환하는 구조를 스스로 설계: food = 현재 칸 + 네 방향 dfs 합.
  바깥에 누적 변수 두는 것보다 훨씬 우아한 형태. 재귀 flood fill의 정석.
- ★ 진입 직후 grid[x][y]='X' 덮기를 정확한 위치에 배치.
  이걸 함수 끝에서 하거나 빠뜨렸으면 A→B→A 무한재귀로 RecursionError.
  '재방문 차단을 호출 전에' 한 게 핵심.
- 비교용 ② 버전을 안 보고도 [list(row) for row in maps] 변환을 스스로 넣음.
  → 문자열이 수정 불가임을 미리 의식. 예전 실수 패턴 'list-vs-string 혼동'을 안 밟음.
- int() 변환도 정확히 들어감 (문자 '5' → 숫자 5).

[설계 단계에서 따져본 것 (좋은 습관)]
- "DFS+덮어쓰기가 효율적일 것 같다"는 직관을 그냥 쓰지 않고 근거를 따짐.
  → 덮어쓰기=공간 효율 맞음(visited 배열 불필요). 단 DFS/BFS는 시간복잡도 동일,
    효율 차이가 아니라 트레이드오프(재귀 깊이 한계) 문제임을 확인.
  (예전 실수 패턴 '감이 아니라 수학적 근거로' 를 의식적으로 적용)

[미세 주의점]
- sys.setrecursionlimit(10000): 최악 100x100=10000칸이 한 줄로 이어지면 재귀 깊이가
  딱 10000까지 가서 살짝 빠듯. 이 문제 테스트는 통과하지만 경계에서 아슬아슬.
  → 여유 있게 10**6 또는 100000 권장.

[일반 교훈]
- flood fill = 골격 하나 + 부품 2개(방문체크 / 탐색방식) 조합. 4가지가 다 같은 뼈대.
- 재귀 = 암묵적 스택. ③(명시적 스택)과 ④(재귀)를 비교하면 본질이 같음이 보인다.
- BFS/DFS 전환은 popleft() ↔ pop() 한 줄. 자료구조(큐/스택) 차이일 뿐.
"""
