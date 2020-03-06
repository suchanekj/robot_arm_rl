# Imports
# from robot import Robot
from force_sensor import ForceSensor
from genetic_agent import GeneticAgent
from robot import Robot
import numpy as np

X_RANGE = [-2000, 2000]
Y_RANGE = [2000, 4500]
Z_RANGE = [-1500, 2000]
HAND_RANGE = [-2000, 6800]
# TODO - check this
WRIST_RANGE = [-5000, 5000]

def main():
    
    # Connect to the robot and calibrate it    
    robot = Robot()
    robot.connect()
    robot.calibrate()
    
    # Open connection to the force sensor
    forceSensor = ForceSensor()

    # Initialise the agent
    # TODO - properties of geneticAgent need to be changed
    geneticAgent = GeneticAgent(p_mutation=0.3, p_crossover=0.5, p_replication=0.2, 
                                diversity_factor=1.0, max_mutations=1, max_cross=1, 
                                coordinate_range=[X_RANGE, Y_RANGE, Z_RANGE, 
                                                  HAND_RANGE, WRIST_RANGE], 
                                reward_th=10)

    # Log of all trajectories in all generations, robot positions, force readings,
    # rewards and execution times
    training_log = {}
    training_iteration_index = 1
    # Generate trajectories
    # TODO - find sensible range to search in and generate randomly from there
    # TODO - translate the hard-coded trajectory to trajectory that can be run
    # with the default method, with a better starting position
    

    # Initialise the generation with the trajectories generated above
    # Note generation is a list (actually np array) of vectors (each vector is a trajectory)
    generation_to_execute = np.array([[3, 7, 3, 4, 5, 4, 7, 2, 9, 10, 17, 12, 19, 14, 12]])

    # Keep track of trajectories and their rewards (generations)
    generation_executed = []

    generation_number = 50 # Number of generations to run learning for
    for i in range(generation_number):
        
        robot.run_encoded_pickup()
        robot.write_command_loop()
        print("Iteration", i)
        
        for trajectory in generation_to_execute:
        
            # Run all the trajectories in the generation, get their rewards and 
            # get a new generation from the genetic agent
            print("Trajectory to run:", trajectory)

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
            reward = np.random.randint(0, 5) 
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



if __name__ == "__main__":
    main()