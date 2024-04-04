import heapq
import itertools
import logging

tiebreaker = itertools.count()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Environment:
    def __init__(self, size, obstacles=None, endpoints=None):
        self.size = size
        self.obstacles = obstacles if obstacles else []
        self.endpoints = endpoints if endpoints else []
        logging.info(f"Environment created with size {self.size}, obstacles {self.obstacles}, and endpoints {self.endpoints}")


    def is_valid(self, position):
        valid = 0 <= position[0] < self.size[0] and 0 <= position[1] < self.size[1]
        if valid:
            if position in self.obstacles:
                logging.debug(f"Position {position} is not valid because it's an obstacle.")
                return False
            logging.debug(f"Position {position} is valid.")
            return True
        logging.debug(f"Position {position} is out of bounds and not valid.")
        return False

    def get_neighbors(self, position):
        logging.debug(f"Getting neighbors for position {position}.")

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # 4-directional movement
        neighbors = []
        for d in directions:
            next_position = (position[0] + d[0], position[1] + d[1])
            if self.is_valid(next_position):
                neighbors.append(next_position)
        logging.debug(f"Found neighbors for position {position}: {neighbors}.")
        return neighbors

class Agent:
    def __init__(self, id, current_location):
        self.id = id
        self.current_location = current_location
        self.path = []  # Stores the path assigned by MLA*

class Task:
    def __init__(self, id, pickup_location, delivery_location):
        self.id = id
        self.pickup_location = pickup_location
        self.delivery_location = delivery_location

class Node:
    def __init__(self, position, g=0, label=1, parent=None, tmax=float('inf'), environment=None, tasks=None):
        self.position = position
        self.g = g
        self.label = label
        self.tmax = tmax
        self.parent = parent
        self.environment = environment
        self.tasks = tasks
        self.h = self.calculate_heuristic()
        self.f = self.g + self.h
        self.tiebreaker = next(tiebreaker)  # Tiebreaker for nodes with equal f values

    def calculate_heuristic(self):
        if not self.tasks or self.label - 1 >= len(self.tasks):
            return 0
        goal = self.tasks[self.label - 1].pickup_location if self.label == 1 else self.tasks[self.label - 1].delivery_location
        return abs(self.position[0] - goal[0]) + abs(self.position[1] - goal[1])
    
    def __lt__(self, other):
        # First compare by f value, then by tiebreaker
        return (self.f, self.tiebreaker) < (other.f, other.tiebreaker)

def mla_star(start, tasks, environment):
    logging.info(f"Starting MLA* from {start} with tasks {tasks}.")
    goals = [task.pickup_location for task in tasks] + [tasks[-1].delivery_location]
    open_list = []
    closed_list = set()
    start_node = Node(start, environment=environment, tasks=tasks)
    heapq.heappush(open_list, start_node)

    while open_list:
        current_node = heapq.heappop(open_list)
        logging.debug("Exploring node at %s with label %d", current_node.position, current_node.label)
        if current_node.label == len(goals) + 1:
            return reconstruct_path(current_node)

        closed_list.add(current_node.position)
        for next_position in environment.get_neighbors(current_node.position):
            if next_position in closed_list:
                continue
            neighbor = Node(next_position, g=current_node.g + 1, label=current_node.label, parent=current_node, environment=environment, tasks=tasks)
            if neighbor.position == goals[neighbor.label - 1]:
                neighbor.label += 1
            heapq.heappush(open_list, neighbor)
    return None

def get_neighbors(position):
    # Implement neighbor generation here (e.g., 4-directional or 8-directional movement)
    pass

def reconstruct_path(node):
    logging.debug(f"Reconstructing path starting from node {node.position}.")
    path = []
    while node is not None:
        path.append(node.position)
        node = node.parent
    return path[::-1]

def hbh_assignment(agents, tasks, environment):
    logging.info("Starting hbh_assignment.")
    t = 0
    while tasks:  # Continue until all tasks are assigned
        available_agents = [agent for agent in agents if not agent.path]  # Agents with no assigned task
        if not available_agents:  # No available agents to assign tasks
            break

        # Generate agent-task pairs and sort by h-value (distance from agent to task pickup location)
        agent_task_pairs = []
        for agent in available_agents:
            for task in tasks:
                distance = abs(agent.current_location[0] - task.pickup_location[0]) + \
                           abs(agent.current_location[1] - task.pickup_location[1])
                agent_task_pairs.append((distance, agent, task))
        agent_task_pairs.sort()

        for _, agent, task in agent_task_pairs:
            # Pass the current task as a list to match the expected argument format
            path = mla_star(agent.current_location, [task], environment)
            if path:  # If MLA* finds a feasible path
                agent.path = path  # Assign path to agent
                agent.current_location = task.delivery_location  # Update agent's location to the end of the path
                tasks.remove(task)  # Remove assigned task from the list

        # Optionally, move agents to closest free endpoint if needed
        # This part depends on your specific scenario and environment setup

        t += 1  # Increment time step


# Environment setup
size = (10, 10)  # 10x10 grid
obstacles = [(1, 2), (2, 2), (3, 2)]  # Obstacles in the environment
endpoints = [(0, 9), (9, 0)]  # Endpoints where agents can rest
environment = Environment(size, obstacles, endpoints)

# Agents and Tasks setup
agents = [Agent(1, (0, 0)), Agent(2, (9, 9))]
tasks = [Task(1, (2, 3), (5, 5)), Task(2, (7, 8), (1, 2))]

# Call the updated hbh_assignment function with the environment
hbh_assignment(agents, tasks, environment)

# Print out the paths assigned to each agent
for agent in agents:
    print(f"Agent {agent.id} path: {agent.path}")
