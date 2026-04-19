# 문제 설명
# 문자열 my_string과 이차원 정수 배열 queries가 매개변수로 주어집니다. queries의 원소는 [s, e] 형태로, my_string의 인덱스 s부터 인덱스 e까지를 뒤집으라는 의미입니다. my_string에 queries의 명령을 순서대로 처리한 후의 문자열을 return 하는 solution 함수를 작성해 주세요.

# 제한사항
# my_string은 영소문자로만 이루어져 있습니다.
# 1 ≤ my_string의 길이 ≤ 1,000
# queries의 원소는 [s, e]의 형태로 0 ≤ s ≤ e < my_string의 길이를 만족합니다.
# 1 ≤ queries의 길이 ≤ 1,000

def solution(my_string, queries):
    s_list = list(my_string)
    
    for s, e in queries:
        # 2. 해당 구간을 뒤집어서 다시 그 자리에 할당하기
        # s부터 e까지 포함하기 위해 e+1 사용
        s_list[s:e+1] = s_list[s:e+1][::-1]
        
    # 3. 리스트를 다시 문자열로 합쳐서 반환
    return "".join(s_list)


# 생각해내지 못해서 정답을 참조했음
#최초의 아이디어는 구간별로 reverse함수를 사용하는 거였는데 임시 리스트만 생긴다는 것을 알게됨