import json
from pypibt import PIBT, get_grid

def main():
    # 1. マップの読み込み
    # get_grid関数を使うことで、正しい内部形式でマップが生成されます
    grid = get_grid("assets/warehouse.map")

    # 2. 2台のロボットの初期位置と、最初の目標地点 (x, y) のリスト
    current_starts = [(1, 1), (4, 1)]
    current_goals = [(1, 13), (1, 7)]

    # 3. 追加のタスクキュー (次にロボットに割り当てる目的地のセット)
    task_batches = [
        [(4, 13), (2, 5)],  # 次のタスクセット (ロボット0用, ロボット1用)
        [(3, 9), (1, 1)],
        [(4, 1), (4, 1)]
    ]

    full_history = []

    # 4. タスクがなくなるまでシミュレーションを繰り返す (MAPDループ)
    while True:
        # 現在のスタート地点からゴール地点までの経路を探索
        pibt = PIBT(grid, current_starts, current_goals)
        plan = pibt.run(max_timestep=100)
        
        # plan は各ステップごとの全ロボットの座標リストです
        # historyに追加 (つなぎ目の重複を防ぐため、2回目以降は最初のフレームを省く)
        if not full_history:
            full_history.extend(plan)
        else:
            full_history.extend(plan[1:])

        # 次のタスクセットがあるか確認
        if not task_batches:
            break

        # 次のスタート地点は、現在のゴール地点
        current_starts = current_goals
        # キューから新しいタスクを取り出して次のゴールにする
        current_goals = task_batches.pop(0)

    # 5. JSON形式に変換して保存 (visualize.pyで読み込みやすい形式にする)
    json_history = []
    for step_positions in full_history:
        step_dict = {}
        for agent_id, pos in enumerate(step_positions):
            step_dict[str(agent_id)] = pos # {"0": (x,y), "1": (x,y)} の形にする
        json_history.append(step_dict)

    with open("output.json", "w") as f:
        json.dump(json_history, f, indent=2)

    print("シミュレーション完了: output.json を生成しました。")

if __name__ == "__main__":
    main()
