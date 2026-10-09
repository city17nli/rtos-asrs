# src/core.py
import random

class Robot:
    def __init__(self, robot_id, start_pos):
        self.id = robot_id
        self.pos = start_pos
        self.goal = start_pos
        self.start_pos = start_pos
        self.status = "IDLE"
        self.action_timer = 0       
        self.target_task = None     

class WarehouseSimulator:
    def __init__(self, width, height, obstacles, endpoints):
        self.width = width
        self.height = height
        self.obstacles = set(obstacles)
        self.endpoints = endpoints
        self.robots = []
        self.task_queue = [] 
        self.history = []
        
        self.completed_tasks_count = 0
        self.target_total_tasks = 100 # ★変更：テスト用に100個へ増加！
        self.spawn_counter = 0

        self.shelf_cells = list(self.obstacles)

    def add_robot(self, robot):
        self.robots.append(robot)

    def add_task(self, goal_pos):
        self.task_queue.append(goal_pos)

    def spawn_dynamic_task(self):
        active_or_queued = len(self.task_queue) + sum(1 for r in self.robots if r.status in ["TO_TASK", "PICKING_UP", "TO_ENDPOINT", "DROPPING_OFF"])
        total_created = self.completed_tasks_count + active_or_queued
        
        if total_created < self.target_total_tasks:
            new_task = random.choice(self.shelf_cells)
            self.task_queue.append(new_task)

    def assign_tasks_greedily(self):
        idle_robots = [r for r in self.robots if r.status == "IDLE"]
        for robot in idle_robots:
            if not self.task_queue:
                break
            
            closest_task = None
            best_adj_cell = None
            min_dist = float('inf')
            
            for task in self.task_queue:
                tx, ty = task
                adj_cells = []
                for dx, dy in [(-1, 0), (1, 0)]:
                    nx, ny = tx + dx, ty + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if (nx, ny) not in self.obstacles:
                            adj_cells.append((nx, ny))
                
                if not adj_cells:
                    continue

                for adj in adj_cells:
                    dist = abs(robot.pos[0] - adj[0]) + abs(robot.pos[1] - adj[1])
                    if dist < min_dist:
                        min_dist = dist
                        closest_task = task
                        best_adj_cell = adj
            
            if closest_task:
                robot.target_task = closest_task 
                robot.goal = best_adj_cell       
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
            if robot.status == "PICKING_UP":
                robot.action_timer -= 1
                if robot.action_timer <= 0:
                    best_ep = None
                    min_ep_dist = float('inf')
                    for ep in self.endpoints:
                        dist = abs(robot.pos[0] - ep[0]) + abs(robot.pos[1] - ep[1])
                        if dist < min_ep_dist:
                            min_ep_dist = dist
                            best_ep = ep
                    robot.goal = best_ep
                    robot.status = "TO_ENDPOINT"
                    robot.target_task = None
            
            elif robot.status == "DROPPING_OFF":
                robot.action_timer -= 1
                if robot.action_timer <= 0:
                    robot.status = "IDLE"
                    robot.goal = robot.start_pos 
                    self.completed_tasks_count += 1
                    
            elif robot.status == "TO_TASK" and robot.pos == robot.goal:
                robot.status = "PICKING_UP"
                robot.action_timer = 2 
                
            elif robot.status == "TO_ENDPOINT" and robot.pos == robot.goal:
                robot.status = "DROPPING_OFF"
                robot.action_timer = 2 

        self.spawn_counter += 1
        if self.spawn_counter >= 1: # ★変更：毎ステップ（1歩ごと）タスクが超高頻度で湧く
            self.spawn_dynamic_task()
            self.spawn_counter = 0

        self.assign_tasks_greedily()

        next_positions = {}
        reserved_cells = set()
        sorted_robots = sorted(self.robots, key=lambda r: r.id) 

        for robot in sorted_robots:
            if robot.status in ["PICKING_UP", "DROPPING_OFF"] or robot.pos == robot.goal:
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
            if robot.status in ["TO_ENDPOINT", "DROPPING_OFF"]:
                carrying_robots.append(robot.id)
        
        active_tasks = list(self.task_queue)
        for robot in self.robots:
            if robot.status in ["TO_TASK", "PICKING_UP"] and robot.target_task:
                active_tasks.append(robot.target_task)
                
        step_record["tasks"] = active_tasks
        step_record["carrying"] = carrying_robots 
        
        self.history.append(step_record)

    def is_finished(self):
        all_parked = all(r.status == "IDLE" and r.pos == r.start_pos for r in self.robots)
        return self.completed_tasks_count >= self.target_total_tasks and all_parked

    def run(self, max_steps=8000): 
        step_count = 0
        for _ in range(max_steps):
            self.step()
            step_count += 1
            if self.is_finished():
                print(f"★ すべてのタスク({self.target_total_tasks}個)が完了し、全機帰還しました！ (経過ステップ: {step_count})")
                break