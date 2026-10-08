# src/core.py

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

    def add_robot(self, robot):
        self.robots.append(robot)

    def add_task(self, goal_pos):
        self.task_queue.append(goal_pos)

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
        # 1. ゴール到着判定
        for robot in self.robots:
            if robot.status == "MOVING" and robot.pos == robot.goal:
                robot.status = "IDLE"

        # 2. タスク割当
        self.assign_tasks_greedily()

        # 3. 衝突回避
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

        # 4. 移動と記録（★ここを改造しました！）
        step_record = {}
        for robot in self.robots:
            robot.pos = next_positions[robot.id]
            step_record[str(robot.id)] = robot.pos
        
        # 画面に表示するために「残っているタスク」と「ロボットが今向かっているタスク」を記録
        active_tasks = list(self.task_queue)
        for robot in self.robots:
            if robot.status == "MOVING" and robot.pos != robot.goal:
                active_tasks.append(robot.goal)
        step_record["tasks"] = active_tasks # 履歴に追加
        
        self.history.append(step_record)

    def run(self, steps):
        for _ in range(steps):
            self.step()