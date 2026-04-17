# 2자리 이상의 정수 number가 주어집니다. 주어진 코드는 이 수를 2자리씩 자른 뒤, 자른 수를 모두 더해서 그 합을 출력하는 코드입니다. 코드가 올바르게 작동하도록 한 줄을 수정해 주세요.

# 제한사항
# 10 ≤ number ≤ 2,000,000,000
# number의 자릿수는 2의 배수입니다.
#한 줄만 수정하여 풀기
number = int(input())

answer = 0

for i in range(len(str(number))//2):
    answer += number % 100
    number //= 100

print(answer)

#======================================================================= 위에가 내가 푼 답
number_1 = int(input())
answer_1 = 0
while number:
    answer_1 += number % 100
    number_1 //= 100

print(answer_1)
# 변수 분리를 위해 변수명만 변경
#다른 사람의 풀이를 보며 while문을 다시 공부하게 됨 ---> number가 0이 될때까지 반복하게됨



