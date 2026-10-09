# src/main.py
import json
import os
from core import Robot, WarehouseSimulator

def main():
    os.makedirs("output", exist_ok=True)

    # ★マップを 19(幅) x 15(高さ) に拡大
    width, height = 19, 15
    
    # ★自動倉庫らしい「棚(ラック)」を生成
    obstacles = []
    # x=2,3 / x=7,8 / x=12,13 に縦長の棚を配置（通路がx=4,5,6 / 9,10,11 / 14,15,16 にできる）
    for x in [2, 3, 7, 8, 12, 13]:
        for y in range(2, 12): # y=2から11まで縦に並べる
            obstacles.append((x, y))
            
    # ★エンドポイントを3か所に増設（通路の真下になるように配置）
    endpoints = [(4, 14), (10, 14), (15, 14)]
    
    sim = WarehouseSimulator(width, height, obstacles, endpoints)
    
    # ★ロボットを12台に増員し、マップ上部に横並びで配置
    for i in range(12):
        sim.add_robot(Robot(robot_id=i, start_pos=(i + 2, 0)))

    # 初期タスク
    sim.add_task((8, 1))
    sim.add_task((2, 8))
    sim.add_task((14, 5))

    print("大規模シミュレーションを開始（全100タスククリアまで）...")
    sim.run(max_steps=5000) 

    with open("output/output.json", "w") as f:
        json.dump(sim.history, f, indent=2)
    
    print(f"シミュレーション完了: 合計 {sim.completed_tasks_count} 個のタスクを処理しました。")

if __name__ == "__main__":
    main()