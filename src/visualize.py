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

    max_frames = 800
    if len(history) > max_frames:
        print(f"\n※ステップ数が {len(history)} と膨大なため、最初の {max_frames} ステップのみを切り取ります...")
        history = history[:max_frames]

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

    # 障害物やエンドポイントの散布図（固定部分）
    for ep in endpoints:
        ax.scatter(ep[0], ep[1], c='lime', marker='s', s=400, edgecolors='black', zorder=3)

    colors = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', 
              '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', 
              '#008080', '#e6beff']
    scatters = {}
    
    # 最初のフレームからロボットを取得してプロットオブジェクトを作成
    for key in history[0].keys():
        if key in ["tasks", "carrying"]: continue
        agent_id = int(key)
        c = colors[agent_id % len(colors)]
        scatters[agent_id] = ax.scatter([], [], c=c, s=150, label=f"Robot {agent_id}", zorder=5)

    task_scatter = ax.scatter([], [], c='gold', marker='*', s=300, edgecolors='orange', label="Tasks", zorder=4)
    cargo_scatter = ax.scatter([], [], c='yellow', marker='*', s=100, edgecolors='black', zorder=6)

    ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1.0), fontsize='small')

    # ★ 解決策：補間数を「1」（補間なし）に戻す
    SUB_FRAMES = 1  
    total_frames = len(history)

    def update(frame):
        step_data = history[frame]
        
        # タスク位置の更新
        tasks = step_data.get("tasks", [])
        if tasks:
            task_scatter.set_offsets(tasks)
        else:
            task_scatter.set_offsets(np.empty((0, 2)))

        # ロボット位置の更新（1対1ステップのままで更新）
        for agent_id_str in step_data.keys():
            if agent_id_str in ["tasks", "carrying"]:
                continue
            pos = step_data[agent_id_str]
            scatters[int(agent_id_str)].set_offsets([pos[0], pos[1]])
            
        # 荷物位置の更新
        carrying_ids = step_data.get("carrying", [])
        cargo_positions = []
        for cid in carrying_ids:
            cid_str = str(cid)
            if cid_str in step_data:
                cargo_positions.append(step_data[cid_str])
        
        if cargo_positions:
            cargo_scatter.set_offsets(cargo_positions)
        else:
            cargo_scatter.set_offsets(np.empty((0, 2)))
            
        # blit=True を機能させるため、今回変更があった Artist だけを返す（＝描画負荷を最小化してガタつきをなくす）
        return list(scatters.values()) + [task_scatter, cargo_scatter]

    print("アニメーションをレンダリング中です（数十秒で終わります）...")
    os.makedirs("output", exist_ok=True)
    
    # ★「描画スピードより滑らかさ（ガタつきのなさ）を重視」：
    # 描画更新処理を邪魔しないよう、1コマあたりの間隔（ミリ秒）を微調整
    # 1ステップ＝1コマの場合、早すぎるとカクついて見え、遅すぎるとモッサリするため「80ms」前後が最良の滑らかさに繋がります。
    ani = animation.FuncAnimation(fig, update, frames=total_frames, interval=80, blit=True)
    
    print("GIFとして保存しています...")
    # 保存時の FPS も 1000/interval に合わせてなめらかにループするように最適化
    ani.save("output/simulation_smooth_1x.gif", writer='pillow', fps=12)
    print("完了しました！ output/simulation_smooth_1x.gif を確認してください。")

if __name__ == "__main__":
    main()