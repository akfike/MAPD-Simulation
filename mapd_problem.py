import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap
import numpy as np
import random


class Agent:
    def __init__(self, name, location=None):
        self.name = name
        self.location = location
        self.task_queue = []  # Queue of tasks assigned to the agent
        self.current_task = None

    
    def assign_task(self, task):
        self.task_queue.append(task)
        if not self.current_task:  # If the agent is not currently on a task, start this one
            self.current_task = self.task_queue.pop(0)

    def move_to(self, target, game_map):
        """Move agent one step towards the target, ensuring the new location is free."""
        if not self.location or not target:
            return  # No operation if location or target is undefined

        x, y = self.location
        tx, ty = target

        # Calculate step to move closer to the target
        step_x, step_y = 0, 0
        if x < tx:
            step_x = 1
        elif x > tx:
            step_x = -1

        if y < ty:
            step_y = 1
        elif y > ty:
            step_y = -1

        # Suggested new location
        new_location = (x + step_x, y + step_y)

        # Check if the new location is free (not an obstacle, and not occupied by another agent)
        if game_map.is_position_free(*new_location):
            self.location = new_location

    def complete_task_if_possible(self):
        """Complete the task if at the correct location."""
        if self.current_task:
            # Check if at pickup location and pick up the item
            if self.location == self.current_task.pickup_location:
                print("Picking up")
                self.current_task.pickup()
            # Check if at delivery location and deliver the item
            elif (self.location == self.current_task.delivery_location) and self.current_task.picked_up:
                print("Delivering")
                self.current_task.deliver()
                self.current_task = None  # Task completed
                if len(self.task_queue) > 0:
                    self.current_task = self.task_queue.pop(0)
                    print("New task for agent")

class Task:
    def __init__(self, name, pickup_location, delivery_location):
        self.name = name
        self.pickup_location = pickup_location
        self.delivery_location = delivery_location
        self.picked_up = False
        self.delivered = False

    def pickup(self):
        self.picked_up = True

    def deliver(self):
        self.delivered = True

class Map:
    def __init__(self, width, height, obstacles=[], agents=[]):
        self.width = width
        self.height = height
        self.agents = agents
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.tasks = []
        for (x, y) in obstacles:
            self.grid[y][x] = 1

    def display(self):
        display_grid = [row[:] for row in self.grid]
        for agent in self.agents:
            if agent.location:
                x, y = agent.location
                display_grid[y][x] = 4
            for task in self.tasks:
                px, py = task.pickup_location
                dx, dy = task.delivery_location
                if not task.picked_up:
                    display_grid[py][px] = 2
                if not task.delivered:
                    display_grid[dy][dx] = 3
        return display_grid 

    def is_position_free(self, x, y):
        """Check if a position is free from obstacles and agents."""
        if self.grid[y][x] != 0:  # Check if the cell is not empty or an obstacle
            return False
        # Ensure no other agent is at the position
        for agent in self.agents:
            if agent.location == (x, y):
                return False
        return True
    
    def add_task(self, task):
        x, y = task.pickup_location
        self.grid[y][x] = 2
        x, y = task.delivery_location
        self.grid[y][x] = 3
    
    def find_random_free_position(self):
        """Find a random position on the grid that is not an obstacle, pickup, or delivery location,
            and is not completely surrounded by obstacles."""
        free_positions = [(x, y) for y in range(self.height) for x in range(self.width)
                            if self.is_position_free(x, y)]
        return random.choice(free_positions) if free_positions else None

    def add_random_task(self):
        """Randomly add a new task if conditions are met."""
        if random.random() < 0.5:  # Adjust probability as needed
            pickup = self.find_random_free_position()
            delivery = self.find_random_free_position()
            if pickup and delivery:
                new_task = Task(f"Task {len(self.tasks) + 1}", pickup, delivery)
                print("New task created: ", new_task.pickup_location, " ", new_task.delivery_location)
                self.tasks.append(new_task)
                self.assign_task_to_agent(new_task)
                return True
        return False
    
    def assign_task_to_agent(self, task):
        """Assign a task to the least busy agent, or the closest one if they're equally busy."""
        # Find the agent with the least number of tasks, preferring closer agents for tie-breaking.
        least_busy_agents = sorted(self.agents, key=lambda x: (len(x.task_queue), np.linalg.norm(np.array(x.location) - np.array(task.pickup_location))))
        if least_busy_agents:
            least_busy_agents[0].assign_task(task)
            print(f"Agent {least_busy_agents[0].name} gets task: ", task.pickup_location, " ", task.delivery_location)

    def time_step(self):
        """Simulate a single time step in the environment."""
        # Add a random task
        print("Time step")
        random_task_added = self.add_random_task()
        if random_task_added:
            print("Added new task")
        for agent in self.agents:
            print(f"Agent {agent.name} is at {agent.location}")
            if agent.current_task:
                if not agent.current_task.picked_up:
                    print("Moving")
                    agent.move_to(agent.current_task.pickup_location, self)
                    print("Agent moved to: ", agent.location)
                    agent.complete_task_if_possible()
                elif not agent.current_task.delivered:
                    agent.move_to(agent.current_task.delivery_location, self)
                    print("Agent moved to: ", agent.location)
                    agent.complete_task_if_possible()
                else:
                    print("Something went wrong. Assigned a task but delivered and picked up are true")


# Example setup and the animation block encapsulated within the main guard
if __name__ == "__main__":
    cmap = ListedColormap(['white', 'blue', 'red', 'green', 'yellow'])
    agents = [Agent(name="Agent 1", location=(0, 0)), Agent(name="Agent 2", location=(1, 1))]
    width, height = 10, 10
    obstacles = [(1, 2), (2, 2), (3, 2), (4, 5), (5, 5)]
    game_map = Map(width, height, obstacles=obstacles, agents=agents)

    fig, ax = plt.subplots()
    grid = game_map.display()  # Initial display to set up the grid
    mat = ax.matshow(grid, cmap=cmap)  # Use the custom color map
    plt.colorbar(mat, ticks=range(5), label='Cell Type')

    def update(frame_number):
        """
        Update function for the animation. This will be called at each frame of the animation.
        
        :param frame_number: The current frame number (automatically handled by FuncAnimation).
        """
        print("Frame Number: ", frame_number)
        game_map.time_step()  # Progress the simulation by one time step.
        grid = game_map.display()  # Get the updated display grid.
        mat.set_data(grid)  # Update the displayed data.

    ani = FuncAnimation(fig, update, frames=20, interval=500)  # Adjust 'frames' and 'interval' as needed
    plt.show()