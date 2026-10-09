# src/visualize.py
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

def load_map(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    height = len(lines)
    width = len(lines[0])
    obstacles = []
    endpoints = []
    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            if char == '#':
                obstacles.append((x, y))
            elif char == 'E':
                endpoints.append((x, y))
    return width, height, obstacles, endpoints

def main():
    if not os.path.exists("output/output.json"):
        print("エラー: output/output.json が見つかりません。")
        return

    with open("output/output.json", "r") as f:
        history = json.load(f)

    # ★間引き（history[::4]）を削除しました。これで全ステップが1歩ずつ描画されます！

    width, height, obstacles, endpoints = load_map("maps/layout_A.map")
    
    grid = np.zeros((height, width))
    for (ox, oy) in obstacles:
        grid[oy][ox] = 1

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(grid, cmap='binary')
    
    ax.set_xticks(np.arange(width))
    ax.set_yticks(np.arange(height))
    ax.set_xticks(np.arange(-0.5, width, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, height, 1), minor=True)
    ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5)
    ax.tick_params(axis='both', which='major', labelsize=8)

    for ep in endpoints:
        ax.scatter(ep[0], ep[1], c='lime', marker='s', s=400, edgecolors='black', zorder=3)

    colors = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', 
              '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', 
              '#008080', '#e6beff']
    scatters = {}
    
    for key in history[0].keys():
        if key in ["tasks", "carrying"]: continue
        agent_id = int(key)
        c = colors[agent_id % len(colors)]
        scatters[agent_id] = ax.scatter([], [], c=c, s=150, label=f"Robot {agent_id}", zorder=5)

    task_scatter = ax.scatter([], [], c='gold', marker='*', s=300, edgecolors='orange', label="Tasks", zorder=4)
    cargo_scatter = ax.scatter([], [], c='yellow', marker='*', s=100, edgecolors='black', zorder=6)

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

    print(f"\n全 {len(history)} ステップのアニメーション(GIF)をフルレンダリング中です。")
    print("PCの性能によっては 1〜3分 ほどかかります。少々お待ちください...")
    
    # ★変更：intervalを30（超高速・約30fps）に変更し、滑らかかつスピーディーに再生
    ani = animation.FuncAnimation(fig, update, frames=len(history), interval=30, blit=True)
    os.makedirs("output", exist_ok=True)
    ani.save("output/animation.gif", writer='pillow')
    print("アニメーション生成完了: output/animation.gif を保存しました。")

if __name__ == "__main__":
    main()