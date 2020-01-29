# 집합의 모든 부분 집합 생성해주는 함수
def get_subset(string_list):
    
    power_set = [[]]
    
    for s in string_list:
        for sub_set in power_set:
            power_set = power_set + [list(sub_set) + [s]]
            
    # 부분집합 길이가 2 이상인 것만 남기고 제거
    power_set = [x for x in power_set[1:] if len(x) >= 2]
    
    return power_set

# 문자열 내부에 중복 문자 있는 지 체크해주는 함수
def check_overlapping(string_list):
    
    concat_string = "".join(string_list)
    char_list = list(concat_string)
    
    if len(char_list)!=len(set(char_list)):
        return True # 중복
    else:
        return False


def solution(A):
    
    string_list = []
    answer = 0

    # 중복 문자가 없는 부분 집합 추출
    for a in get_subset(A):
        if check_overlapping(a) == False:
            string_list.append("".join(a))

    max_len = 0
    # calculate the largest string
    for concat_s in string_list:
        if len(concat_s) > max_len:
             max_len = len(concat_s)

    return max_len
    
solution(['co','dil','ity'])
