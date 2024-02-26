import pyodrivecan
import asyncio

async def controller(odrive):
        odrive.set_torque(0.1)  #Set torque to 0.1 Nm 
        await asyncio.sleep(15) # Need this line in order for the async functions to work. 
        odrive.set_torque(0)    # Set torque to 0 Nm

        # Set running flag to False to stop collecting and storing O-Drive to database.
        odrive.running = False  
        

if __name__ == "__main__":
    # Create ODriveCAN object with a node_id = 0 
    odrive = pyodrivecan.ODriveCAN(0)
    
    # Initialize the odrive object 
    odrive.initCanBus()

    #Set O-Drive to torque control
    odrive.set_controller_mode("torque_control")

    # This will use the run method to pass in the async controller function
    #and automatically run the odrive 
    odrive.run(controller(odrive))
