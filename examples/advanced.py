import pyodrivecan
import asyncio


# Create an instance of the ODriveCAN class (by default axis_state_name is closed_loop_control)
odrive = pyodrivecan.ODriveCAN(nodeID=0x01)

# Initialize CAN bus
odrive.initCanBus()

#Set O-Drive to position control
odrive.set_controller_mode("position_control")

# Set motor to a specific position
odrive.set_position(100.0)

#Set O-Drive to velocity control
odrive.set_controller_mode("velocity_control")

# Set motor velocity
odrive.set_velocity(1.0)

#Set O-Drive to torque control
odrive.set_controller_mode("torque_control")

# Set motor torque
odrive.set_torque(0.1)

# Issue an emergency stop command
odrive.estop()

# Clear errors on the O-Drive
odrive.clear_errors()

# Set the motor to an absolute position for the new default encoder "zero" postion to the current position.
odrive.set_absolute_position()

# Start the asynchronous event loop
odrive.run()