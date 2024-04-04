import json
import numpy as np

class MapEnvironment:
    def __init__(self, dimensions, map_layout):
        self.dimensions = dimensions
        self.map_layout = np.array(map_layout)
        self.agents = []

    def add_agent(self, start, goal, scenario_type=None):
        agent = {'start': start, 'goal': goal, 'type': scenario_type}
        self.agents.append(agent)

def load_map(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        map_layout = [list(line.strip()) for line in lines[4:]]  # Adjust as per your map file format
    return map_layout  # Return only the map layout

def load_scenario(file_path, environment):
    with open(file_path, 'r') as file:
        # Identify the scenario type based on the file name
        scenario_type = "even" if "even" in file_path else "random"
        
        for line in file:
            start, goal = parse_line_to_positions(line)
            # Pass the scenario type as an additional parameter to add_agent
            environment.add_agent(start, goal, scenario_type)

def parse_line_to_positions(line):
    # Convert line to start and goal positions; implementation depends on your scenario file format
    return start_position, goal_position

def main(benchmark_file):
    with open(benchmark_file, 'r') as file:
        benchmarks = json.load(file)
    
    for benchmark in benchmarks:
        print(f"Running Benchmark: {benchmark['name']}")
        dimensions = (benchmark['number_rows'], benchmark['number_columns'])
        map_layout = load_map(benchmark['map_file'])  # Now correctly expects only the map layout
        environment = MapEnvironment(dimensions, map_layout)
        
        for scenario_file in benchmark['scenario_files']:
            print(f"  Scenario: {scenario_file}")
            load_scenario(scenario_file, environment)
            
            # Integrate and run your EPEA* algorithm here
            # Reset environment for the next scenario
            environment.reset_agents()

        # Log benchmark-wide metrics here


if __name__ == "__main__":
    main("benchmarks.json")
