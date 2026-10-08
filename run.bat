chcp 65001 > nul
@echo off
echo シミュレーションを開始します...
docker compose up --build

echo.
echo コンテナから画像を抽出しています...
docker compose cp simulator:/app/output/animation.gif ./output/animation.gif
docker compose cp simulator:/app/output/output.json ./output/output.json

echo.
echo 全ての処理が完了しました！ output フォルダを確認してください。