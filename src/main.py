# src/main.py
import json
import os
from core import Robot, WarehouseSimulator

def main():
    os.makedirs("output", exist_ok=True)

    width, height = 10, 10
    obstacles = [(5, 4), (5, 5), (5, 6)]
    sim = WarehouseSimulator(width, height, obstacles)
    
    # ロボットを2台配置
    sim.add_robot(Robot(robot_id=0, start_pos=(1, 1)))
    sim.add_robot(Robot(robot_id=1, start_pos=(8, 8)))

    # 最初だけ3つほどタスクを配置しておく（あとは自動で湧きます）
    sim.add_task((8, 1))
    sim.add_task((2, 8))
    sim.add_task((8, 5))

    print("動的タスク生成シミュレーションを開始（合計50個クリアまで）...")
    # タスクが次々湧くため、ステップ数は長め（例: 300ステップ）に設定
    sim.run(max_steps=300)

    with open("output/output.json", "w") as f:
        json.dump(sim.history, f, indent=2)
    
    print(f"シミュレーション完了: 合計 {sim.completed_tasks_count} 個のタスクを処理しました。")

if __name__ == "__main__":
    main()