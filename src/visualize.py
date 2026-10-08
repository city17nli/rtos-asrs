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

    width, height = 10, 10
    obstacles = [(5, 4), (5, 5), (5, 6)]
    endpoint = (4, 9) 
    
    grid = np.zeros((height, width))
    for (ox, oy) in obstacles:
        grid[oy][ox] = 1

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(grid, cmap='binary')
    ax.set_xticks(np.arange(-0.5, width, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, height, 1), minor=True)
    ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5)

    # エンドポイント（緑の四角）を描画
    ax.scatter(endpoint[0], endpoint[1], c='lime', marker='s', s=400, edgecolors='black', label="Endpoint", zorder=3)

    colors = ['red', 'blue', 'green', 'orange', 'purple'] 
    scatters = {}
    
    # 1. 各ロボット本体を描画
    for key in history[0].keys():
        if key in ["tasks", "carrying"]: continue
        agent_id = int(key)
        c = colors[agent_id % len(colors)]
        scatters[agent_id] = ax.scatter([], [], c=c, s=150, label=f"Robot {agent_id}", zorder=5)

    # 2. 落ちているタスク（大きな星）を描画
    task_scatter = ax.scatter([], [], c='gold', marker='*', s=300, edgecolors='orange', label="Tasks", zorder=4)
    
    # ★追加：3. ロボットが持っている荷物（小さな星）を描画
    # zorderを6にして、ロボット(5)の上に重なるようにします
    cargo_scatter = ax.scatter([], [], c='yellow', marker='*', s=100, edgecolors='black', zorder=6)

    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

    def update(frame):
        step_data = history[frame]
        
        # 落ちているタスクの更新
        tasks = step_data.get("tasks", [])
        if tasks:
            task_scatter.set_offsets(tasks)
        else:
            task_scatter.set_offsets(np.empty((0, 2)))

        # ロボット本体の更新
        for agent_id_str, pos in step_data.items():
            if agent_id_str in ["tasks", "carrying"]:
                continue
            scatters[int(agent_id_str)].set_offsets([pos[0], pos[1]])
            
        # ★追加：荷物マークの更新
        carrying_ids = step_data.get("carrying", [])
        cargo_positions = []
        for cid in carrying_ids:
            # 荷物を持っているロボットの現在の座標を取得して、マークの座標リストに追加
            if str(cid) in step_data:
                cargo_positions.append(step_data[str(cid)])
        
        if cargo_positions:
            cargo_scatter.set_offsets(cargo_positions)
        else:
            cargo_scatter.set_offsets(np.empty((0, 2)))
            
        return list(scatters.values()) + [task_scatter, cargo_scatter]

    # ★変更：再生スピードを遅くする (interval=200 -> 400 に変更)
    ani = animation.FuncAnimation(fig, update, frames=len(history), interval=400, blit=True)
    os.makedirs("output", exist_ok=True)
    ani.save("output/animation.gif", writer='pillow')
    print("アニメーション生成完了: output/animation.gif を保存しました。")

if __name__ == "__main__":
    main()