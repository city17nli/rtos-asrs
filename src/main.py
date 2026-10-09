# src/main.py
import json
import os
import random
from core import Robot, WarehouseSimulator

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
    os.makedirs("output", exist_ok=True)

    width, height, obstacles, endpoints = load_map("maps/layout_A.map")
    
    sim = WarehouseSimulator(width, height, obstacles, endpoints)
    
    for i in range(8):
        sim.add_robot(Robot(robot_id=i, start_pos=(i + 2, 0)))

    # ★変更：初期タスクを「棚(shelf_cells)」の上に配置する！
    for _ in range(3):
        sim.add_task(random.choice(sim.shelf_cells))

    print("大規模シミュレーションを開始（全100タスククリアまで）...")
    sim.run(max_steps=5000) 

    with open("output/output.json", "w") as f:
        json.dump(sim.history, f, indent=2)
    
    print(f"シミュレーション完了: 合計 {sim.completed_tasks_count} 個のタスクを処理しました。")

if __name__ == "__main__":
    main()