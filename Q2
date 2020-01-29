import random
import string
def solution(S):
    answer=""

    #회문 판단시, 양쪽 다 ?일 경우 특정 랜덤 알파벳이 나오도록 저장.
    random_letter="".join([random.choice(string.ascii_lowercase)for _ in range(1)])

    #회문이 안 되는 경우 "NO"를 출력
    for i in range(len(S)//2):
        if S[i]!=S[-1-i] and S[i]!="?" and S[-1-i]!="?":
            return "NO"

    #주어진 단어가 회문이 되도록 생성
    for i in range(len(S)):
        if S[i]=="?" and S[-1-i]=="?":
            answer+=random_letter
            
        elif S[i]=="?":
            answer+=S[-1-i]
            
        else:
            answer+=S[i]
            
    return answer

