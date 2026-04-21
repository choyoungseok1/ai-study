# 1.I/0을 가장먼저 생각할 것
#     - 무엇을 입력으로 어떤 출력을 얻을지 고민하기
#3과 5의 배수 구하기

# 입력: 1부터 999까지(1,000 미만의 자연수)
# 출력: 3의 배수와 5의 배수의 총합
# 생각해 볼 것:
# 3의 배수와 5의 배수는 어떻게 찾지?
# 3의 배수와 5의 배수가 겹칠 때는 어떻게 하지? 즉 15의 배수 처리

result = 0
for n in range(1,1000):
    if n % 3 == 0 or n % 5 == 0 :
        result += n
        
print(result)


# A 씨는 게시판 프로그램을 작성하고 있다. 그런데 게시물의 총 개수와 한 페이지에 보여 줄 게시물 수를 입력받아 총 페이지 수를 출력하는 프로그램이 필요하다고 한다.

# 이렇게 게시판의 페이지 수를 구하는 것을 '페이징'이라고 부른다.

# 함수 이름은? get_total_page
# 입력받는 값은? 게시물의 총 개수(m), 한 페이지에 보여 줄 게시물 수(n)
# 출력하는 값은? 총 페이지 수

def get_total_page(m,n):
    if m % n == 0:
        return m//n
    else :
        return m//n +1
    
print(get_total_page(5, 10))
print(get_total_page(15, 10))
print(get_total_page(25, 10))
print(get_total_page(30, 10))


# 이번에는 컴퓨터와 대결하는 숫자 야구 게임을 만들어 보자. 숫자 야구는 상대방이 정한 서로 다른 3자리 숫자를 맞히는 게임이다. 숫자를 추측하면 스트라이크와 볼로 힌트를 알려주고, 이 힌트를 바탕으로 정답을 찾아가는 것이 이 게임의 핵심이다.
import random

nums = random.sample(range(1, 10), 3)
count = 0

while True:
    question = input("3자리 숫자를 입력하세요: ")
    guess = list(map(int, question))
    count += 1

    strike = 0
    ball = 0

    for i in range(3):
        if guess[i] == nums[i]:
            strike += 1
        elif guess[i] in nums:
            ball += 1

    if strike == 3:
        print(f"정답! {count}번 만에 맞혔습니다.")
        break

    print(f"{strike}스트라이크 {ball}볼")
    
    
#이번에는 문자열을 암호화하는 시저 암호 프로그램을 만들어 보자. 시저 암호는 고대 로마의 율리우스 카이사르(시저)가 사용했다고 알려진 암호 방식으로, 알파벳을 일정한 수만큼 밀어서 다른 글자로 바꾸는 것이다. 예를 들어 A를 3칸 밀면 D가 되고, B는 E가 된다.
def caesar(word, key):
    result = ""
    for char in word:
        num = ord(char) - ord('A')
        shifted = (num + key) % 26
        result += chr(shifted + ord('A'))
    return result

word = input("문자열을 입력하세요: ")
key = int(input("밀 칸 수를 입력하세요: "))

print(f"암호화: {caesar(word, key)}")