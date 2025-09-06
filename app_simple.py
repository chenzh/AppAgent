from flask import Flask, request, render_template, send_file, flash, redirect, url_for
import os
import uuid
from werkzeug.utils import secure_filename
import tempfile
import subprocess
import shutil

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# 配置
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'docx', 'doc'}

# 确保文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_with_libreoffice(input_path, output_path):
    """使用LibreOffice命令行工具转换文件"""
    try:
        # 使用LibreOffice转换
        cmd = [
            'libreoffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', os.path.dirname(output_path),
            input_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            # LibreOffice会生成PDF文件，文件名与输入文件相同但扩展名为.pdf
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            generated_pdf = os.path.join(os.path.dirname(output_path), f"{base_name}.pdf")
            
            if os.path.exists(generated_pdf):
                # 移动到目标位置
                shutil.move(generated_pdf, output_path)
                return True
            else:
                return False
        else:
            print(f"LibreOffice error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("转换超时")
        return False
    except Exception as e:
        print(f"转换错误: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_file():
    if 'file' not in request.files:
        flash('没有选择文件')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('没有选择文件')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # 生成唯一文件名
        unique_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        
        # 保存上传的文件
        upload_filename = f"{unique_id}_{filename}"
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], upload_filename)
        file.save(upload_path)
        
        try:
            # 转换文件
            output_filename = f"{unique_id}_{name}.pdf"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
            # 使用LibreOffice转换
            if convert_with_libreoffice(upload_path, output_path):
                # 清理上传的文件
                os.remove(upload_path)
                return send_file(output_path, as_attachment=True, download_name=f"{name}.pdf")
            else:
                raise Exception("文件转换失败")
            
        except Exception as e:
            # 清理文件
            if os.path.exists(upload_path):
                os.remove(upload_path)
            flash(f'转换失败: {str(e)}')
            return redirect(url_for('index'))
    
    else:
        flash('不支持的文件格式。请上传 .docx 或 .doc 文件')
        return redirect(url_for('index'))

@app.route('/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)