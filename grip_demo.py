from robot import Robot

# Initialize robot arm (requires user input)
RobotArm = Robot()


def main():
    """ Current temporary routine for picking up a screwdriver """
    
    # Move to HOME
    RobotArm.move_home()

    # Switch to JOINT
    RobotArm.to_joint()

    # Level arm and hand
    RobotArm.level_hand()

    # Switch to CARTESIAN
    RobotArm.to_cartesian()

    # Move down
    RobotArm.give_command('0 0 -1500 MOVE')

    # Rotate hand
    RobotArm.give_command('TELL WRIST 5000 MOVE')

    # Switch to CARTESIAN
    RobotArm.to_cartesian()

    # Move up
    RobotArm.give_command('0 0 3000 MOVE')

    # Move forward
    RobotArm.give_command('0 2000 0 MOVE')

    command = input('Move home? [y/n]: ')
    if command == 'y':
    	RobotArm.move_home()
    elif command == "n":
    	pass
    else:
    	raise Exception('Unknown command')


if __name__ == "__main__":
    main()
