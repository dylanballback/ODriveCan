#This is where my package code will live. 

#Dylan's Example for reference on how to setup function with docstring format.
def hello(word):
    """
    Docstring Example description.

    Para:
        word - this will take in a string and prints "Hello" + string.
        

    Example:
        >>> import odrivecan
        >>> odrive.hello("Dylan")
        ...
        ... Hello Dylan
    """

    #First example print function. 
    print("Hello" + word)



import board 
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
    def __init__(self, nodeID, canBusID="can0", canBusType="socketcan"):
        self.canBusID = canBusID
        self.canBusType = canBusType
        self.nodeID = nodeID
        self.canBus = None  # Initialize with None




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

        # Set the Odrive to closed axis state control
        self.closed_loop_control()



    def flush_can_buffer(self):
        #Flush CAN RX buffer to ensure no old pending messages.
        while not (self.canBus.recv(timeout=0) is None): pass
        print("I have cleared all CAN Messages on the BUS!")


    
    # Put axis into closed loop control state
    def closed_loop_control(self):
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
        self.canBus.send(can.Message(
            arbitration_id=(self.nodeID << 5 | 0x0C),
            data=struct.pack('<fhh', float(position), velocity_feedforward, torque_feedforward),
            is_extended_id=False
        ))
        print(f"Successfully moved ODrive {self.nodeID} to {position}")
        


    # Function to set velocity for a specific O-Drive
    def set_velocity(self, velocity, torque_feedforward=0.0):
        self.canBus.send(can.Message(
            arbitration_id=(self.nodeID << 5 | 0x0d),  # 0x0d: Set_Input_Vel
            data=struct.pack('<ff', velocity, torque_feedforward),
            is_extended_id=False
        ))



    # Function to set torque for a specific O-Drive
    def set_torque(self, torque):
        self.canBus.send(can.Message(
            arbitration_id=(self.nodeID << 5 | 0x0E),  # 0x0E: Set_Input_Torque
            data=struct.pack('<f', torque),
            is_extended_id=False
        ))
        print(f"Successfully set ODrive {self.nodeID} to {torque} [Nm]")

#-------------------------------------- Motor Controls END-------------------------------------------------
        



