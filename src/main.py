# src/main.py
import json
import os
import random  # ★ランダム機能を追加
from core import Robot, WarehouseSimulator

def main():
    os.makedirs("output", exist_ok=True)

    # 10x10の倉庫、中央に障害物
    width, height = 10, 10
    obstacles = [(5, 4), (5, 5), (5, 6)]
    sim = WarehouseSimulator(width, height, obstacles)
    
    # ロボットを2台配置
    sim.add_robot(Robot(robot_id=0, start_pos=(1, 1)))
    sim.add_robot(Robot(robot_id=1, start_pos=(8, 8)))

    # ★追加：障害物以外の「安全なマス」のリストを作成
    valid_cells = []
    for y in range(height):
        for x in range(width):
            if (x, y) not in obstacles:
                valid_cells.append((x, y))

    # ★追加：タスクをランダムに10個生成
    num_tasks = 10
    for _ in range(num_tasks):
        # 安全なマスの中からランダムに1つ選んでタスクに追加
        random_task = random.choice(valid_cells)
        sim.add_task(random_task)

    print(f"ランダムタスクを{num_tasks}個生成しました。シミュレーションを開始...")
    sim.run(steps=50) # タスクを増やしたので、ステップ数(時間)も少し長めに回す

    with open("output/output.json", "w") as f:
        json.dump(sim.history, f, indent=2)
    
    print("完了: output/output.json を保存しました。")

if __name__ == "__main__":
    main()