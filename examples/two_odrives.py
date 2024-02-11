import pyodrivecan
import asyncio
from datetime import datetime, timedelta


#Functions to clamp a variables upper and lower limit.        
def clamp(x, lower, upper):
    return lower if x < lower else upper if x > upper else x


#Example of how you can create a controller to get data from the O-Drives and then send motor comands based on that data.
async def controller(odrive1, odrive2):
        odrive1.set_torque(0)
        odrive2.set_torque(0)

        #Run for set time delay example runs for 15 seconds.
        stop_at = datetime.now() + timedelta(seconds=15)
        while datetime.now() < stop_at:
            await asyncio.sleep(0) #Need this for async to work.
            
            x1 = await odrive1.get_velocity() - 9.5 
            #print(x1)
            clamp(x1, 0, 0.2) #Currently my motor is limited to 0 - 0.2 Nm
            odrive1.set_torque(x1)

            x2 = await odrive2.get_velocity() - 9.5
            #print(x2)
            clamp(x2, 0, 0.2) #Currently my motor is limited to 0 - 0.2 Nm
            odrive2.set_torque(x2)
            print(x1, x2)

        #await asyncio.sleep(15) #no longer need this the timedelta =15 runs the program for 15 seconds.
        odrive1.running = False
        odrive2.running = False



# Run multiple busses.
async def main():
    #Set up Node_ID 0
    odrive1 = pyodrivecan.ODriveCAN(0)
    odrive1.initCanBus()
    
    #Set up Node_ID 1 
    odrive2 = pyodrivecan.ODriveCAN(1)
    odrive2.initCanBus()
    
    #Set up Node_ID 2 
    #odrive3 = ODriveCAN(2)
    #odrive3.initCanBus()

    #add each odrive to the async loop so they will run.
    await asyncio.gather(
        odrive1.loop(),
        odrive2.loop(),
        #odrive3.loop(),
        controller(odrive1, odrive2) 
    )

if __name__ == "__main__":
    asyncio.run(main())

    