import unittest
from mapd_problem import Agent, Task, Map
import numpy as np

class TestSimulation(unittest.TestCase):
    def test_assign_task(self):
        agent = Agent(name="Test Agent")
        task = Task(name="Task 1", pickup_location=(0, 0), delivery_location=(1, 1))
        agent.assign_task(task)
        self.assertEqual(agent.current_task, task)
        self.assertEqual(len(agent.task_queue), 0)
    
    def test_task_pickup_and_delivery(self):
        task = Task(name="Task 1", pickup_location=(0, 0), delivery_location=(1, 1))
        self.assertFalse(task.picked_up)
        self.assertFalse(task.delivered)
        
        task.pickup()
        self.assertTrue(task.picked_up)
        self.assertFalse(task.delivered)
        
        task.deliver()
        self.assertTrue(task.delivered)
    
    def test_is_position_free(self):
        game_map = Map(width=5, height=5, obstacles=[(2, 2)], agents=[])
        self.assertTrue(game_map.is_position_free(0, 0))
        self.assertFalse(game_map.is_position_free(2, 2))  # Obstacle position
        
        game_map.agents.append(Agent(name="Agent 1", location=(1, 1)))
        self.assertFalse(game_map.is_position_free(1, 1))  # Agent position
        self.assertTrue(game_map.is_position_free(0, 1))

    def test_agent_movement(self):
        game_map = Map(width=5, height=5, obstacles=[], agents=[])
        agent = Agent(name="Agent 1", location=(0, 0))
        game_map.agents.append(agent)
        
        target = (2, 2)
        agent.move_to(target, game_map)
        
        # Assuming agent makes one move towards the target
        self.assertEqual(agent.location, (1, 1))

    def test_task_queue_management(self):
        agent = Agent(name="Agent 2")
        task1 = Task(name="Task 1", pickup_location=(0, 0), delivery_location=(1, 1))
        task2 = Task(name="Task 2", pickup_location=(2, 2), delivery_location=(3, 3))
        
        agent.assign_task(task1)
        agent.assign_task(task2)
        
        self.assertEqual(agent.current_task, task1)
        self.assertIn(task2, agent.task_queue)
    
    def test_task_completion(self):
        game_map = Map(width=5, height=5, obstacles=[], agents=[])
        agent = Agent(name="Agent 3", location=(0, 0))
        task = Task(name="Task 3", pickup_location=(0, 0), delivery_location=(1, 1))
        agent.assign_task(task)
        
        agent.complete_task_if_possible()  # Pickup
        self.assertTrue(task.picked_up)
        self.assertFalse(task.delivered)
        
        agent.location = task.delivery_location
        agent.complete_task_if_possible()  # Deliver
        self.assertTrue(task.delivered)
    
    def test_add_random_task(self):
        game_map = Map(width=5, height=5, obstacles=[(1, 1)], agents=[])
        success = game_map.add_random_task()
        
        if success:
            self.assertEqual(len(game_map.tasks), 1)
        else:
            self.assertEqual(len(game_map.tasks), 0)

    def test_find_random_free_position(self):
        game_map = Map(width=3, height=3, obstacles=[(1, 1), (2, 2)], agents=[Agent(name="A", location=(0, 1))])
        position = game_map.find_random_free_position()
        
        # The position should not be an obstacle or under the agent
        self.assertNotEqual(position, (1, 1))
        self.assertNotEqual(position, (2, 2))
        self.assertNotEqual(position, (0, 1))
    
    def test_time_step(self):
        game_map = Map(width=5, height=5, obstacles=[(1, 1), (2, 2)], agents=[Agent(name="A", location=(0, 1)), Agent(name="B", location=(0, 3))])

        # Force the addition of a task to ensure determinism in the test
        new_task = Task(name="Task 1", pickup_location=(0, 2), delivery_location=(2, 0))
        game_map.tasks.append(new_task)
        game_map.assign_task_to_agent(new_task)

        # Ensure the task is assigned properly
        self.assertEqual(len(game_map.tasks), 1)
        self.assertIsNotNone(game_map.agents[0].current_task)

        game_map.time_step()







