from flask import Flask, g, Response, make_response, render_template, Markup, request
from flask import redirect, flash, url_for
from werkzeug.utils import secure_filename
import os, cv2, sys, requests, json
from pydub import AudioSegment
import random
import subprocess

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['avi','mp4', 'wmv'])

def allowed_file(fname): #업로드 파일 형식 지정
    return '.' in fname and \
        fname.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def up():
    return render_template('upload.html')


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
       f = request.files['file']
       filename = f.filename
       allow = allowed_file(filename)
       if 'file' not in request.files: #선택한 파일이 위치가 이동되거나 변동 사항이 있을 때
           flash('No file part')
           return redirect(url_for('up'))
       if f.filename=='': #선택된 파일이 없을 때
           flash('No selected file')
           return redirect(url_for('up'))
       if allow==True:
           f.save("./static/uploads/raw_video/"+secure_filename(f.filename))
           return movie_divide(secure_filename(f.filename))
           #return render_template('app.html', up_file=f.filename)
       if allow==False: #파일 형식이 허용되지 않는 파일일 때
           flash('type error')
           return redirect(url_for('up'))


def movie_divide(vname): #영상 -> 사진 분할. 매개변수로는 영상 제목 넘겨줌.

    video_dir = os.path.abspath("./static/uploads/raw_video")

    # # 비디오 파일 가져오기
    # for f in os.listdir(video_dir):
    #     if f.split('.')[-1] in ALLOWED_EXTENSIONS:
    #         fdir = f

    fdir = os.path.join(video_dir,vname)

    count = 0
    vidcap = cv2.VideoCapture(fdir)

    while True:
        vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*1000)) #1초에 한장 캡쳐
        success,image = vidcap.read()
        if not success:
            break
        if os.path.isdir("./static/uploads/images"):
            cv2.imwrite("./static/uploads/images/frame%d.jpg" % count, image)
        else:
            os.mkdir("./static/uploads/images")
            cv2.imwrite("./static/uploads/images/frame%d.jpg" % count, image)

        count += 1
    vidcap.release()

    return change_cal(vname)

#API 요청해 json 파일 받기

"""
def get_json(vname):
    count=1
    dir = os.path.abspath("./static/uploads/images")
    fname = os.listdir(dir)
    fdir=list()

    client_id = "68lu4vh157" #API 클라 아이디랑 secret key
    client_secret = "wxrDd1kSPAmq5P14HLV7XNmddjCassOqIivC6QsL"
    url = "https://naveropenapi.apigw.ntruss.com/vision-pose/v1/estimate" # 사람 인식


    for i in fname:
        fdir.append(os.path.join(dir, i))
    for i in fdir:
        files = {'image': open(i, 'rb')}
        headers = {'X-NCP-APIGW-API-KEY-ID': client_id, 'X-NCP-APIGW-API-KEY': client_secret }
        response = requests.post(url,  files=files, headers=headers)
        rescode = response.status_code
        if(rescode==200):
            strTodict = json.loads(response.text)
            with open("./static/uploads/json/test%d.json" % count,'w', encoding='utf-8') as make_file:
                json.dump(strTodict , make_file, indent="\t")
            count+=1
    else:
        print("Error Code:" + rescode)

    return change_cal(vname)
"""
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
def change_cal(vname):
    jsondir = os.path.abspath("./static/uploads/json")
    fname = os.listdir(jsondir)
    fdir=list()
    for i in range(len(fname)):
        fdir.append(os.path.join(jsondir,fname[i]))
    data=list()
    for i in fdir:
        with open(i, 'r') as f:
            data.append(json.load(f))

    rhand_x_diff=list()
    rhand_y_diff=list()
    
    for i in range(len(data)-1):
        try:
            rhand_x_diff.append(data[i+1]['predictions'][0]['4']['x']-data[i]['predictions'][0]['4']['x'])
            rhand_y_diff.append(data[i+1]['predictions'][0]['4']['y']-data[i]['predictions'][0]['4']['y'])
        except KeyError: #한 쪽에 인식이 안 된 경우.
            rhand_x_diff.append(0)
            rhand_y_diff.append(0)
    
    return make_music(rhand_x_diff, rhand_y_diff, vname)

def make_music(xdif, ydif, vname):
    musicdir = os.path.abspath("./static/uploads/music")
    music_name=os.listdir(musicdir)
    mdir = list()
    for i in range(len(music_name)):
        mdir.append(os.path.join(musicdir, music_name[i]))

    sound=list()
    for i in mdir:
        sound.append(AudioSegment.from_file(i))

    for i in sound:
        i = sound[:1000] #mp3파일 1초로 만들기

    music = sound[0]
    num = 0

    for i in range(len(xdif)-1):
        diff = (abs(xdif[i])+abs(ydif[i]))-(abs(xdif[i+1])+abs(ydif[i+1]))
        if diff>0:
            if num==len(sound)-1:
                music += sound[num]
                num = random.randint(0, len(sound)-1)
            else :
                num = random.randint(num, len(sound)-1)
                music += sound[num]
        else:
            if num==0:
                music += sound[num]
                num = random.randint(0, len(sound)-1)
            else :
                num = random.randint(0, num)
                music += sound[num]
    
    music.export("./static/uploads/music.mp3", format="mp3")

    return make_mv(vname)

def make_mv(vname):
    dir = os.path.abspath("./static/uploads")
    fdir = os.path.join(dir, vname)
    rmfdir = os.path.join (dir, "rm.mp4")
    finaldir = os.path.join (dir, "final.mp4")
    mdir = os.path.join(dir, "music.mp3")
    subprocess.call( #비디오 내 오디오 삭제
        'ffmpeg -i %s -c copy -an %s' % (fdir, rmfdir),
        shell=True)
    subprocess.call( #비디오와 새로운 오디오 합성
        'ffmpeg -i %s -i %s -c:v copy -c:a aac -strict experimental %s' % (mdir, rmfdir, finaldir),
        shell=True
    )
    return render_template('app.html', up_file="final.mp4")
    

if __name__ == '__main__':
    app.run()
