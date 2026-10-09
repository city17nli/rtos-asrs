# src/core.py
import random

class Robot:
    def __init__(self, robot_id, start_pos):
        self.id = robot_id
        self.pos = start_pos
        self.goal = start_pos
        self.start_pos = start_pos
        self.status = "IDLE"

class WarehouseSimulator:
    def __init__(self, width, height, obstacles, endpoints):
        self.width = width
        self.height = height
        self.obstacles = set(obstacles)
        self.endpoints = endpoints # ★リスト(複数)に変更
        self.robots = []
        self.task_queue = [] 
        self.history = []
        
        self.completed_tasks_count = 0
        self.target_total_tasks = 100 # ★規模が大きくなったので100個に増量！
        self.spawn_counter = 0

        self.valid_cells = []
        for y in range(height):
            for x in range(width):
                if (x, y) not in obstacles and (x, y) not in endpoints:
                    self.valid_cells.append((x, y))

    def add_robot(self, robot):
        self.robots.append(robot)

    def add_task(self, goal_pos):
        self.task_queue.append(goal_pos)

    def spawn_dynamic_task(self):
        active_or_queued = len(self.task_queue) + sum(1 for r in self.robots if r.status in ["TO_TASK", "TO_ENDPOINT"])
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
                robot.status = "TO_TASK"
                self.task_queue.remove(closest_task)

    def get_next_step(self, current, goal, avoid_cells):
        if current == goal:
            return current
        
        queue = [[current]]
        visited = set([current])
        
        while queue:
            path = queue.pop(0)
            node = path[-1]
            
            if node == goal:
                return path[1]
                
            cx, cy = node
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = cx + dx, cy + dy
                nxt = (nx, ny)
                
                if nx < 0 or nx >= self.width or ny < 0 or ny >= self.height:
                    continue
                if nxt in self.obstacles:
                    continue
                if len(path) == 1 and nxt in avoid_cells:
                    continue
                    
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(path + [nxt])
                    
        return current

    def step(self):
        for robot in self.robots:
            # ★変更：荷物を拾ったら「一番近い配送口(エンドポイント)」を探して向かう
            if robot.status == "TO_TASK" and robot.pos == robot.goal:
                best_ep = None
                min_ep_dist = float('inf')
                for ep in self.endpoints:
                    dist = abs(robot.pos[0] - ep[0]) + abs(robot.pos[1] - ep[1])
                    if dist < min_ep_dist:
                        min_ep_dist = dist
                        best_ep = ep
                
                robot.goal = best_ep
                robot.status = "TO_ENDPOINT"
                
            elif robot.status == "TO_ENDPOINT" and robot.pos == robot.goal:
                robot.status = "IDLE"
                robot.goal = robot.start_pos 
                self.completed_tasks_count += 1

        self.spawn_counter += 1
        if self.spawn_counter >= 3:
            self.spawn_dynamic_task()
            self.spawn_counter = 0

        self.assign_tasks_greedily()

        next_positions = {}
        reserved_cells = set()
        sorted_robots = sorted(self.robots, key=lambda r: r.id) 

        for robot in sorted_robots:
            if robot.pos == robot.goal:
                next_pos = robot.pos
            else:
                avoid_cells = set(reserved_cells)
                for other in self.robots:
                    if other.id != robot.id and other.id not in next_positions:
                        avoid_cells.add(other.pos)
                
                next_pos = self.get_next_step(robot.pos, robot.goal, avoid_cells)
            
            if next_pos in reserved_cells:
                next_pos = robot.pos

            next_positions[robot.id] = next_pos
            reserved_cells.add(next_pos)

        step_record = {}
        carrying_robots = [] 
        
        for robot in self.robots:
            robot.pos = next_positions[robot.id]
            step_record[str(robot.id)] = robot.pos
            if robot.status == "TO_ENDPOINT":
                carrying_robots.append(robot.id)
        
        active_tasks = list(self.task_queue)
        for robot in self.robots:
            if robot.status == "TO_TASK":
                active_tasks.append(robot.goal)
                
        step_record["tasks"] = active_tasks
        step_record["carrying"] = carrying_robots 
        
        self.history.append(step_record)

    def is_finished(self):
        all_idle = all(r.status == "IDLE" for r in self.robots)
        return self.completed_tasks_count >= self.target_total_tasks and all_idle

    def run(self, max_steps=5000):
        step_count = 0
        for _ in range(max_steps):
            self.step()
            step_count += 1
            if self.is_finished():
                print(f"★ すべてのタスク({self.target_total_tasks}個)が完了しました！ (経過ステップ: {step_count})")
                break