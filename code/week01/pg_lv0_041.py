# 문제 설명
# 정수가 담긴 리스트 num_list가 주어집니다. num_list의 홀수만 순서대로 이어 붙인 수와 짝수만 순서대로 이어 붙인 수의 합을 return하도록 solution 함수를 완성해주세요.

# 제한사항
# 2 ≤ num_list의 길이 ≤ 10
# 1 ≤ num_list의 원소 ≤ 9
# num_list에는 적어도 한 개씩의 짝수와 홀수가 있습니다.

#나의 최초 코드

def solution(num_list):
    answer = 0
    odd_sum = ""
    even_sum = ""
    for i in range(len(num_list)):
        if num_list[i] % 2 == 0:
            even_sum += str(num_list[i])
        else :
            odd_sum += str(num_list[i])
            
    answer = eval(f'{even_sum} + {odd_sum}')
    return answer

#특정 상황에서 Runtime error 발생 이유 : eval 함수가 루프 안에 있었음 수정 후 해결됨
#다른 사람들의 코드를 보면서 느낀점1: 굳이 len()함수를 쓸 필요 X Num_list 요소를 그대로 가져와도 됨
#느낀점 2  eval 함수 대신 그냥 int() 두 번 써도 됐음.