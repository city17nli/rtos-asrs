# src/main.py
import json
import os
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

    # タスクをバラバラに追加 (順番ではなく、距離の近さでロボットが選ぶようになります)
    sim.add_task((8, 1)) # ロボット1(8,8)よりロボット0(1,1)に近いが...？
    sim.add_task((2, 8)) 
    sim.add_task((8, 5))
    sim.add_task((1, 5))

    print("貪欲法ベースラインによるシミュレーションを開始...")
    sim.run(steps=30) # 少し長めに動かす

    with open("output/output.json", "w") as f:
        json.dump(sim.history, f, indent=2)
    
    print("完了: output/output.json を保存しました。")

if __name__ == "__main__":
    main()