import pyodrivecan
import asyncio
import math
from datetime import datetime, timedelta


mass = 0.12  # Kg weights = 0.090
length = 0.11  # Meters

async def controller(odrive):
    await asyncio.sleep(1)

    #Run for set time delay example runs for 15 seconds.
    stop_at = datetime.now() + timedelta(seconds=10000)
    while datetime.now() < stop_at:
        current_position_rev = odrive.position

        # Normalize to 0-1 range for a single revolution
        normalized_position = current_position_rev % 1

        # Convert normalized position to radians (0 to 2pi)
        current_position_rad = normalized_position * 2 * math.pi

        # Calculate next torque
        next_torque = math.sin(current_position_rad) * mass * length * 9.8

        # Limit next_torque to between -0.129 and 0.129
        next_torque = max(-0.2, min(0.2, next_torque))
        
        # Set the calculated torque
        odrive.set_torque(next_torque) 
        print(f"Normalized position {normalized_position} (revs), Current Position {current_position_rad} (rad), Torque Set to {next_torque} (Nm)")

        await asyncio.sleep(0.0015)  # 15ms sleep, adjust based on your control loop requirements


#Set up Node_ID 10 ACTIV NODE ID = 10
odrive = pyodrivecan.ODriveCAN(0)

# Run multiple busses.
async def main():
    odrive.clear_errors(identify=False)
    print("Cleared Errors")
    await asyncio.sleep(1)

    #Initalize odrive
    odrive.initCanBus()

    
    print("Put Arm at bottom center to calibrate Zero Position.")
    await asyncio.sleep(1)
    odrive.set_absolute_position(position=0)
    await asyncio.sleep(1)
    current_position = odrive.position
    print(f"Encoder Absolute Position Set: {current_position}")

    #odrive.setAxisState("closed_loop_control")

    #add each odrive to the async loop so they will run.
    await asyncio.gather(
        odrive.loop(),
        controller(odrive) 
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("KeyboardInterrupt caught, stopping...")
        odrive.estop()
        
