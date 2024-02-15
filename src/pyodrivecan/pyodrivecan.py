from .odrivedatabase import OdriveDatabase
import asyncio
import can
import struct
import time


class ODriveCAN:
    """
    A class for setting up O-Drive motor controllers using CAN comunincation with python on a raspberry pi with the waveshare RS485 CAN HAT.

    Attributes:
        Specifically for setting up CAN comunication between Raspberry Pi and CAN Communication Type:
            canBusID (String): Can Bus ID should be default "can0" but if you have muilitiple can buses on your device you can modify here

            canBusType (String): python-can package CAN communication type we by default us "socketcan"

        O-Drive Controller Specific Attributes:
        nodeID (integer): The node ID can be set by the 
    """
    def __init__(
            self,
            nodeID,
            canBusID="can0",
            canBusType="socketcan",
            closed_loop_control_flag = True,
            position=None,
            velocity=None,
            torque_target=None,
            torque_estimate=None,
            bus_voltage=None,
            bus_current=None,
            iq_setpoint=None,
            iq_measured=None,
            electrical_power=None,
            mechanical_power=None,
            database='odrive_data.db'):
    
        self.canBusID = canBusID
        self.canBusType = canBusType
        self.nodeID = nodeID
        self.closed_loop_control_flag = closed_loop_control_flag #Default to TRUE closed loop control set in init function.
        self.canBus = can.interface.Bus(canBusID, bustype=canBusType)
        self.database = OdriveDatabase(database)
        self.collected_data = []  # Initialize an empty list to store data
        self.start_time = time.time()  # Capture the start time when the object is initialized
        self.latest_data = {}
        self.running = True
        #O-Drive Data
        self.position = position
        self.velocity = velocity
        self.torque_target = torque_target
        self.torque_estimate = torque_estimate
        self.bus_voltage = bus_voltage
        self.bus_current = bus_current
        self.iq_setpoint = iq_setpoint
        self.iq_measured = iq_measured
        self.electrical_power = electrical_power
        self.mechanical_power = mechanical_power

    def initCanBus(self):
        """
        Initalize connection to CAN Bus

        canBusID (String): Default "can0" this is the name of the can interface
        canBus (String): Default "socketcan" this is the python can libary CAN type
        """
         # Create and assign the CAN bus interface object to self.canBus
        self.canBus = can.interface.Bus(self.canBusID, bustype=self.canBusType)

        # Flush the CAN Bus of any previous messages
        self.flush_can_buffer()
        if self.closed_loop_control_flag:
            # Set the Odrive to closed axis state control
            self.closed_loop_control()



    def flush_can_buffer(self):
        """
        Flushes the CAN receive buffer to clear any pending messages.

        Example:
            >>> odrive_can.flush_can_buffer()
        """
        #Flush CAN RX buffer to ensure no old pending messages.
        while not (self.canBus.recv(timeout=0) is None): pass
        print("I have cleared all CAN Messages on the BUS!")


    
    # Put axis into closed loop control state
    def closed_loop_control(self):
        """
        Sets the ODrive controller to closed-loop control mode.

        Example:
            >>> odrive_can.closed_loop_control()
            ...
            ... Successfully set control state to ODrive #NodeID.
        """

        self.flush_can_buffer()
        print(f"Attempting to set control state to ODrive {self.nodeID}...")
        try:
            self.canBus.send(can.Message(
                arbitration_id=(self.nodeID << 5 | 0x07), # 0x07: Set_Axis_State
                data=struct.pack('<I', 8), # 8: AxisState.CLOSED_LOOP_CONTROL
                is_extended_id=False
            ))
            
            print(f"Checking Hearbeat for ODrive {self.nodeID}")
            # Wait for axis to enter closed loop control by scanning heartbeat messages
            for msg in self.canBus:
                if msg.arbitration_id == (self.nodeID << 5 | 0x01): # 0x01: Heartbeat
                    error, state, result, traj_done = struct.unpack('<IBBB', bytes(msg.data[:7]))
                    if state == 8: # 8: AxisState.CLOSED_LOOP_CONTROL
                        break
            print(f"Successfully set control state to ODrive {self.nodeID}")

        except Exception as e:
            print(f"Error connecting to ODrive {self.nodeID}: {str(e)}")



    #Shutdown can bus at the end of a program. 
    def bus_shutdown(self):
        """
        Run this method at the end of your program to shundown the can bus to prevent can errors.

        Example:
        >>> import pyodrivecan
        >>> odrivecan.bus_shutdown()
        ...
        ... Can bus successfully shut down.
        """

        self.canBus.shutdown

        print("Can bus successfully shut down.")

    

