#!/usr/bin/env python

import __future__
import os

import shell
import arm

def main():
    # Check for admin privileges.
    ''' if os.getuid() != 0:
        print('Sorry, the R12 Shell must be run with admin privileges.')
        print('Try running with \'sudo\'.')
        return 1'''

    # Open the interactive shell.
    r12shell = shell.ArmShell(arm.Arm())
    r12shell.cmdloop()


if __name__ == '__main__':
    main()
