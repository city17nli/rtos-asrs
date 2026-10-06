import json
from pypibt import PIBT
from pypibt.env import Env, Agent

def main():
    # 1. 環境とエージェントの設定
    env = Env(map_file="assets/warehouse.map")
    
    # 2台のロボットの初期位置と最初の目標
    agents = [
        Agent(id=0, start=(1, 1), goal=(1, 13)),
        Agent(id=1, start=(4, 1), goal=(1, 7))
    ]
    solver = PIBT(env, agents)

    # 2. 次々と割り当てるタスク(目的地)のリスト
    task_queue = [(4, 13), (2, 5), (3, 9), (1, 1), (4, 1)]
    history = []
    simulation_steps = 50

    # 3. シミュレーションループ
    for step in range(simulation_steps):
        solver.step()
        
        # 現在の座標を記録 (エージェントIDをキーとする辞書)
        current_positions = {agent.id: list(agent.pos) for agent in agents}
        history.append(current_positions)
        
        # ゴールに到達したエージェントに次のタスクを割り当て
        for agent in agents:
            if agent.pos == agent.goal and task_queue:
                next_goal = task_queue.pop(0)
                agent.goal = next_goal
                agent.reset_priority() # 優先度をリセット

    # 4. 結果をJSONファイルとして保存
    with open("output.json", "w") as f:
        json.dump(history, f, indent=2)
    
    print("シミュレーション完了: output.json を生成しました。")

if __name__ == "__main__":
    main()
