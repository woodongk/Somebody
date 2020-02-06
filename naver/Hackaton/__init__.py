from flask import Flask, render_template, request, flash, redirect
from flask import url_for
from werkzeug import secure_filename
import cv2
import os

app = Flask(__name__)
app.debug = True

ALLOWED_EXTENSIONS = set(['avi','mp4', 'wmv'])

def allowed_file(fname):
    return '.' in fname and \
        fname.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def defalut():
    return render_template('index.html')

@app.route('/', methods = ['GET', 'POST'])
def load_file():
    if request.method == 'POST':
       f = request.files['file']
       filename = f.filename
       allow = allowed_file(filename)
       if 'file' not in request.files:
           flash('No file part')
           return redirect(url_for('load_file'))
       if f.filename=='':
           flash('No selected file')
           return redirect(url_for('load_file'))
       if allow==True:
           fname = secure_filename(f.filename)
           f.save("./Hackaton/mv/"+fname)
           return redirect(url_for('movie_divide'))
       if allow==False:
            return redirect(url_for('load_file'))

        
@app.route('/uploader')
def movie_divide():
    dir = os.path.abspath("./Hackaton/mv")
    fname = os.listdir(dir)
    fdir = os.path.join(dir, fname[0])


    count = 0
    vidcap = cv2.VideoCapture(fdir)
    while True:
        success,image = vidcap.read()
        if not success:
            break
        print ('Read a new frame: ', success)
        fname = "{}.jpg".format("{0:05d}".format(count))
        cv2.imwrite("./Hackaton/mvimages/frame%d.jpg" % count, image) # save frame as JPEG file
        count += 1
    vidcap.release()

    return render_template('end.html')
    
app.secret_key = os.urandom(50)
