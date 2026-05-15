# 문제 설명
# 양의 정수 n이 매개변수로 주어집니다. n × n 배열에 1부터 n2 까지 정수를 인덱스 [0][0]부터 시계방향 나선형으로 배치한 이차원 배열을 return 하는 solution 함수를 작성해 주세요.

# 제한사항
# 1 ≤ n ≤ 30

def solution(n):
    # 1. n x n 배열을 0으로 초기화
    matrix = [[0] * n for _ in range(n)]
    
    # 2. 이동 방향: 우 -> 하 -> 좌 -> 상 (시계 방향)
    dr = [0, 1, 0, -1]
    dc = [1, 0, -1, 0]
    
    r, c = 0, 0    # 현재 위치
    dist = 0       # 현재 방향 (0:우, 1:하, 2:좌, 3:상)
    
    for i in range(1, n * n + 1):
        matrix[r][c] = i  # 숫자 채우기
        
        # 다음 이동할 위치 미리 계산
        nr = r + dr[dist]
        nc = c + dc[dist]
        
        # 다음 위치가 범위를 벗어나거나 이미 숫자가 채워져 있다면 방향 전환
        if not (0 <= nr < n and 0 <= nc < n) or matrix[nr][nc] != 0:
            dist = (dist + 1) % 4
            nr = r + dr[dist]
            nc = c + dc[dist]
        
        # 위치 업데이트
        r, c = nr, nc
        
    return matrix

#사실 지금봐도 코드이해가 잘 안됨