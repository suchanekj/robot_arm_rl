# Imports
# from robot import Robot
# from force_sensor import ForceSensor
from genetic_agent import GeneticAgent
import numpy as np


forceSensor = ForceSensor
robotArm = Robot()
robotArm.connect() # Note that it is assumed arm is already calibrated so did not call calibrate here
# TODO - properties of geneticAgent need to be changed
geneticAgent = GeneticAgent(p_mutation=0.3, p_crossover=0.5, p_replication=0.2, diversity_factor=1.0,
                 max_mutations=1, max_cross=1, coordinate_range=[[0, 1], [0, 1]], reward_th=10)

def run_trajectory(traj):
    # Accepts length 15 array, traj
    # Assume each point consists of values for [WAIST, SHOULDER, ELBOW, L-HAND, WRIST] in this order
    assert len(traj) == 15

    # Extracts the three points
    first_point = traj[0:5]
    second_point = traj[5:10]
    third_point = traj[10:]
    points = [first_point, second_point, third_point]

    # Print out for debugging
    print("First point:", first_point)
    print("Second point:", second_point)
    print("Third point:", third_point)

    # Get robot to move to the 3 points
    for n in range (len(points)):
        print("Point {}".format(n+1))
        # Select the point
        point = points[n]
        x = point[0] # Assume first three values represent the xyz coordinate
        y = point[1]
        z = point[2]
        l_hand_value = point[3] # Assume 4th value is the amount to move L_HAND by
        wrist_value = point[4] # Assume 5th value is the amount to move WRIST by

        # Move to cartesian position
        # Check if safe first
        cartesian_roboforth_command = '{} {} {} MOVETO'.format(x, y, z)
        robotArm.is_safe_cartesian(cartesian_roboforth_command)
        # Now move if safe
        robotArm.move_to_cart(x, y, z)

        # Move L_HAND
        # Check if safe first
        l_hand_roboforth_command = 'TELL L-HAND {} MOVETO'.format(l_hand_value)
        robotArm.is_safe_joint(l_hand_roboforth_command)
        # Now move if safe
        robotArm.rotate_by('L-HAND', l_hand_value)

        # Move WRIST
        # Check if safe first
        wrist_roboforth_command = 'TELL WRIST {} MOVETO'.format(wrist_value)
        robotArm.is_safe_joint(wrist_roboforth_command)
        # Now move if safe
        robotArm.rotate_by('WRIST', wrist_value)

def main():
    # Generate trajectories
    # TODO - not sure how to do this yet


    # Initialise the generation with the trajectories generated above
    # Note generation is a list (actually np array) of vectors (each vector is a trajectory)
    current_generation = np.array([[3, 7, 3, 4, 5, 4, 7, 2, 9, 10, 17, 12, 19, 14, 12]])

    # Keep track of trajectories and their rewards (generations)
    generation_w_reward = []

    n = 50 # Number of iterations
    for i in range(n):
        print("Iteration", i)

        # We will run the newly generated trajectory (or initially generated trajectory if first iteration)
        new_traj = current_generation[-1]  # trajectory to run is the last one from current_generation (the new one)
        print("Trajectory to run:", new_traj)

        # Make sure arm is in same starting position
        robotArm.get_ready() # Go to start position TODO - need to check this

        # Start logging force sensor outputs
        forceSensor.log_pickup() # TODO - probably need to change this

        # Run trajectory
        run_trajectory(new_traj)

        # Calculate reward (using force sensor readings) TODO
        reward = np.random.randint(0, 5) # TODO - log_pickup needs to be changed so it returns the force sensor outputs and doesn't just save them to json file
        print("Reward obtained: ", reward)

        # Add the new trajectory along with its reward to the generation
        traj_reward_list = (new_traj, reward)
        generation_w_reward.append(traj_reward_list)
        print("Trajectory with reward: ", traj_reward_list)
        print("New generation (with reward):", generation_w_reward)

        # Run learning agent to get new trajectories
        current_generation = geneticAgent.get_new_generation(np.array(generation_w_reward)) # note current_generation is list of
        # trajectories but without rewards



if __name__ == "__main__":
    main()