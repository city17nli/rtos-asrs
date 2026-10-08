# 軽量なPython 3.11環境をベースにする
FROM python:3.11-slim

# コンテナ内の作業ディレクトリを /app に設定
WORKDIR /app

# ライブラリのリストをコンテナにコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# コンテナが起動したときに自動で実行されるコマンド
# (&& を使うことで、main.py が成功したら visualize.py を実行する)
CMD python src/main.py && python src/visualize.py