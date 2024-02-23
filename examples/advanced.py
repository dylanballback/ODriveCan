import pyodrivecan
import asyncio
from datetime import datetime, timedelta

"""
This is an example on how to use some of the methods inside the pyodrivecan class.
    
    Define an object of the class with its nodeID and initalize it:
    - pyodrivecan.ODriveCAN(#nodeID)
    - initCanBus()

    - set_controller_mode()
        - position
        - velocity
        - torque 

    - set_position()    
    - set_velocity()
    - set_torque()

    If keyboard inturrenpt the O-Drive will use the E-Stop method:
    - estop()

    At the start of the program it will use the Clear Errors method to ensure their is no remaining error like from the E-Stop. 
    - clear_errors()

"""


#Example of how you can create a controller to get data from the O-Drives and then send motor comands based on that data.
async def controller(odrive):

        #Run for set time delay example runs for 15 seconds.
        stop_at = datetime.now() + timedelta(seconds=15)
        while datetime.now() < stop_at:
            await asyncio.sleep(0) #Need this for async to work.
            #Set O-Drive to position control
            odrive.set_controller_mode("position_control")
            print("Set O-Drive to Position Control.")
            await asyncio.sleep(3) #Wait 1 second
            
            # Set motor to a specific position
            position = 20
            odrive.set_position(position)
            print(f"Set position to {position} (revs) on {odrive.nodeID}")
            await asyncio.sleep(3) #Wait 1 second            
            
            #Set O-Drive to velocity control
            odrive.set_controller_mode("velocity_control")
            print("Set O-Drive to Velocity Control.")
            await asyncio.sleep(3) #Wait 1 second

            # Set motor velocity
            velocity = 1.0
            odrive.set_velocity(velocity)
            print(f"Set velocity to {velocity} (rev/s) on {odrive.nodeID}")
            await asyncio.sleep(3) #Wait 1 second 

            #Set O-Drive to torque control
            odrive.set_controller_mode("torque_control")
            print("Set O-Drive to Torque Control.")
            await asyncio.sleep(1) #Wait 1 second

            # Set motor torque
            torque = 0.1
            odrive.set_torque(torque)
            print(f"Set torque to {torque} (Nm) on {odrive.nodeID}")
            await asyncio.sleep(1) #Wait 1 second 

        #Test if we can set axis state to idle.
        odrive.setAxisState("idle")
        await asyncio.sleep(1)#Wait 1 second
        print("O-Drive Axis State set to idle.")
        odrive.running = False  # Stop the loop after the timedelta.



# Run multiple busses.
async def main():
    # Create an instance of the ODriveCAN class with Node_ID 10(by default axis_state_name is closed_loop_control)
    odrive = pyodrivecan.ODriveCAN(10)
    try:
        # Initialize CAN bus
        odrive.initCanBus()
        
        # Clear errors on the O-Drive
        odrive.clear_errors()
        print("Cleared errors on ODrive, waiting for 3 seconds...")
        await asyncio.sleep(3)  # Wait 3 seconds to ensure errors are cleared

        # Add the ODrive to the async loop and run the controller
        await asyncio.gather(
            odrive.loop(),
            controller(odrive)
        )

    except KeyboardInterrupt:
        # Trigger an emergency stop on keyboard interrupt
        print("Keyboard interrupt received, sending e-stop...")
        odrive.estop()
        await asyncio.sleep(1)  # Give some time for e-stop command to be processed
        odrive.running = False  # Stop the loop
        odrive.bus_shutdown()  # Shutdown the bus properly
        print("ODrive emergency stop has been issued.")
    finally:
        # This will run whether there was an exception or not           
        odrive.running = False  # Stop the loop
        odrive.bus_shutdown()  # Shutdown the bus properly
        print("Program has been stopped.")



if __name__ == "__main__":
    asyncio.run(main())