#-------------------------------------- Motor Feedback with CAN RTR ----------------------------------------------------

    def send_rtr_message(self, request_id):
        try:
            # Create an RTR frame
            rtr_frame = can.Message(
                arbitration_id=(self.nodeID << 5 | request_id),
                is_remote_frame=True,
                is_extended_id=False
            )

            # Send the RTR frame
            self.canBus.send(rtr_frame)

        except Exception as e:
            print(f"Error sending RTR message to ODrive {self.nodeID}, request_id {request_id}: {str(e)}")



    def get_encoder_estimate_rtr(self):
        """
        Get Encoder Estimates for specific O-Drive Controller Axis through CAN BUS

        CAN Get_Encoder_Estimates: 0x09
                    - Pos_Estimate 
                    - Vel_Estimate

        Returns:
            Pos_Estimate
            Vel_Estimate 
        """
        request_id = 0x09
        self.send_rtr_message(request_id)

        # Wait for a response
        response = self.canBus.recv(timeout=1.0)

        if response:
            pos, vel = struct.unpack('<ff', bytes(response.data))
            #print(f"O-Drive {self.nodeID} - pos: {pos:.3f} [turns], vel: {vel:.3f} [turns/s]")
            return pos, vel
        else:
            print(f"No response received for ODrive {self.nodeID}, request_id {request_id}")



    def get_torque_rtr(self):
        """
        Get Torque Target & Estimate for specific O-Drive Controller Axis through CAN BUS with RTR bit.
        This doesn't require the cyclic message to be set up on the O-Drive Firmware.

        CAN Get_Encoder_Estimates: 0x1C
                    - Torque_Target    (Nm)
                    - Torque_Estimate  (Nm)

        Returns:
            Torque_Target
            Torque_Estimate 
        """
        request_id = 0x1C
        self.send_rtr_message(request_id)

        # Wait for a response
        response = self.canBus.recv(timeout=1.0)

        if response:
            torque_target, torque_estimate = struct.unpack('<ff', bytes(response.data))
            #print(f"O-Drive {self.nodeID} - Torque Target: {torque_target:.3f} [Nm], Torque Estimate: {torque_estimate:.3f} [Nm]")
            return torque_target, torque_estimate
        else:
            print(f"No response received for ODrive {self.nodeID}, request_id {request_id}")



    def get_bus_voltage_current_rtr(self):
        """
        Get Bus Voltage & Current for specific O-Drive Controller Axis through CAN BUS with RTR bit.
        This doesn't require the cyclic message to be set up on the O-Drive Firmware.

        CAN Get_Encoder_Estimates: 0x17
                    - Bus_Voltage    (V)
                    - Bus_Current    (Amps)

        Returns:
            Torque_Target 
            Torque_Estimate 
        """
        request_id = 0x17
        self.send_rtr_message(request_id)

        # Wait for a response
        response = self.canBus.recv(timeout=1.0)

        if response:
            bus_voltage, bus_current = struct.unpack('<ff', bytes(response.data))
            #print(f"O-Drive {self.nodeID} - Bus Voltage: {bus_voltage:.3f} [V], Bus Current: {bus_current:.3f} [A]")
            return bus_voltage, bus_current
        else:
            print(f"No response received for ODrive {self.nodeID}, request_id {request_id}")



    def get_iq_setpoint_measured_rtr(self):
        """
        Get Iq Setpoint & Measured for specific O-Drive Controller Axis through CAN BUS with RTR bit.
        This doesn't require the cyclic message to be set up on the O-Drive Firmware.

        CAN Get_Encoder_Estimates: 0x1C
                    - Iq_Setpoint    (Amps)
                    - Iq_Measured    (Amps)

        Returns:
            Torque_Target
            Torque_Estimate 
        """
        request_id = 0x14
        self.send_rtr_message(request_id)

        # Wait for a response
        response = self.canBus.recv(timeout=1.0)

        if response:
            iq_setpoint, iq_measured = struct.unpack('<ff', bytes(response.data))
            #print(f"O-Drive {self.nodeID} - Iq Setpoint: {iq_setpoint:.3f} [A], Iq Measured: {iq_measured:.3f} [A]")
            return iq_setpoint, iq_measured
        else:
            print(f"No response received for ODrive {self.nodeID}, request_id {request_id}")


    
    def get_all_data_rtr(self):
        # Collect data from each function
        encoder_data = self.get_encoder_estimate_rtr()
        torque_data = self.get_torque_rtr()
        voltage_current_data = self.get_bus_voltage_current_rtr()
        iq_setpoint_measured_data = self.get_iq_setpoint_measured_rtr()

        # Format each value to 3 decimal places if they are numeric
        def format_data(data):
            if isinstance(data, tuple):
                return tuple(format(x, '.3f') if isinstance(x, (int, float)) else x for x in data)
            return data

        encoder_data_formatted = format_data(encoder_data)
        torque_data_formatted = format_data(torque_data)
        voltage_current_data_formatted = format_data(voltage_current_data)
        iq_setpoint_measured_data_formatted = format_data(iq_setpoint_measured_data)

        # Print formatted data
        print("Data: {}, {},  {}, {}"
            .format(encoder_data_formatted, torque_data_formatted, voltage_current_data_formatted, iq_setpoint_measured_data_formatted))

        # Compile all data into a single structure (dictionary for better readability)
        all_data = {
            "encoder_data": encoder_data,
            "torque_data": torque_data,
            "voltage_current_data": voltage_current_data,
            "iq_setpoint_measured_data": iq_setpoint_measured_data
        }

        # Format and print all data in one line not limiting how many decimal places printed.
        #print("Data: {}, {}, {}, {}".format(encoder_data, torque_data, voltage_current_data, iq_setpoint_measured_data))

        return all_data

    """
    2/7/24

     I want to create a method/function that will take all the data from the 'get_all_data_rtr()' and then put it into a sqlite database.
    
     How can I make it so that I can collect this data and add it to a database but it won't interfere if I also want to be sending motor
     commands at different time intervals?

     Is that something I can build into the package and make it automatically handle itself or is it more based on use case? 
    """

