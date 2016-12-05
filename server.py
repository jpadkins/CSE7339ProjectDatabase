import os
from flask import Flask, Response, flash, request, redirect, url_for
from flask.ext.login import LoginManager, UserMixin, login_required
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './uploads'

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class User(UserMixin):
    user_database = {"JohnDoe": ("JohnDoe", "John"),
                     "JaneDoe": ("JaneDoe", "Jane")}

    def __init__(self, username, password):
        self.id = username
        self.password = password

    @classmethod
    def get(cls, id):
        return cls.user_database.get(id)

@login_manager.request_loader
def load_user(request):
    token = request.headers.get('Authorization')
    if token is None:
        token = request.args.get('token')

    if token is not None:
        username, password = token.split(':')
        user_entry = User.get(username)
        if (user_entry is not None):
            user = User(user_entry[0], user_entry[1])
            if (user.password == password):
                return user
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print(request.form['api'])
        if 'file' not in request.files:
            flash('No File')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No File')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('index', filename=filename))

    return '''
    <!doctype html>
    <title>Upload New File</title>
    <h1>Upload New File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p>
        <select name=api>
          <option value="0">Google Drive</option>
          <option value="1">DropBox</option>
          <option value="2">Box</option>
          <option value="3">Local</option>
        </select>
        <input type=file name=file>
        <input type=submit value=Upload>
      </p>
    </form>
    '''

@app.route("/protected/", methods=['GET'])
@login_required
def protected():
    return Response(response="Protected", status=200)

if __name__ == '__main__':
    app.config['SECRET_KEY'] = "ITSASECRET"
    app.run(port=5000, debug=True)
