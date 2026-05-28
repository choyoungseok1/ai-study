# 문제 설명
# [본 문제는 정확성과 효율성 테스트 각각 점수가 있는 문제입니다.]

# 카카오는 하반기 경력 개발자 공개채용을 진행 중에 있으며 현재 지원서 접수와 코딩테스트가 종료되었습니다. 이번 채용에서 지원자는 지원서 작성 시 아래와 같이 4가지 항목을 반드시 선택하도록 하였습니다.

# 코딩테스트 참여 개발언어 항목에 cpp, java, python 중 하나를 선택해야 합니다.
# 지원 직군 항목에 backend와 frontend 중 하나를 선택해야 합니다.
# 지원 경력구분 항목에 junior와 senior 중 하나를 선택해야 합니다.
# 선호하는 소울푸드로 chicken과 pizza 중 하나를 선택해야 합니다.
# 인재영입팀에 근무하고 있는 니니즈는 코딩테스트 결과를 분석하여 채용에 참여한 개발팀들에 제공하기 위해 지원자들의 지원 조건을 선택하면 해당 조건에 맞는 지원자가 몇 명인 지 쉽게 알 수 있는 도구를 만들고 있습니다.
# 예를 들어, 개발팀에서 궁금해하는 문의사항은 다음과 같은 형태가 될 수 있습니다.
# 코딩테스트에 java로 참여했으며, backend 직군을 선택했고, junior 경력이면서, 소울푸드로 pizza를 선택한 사람 중 코딩테스트 점수를 50점 이상 받은 지원자는 몇 명인가?

# 물론 이 외에도 각 개발팀의 상황에 따라 아래와 같이 다양한 형태의 문의가 있을 수 있습니다.

# 코딩테스트에 python으로 참여했으며, frontend 직군을 선택했고, senior 경력이면서, 소울푸드로 chicken을 선택한 사람 중 코딩테스트 점수를 100점 이상 받은 사람은 모두 몇 명인가?
# 코딩테스트에 cpp로 참여했으며, senior 경력이면서, 소울푸드로 pizza를 선택한 사람 중 코딩테스트 점수를 100점 이상 받은 사람은 모두 몇 명인가?
# backend 직군을 선택했고, senior 경력이면서 코딩테스트 점수를 200점 이상 받은 사람은 모두 몇 명인가?
# 소울푸드로 chicken을 선택한 사람 중 코딩테스트 점수를 250점 이상 받은 사람은 모두 몇 명인가?
# 코딩테스트 점수를 150점 이상 받은 사람은 모두 몇 명인가?
# 즉, 개발팀에서 궁금해하는 내용은 다음과 같은 형태를 갖습니다.

# * [조건]을 만족하는 사람 중 코딩테스트 점수를 X점 이상 받은 사람은 모두 몇 명인가?
# [문제]
# 지원자가 지원서에 입력한 4가지의 정보와 획득한 코딩테스트 점수를 하나의 문자열로 구성한 값의 배열 info, 개발팀이 궁금해하는 문의조건이 문자열 형태로 담긴 배열 query가 매개변수로 주어질 때,
# 각 문의조건에 해당하는 사람들의 숫자를 순서대로 배열에 담아 return 하도록 solution 함수를 완성해 주세요.

# [제한사항]
# info 배열의 크기는 1 이상 50,000 이하입니다.
# info 배열 각 원소의 값은 지원자가 지원서에 입력한 4가지 값과 코딩테스트 점수를 합친 "개발언어 직군 경력 소울푸드 점수" 형식입니다.
# 개발언어는 cpp, java, python 중 하나입니다.
# 직군은 backend, frontend 중 하나입니다.
# 경력은 junior, senior 중 하나입니다.
# 소울푸드는 chicken, pizza 중 하나입니다.
# 점수는 코딩테스트 점수를 의미하며, 1 이상 100,000 이하인 자연수입니다.
# 각 단어는 공백문자(스페이스 바) 하나로 구분되어 있습니다.
# query 배열의 크기는 1 이상 100,000 이하입니다.
# query의 각 문자열은 "[조건] X" 형식입니다.
# [조건]은 "개발언어 and 직군 and 경력 and 소울푸드" 형식의 문자열입니다.
# 언어는 cpp, java, python, - 중 하나입니다.
# 직군은 backend, frontend, - 중 하나입니다.
# 경력은 junior, senior, - 중 하나입니다.
# 소울푸드는 chicken, pizza, - 중 하나입니다.
# '-' 표시는 해당 조건을 고려하지 않겠다는 의미입니다.
# X는 코딩테스트 점수를 의미하며 조건을 만족하는 사람 중 X점 이상 받은 사람은 모두 몇 명인 지를 의미합니다.
# 각 단어는 공백문자(스페이스 바) 하나로 구분되어 있습니다.
# 예를 들면, "cpp and - and senior and pizza 500"은 "cpp로 코딩테스트를 봤으며, 경력은 senior 이면서 소울푸드로 pizza를 선택한 지원자 중 코딩테스트 점수를 500점 이상 받은 사람은 모두 몇 명인가?"를 의미합니다.

from itertools import combinations
from bisect import bisect_left
def solution(info, query):
    answer = []

    table = {}
    for person in info:
        parts = person.split()
        conditions = parts[:4]
        score = int(parts[4])
        for i in range(5):
            for combo in combinations(range(4), i):
                key = conditions[:]  # 복사
                for j in combo:
                    key[j] = "-"
                key = " ".join(key)
                table[key] = table.get(key,[])
                table[key].append(score)
       # 정렬 (쿼리 처리 전에)
    for key in table:
        table[key].sort()

    # 쿼리 처리 (for문 안에서)
    for q in query:
        parts = q.replace(" and ", " ").split()
        key = " ".join(parts[:4])
        score = int(parts[4])
        if key in table:
            # bisect_left로 개수 구해서 answer에 append
            answer.append(len(table[key])-bisect_left(table[key],score))
            
        else:
            answer.append(0)

    return answer

# 잘한 점:

# 딕셔너리로 조건별 분류하자는 아이디어를 직접 냈어. 문제 구조를 잘 파악한 거야.
# - 와일드카드를 쿼리 시점이 아니라 데이터 구축 시점에 처리하는 핵심 발상을 이해했어.
# bisect_left로 개수 구하는 로직 len - bisect_left를 바로 적용했어.

# 고쳐야 할 점:

# bisect_left 대상을 잘못 넣었어. query에 적용하려고 한 건 "이 함수가 뭘 하는지" 정확히 안 잡힌 상태에서 쓴 거야. 라이브러리 쓸 때는 입력이 뭐고 출력이 뭔지 먼저 확인하는 습관.
# for문 안의 결과를 밖에서 처리하려고 했어. 매 반복마다 append해야 하는데 for문 끝나고 마지막 값만 쓴 거지. 이건 실수 패턴 2번(return 위치)이랑 같은 맥락이야.
# 정렬을 빠뜨렸어. 이진탐색 = 정렬 전제. 이건 짝으로 기억해.

# 오늘 이진탐색 정리:

# 기본 구현: left, right, mid로 반씩 쪼개기
# 실전 활용: 정렬된 데이터에서 bisect_left로 O(log n) 탐색
# 핵심 패턴: 미리 분류 + 정렬 → 쿼리 시 이진탐색