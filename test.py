def solution(board, moves):
    answer = 0
    bucket = []
    transpose = [[board[i][j] for i in range(len(board))] for j in range(len(board[0])) ]
    # for move in moves:
    #     if bucket == [] :
    #         for i in range(len(transpose[1])):
    #             if transpose[move-1][i] != 0:
    #                 bucket.append(transpose[move-1][i])
    #                 transpose[move-1][i] = 0
    #                 break
    #     elif len(bucket)>=1:
    #         for i in range(len(transpose[1])):
    #             if transpose[move-1][i] != 0 and transpose[move-1][i] == bucket[-1]:
    #                 bucket.pop()
    #                 answer +=2
    #                 transpose[move-1][i] = 0
    #                 break
    #             elif transpose[move-1][i] != 0 and transpose[move-1][i] != bucket[-1]:
    #                 bucket.append(transpose[move-1][i])
    #                 transpose[move-1][i] = 0
    #                 break
    for move in moves:
        for i in range(len(transpose[1])):
            if bucket != [] and bucket[-1] == transpose[move-1][i] and transpose[move-1][i] != 0:
                bucket.pop()
                transpose[move-1][i] = 0
                answer +=2
                break
            elif  transpose[move-1][i] != 0:
                bucket.append(transpose[move-1][i])
                transpose[move-1][i] = 0
                break
    return answer
    


board = [[0,0,0,0,0],[0,0,1,0,3],[0,2,5,0,1],[4,2,4,4,2],[3,5,1,3,1]]
moves = [1,5,3,5,1,2,1,4]
print(solution(board,moves))