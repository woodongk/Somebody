from flask import render_template
from pydub import AudioSegment
import os, cv2, requests, json, random, subprocess, shutil
import numpy as np
from collections import Counter

# 영상 -> 사진 분할. 매개변수로는 영상 제목 넘겨줌.
# 1초에 1번, n= 2 : 1초에 2번캡처
def movie_divide(vname,n):
    print("METHOD : movie_divide")
    dir = os.path.abspath("./static/uploads")
    fdir = os.path.join(dir, vname)

    img_dir = "./static/uploads/images"
    # image 폴더 있다면 삭제
    if os.path.exists(img_dir) and os.path.isdir(img_dir):
        shutil.rmtree(img_dir)
    # image 폴더 생성
    os.mkdir(img_dir)

    vidcap = cv2.VideoCapture(fdir)
    count = 0

    # find frame rate of a video
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    ## fps 반올림
    print("video 프레임 rate :", round(fps))
    s_vidfps = round(fps) / n

    while (vidcap.isOpened()):
        # Capture frame-by-frame
        success, image = vidcap.read()
        # count 값 업데이트 기준으로 frame 업데이트됨
        if success == True:
            if count % s_vidfps == 0:
                cv2.imwrite(os.path.join(img_dir,"frame{:02d}.jpg".format(int(count / s_vidfps))),image)  # save frame as JPEG file
            count += 1
        else:
            break

    return get_json(vname)

# API 요청해 json 파일 받기
def get_json(vname):
    print("METHOD : get_json")

    json_dir = "./static/uploads/json"
    if os.path.exists(json_dir) and os.path.isdir(json_dir):
        shutil.rmtree(json_dir)
    # image 폴더 생성
    os.mkdir(json_dir)

    count = 1
    dir = os.path.abspath("./static/uploads/images")
    fname = sorted(os.listdir(dir))
    fdir = list()

    client_id = "ikkq6wbgvq" # API client 아이디랑 secret key
    client_secret = "DzLfqBH0jvOALQT536QR2eEsrvGxwxlbxY21IKlE"
    url = "https://naveropenapi.apigw.ntruss.com/vision-pose/v1/estimate" # 사람 인식

    for i in fname:
        fdir.append(os.path.join(dir, i))
    for i in fdir:
        print("Requesting... %s" % i)
        files = {'image': open(i, 'rb')}
        headers = {'X-NCP-APIGW-API-KEY-ID': client_id, 'X-NCP-APIGW-API-KEY': client_secret }
        response = requests.post(url,  files=files, headers=headers)
        rescode = response.status_code

        if(rescode == 200):
            strTodict = json.loads(response.text)
            with open("./static/uploads/json/test%02d.json" % count, 'w', encoding='utf-8') as make_file:
                json.dump(strTodict, make_file, indent="\t")
            count += 1
        else:
            print("Error Code:" + str(rescode))

    return change_cal(vname)

"""
json_data['predictions'][0]['0']['x'] --> dict key = score, x, y
구성
key predictions
list
key '0' '1' ... '17' 해당 신체 부위 key
key 'score' 'x' 'y'
최종 산출 : float score, x, y에 해당하는 값
"""
"""
신체 부위 키 값
0 코
1 목
2 오른쪽 어깨
3 오른쪽 팔꿈치
4 오른쪽 손목
5 왼쪽 어깨
6 왼쪽 팔꿈치
7 왼쪽 손목
8 오른쪽 엉덩이
9 오른쪽 무릎
10 오른쪽 발목
11 왼쪽 엉덩이
12 왼쪽 무릎
13 왼쪽 발목
14 오른쪽 눈
15 왼쪽 눈
16 오른쪽 귀
17 왼쪽 귀
"""
"""
#ISSUE
- 만약 부위가 인식이 안된 경우는 어떻게 처리할 것인가?
- 변화량이 급격히 변할 경우는? 즉, 인식이 잘못되었을 경우는 어떻게 보간할 것인가?
- 음악 구성을 어떤 식으로 할 것인가에 대한 명확한 기준을 세워야할 듯함.
변화량을 이용한다는 것이 음악을 구성한다는 것에 있어 어떠한 메리트를 지니고 있는가...
"""
def abs_diff_dict(d1,d2):
    d1 = Counter(d1)
    d2 = Counter(d2)
    
    d2.subtract(d1)
    d2 = dict(d2)
    
    return np.abs(d2['x']) + np.abs(d2['y'])

