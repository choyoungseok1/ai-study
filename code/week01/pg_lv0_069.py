# 문자열 my_string과 정수 배열 indices가 주어질 때, my_string에서 indices의 원소에 해당하는 인덱스의 글자를 지우고 이어 붙인 문자열을 return 하는 solution 함수를 작성해 주세요.

# 제한사항
# 1 ≤ indices의 길이 < my_string의 길이 ≤ 100
# my_string은 영소문자로만 이루어져 있습니다
# 0 ≤ indices의 원소 < my_string의 길이
# indices의 원소는 모두 서로 다릅니다.

#내 풀이
def solution(my_string, indices):
    temp = list(my_string)
    
    for i in indices:
        temp[i] = "" # 해당 위치를 빈칸으로 만듦
        
    return "".join(temp) # 빈칸을 제외하고 나머지 글자들을 합침
#남의 풀이
def solution(my_string, indices):
    my_string = list(my_string)
    for i in sorted(indices, reverse=True):
        del my_string[i]
    return ''.join(my_string)

#뒤집어 빼는 방법인데 이게 왜 되지 라는 고민을 하게했음.