FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ↓ この1行を追加！（PCの全ファイルをコンテナの /app に強制コピーする）
COPY . .

CMD python src/main.py && python src/visualize.py