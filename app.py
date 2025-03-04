from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import os
import random

app = Flask(__name__)

UPLOAD_FOLDER = 'files'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'csv', 'xlsx', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024
app.secret_key = os.urandom(24)

ACCESS_PASSWORD = str(random.randint(10000000, 99999999))
print(' * Generated Access Password: ' + ACCESS_PASSWORD[:4] + '-' + ACCESS_PASSWORD[4:])

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_list():
    return sorted([f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))])

def get_folder_contents(path=""):
    """Return a sorted list of files and directories in the given path, with directories first."""
    full_path = os.path.join(UPLOAD_FOLDER, path)

    if not os.path.exists(full_path):
        return []

    items = []
    for item in os.listdir(full_path):
        item_path = os.path.join(full_path, item)
        is_dir = os.path.isdir(item_path)
        items.append({'name': item, 'is_dir': is_dir})

    items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))

    return items

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def index(path=""):
    if 'authenticated' not in session:
        return redirect(url_for('login'))

    full_path = os.path.join(UPLOAD_FOLDER, path)
    os.makedirs(full_path, exist_ok=True)  # Ensure directory exists

    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file part', files=get_folder_contents(path), current_path=path)

        file = request.files['file']

        if file.filename == '':
            return render_template('index.html', error='No selected file', files=get_folder_contents(path), current_path=path)

        if file and allowed_file(file.filename):
            file.save(os.path.join(full_path, file.filename))
            return render_template('index.html', message='File uploaded successfully!', files=get_folder_contents(path), current_path=path)

        return render_template('index.html', error='Invalid file type', files=get_folder_contents(path), current_path=path)

    return render_template('index.html', files=get_folder_contents(path), current_path=path)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entered_password = request.form.get('password')
        if entered_password == ACCESS_PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid password")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

@app.route('/download/<filename>')
def download_file(filename):
    if 'authenticated' not in session:
        return redirect(url_for('login'))
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=False)
