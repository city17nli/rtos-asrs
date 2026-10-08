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
    
    grid = np.zeros((height, width))
    for (ox, oy) in obstacles:
        grid[oy][ox] = 1

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(grid, cmap='binary')
    ax.set_xticks(np.arange(-0.5, width, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, height, 1), minor=True)
    ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5)

    # 3. ロボットとタスクの初期プロット
    colors = ['red', 'blue', 'green', 'orange']
    scatters = {}
    
    # ロボットの点を準備
    for key in history[0].keys():
        if key == "tasks": continue
        agent_id = int(key)
        c = colors[agent_id % len(colors)]
        scatters[agent_id] = ax.scatter([], [], c=c, s=150, label=f"Robot {agent_id}", zorder=5)

    # タスク用の点を準備（大きな黄色の星マーク）
    task_scatter = ax.scatter([], [], c='gold', marker='*', s=300, edgecolors='orange', label="Tasks", zorder=4)

    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

    # 4. アニメーション更新処理
    def update(frame):
        step_data = history[frame]
        
        # タスクを描画（タスクが無くなったら空にする）
        tasks = step_data.get("tasks", [])
        if tasks:
            task_scatter.set_offsets(tasks)
        else:
            task_scatter.set_offsets(np.empty((0, 2)))

        # ロボットを描画
        for agent_id_str, pos in step_data.items():
            if agent_id_str == "tasks":
                continue # tasksはロボットではないのでスキップ
            scatters[int(agent_id_str)].set_offsets([pos[0], pos[1]])
            
        return list(scatters.values()) + [task_scatter]

    # 5. GIFの保存
    ani = animation.FuncAnimation(fig, update, frames=len(history), interval=300, blit=True)
    os.makedirs("output", exist_ok=True)
    ani.save("output/animation.gif", writer='pillow')
    print("アニメーション生成完了: output/animation.gif を保存しました。")

if __name__ == "__main__":
    main()