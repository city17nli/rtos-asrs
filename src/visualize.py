import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# マップの読み込み
with open('assets/warehouse.map', 'r') as f:
    lines = f.readlines()[4:] # ヘッダをスキップ
grid = np.array([[1 if c in ['@', 'T'] else 0 for c in line.strip()] for line in lines])

# シミュレーション履歴の読み込み
with open('output.json', 'r') as f:
    history = json.load(f)

# 描画のセットアップ
fig, ax = plt.subplots(figsize=(8, 5))
ax.imshow(grid, cmap='binary') # 地図を描画

# ロボットの色分け設定
colors = ['red', 'blue', 'green', 'orange']
scatters = {}
for agent_id_str in history[0].keys():
    agent_id = int(agent_id_str)
    c = colors[agent_id % len(colors)]
    # 初期位置にプロット
    scatters[agent_id] = ax.scatter([], [], c=c, s=100, label=f"Robot {agent_id}")

ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

# アニメーション更新関数
def update(frame):
    step_data = history[frame]
    for agent_id_str, pos in step_data.items():
        # matplotlibのscatterは(x, y)で指定するため、pos[0], pos[1]の順でセット
        scatters[int(agent_id_str)].set_offsets([pos[0], pos[1]])
    return list(scatters.values())

# アニメーション作成と保存
ani = animation.FuncAnimation(fig, update, frames=len(history), interval=200, blit=True)
ani.save('output.gif', writer='pillow')
print("アニメーション生成完了: output.gif を保存しました。")
