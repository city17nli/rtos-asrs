# src/main.py
import json
import os
# core.py からクラスを読み込む
from core import Robot, WarehouseSimulator

def main():
    # outputフォルダがなければ作成
    os.makedirs("output", exist_ok=True)

    # 1. 環境のセットアップ (10x10の倉庫、中央に障害物)
    width, height = 10, 10
    obstacles = [(5, 4), (5, 5), (5, 6)]
    sim = WarehouseSimulator(width, height, obstacles)
    
    # 2. ロボットの配置
    sim.add_robot(Robot(robot_id=0, start_pos=(1, 1)))
    sim.add_robot(Robot(robot_id=1, start_pos=(1, 8)))

    # 3. 発生するタスク(目的地)の追加
    sim.add_task((8, 8))
    sim.add_task((8, 1))
    sim.add_task((2, 5))

    # 4. シミュレーション実行 (20ステップ)
    print("シミュレーションを開始します...")
    sim.run(steps=20)

    # 5. 結果を保存
    output_path = "output/output.json"
    with open(output_path, "w") as f:
        json.dump(sim.history, f, indent=2)
    
    print(f"シミュレーション完了: {output_path} を保存しました。")

if __name__ == "__main__":
    main()