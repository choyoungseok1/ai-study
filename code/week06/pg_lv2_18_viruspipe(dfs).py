# 문제 설명
# 1번부터 n번까지 번호가 붙은 n개의 배양체를 n-1개의 파이프로 이어 하나의 트리 모양을 만들었습니다. 각 파이프는 A,B,C 3개의 종류 중 하나로 초기에 모든 파이프는 닫혀있습니다.

# 배양체 중 하나가 바이러스에 감염되어 있습니다. 바이러스에 감염된 배양체는 열린 파이프를 통해 연결된 다른 인접한 배양체를 감염시킵니다.

# 당신은 종류가 같은 파이프를 한꺼번에 모두 열었다가 닫을 수 있습니다. 단, 한 종류의 파이프를 연 후 다시 닫기 전에 다른 종류의 파이프를 열 수 없습니다. 파이프를 열었다 닫는 행동을 최대 k번 반복해 최대한 많은 배양체에 바이러스를 감염시키려고 합니다.

# 배양체의 개수를 나타내는 정수 n, 감염된 배양체의 노드 번호를 나타내는 정수 infection, 파이프의 정보를 나타내는 2차원 정수 배열 edges, 최대 행동 수를 나타내는 정수 k가 매개변수로 주어집니다. 최대 k번 파이프를 열었다 닫은 후, 감염된 배양체 개수의 최댓값을 return 하도록 solution 함수를 완성해 주세요.

# 제한사항
# 2 ≤ n ≤ 100
# 1 ≤ infection ≤ n
# edges의 길이 = n-1
# edges[i]는 [x, y, type]의 형태로 x번 노드의 배양체와 y번 노드의 배양체 사이가 type 종류의 파이프로 연결되어 있음을 의미합니다.
# 1 ≤ x < y ≤ n
# 1 ≤ type ≤ 3
# 1은 A, 2는 B, 3은 C 를 나타냅니다.
# 1 ≤ k ≤ 10

def solution(n, infection, edges, k):
    # --- 그래프 구성 ---
    # edges의 [x, y, type]을 양방향 인접 리스트로 변환
    # 각 노드의 이웃을 (이웃노드, 파이프타입) 튜플로 저장
    graph = {}
    for x, y, t in edges:
        graph[x] = graph.get(x, [])
        graph[x].append((y, t))  # x → y 방향, 타입 t
        graph[y] = graph.get(y, [])
        graph[y].append((x, t))  # y → x 방향, 타입 t (양방향)

    # --- 감염 퍼뜨리기 (BFS) ---
    # 특정 타입의 파이프를 열었을 때 감염이 연쇄적으로 퍼지는 걸 처리
    # 감염된 모든 노드에서 동시에 출발해서, 해당 타입 파이프로 연결된 노드를 전부 감염
    def spread(infected_set, t_type):
        from collections import deque
        queue = deque(list(infected_set))  # 현재 감염된 노드들을 큐에 넣고
        visited = set(infected_set)        # 이미 감염된 건 방문 처리

        while queue:
            curr = queue.popleft()         # 감염 노드 하나 꺼내서
            if curr in graph:
                for nxt, p_type in graph[curr]:     # 이웃 순회
                    if p_type == t_type and nxt not in visited:  # 타입 일치 + 미감염
                        visited.add(nxt)    # 감염 처리
                        queue.append(nxt)   # 큐에 넣어서 연쇄 감염 계속
        return visited  # 새로운 감염 집합 리턴

    # --- DFS로 모든 선택 경우 탐색 ---
    # 매번 A(1), B(2), C(3) 중 하나를 선택 → 최대 3^k 경우의 수
    max_infected = 0

    def dfs(rem_k, current_infected):
        nonlocal max_infected
        max_infected = max(max_infected, len(current_infected))  # 현재까지 최대 감염 수 갱신

        if rem_k == 0 or len(current_infected) == n:  # k번 다 썼거나 전부 감염되면 종료
            return

        for t_type in [1, 2, 3]:                          # A, B, C 각각 시도
            next_infected = spread(current_infected, t_type)  # 해당 타입으로 퍼뜨리기

            if len(next_infected) > len(current_infected):  # 새로 감염된 게 있을 때만 진행
                dfs(rem_k - 1, next_infected)               # 남은 횟수 -1로 재귀
            # 새로 감염된 게 없으면 의미없으니 스킵 (가지치기)

    dfs(k, {infection})  # 초기 감염 노드 하나로 시작

    return max_infected


# 잘한 점:

# spread 함수를 BFS로 분리한 게 깔끔해. 감염 퍼뜨리기와 선택 탐색을 역할 분리한 거야.
# len(next_infected) > len(current_infected) 가지치기가 좋았어. 변화 없는 경우를 스킵해서 불필요한 탐색 줄임.
# set으로 감염 집합 관리한 것도 맞아. 중복 방지 + in 연산 O(1).

# 고쳐야 할 점:

# from collections import deque를 함수 안에 넣으면 매번 import해. 맨 위로 빼는 게 좋아.
# infectedn = [infection]이랑 answer = 0이 선언만 되고 안 쓰여. 불필요한 변수는 지우는 습관.
# max_infected 갱신을 종료 조건 전에 하는 건 잘 했어. 종료 조건 안에만 넣으면 k를 다 안 쓰고도 최대인 경우를 놓칠 수 있으니까.