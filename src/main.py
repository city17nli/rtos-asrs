# src/main.py
import json
import os
from core import Robot, WarehouseSimulator

def main():
    os.makedirs("output", exist_ok=True)

    width, height = 10, 10
    obstacles = [(5, 4), (5, 5), (5, 6)]
    endpoint = (4, 9) 
    
    sim = WarehouseSimulator(width, height, obstacles, endpoint)
    
    sim.add_robot(Robot(robot_id=0, start_pos=(0, 0)))
    sim.add_robot(Robot(robot_id=1, start_pos=(1, 0)))
    sim.add_robot(Robot(robot_id=2, start_pos=(2, 0)))
    sim.add_robot(Robot(robot_id=3, start_pos=(3, 0)))
    sim.add_robot(Robot(robot_id=4, start_pos=(4, 0)))

    sim.add_task((8, 1))
    sim.add_task((2, 8))
    sim.add_task((8, 5))

    print("動的タスク生成シミュレーションを開始（全タスククリアまで）...")
    # 完了するまでループ。無限ループ防止の安全装置として5000をセット。
    sim.run(max_steps=5000) 

    with open("output/output.json", "w") as f:
        json.dump(sim.history, f, indent=2)
    
    print(f"シミュレーション完了: 合計 {sim.completed_tasks_count} 個のタスクを処理しました。")

if __name__ == "__main__":
    main()