# 문제 설명
# 프로그래머스 팀에서는 기능 개선 작업을 수행 중입니다. 각 기능은 진도가 100%일 때 서비스에 반영할 수 있습니다.

# 또, 각 기능의 개발속도는 모두 다르기 때문에 뒤에 있는 기능이 앞에 있는 기능보다 먼저 개발될 수 있고, 이때 뒤에 있는 기능은 앞에 있는 기능이 배포될 때 함께 배포됩니다.

# 먼저 배포되어야 하는 순서대로 작업의 진도가 적힌 정수 배열 progresses와 각 작업의 개발 속도가 적힌 정수 배열 speeds가 주어질 때 각 배포마다 몇 개의 기능이 배포되는지를 return 하도록 solution 함수를 완성하세요.

# 제한 사항
# 작업의 개수(progresses, speeds배열의 길이)는 100개 이하입니다.
# 작업 진도는 100 미만의 자연수입니다.
# 작업 속도는 100 이하의 자연수입니다.
# 배포는 하루에 한 번만 할 수 있으며, 하루의 끝에 이루어진다고 가정합니다. 예를 들어 진도율이 95%인 작업의 개발 속도가 하루에 4%라면 배포는 2일 뒤에 이루어집니다.

def solution(progresses, speeds):
    answer = []
    time = []
    for i in range(len(speeds)):
        if (100-progresses[i])%speeds[i] == 0:
            time.append((100-progresses[i])/speeds[i])
        else :
            time.append((100-progresses[i])//speeds[i]+1)
    count = 1
    polar = time[0]
    for i in range(1,len(time)):
        if polar >= time[i]:
            count += 1
        else :
            answer.append(count)
            count = 1
            polar = time[i]
    answer.append(count)
    return answer


# 잘한 점:

# 소요일 계산에서 올림 처리를 나머지 체크로 정확하게 구현했어
# 큐 방식으로 한 번 순회로 풀겠다는 방향을 잡은 게 좋았어
# 기준값(polar)과 비교하는 구조를 스스로 설계했어

# 개선할 점:

# 기준값 업데이트 실수 — polar를 매번 바꿔서 "앞 작업이 뒤를 막고 있다"는 핵심 조건을 놓칠 뻔했어. 큐 문제에서는 기준이 바뀌는 시점을 정확히 파악하는 게 중요해
# count 초기값/마지막 처리 — 첫 원소 포함, 마지막 그룹 append를 빠뜨리기 쉬워. 이건 반복 패턴이니까 기억해둬: "for문 밖에서 초기화, for문 끝나고 마지막 처리"
# 소요일 계산은 math.ceil((100 - p) / s)로 한 줄로 가능해. 알아두면 편해

# 새로 배운 패턴:

# 큐에서 앞이 뒤를 막는 구조 — 기준값 유지하면서 그룹핑. 이 패턴 자주 나와