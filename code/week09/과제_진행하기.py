"""
프로그래머스 Lv2 - 과제 진행하기
https://school.programmers.co.kr/learn/courses/30/lessons/176962

[핵심 아이디어]
- "hh:mm" 시각을 분 단위 정수로 바꾸고, 시작 시각 기준으로 정렬한다.
- 멈춘 과제는 stack(LIFO)에 [이름, 남은시간] 형태로 보관한다.
  ("가장 최근에 멈춘 과제부터 재개" == LIFO 라서 stack이 딱 맞음)
- 각 과제를 시작할 때, 다음 과제가 시작되기 전까지의 '틈(available)'과
  이 과제의 소요시간(cur_play)을 비교한다.
    · cur_play <= available  -> 틈 안에 끝남. answer에 넣고,
        남는 시간으로 stack에 멈춰둔 과제들을 while로 '연쇄' 처리한다.
        (남는 시간이 충분하면 멈춘 과제 여러 개를 연달아 끝낼 수 있음)
    · cur_play >  available  -> 중간에 끊김. 남은 시간(cur_play - available)을
        계산해서 stack에 push한다.
- "끝나는 시각 == 다음 시작 시각"이면 끝난 것으로 판단 -> 부등호는 '<=' 사용.
- for문은 마지막 직전(n-1)까지만 돈다. 마지막 과제는 뒤에 '다음 틈'이 없으므로
  루프 밖에서 따로 처리하고, 남아있는 stack을 LIFO 순서로 모두 비운다.

[시간복잡도] O(n log n)
  - 정렬이 지배적. 시뮬레이션은 각 과제가 stack에 최대 1번 push/pop 되므로 O(n).
  - n <= 1000 이라 충분히 여유.
"""


def solution(plans):
    # 1) "hh:mm" -> 분 변환 + [이름, 시작분, 소요시간(int)]으로 한 덩어리로 묶기
    #    (이름/시작/소요를 따로 떼면 정렬할 때 짝이 깨지므로 통째로 묶는 게 안전)
    new_plan = []
    for name, start, playtime in plans:
        h, m = map(int, start.split(":"))
        start_min = h * 60 + m
        new_plan.append([name, start_min, int(playtime)])

    # 2) 시작 시각(분) 기준 정렬
    new_plan.sort(key=lambda x: x[1])

    answer = []
    stopplan = []  # 멈춘 과제 보관: [이름, 남은시간], 가장 최근에 멈춘 게 맨 위(LIFO)

    # 3) 마지막 직전까지: '다음 과제 시작 전 틈'과 소요시간을 비교하며 진행
    for i in range(len(new_plan) - 1):
        cur_name, cur_start, cur_play = new_plan[i]
        next_start = new_plan[i + 1][1]

        available = next_start - cur_start  # 다음 과제 시작 전까지의 여유 시간

        if cur_play <= available:           # (가) 틈 안에 끝남
            answer.append(cur_name)
            available -= cur_play           # 끝내고 남은 시간

            # 남는 시간으로 멈춰둔 과제를 가장 최근 것부터 연쇄 처리
            while stopplan and available:
                prev_name, prev_play = stopplan.pop()
                if prev_play <= available:   # 멈췄던 과제도 남는 시간 안에 끝남
                    answer.append(prev_name)
                    available -= prev_play
                else:                        # 다 못 끝냄 -> 남은 만큼 깎아서 도로 보관
                    stopplan.append([prev_name, prev_play - available])
                    available = 0            # 남는 시간 소진 -> while 종료
        else:                                # (나) 틈을 넘김 -> 중단, 남은 시간 보관
            stopplan.append([cur_name, cur_play - available])

    # 4) 마지막 과제 처리 + 남아있는 멈춘 과제 전부 비우기 (LIFO)
    answer.append(new_plan[-1][0])
    while stopplan:
        answer.append(stopplan.pop()[0])

    return answer


if __name__ == "__main__":
    # 프로그래머스 공식 예제
    tests = [
        (
            [["korean", "11:40", "30"], ["english", "12:10", "10"], ["math", "12:30", "30"]],
            ["korean", "english", "math"],
        ),
        (
            [["science", "12:40", "50"], ["music", "12:20", "40"],
             ["history", "14:00", "30"], ["computer", "12:30", "100"]],
            ["science", "history", "computer", "music"],
        ),
        (
            [["aaa", "12:00", "20"], ["bbb", "12:10", "30"], ["ccc", "12:40", "10"]],
            ["bbb", "ccc", "aaa"],
        ),
    ]

    all_pass = True
    for idx, (plans, expected) in enumerate(tests, 1):
        got = solution(plans)
        ok = got == expected
        all_pass &= ok
        print(f"test {idx}: {'OK ' if ok else 'FAIL'} | got={got}")
    print("=" * 40)
    print("ALL PASS" if all_pass else "SOME FAILED")
