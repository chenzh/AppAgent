# Word转PDF在线工具

一个简单、快速、安全的Word文档转PDF在线工具，支持拖拽上传和即时下载。

## 功能特点

- 🚀 **快速转换**: 高效的转换算法，几秒钟内完成转换
- 🔒 **安全可靠**: 文件处理完成后自动删除，保护用户隐私
- 📱 **响应式设计**: 支持各种设备，随时随地使用
- 🎨 **现代界面**: 美观的用户界面，优秀的用户体验
- 📁 **拖拽上传**: 支持拖拽文件到上传区域
- 💾 **即时下载**: 转换完成后立即下载PDF文件

## 支持的文件格式

- `.docx` - Microsoft Word 2007及以后版本
- `.doc` - Microsoft Word 97-2003版本

## 文件大小限制

- 最大文件大小: 16MB

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python app.py
```

### 3. 访问应用

打开浏览器访问: http://localhost:5000

## 技术栈

- **后端**: Python Flask
- **前端**: HTML5, CSS3, JavaScript
- **文件转换**: docx2pdf
- **样式**: 自定义CSS + Font Awesome图标

## 项目结构

```
├── app.py                 # Flask应用主文件
├── requirements.txt       # Python依赖包
├── README.md             # 项目说明文档
├── templates/            # HTML模板
│   └── index.html        # 主页面模板
├── static/               # 静态文件
│   ├── css/
│   │   └── style.css     # 样式文件
│   └── js/
│       └── script.js     # JavaScript文件
├── uploads/              # 上传文件临时目录
└── outputs/              # 输出文件临时目录
```

## 使用说明

1. **上传文件**: 
   - 点击"选择文件"按钮选择Word文档
   - 或者直接拖拽文件到上传区域

2. **开始转换**: 
   - 确认文件信息后，点击"开始转换"按钮
   - 等待转换完成

3. **下载PDF**: 
   - 转换完成后，PDF文件会自动下载到您的设备

## 注意事项

- 请确保上传的文件是有效的Word文档
- 文件大小不能超过16MB
- 转换过程中请勿关闭浏览器
- 转换完成后，服务器上的临时文件会自动删除

## 部署说明

### 使用Docker部署

1. 创建Dockerfile:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

2. 构建和运行:

```bash
docker build -t word-to-pdf .
docker run -p 5000:5000 word-to-pdf
```

### 使用Gunicorn部署

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。