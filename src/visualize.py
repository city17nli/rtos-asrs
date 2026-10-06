# src/visualize.py
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

def main():
    # jsonファイルの存在確認
    if not os.path.exists("output/output.json"):
        print("エラー: output/output.json が見つかりません。先に main.py を実行してください。")
        return

    # 1. 履歴データの読み込み
    with open("output/output.json", "r") as f:
        history = json.load(f)

    # 2. マップの描画設定 (main.pyと同じ設定を手動で合わせるか、設定ファイルから読む)
    width, height = 10, 10
    obstacles = [(5, 4), (5, 5), (5, 6)]
    
    grid = np.zeros((height, width))
    for (ox, oy) in obstacles:
        grid[oy][ox] = 1  # 障害物は1 (描画の都合上、yとxを反転させて配列に格納)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(grid, cmap='binary')
    ax.set_xticks(np.arange(-0.5, width, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, height, 1), minor=True)
    ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5)

    # 3. ロボットの初期プロット
    colors = ['red', 'blue', 'green', 'orange']
    scatters = {}
    for agent_id_str in history[0].keys():
        agent_id = int(agent_id_str)
        c = colors[agent_id % len(colors)]
        scatters[agent_id] = ax.scatter([], [], c=c, s=150, label=f"Robot {agent_id}", zorder=5)

    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

    # 4. アニメーション更新処理
    def update(frame):
        step_data = history[frame]
        for agent_id_str, pos in step_data.items():
            # matplotlibのscatterは(x, y)の順
            scatters[int(agent_id_str)].set_offsets([pos[0], pos[1]])
        return list(scatters.values())

    # 5. GIFの保存
    ani = animation.FuncAnimation(fig, update, frames=len(history), interval=300, blit=True)
    os.makedirs("output", exist_ok=True)
    ani.save("output/animation.gif", writer='pillow')
    print("アニメーション生成完了: output/animation.gif を保存しました。")

if __name__ == "__main__":
    main()