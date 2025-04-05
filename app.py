from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
app.config['ALLOWED_EXTENSIONS'] = {
    'doc', 'docx',
    'xls', 'xlsx',
    'ppt', 'pptx',
    'pdf',
    'txt',
    'jpg', 'jpeg', 'png', 'gif', 'bmp',
    'mp3', 'wav', 'flac', 'aac',
    'mp4', 'avi', 'mkv', 'wmv',
    'zip', 'rar', '7z',
    'exe', 'dll', 'py', 'java',
    'dmg', 'iso',
    'psd', 'indd',
    'raw',
    'wma',
    'mid', 'midi',
    'torrent',
    'accdb',
    'odt',
    'pst',
    'tmp',
    'cfg',
    'log'
}
app.secret_key = 'supersecretkey'

# 确保 static 目录及其子目录存在
required_dirs = ['documents', 'images', 'audios', 'videos', 'archives', 'programs', 'others']
for dir_name in required_dirs:
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], dir_name), exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET'])
def index():
    # 获取所有文件并过滤
    all_files = []
    document_files = [f for f in os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'documents')) if
                      f.endswith(tuple(['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.txt']))]
    image_files = [f for f in os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'images')) if
                   f.endswith(tuple(['.png', '.jpg', '.jpeg', '.gif', '.bmp']))]
    video_files = [f for f in os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'videos')) if
                   f.endswith(tuple(['.mp4', '.avi', '.mkv', '.wmv']))]
    audio_files = [f for f in os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'audios')) if
                   f.endswith(tuple(['.mp3', '.wav', '.flac', '.aac']))]
    archive_files = [f for f in os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'archives')) if
                     f.endswith(tuple(['.zip', '.rar', '.7z']))]
    program_files = [f for f in os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'programs')) if
                     f.endswith(tuple(['.exe', '.dll', '.py', '.java']))]
    other_files = [f for f in os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'others'))]

    all_files.extend([('document', f) for f in document_files])
    all_files.extend([('image', f) for f in image_files])
    all_files.extend([('video', f) for f in video_files])
    all_files.extend([('audio', f) for f in audio_files])
    all_files.extend([('archive', f) for f in archive_files])
    all_files.extend([('program', f) for f in program_files])
    all_files.extend([('other', f) for f in other_files])

    return render_template('index.html', files=all_files)

@app.route('/preview/<path:filename>')
def preview_file(filename):
    file_path = ''
    file_type = ''

    if filename.lower().endswith(('.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.txt')):
        file_path = 'documents/' + filename
        file_type = 'document'
    elif filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
        file_path = 'images/' + filename
        file_type = 'image'
    elif filename.lower().endswith(('.mp4', '.avi', '.mkv', '.wmv')):
        file_path = 'videos/' + filename
        file_type = 'video'
    elif filename.lower().endswith(('.mp3', '.wav', '.flac', '.aac')):
        file_path = 'audios/' + filename
        file_type = 'audio'
    elif filename.lower().endswith(('.zip', '.rar', '.7z')):
        file_path = 'archives/' + filename
        file_type = 'archive'
    elif filename.lower().endswith(('.exe', '.dll', '.py', '.java')):
        file_path = 'programs/' + filename
        file_type = 'program'
    else:
        file_path = 'others/' + filename
        file_type = 'other'

    if file_path:
        file_preview_data = {
            'type': file_type,
            'path': file_path,
            'name': filename
        }
    else:
        file_preview_data = None

    return render_template('preview.html', file_preview_data=file_preview_data)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            flash('没有文件部分')
            return redirect(request.url)
        file = request.files['file']
        # 如果用户没有选择文件，浏览器也会提交一个part-without-filename
        if file.filename == '':
            flash('没有选择文件')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # 根据文件类型将其保存到相应的目录
            save_path = None
            if filename.lower().endswith(('.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.txt')):
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], 'documents', filename)
            elif filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], 'images', filename)
            elif filename.lower().endswith(('.mp4', '.avi', '.mkv', '.wmv')):
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', filename)
            elif filename.lower().endswith(('.mp3', '.wav', '.flac', '.aac')):
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], 'audios', filename)
            elif filename.lower().endswith(('.zip', '.rar', '.7z')):
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], 'archives', filename)
            elif filename.lower().endswith(('.exe', '.dll', '.py', '.java')):
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], 'programs', filename)
            else:
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], 'others', filename)

            if save_path:
                file.save(save_path)
                flash(f'文件 {filename} 上传成功！')
            else:
                flash('无法确定文件类型或保存路径。')
        else:
            flash(
                '允许的文件类型包括：doc, docx, xls, xlsx, ppt, pptx, pdf, txt, jpg, jpeg, png, gif, bmp, mp3, wav, flac, aac, mp4, avi, mkv, wmv, zip, rar, 7z, exe, dll, py, java, dmg, iso, psd, indd, raw, wma, mid, midi, torrent, accdb, odt, pst, tmp, cfg, log')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'发生错误: {str(e)}')
    return redirect(url_for('index'))

@app.route('/delete/<path:filename>', methods=['POST'])
def delete_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            flash(f'文件 {filename} 已删除！')
        else:
            flash(f'文件 {filename} 不存在。')
    except Exception as e:
        flash(f'删除文件时发生错误: {str(e)}')
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("UPLOAD_FOLDER:", app.config['UPLOAD_FOLDER'])  # 打印上传文件夹路径
    app.run(debug=True)



