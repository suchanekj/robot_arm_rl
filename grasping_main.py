# Imports
# from robot import Robot
from force_sensor import ForceSensor
from genetic_agent import GeneticAgent
from robot import Robot

import json
import numpy as np

X_RANGE = [-1500, 1500]
Y_RANGE = [2000, 4000]
Z_RANGE = [-1000, 2000]
HAND_RANGE = [-100, 4800]
WRIST_RANGE = [-5000, 5000]
# Force threshold for detecting touch
FORCE_THR = 10.0
# TODO - find sensible range to search in and generate randomly from there
COORDINATE_RANGE =[X_RANGE, Y_RANGE, Z_RANGE, HAND_RANGE, WRIST_RANGE]
N_TRAJECTORIES_PER_GENERATION = 3
LEN_TRAJECTORY = 15

def get_rewards(force_log):
    touch_reward = 0
    # Reward for touching the cylinder at all
    if any(abs(force_reading)>FORCE_THR for force_reading in force_log['fv']):
        touch_reward = 1
    if any(abs(force_reading)>FORCE_THR for force_reading in force_log['fh1']):
        touch_reward = 1
    if any(abs(force_reading)>FORCE_THR for force_reading in force_log['fh2']):
        touch_reward = 1
    return touch_reward

def main():
    
    # Connect to the robot and calibrate it    
    robot = Robot()
    robot.connect()
    robot.calibrate()
    
    # Open connection to the force sensor
    forceSensor = ForceSensor()

    # Initialise the agent

    geneticAgent = GeneticAgent(p_mutation=0.2, p_crossover=0.2, p_replication=0.6, 
                                diversity_factor=0.0001, max_mutations=2, max_cross=2, 
                                coordinate_range=COORDINATE_RANGE, reward_th=1)

    # Log of all trajectories in all generations, robot positions, force readings,
    # rewards and execution times
    training_log = {}
    training_iteration_index = 1
    # Generate trajectories

    # TODO - translate the hard-coded trajectory to trajectory that can be run
    # with the default method, with a better starting position
    
    
    # Initialise the generation with the trajectories generated above
    # Note generation is a list (actually np array) of vectors (each vector is a trajectory)
    generation_to_execute = np.zeros((N_TRAJECTORIES_PER_GENERATION,
                                      LEN_TRAJECTORY))
    for tr_idx, trajectory in enumerate(generation_to_execute):
        for var_idx, var in enumerate(trajectory):
            generation_to_execute[tr_idx][var_idx] = int(np.random.uniform(COORDINATE_RANGE[var_idx%5][0],
                                                                           COORDINATE_RANGE[var_idx%5][1]))

    # Keep track of trajectories and their rewards (generations)
    generation_executed = []

    generation_number = 2 # Number of generations to run learning for
    for i in range(generation_number):
        
        #robot.run_encoded_pickup()
        #robot.write_command_loop()
        print("Iteration", i)
        
        for trajectory in generation_to_execute:
        
            # Run all the trajectories in the generation, get their rewards and 
            # get a new generation from the genetic agent
            print("Trajectory to run: ", trajectory)
            run = input("Run?")
            
            # Reset to starting position
            # TODO - implement a better starting position in rest
            robot.reset() 

            # Start logging force sensor outputs
            ts = forceSensor.start_logging_forces() 
            
            # Run trajectory
            position_log = robot.run_trajectory(trajectory)

            force_log, tf = forceSensor.end_logging_forces()
            
            # Calculate reward (using force sensor readings) TODO
            # TODO - get reward from the force log
            # Indicate somewhere what reward is being used
            reward = get_rewards(force_log)
            print("Reward obtained: ", reward)
            
            training_log[training_iteration_index] = {'position_log': position_log,
                        'force_log': force_log, 't': [ts, tf], 'reward': reward}
            training_iteration_index+=1
            
            # Add the new trajectory along with its reward to the generation
            traj_reward_list = [trajectory, reward]
            generation_executed.append(traj_reward_list)
        
            print("Trajectory with reward: ", traj_reward_list)
            #print("New generation (with reward):", generation_w_reward)

        # Run learning agent to get new trajectories
        generation_to_execute = geneticAgent.get_new_generation(np.array(generation_executed)) 

    with open('training_log', 'w+') as f:
        json.dump(training_log, f)
    print('Training complete')

if __name__ == "__main__":
    main()