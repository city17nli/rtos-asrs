FROM python:3.14.8-slim

# GUIおよび画像処理（GIF生成等）に必要なシステムライブラリのインストール
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libx11-6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# output内にあるrequirements.txtをコピーしてインストール
COPY output/requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# プロジェクト全体をコンテナにコピー
COPY . .

# 実行コマンド
CMD ["python", "src/main.py"]