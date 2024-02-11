import pyodrivecan
import asyncio

async def controller(odrive):
        odrive.set_torque(0.2)
        await asyncio.sleep(15)
        odrive.running = False
        

if __name__ == "__main__":
    # Initialize ODriveCAN to node_id 0 
    odrive = pyodrivecan.ODriveCAN(0)
    odrive.initCanBus()
    odrive.run(controller(odrive))

    