def solution(A, B):
    answer=0
    
    #A와 B를 곱한 후, 이진수로 변환하고 이를 string 타입으로 변환
    mul = str(bin(A*B))

    #string mul 변수 내에 1이 몇 개나 있는지 세는 반복문
    for i in mul:
        if i=="1":
            answer+=1

    return answer