# 좌표 변화량 산출
def change_cal(vname):
    print("METHOD : change_cal")
    jsondir = os.path.abspath("./static/uploads/json")
    fname = sorted(os.listdir(jsondir))
    fdir = list()
    for i in range(len(fname)):
        fdir.append(os.path.join(jsondir, fname[i]))
    data = list()
    for i in fdir:
        with open(i, 'r') as f:
            data.append(json.load(f))

    diff = list() 

    body_list = ['0','1','3','4','6','7','9','10','12','13']

    for i in range(len(data) - 1):
        body_diff = []
        for body in body_list:
            try:
                d1 = data[i]['predictions'][0][body]
                d2 = data[i+1]['predictions'][0][body]
                body_diff.append(abs_diff_dict(d1,d2))
                
            except KeyError:  # 한 쪽에 인식이 안 된 경우.
                body_diff.append(0)

        diff.append(body_diff)

    for file in os.scandir(jsondir):
        os.remove(file.path)

    print(np.array(diff).shape)

    return make_music(diff, vname)


def make_music(diff, vname):
    print("METHOD : make_music")
    
    final_diff=list()
    sound = list()
    tmp_list=[0,1,2,3,4,5,6,7,8]

    all_avg=0
    tmp_avg=0
    avg=list()

    rhythm = [[1000],[500,500],[400,200,400],[300,300,400]]
    
    for i in range(len(diff[0])):
        for j in range(len(diff)):
            tmp_avg+=diff[j][i]
        avg.append(tmp_avg)

    print("avg : ",avg)

    for i in range(len(avg)):
        all_avg+=avg[i]

    all_avg/=len(avg)

    print("all_avg = ", all_avg)
        
    for k in range(len(diff[0])):
        for i in range(len(tmp_list)-1):
            for j in range(len(tmp_list)-i-1):
                if diff[tmp_list[j]][k]<diff[tmp_list[j+1]][k]:
                    tmp_list[j],tmp_list[j+1]=tmp_list[j+1], tmp_list[j]
        final_diff.append(tmp_list)
        tmp_list=[0,1,2,3,4,5,6,7,8]

    sound = list()

    sound.append(AudioSegment.from_mp3("./static/uploads/music_source/crash.mp3")-6)
    sound.append(AudioSegment.from_mp3("./static/uploads/music_source/hat.mp3")-6)
    sound.append(AudioSegment.from_mp3("./static/uploads/music_source/tom H.mp3"))
    sound.append(AudioSegment.from_mp3("./static/uploads/music_source/kick.mp3"))
    sound.append(AudioSegment.from_mp3("./static/uploads/music_source/snare.mp3"))
    sound.append(AudioSegment.from_mp3("./static/uploads/music_source/bongo H.mp3"))
    sound.append(AudioSegment.from_mp3("./static/uploads/music_source/clap.mp3"))
    sound.append(AudioSegment.from_mp3("./static/uploads/music_source/cow bell.mp3"))
    sound.append(AudioSegment.from_mp3("./static/uploads/music_source/maracas.mp3"))
    sound.append(AudioSegment.from_mp3("./static/uploads/music_source/ride.mp3"))
    base_music = AudioSegment.from_mp3("./static/uploads/music_source/rim.mp3")

    for i in range(len(sound)):
        sound[i] = sound[i][:500]


    base_music=base_music[:500] #base

    base=base_music
    music = sound[1].overlay(sound[2])+sound[3].overlay(sound[4])

    for i in range(len(final_diff)):
        base+=base_music

    for i in range(len(final_diff)):
        music += sound[final_diff[i][0]].overlay(sound[final_diff[i][1]])
        music += sound[final_diff[i][2]].overlay(sound[final_diff[i][3]])

    mel_dir = os.path.abspath("./static/uploads/music_source/blues_scale")
    melody_l = os.listdir(mel_dir)
    melody_lst=list()

    for i in range(len(melody_l)):
        melody_lst.append(os.path.join(mel_dir, melody_l[i]))

    melody=list()

    for i in range(len(melody_lst)):
        melody.append(AudioSegment.from_mp3(melody_lst[i])-4)


    #for i in range(len(melody)): #멜로디는 0.5초
    #    melody[i]=melody[i][:500]
    
    mel = melody[6]
    cur = 6

    ch_rhythm=0

    for i in range(len(avg)):
        ch_rhythm=random.randint(0, len(rhythm)-1)
        for i in range(len(rhythm[ch_rhythm])):
            if(avg[i]<all_avg):
                #cur = random.randint(0, cur)
                #if(cur==0):
                #    cur = random.randint(0, cur+6)
                if(cur==0):
                    avg[i]=all_avg+1
                    cur+=1
                    mel+= melody[cur][:rhythm[ch_rhythm][i]]  
                else:
                    cur-=1
                    mel += melody[cur][:rhythm[ch_rhythm][i]]
                #cur = random.randint(0, cur)
                #if(cur==0):
                #    cur = random.randint(0, cur+6)
                #mel += melody[cur][:rhythm[ch_rhythm][i]]
            else:
                #cur = random.randint(cur, len(melody)-1)
                #if(cur==len(melody)-1):
                #    cur = random.randint(cur-6, len(melody)-1)
                if(cur==len(melody)-1):
                    avg[i]=all_avg-1
                    cur-=1
                    mel +=melody[cur][:rhythm[ch_rhythm][i]]
                else:
                    cur+=1
                    mel +=melody[cur][:rhythm[ch_rhythm][i]]
                #cur = random.randint(cur, len(melody)-1)
                #if(cur==len(melody)-1):
                #    cur = random.randint(cur-6, len(melody)-1)
                #mel +=melody[cur][:rhythm[ch_rhythm][i]]

    

    music= music.overlay(base)
    music = music.overlay(mel)

    music.export("./static/uploads/music.mp3", format="mp3")
    
    return make_mv(vname, diff)

