from flask import render_template
from pydub import AudioSegment
import os, cv2, requests, json, random, subprocess,shutil


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
    count = 1
    dir = os.path.abspath("./static/uploads/images")
    fname = os.listdir(dir)
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
            with open("./static/uploads/json/test%d.json" % count, 'w', encoding='utf-8') as make_file:
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


# 좌표 변화량 산출
def change_cal(vname):
    print("METHOD : change_cal")
    jsondir = os.path.abspath("./static/uploads/json")
    fname = os.listdir(jsondir)
    fdir = list()
    for i in range(len(fname)):
        fdir.append(os.path.join(jsondir, fname[i]))
    data = list()
    for i in fdir:
        with open(i, 'r') as f:
            data.append(json.load(f))

    head_diff = list()
    rhand_diff = list()
    lhand_diff = list()
    rfoot_diff = list()
    lfoot_diff = list()
    diff = list()

    for i in range(len(data) - 1):
        try:
            head_diff.append(abs(data[i + 1]['predictions'][0]['0']['x'] - data[i]['predictions'][0]['0']['x']) + abs(data[i + 1]['predictions'][0]['0']['y'] - data[i]['predictions'][0]['0']['y']))
        except KeyError:  # 한 쪽에 인식이 안 된 경우.
            head_diff.append(0)
    for i in range(len(data) - 1):
        try:
            rhand_diff.append(abs(data[i + 1]['predictions'][0]['4']['x'] - data[i]['predictions'][0]['4']['x']) + abs(data[i + 1]['predictions'][0]['4']['y'] - data[i]['predictions'][0]['4']['y']))
        except KeyError:  # 한 쪽에 인식이 안 된 경우.
            rhand_diff.append(0)
    for i in range(len(data) - 1):
        try:
            lhand_diff.append(abs(data[i + 1]['predictions'][0]['7']['x'] - data[i]['predictions'][0]['7']['x']) + abs(data[i + 1]['predictions'][0]['7']['y'] - data[i]['predictions'][0]['7']['y']))
        except KeyError:  # 한 쪽에 인식이 안 된 경우.
            lhand_diff.append(0)
    for i in range(len(data) - 1):
        try:
            rfoot_diff.append(abs(data[i + 1]['predictions'][0]['10']['x'] - data[i]['predictions'][0]['10']['x']) + abs(data[i + 1]['predictions'][0]['10']['y'] - data[i]['predictions'][0]['10']['y']))
        except KeyError:  # 한 쪽에 인식이 안 된 경우.
            rfoot_diff.append(0)
    for i in range(len(data) - 1):
        try:
            lfoot_diff.append(abs(data[i + 1]['predictions'][0]['13']['x'] - data[i]['predictions'][0]['13']['x']) + abs(data[i + 1]['predictions'][0]['13']['y'] - data[i]['predictions'][0]['13']['y']))
        except KeyError:  # 한 쪽에 인식이 안 된 경우.
            lfoot_diff.append(0)
    
    diff.append(head_diff)
    diff.append(rhand_diff)
    diff.append(lhand_diff)
    diff.append(rfoot_diff)
    diff.append(lfoot_diff)

  

    return make_music(diff, vname)


# 변화량에 따른 사운드 제작
def make_music(diff, vname):
    print("METHOD : make_music")
    
    final_diff=list()
    sound = list()
    tmp_list=[0,1,2,3,4]

    for k in range(len(diff[0])):
        for i in range(len(tmp_list)-1):
            for j in range(len(tmp_list)-i-1):
                if diff[tmp_list[j]][k]<diff[tmp_list[j+1]][k]:
                    tmp_list[j],tmp_list[j+1]=tmp_list[j+1], tmp_list[j]
        final_diff.append(tmp_list)
        tmp_list=[0,1,2,3,4]

    sound = list()

    sound.append(AudioSegment.from_mp3("./static/uploads/music_source/crash.mp3"))
    sound.append(AudioSegment.from_mp3("./static/uploads/music_source/hat.mp3"))
    sound.append(AudioSegment.from_mp3("./static/uploads/music_source/tom H.mp3"))
    sound.append(AudioSegment.from_mp3("./static/uploads/music_source/kick.mp3"))
    sound.append(AudioSegment.from_mp3("./static/uploads/music_source/snare.mp3"))
    base_music = AudioSegment.from_mp3("./static/uploads/music_source/base.mp3")

    #for i in sound:
    #    i = i[:500]

    sound[0]=sound[0][:500]
    sound[1]=sound[1][:500]
    sound[2]=sound[2][:500]
    sound[3]=sound[3][:500]
    sound[4]=sound[4][:500]
    base_music=base_music[:500]

    base=base_music
    music = sound[1].overlay(sound[2])+sound[3].overlay(sound[4])

    for i in range(len(final_diff)):
        base+=base_music
    

    for i in range(len(final_diff)):
        music += sound[final_diff[i][0]].overlay(sound[final_diff[i][1]])
        music += sound[final_diff[i][2]].overlay(sound[final_diff[i][3]])

    music= music.overlay(base)

    music.export("./static/uploads/music.mp3", format="mp3")
    
    return make_mv(vname)


# 원본 동영상과 제작한 사운드 결합
def make_mv(vname):
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
    return render_template('app.html', up_file="final.mp4")