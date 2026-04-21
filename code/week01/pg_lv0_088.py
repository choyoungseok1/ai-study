# 문제 설명
# 정수 배열 arr가 주어집니다. arr의 각 원소에 대해 값이 50보다 크거나 같은 짝수라면 2로 나누고, 50보다 작은 홀수라면 2를 곱하고 다시 1을 더합니다.

# 이러한 작업을 x번 반복한 결과인 배열을 arr(x)라고 표현했을 때, arr(x) = arr(x + 1)인 x가 항상 존재합니다. 이러한 x 중 가장 작은 값을 return 하는 solution 함수를 완성해 주세요.

# 단, 두 배열에 대한 "="는 두 배열의 크기가 서로 같으며, 같은 인덱스의 원소가 각각 서로 같음을 의미합니다.

# 제한사항
# 1 ≤ arr의 길이 ≤ 1,000,000
# 1 ≤ arr의 원소의 값 ≤ 100
# 최초의 아이디어는 각 2차원 리스트를 만들어서 arr과 바뀐 arr 을 저장 -> 마지막에서 2번째 index를 가져오는 방식을 선택함
#Runtime error 발생 : 리스트에 할당 가능한 수를 초과

def solution(arr):
    answer = 0
    prev_arr = arr
    while True:
        curr_arr =[]
        for num in prev_arr:
            if num >= 50 and num % 2 == 0:
                curr_arr.append(num // 2)
            elif num < 50 and num % 2 == 1:
                curr_arr.append(num * 2 + 1)
            else:
                curr_arr.append(num)
        if prev_arr == curr_arr :
            return answer
        else : 
            prev_arr = curr_arr
            answer +=1
    #최종 답안