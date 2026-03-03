# 智能报价系统 - 后端 API (FastAPI + Uvicorn)
FROM python:3.12-slim

WORKDIR /app

# 国内镜像加速（阿里云）：apt 源 + pip 源
RUN sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources \
    && sed -i 's|security.debian.org|mirrors.aliyun.com/debian-security|g' /etc/apt/sources.list.d/debian.sources

# 系统依赖（psycopg2 需 libpq；poppler-utils 用于 pdf2image 将扫描型 PDF 转为图片；libgl1 用于 OpenCV）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt

COPY . .

EXPOSE 5002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5002"]
