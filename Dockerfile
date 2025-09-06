FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p uploads outputs

# 暴露端口
EXPOSE 5000

# 运行应用
CMD ["python", "app.py"]