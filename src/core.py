# src/core.py

class Robot:
    """ロボットの設計図"""
    def __init__(self, robot_id, start_pos):
        self.id = robot_id
        self.pos = start_pos
        self.goal = start_pos
        self.status = "IDLE"  # 状態管理（IDLE: 待機, MOVING: 移動中）

class WarehouseSimulator:
    """倉庫全体の管理と経路探索を行う設計図"""
    def __init__(self, width, height, obstacles):
        self.width = width
        self.height = height
        self.obstacles = set(obstacles)
        self.robots = []
        self.task_queue = []
        self.history = []

    def add_robot(self, robot):
        self.robots.append(robot)

    def add_task(self, goal_pos):
        self.task_queue.append(goal_pos)

    def get_next_step(self, current, goal):
        """目的地への次の1歩を計算（単純なマンハッタン距離）"""
        cx, cy = current
        gx, gy = goal
        
        candidates = []
        if cx < gx: candidates.append((cx + 1, cy))
        elif cx > gx: candidates.append((cx - 1, cy))
        if cy < gy: candidates.append((cx, cy + 1))
        elif cy > gy: candidates.append((cx, cy - 1))
        
        for nxt in candidates:
            if nxt not in self.obstacles:
                return nxt
        return current

    def step(self):
        """1タイムステップ分の移動処理"""
        # タスク割当
        for robot in self.robots:
            if robot.pos == robot.goal and self.task_queue:
                robot.goal = self.task_queue.pop(0)
                robot.status = "MOVING"

        next_positions = {}
        reserved_cells = set()

        # 優先度順(今回はID順)に次の場所を予約して衝突回避
        sorted_robots = sorted(self.robots, key=lambda r: r.id) 
        for robot in sorted_robots:
            if robot.pos == robot.goal:
                next_pos = robot.pos
            else:
                next_pos = self.get_next_step(robot.pos, robot.goal)
            
            if next_pos in reserved_cells:
                next_pos = robot.pos  # 衝突するなら待機

            next_positions[robot.id] = next_pos
            reserved_cells.add(next_pos)

        # 移動と履歴保存
        step_record = {}
        for robot in self.robots:
            robot.pos = next_positions[robot.id]
            step_record[str(robot.id)] = robot.pos
        
        self.history.append(step_record)

    def run(self, steps):
        """指定したステップ数だけシミュレーションを回す"""
        for _ in range(steps):
            self.step()