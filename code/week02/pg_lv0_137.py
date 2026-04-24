# 문제 설명
# 이차원 정수 배열 arr이 매개변수로 주어집니다. arr의 행의 수가 더 많다면 열의 수가 행의 수와 같아지도록 각 행의 끝에 0을 추가하고, 열의 수가 더 많다면 행의 수가 열의 수와 같아지도록 각 열의 끝에 0을 추가한 이차원 배열을 return 하는 solution 함수를 작성해 주세요.

# 제한사항
# 1 ≤ arr의 길이 ≤ 100
# 1 ≤ arr의 원소의 길이 ≤ 100
# arr의 모든 원소의 길이는 같습니다.
# 1 ≤ arr의 원소의 원소 ≤ 1,000

def solution(arr):
    row_cnt = len(arr)
    col_cnt = len(arr[0])
    
    # 1. 행이 더 많은 경우 (열을 추가)
    if row_cnt > col_cnt:
        for i in range(row_cnt):
            # 부족한 열 개수만큼 0 추가
            arr[i].extend([0] * (row_cnt - col_cnt))
            
    # 2. 열이 더 많은 경우 (행을 추가)
    elif col_cnt > row_cnt:
        # 부족한 행 개수만큼 [0, 0, ... 0] 줄 추가
        for _ in range(col_cnt - row_cnt):
            arr.append([0] * col_cnt)
            
    return arr

#extend(): 여러 요소를 한번에 더하기 리스트에
#제미나이의 코드
def solution(arr):
    # 행과 열 중 더 큰 값을 n으로 설정
    n = max(len(arr), len(arr[0]))
    
    # 1. 모든 행의 길이를 n으로 맞춤 (부족하면 0 채우기)
    # 2. 행의 개수가 n보다 작으면 부족한 만큼 [0]*n 행을 추가
    return [row + [0] * (n - len(row)) for row in arr] + [[0] * n for _ in range(n - len(arr))]
