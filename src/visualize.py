# src/visualize.py
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

def main():
    if not os.path.exists("output/output.json"):
        print("エラー: output/output.json が見つかりません。")
        return

    with open("output/output.json", "r") as f:
        history = json.load(f)

    # ★main.pyと同じレイアウト設定
    width, height = 19, 15
    obstacles = []
    for x in [2, 3, 7, 8, 12, 13]:
        for y in range(2, 12):
            obstacles.append((x, y))
    endpoints = [(4, 14), (10, 14), (15, 14)]
    
    grid = np.zeros((height, width))
    for (ox, oy) in obstacles:
        grid[oy][ox] = 1

    fig, ax = plt.subplots(figsize=(10, 8)) # ★少し画面を大きく
    ax.imshow(grid, cmap='binary')
    ax.set_xticks(np.arange(-0.5, width, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, height, 1), minor=True)
    ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5)

    # ★エンドポイント(3か所)を描画
    for ep in endpoints:
        ax.scatter(ep[0], ep[1], c='lime', marker='s', s=400, edgecolors='black', zorder=3)

    # ★ロボット用の色を12色用意
    colors = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', 
              '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', 
              '#008080', '#e6beff']
    scatters = {}
    
    # 1. 各ロボット本体を描画
    for key in history[0].keys():
        if key in ["tasks", "carrying"]: continue
        agent_id = int(key)
        c = colors[agent_id % len(colors)]
        scatters[agent_id] = ax.scatter([], [], c=c, s=150, label=f"Robot {agent_id}", zorder=5)

    # 2. 落ちているタスク
    task_scatter = ax.scatter([], [], c='gold', marker='*', s=300, edgecolors='orange', label="Tasks", zorder=4)
    
    # 3. 持っている荷物
    cargo_scatter = ax.scatter([], [], c='yellow', marker='*', s=100, edgecolors='black', zorder=6)

    # 凡例はロボットが多いので枠外へ
    ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1.0), fontsize='small')

    def update(frame):
        step_data = history[frame]
        
        tasks = step_data.get("tasks", [])
        if tasks:
            task_scatter.set_offsets(tasks)
        else:
            task_scatter.set_offsets(np.empty((0, 2)))

        for agent_id_str, pos in step_data.items():
            if agent_id_str in ["tasks", "carrying"]:
                continue
            scatters[int(agent_id_str)].set_offsets([pos[0], pos[1]])
            
        carrying_ids = step_data.get("carrying", [])
        cargo_positions = []
        for cid in carrying_ids:
            if str(cid) in step_data:
                cargo_positions.append(step_data[str(cid)])
        
        if cargo_positions:
            cargo_scatter.set_offsets(cargo_positions)
        else:
            cargo_scatter.set_offsets(np.empty((0, 2)))
            
        return list(scatters.values()) + [task_scatter, cargo_scatter]

    ani = animation.FuncAnimation(fig, update, frames=len(history), interval=300, blit=True)
    os.makedirs("output", exist_ok=True)
    ani.save("output/animation.gif", writer='pillow')
    print("アニメーション生成完了: output/animation.gif を保存しました。")

if __name__ == "__main__":
    main()