#-------------------------------------- Motor Controls START------------------------------------------------
    # Function to set position for a specific O-Drive
    def set_position(self, position, velocity_feedforward=0, torque_feedforward=0):
        """
        Sets the position of the ODrive motor.

        Para:
            position (float): Target position for the motor.
            velocity_feedforward (float): Feedforward velocity, default is 0.
            torque_feedforward (float): Feedforward torque, default is 0.

        Example:
            >>> odrive_can.set_position(1000.0)
        """

        self.canBus.send(can.Message(
            arbitration_id=(self.nodeID << 5 | 0x0C),
            data=struct.pack('<fhh', float(position), velocity_feedforward, torque_feedforward),
            is_extended_id=False
        ))
        #print(f"Successfully moved ODrive {self.nodeID} to {position}")
        

    # Function to set velocity for a specific O-Drive
    def set_velocity(self, velocity, torque_feedforward=0.0):
        """
        Sets the velocity of the ODrive motor.

        Para:
            velocity (float): Target velocity for the motor.
            torque_feedforward (float): Feedforward torque, default is 0.

        Example:
            >>> odrive_can.set_velocity(500.0)
        """

        self.canBus.send(can.Message(
            arbitration_id=(self.nodeID << 5 | 0x0d),  # 0x0d: Set_Input_Vel
            data=struct.pack('<ff', velocity, torque_feedforward),
            is_extended_id=False
        ))


    # Function to set torque for a specific O-Drive
    def set_torque(self, torque):
        """
        Sets the torque of the ODrive motor.

        Para:
            torque (float): Target torque for the motor.

        Example:
            >>> odrive_can.set_torque(10.0)
        """
        
        self.canBus.send(can.Message(
            arbitration_id=(self.nodeID << 5 | 0x0E),  # 0x0E: Set_Input_Torque
            data=struct.pack('<f', torque),
            is_extended_id=False
        ))
        #print(f"Successfully set ODrive {self.nodeID} to {torque} [Nm]")
#-------------------------------------- Motor Controls END-------------------------------------------------



#-------------------------------------- Motor Feedback ----------------------------------------------------
# In order for these functions to work you need to have the O-Drive set with the Cyclic messages 
# The cyclic messgaes for CAN will make the O-Drive automatically send the data you want to collect at the set rate.



    def process_can_message(self, message):
        """
        Processes received CAN messages and updates the latest data.
        """
        
        arbitration_id = message.arbitration_id
        data = message.data
        if arbitration_id == (self.nodeID << 5 | 0x09):  # Encoder estimate
            position, velocity = struct.unpack('<ff', data)
            self.position = position
            self.velocity = velocity
            #print(f"Encoder Estimate - Position: {position:.3f} turns, Velocity: {velocity:.3f} turns/s")
        elif arbitration_id == (self.nodeID << 5 | 0x1C):  # Torque
            torque_target, torque_estimate = struct.unpack('<ff', data)
            self.torque_target = torque_target
            self.torque_estimate = torque_estimate
            #print(f"Torque - Target: {torque_target:.3f} Nm, Estimate: {torque_estimate:.3f} Nm")
        elif arbitration_id == (self.nodeID << 5 | 0x17):  # Bus voltage and current
            bus_voltage, bus_current = struct.unpack('<ff', data)
            self.bus_voltage = bus_voltage
            self.bus_current = bus_current
            #print(f"Bus Voltage and Current - Voltage: {bus_voltage:.3f} V, Current: {bus_current:.3f} A")
        elif arbitration_id == (self.nodeID << 5 | 0x14):  # IQ setpoint and measured
            iq_setpoint, iq_measured = struct.unpack('<ff', data)
            self.iq_setpoint = iq_setpoint
            self.iq_measured = iq_measured
            #print(f"IQ Setpoint and Measured - Setpoint: {iq_setpoint:.3f} A, Measured: {iq_measured:.3f} A")
        elif arbitration_id == (self.nodeID << 5 | 0x1D):  # Powers
            electrical_power, mechanical_power = struct.unpack('<ff', data)
            self.electrical_power = electrical_power
            self.mechanical_power = mechanical_power
            #print(f"Powers - Electrical: {electrical_power:.3f} W, Mechanical: {mechanical_power:.3f} W")

    #This is aysnc receiving the messages from the can bus and feeding them into the process_can_message method.
    async def recv_all(self):
        while self.running:
            await asyncio.sleep(0)
            msg = self.canBus.recv(timeout=0)
            if msg is not None:
                self.process_can_message(msg)

    
    #This is aysnc saving the data to a database at a set rate (timeout=0.1) every 0.1 seconds.
    async def save_data(self, timeout=0.1):
        # Fetch the next trial_id
        next_trial_id = self.database.get_next_trial_id()
        print(f"Using trial_id: {next_trial_id}")
        node_id = self.nodeID
        while self.running:
            await asyncio.sleep(timeout)
            # Calculate elapsed time since the start of the program
            current_time = time.time() - self.start_time
            self.database.add_odrive_data(
                next_trial_id,
                node_id,
                current_time,
                self.position,
                self.velocity,
                self.torque_target,
                self.torque_estimate,
                self.bus_voltage,
                self.bus_current,
                self.iq_setpoint,
                self.iq_measured,
                self.electrical_power,
                self.mechanical_power
            )

    async def get_velocity(self):
        """
        This function makes sure that the returned velocity is not 'None'
        """
        while self.running and self.velocity is None:
            await asyncio.sleep(0)
        return self.velocity

    #This is the async loop that runs the receve_msgs and save_data methods async.
    async def loop(self, *others):
        await asyncio.gather(
            self.recv_all(),
            self.save_data(),
            *others,
        )

    def run(self, *others):
        asyncio.run(self.loop(*others))
