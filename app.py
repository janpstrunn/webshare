from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, abort
import os
import random
from werkzeug.utils import secure_filename

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'files')
ALLOWED_EXTENSIONS = {
    'txt', 'md', 'pdf', 'epub', 'docx', 'odt', 'zip', 'doc', 'png', 'jpg', 'jpeg', 'gif',
    'csv', 'xlsx', 'pptx', 'ppt', 'rtf', 'html', 'xml', 'json', 'yaml', 'mp3', 'mp4', 'avi',
    'mov', 'mkv', 'wav', 'flac', 'aac', 'ogg', 'webm', 'css', 'js', 'tar', 'tar.gz',
    'tar.bz2', '7z', 'bz2', 'gz', 'rar', 'tiff', 'bmp', 'svg', 'psd', 'ai', 'indd', 'sh',
    'exe', 'bat', 'apk', 'iso', 'img', 'dmg', 'mpg', 'flv', 'wma', 'webp', 'avif', 'heif'
}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024
app.secret_key = os.urandom(24)

ACCESS_PASSWORD = str(random.randint(10000000, 99999999))
print(f' * Generated Access Password: {ACCESS_PASSWORD[:4]}-{ACCESS_PASSWORD[4:]}')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_folder_contents(path=""):
    safe_path = os.path.normpath(os.path.join(UPLOAD_FOLDER, path))
    if not safe_path.startswith(UPLOAD_FOLDER):
        abort(403)

    if not os.path.exists(safe_path):
        return []

    items = []
    for item in os.listdir(safe_path):
        item_path = os.path.join(safe_path, item)
        is_dir = os.path.isdir(item_path)
        items.append({'name': item, 'is_dir': is_dir})

    items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
    return items

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def index(path=""):
    if 'authenticated' not in session:
        return redirect(url_for('login'))

    safe_path = os.path.normpath(os.path.join(UPLOAD_FOLDER, path))
    if not safe_path.startswith(UPLOAD_FOLDER):
        abort(403)

    os.makedirs(safe_path, exist_ok=True)

    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == "":
            return render_template('index.html', error='No file selected', files=get_folder_contents(path), current_path=path)

        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(safe_path, filename))
            return render_template('index.html', message='File uploaded successfully!', files=get_folder_contents(path), current_path=path)
        else:
            return render_template('index.html', error='Invalid file type', files=get_folder_contents(path), current_path=path)

    return render_template('index.html', files=get_folder_contents(path), current_path=path)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entered_password = request.form.get('password')
        if entered_password == ACCESS_PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('index'))
        return render_template('login.html', error="Invalid password")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

@app.route('/download/<path:filepath>')
def download_file(filepath):
    if 'authenticated' not in session:
        return redirect(url_for('login'))
    safe_path = os.path.normpath(os.path.join(UPLOAD_FOLDER, filepath))
    if not safe_path.startswith(UPLOAD_FOLDER) or not os.path.isfile(safe_path):
        abort(403)
    return send_from_directory(UPLOAD_FOLDER, filepath, as_attachment=True)

@app.route('/media/<path:filename>')
def media_file(filename):
    if 'authenticated' not in session:
        return redirect(url_for('login'))
    safe_path = os.path.normpath(os.path.join(UPLOAD_FOLDER, filename))
    if not safe_path.startswith(UPLOAD_FOLDER) or not os.path.isfile(safe_path):
        abort(403)
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=False)
