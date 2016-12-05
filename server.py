import os
from cloud_storage_app_database import CredentialsWrapper
from flask import Flask, Response, flash, request, redirect, url_for, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
global_stuff = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    if global_stuff.has_key('current_user'):
        if request.method == 'POST':
            print(request.form['api'])
            if 'file' not in request.files:
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
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
        <br>
        <form action=/logout method=get>
          <input type=submit value=logout>
        </form>
        '''
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if not global_stuff.has_key('current_user'):
        if request.method == 'POST':
            global_stuff['current_user'] = CredentialsWrapper(request.form['username'],
                                                            request.form['password'])
            return redirect(url_for('index'))
        return '''
        <!doctype html>
        <title>Login</title>
        <h1>Login</h1>
        <form action="" method=post >
        <p>
            <input type=text name=username>
            <input type=password name=password>
            <input type=submit value=Upload>
        </p>
        </form>
        '''
    else:
        return redirect(url_for('index'))

@app.route('/logout', methods=['GET'])
def logout():
    if global_stuff.has_key('current_user'):
        global_stuff.pop('current_user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.config['SECRET_KEY'] = "ITSASECRET"
    app.run(port=5000, debug=True)
