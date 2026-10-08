# src/core.py
import random

class Robot:
    def __init__(self, robot_id, start_pos):
        self.id = robot_id
        self.pos = start_pos
        self.goal = start_pos
        self.status = "IDLE"

class WarehouseSimulator:
    def __init__(self, width, height, obstacles):
        self.width = width
        self.height = height
        self.obstacles = set(obstacles)
        self.robots = []
        self.task_queue = [] 
        self.history = []
        
        # 統計・動的生成用の変数
        self.completed_tasks_count = 0
        self.target_total_tasks = 50  # 目標クリア数
        self.spawn_counter = 0        # タスク生成タイミングを測るカウンター

        # 障害物以外の安全なマスをあらかじめリストアップ
        self.valid_cells = []
        for y in range(height):
            for x in range(width):
                if (x, y) not in obstacles:
                    self.valid_cells.append((x, y))

    def add_robot(self, robot):
        self.robots.append(robot)

    def add_task(self, goal_pos):
        self.task_queue.append(goal_pos)

    def spawn_dynamic_task(self):
        """一定条件を満たしたときに新しいタスクをランダム生成する"""
        # すでに生成した総数（キュー内 ＋ クリア済み ＋ ロボットが持っているもの）が目標に達していなければ追加
        active_or_queued = len(self.task_queue) + sum(1 for r in self.robots if r.status == "MOVING")
        total_created = self.completed_tasks_count + active_or_queued
        
        if total_created < self.target_total_tasks:
            new_task = random.choice(self.valid_cells)
            self.task_queue.append(new_task)

    def assign_tasks_greedily(self):
        idle_robots = [r for r in self.robots if r.status == "IDLE"]
        for robot in idle_robots:
            if not self.task_queue:
                break
            
            closest_task = None
            min_dist = float('inf')
            
            for task in self.task_queue:
                dist = abs(robot.pos[0] - task[0]) + abs(robot.pos[1] - task[1])
                if dist < min_dist:
                    min_dist = dist
                    closest_task = task
            
            if closest_task:
                robot.goal = closest_task
                robot.status = "MOVING"
                self.task_queue.remove(closest_task)

    def get_next_step(self, current, goal):
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
        # 1. ゴール到着判定（タスク完了カウントを進める）
        for robot in self.robots:
            if robot.status == "MOVING" and robot.pos == robot.goal:
                robot.status = "IDLE"
                self.completed_tasks_count += 1

        # 2. 動的タスク生成の判定（例: 2ステップごとに1個新しいタスクをスポーン）
        self.spawn_counter += 1
        if self.spawn_counter >= 2:
            self.spawn_dynamic_task()
            self.spawn_counter = 0

        # 3. 貪欲法によるタスク割当
        self.assign_tasks_greedily()

        # 4. 衝突回避
        next_positions = {}
        reserved_cells = set()
        sorted_robots = sorted(self.robots, key=lambda r: r.id) 

        for robot in sorted_robots:
            if robot.pos == robot.goal:
                next_pos = robot.pos
            else:
                next_pos = self.get_next_step(robot.pos, robot.goal)
            
            if next_pos in reserved_cells:
                next_pos = robot.pos

            next_positions[robot.id] = next_pos
            reserved_cells.add(next_pos)

        # 5. 移動と記録
        step_record = {}
        for robot in self.robots:
            robot.pos = next_positions[robot.id]
            step_record[str(robot.id)] = robot.pos
        
        active_tasks = list(self.task_queue)
        for robot in self.robots:
            if robot.status == "MOVING" and robot.pos != robot.goal:
                active_tasks.append(robot.goal)
        step_record["tasks"] = active_tasks
        
        self.history.append(step_record)

    def is_finished(self):
        """目標のタスク数をすべてクリアし、全ロボットが待機状態になったか"""
        all_idle = all(r.status == "IDLE" for r in self.robots)
        return self.completed_tasks_count >= self.target_total_tasks and all_idle

    def run(self, max_steps=1000):
        """目標達成するか、最大ステップ数に達するまでループ"""
        for _ in range(max_steps):
            self.step()
            if self.is_finished():
                break