from flask import Flask, g, Response, make_response, render_template, Markup, request
from werkzeug.utils import secure_filename

app = Flask(__name__)


@app.route('/')
def up():
    return render_template('upload.html')


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save("./static/uploads/"+secure_filename(f.filename))
        return render_template('app.html', up_file=f.filename)


if __name__ == '__main__':
    app.run()
