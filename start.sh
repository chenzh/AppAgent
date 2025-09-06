#!/bin/bash

echo "正在安装依赖..."

# 尝试使用pip3安装依赖
pip3 install --user Flask==2.3.3 Werkzeug==2.3.7 docx2pdf==0.1.8 python-docx==0.8.11

# 如果上面的命令失败，尝试使用--break-system-packages
if [ $? -ne 0 ]; then
    echo "使用--break-system-packages安装依赖..."
    pip3 install --break-system-packages Flask==2.3.3 Werkzeug==2.3.7 docx2pdf==0.1.8 python-docx==0.8.11
fi

echo "启动应用..."
python3 app.py