# 원본 동영상과 제작한 사운드 결합
def make_mv(vname, diff):
    print("METHOD : make_mv")
    dir = os.path.abspath("./static/uploads")
    fdir = os.path.join(dir, vname)
    rmfdir = os.path.join(dir, "rm.mp4")
    finaldir = os.path.join(dir, "final.mp4")
    mdir = os.path.join(dir, "music.mp3")
    subprocess.call(  # 비디오 내 오디오 삭제
        'ffmpeg -y -i %s -c copy -an %s' % (fdir, rmfdir),
        shell=True)
    subprocess.call(  # 비디오와 새로운 오디오 합성
        'ffmpeg -y -i %s -i %s -c:v copy -c:a aac -strict experimental %s' % (mdir, rmfdir, finaldir),
        shell=True
    )
    return render_template('app.html', up_file="final.mp4", soundlog=active_body_stat(diff, 0.1))

# change_cal 통해 만들어진 변화량 통해 사운드 로그 생
def active_body_stat(diff, threshold):
    active_body_lst = []
    cnt = 0

    body_dict = {
        0: '머리',
        4: '오른쪽손',
        7: '왼쪽손',
        10: '오른쪽발',
        13: '왼쪽발'
    }

    for i, body in zip(range(5), body_dict.values()):
        body_cnt_by_thres = len(np.where(np.array(diff[i]) > threshold)[0])
        active_body_lst.append((body, body_cnt_by_thres))
    print(active_body_lst)

    return active_body_lst
