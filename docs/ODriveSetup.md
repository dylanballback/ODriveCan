# ODriveCan

!!! Info This is a tutorial page on how to configure your O-Drive S1 or Pro in order to use this package. 
    If this is your first time using your O-Drive, I strongly recommend to see the [O-Drive Documentation](https://docs.odriverobotics.com/v/latest/guides/getting-started.html)  
    and start with their tutorial and using the web GUI to get your motor spinning for the first time.

  
    In this example I will be using a Raspberry Pi 2 Zero W with the WaveShare RS485 CAN HAT.


!!! Tip 
    If you have not already set up your Raspberry Pi with the [WaveShare RS485 CAN HAT](https://www.amazon.com/RS485-CAN-HAT-Long-Distance-Communication/dp/B07VMB1ZKH/ref=sr_1_3?crid=1DIYQ9H0DCFZX&keywords=waveshare+RS485+CAN+HAT&qid=1707694015&s=electronics&sprefix=waveshare+rs485+can+hat+%2Celectronics%2C97&sr=1-3), please visit this page here to see how to do so: [Raspberry Pi CAN Hat Setup](./piCANHatSetup.md)

&nbsp;

## O-Drive GUI Configuration 

!!! warning O-Drive Firmware >= v0.6.9 to use the pyodrivecan package.
     
    You can check your O-Drive Firmware when connected to the GUI on the bottom left corner:
    <img src="media/odrivesetup/odrive_versionv0.6.9_annotated.png" alt="O-Drive Version >= v0.6.9" style="width: 60%; margin-left: 0%;">
    

&nbsp;

### 1. Power Source


![Power Source Configuration](media/odrivesetup/POWER_SOURCE_Configuration_ANNOTATED.png)

&nbsp;
### 2. Motor 


![Motor Configuration](media/odrivesetup/MOTOR_Configuration_ANNOTATED.png)

&nbsp;
### 3. Encoder 

![Encoder Configuration](media/odrivesetup/ENCODER_Configuration_ANNOTATED.png)


&nbsp;
### 4. Control mode

![Control Mode Configuration](media/odrivesetup/CONTROL_MODE_Configuration_ANNOTATED.png)


&nbsp;
### 5. Interfaces 


<img src="media/odrivesetup/INTERFACES_Configuration_ANNOTATED.png" alt="CAN Inerface Configuration" style="margin-left: 20px;">



&nbsp;
### 6. Apply and Calibrate 

!!! warning
    If you have your O-Drive powered by a power supply/battery and want to plug in the USB, you need to have a USB Isolator, 
    ![DC_Undervoltage_warning](media/odrivesetup/APPLY&CALIBRATE_Configuration_noDCBusVoltage_Error_ANNOTATED.png)

!!!  success
    ![O-Drive Version >= v0.6.9](media/odrivesetup/APPLY&CALIBRATE_COMPLETED_Configuration_ANNOTATED.png)




&nbsp;
#### 7. Set `powers_msg_rate_ms` in Inspector Tab


![Set powers_msg_rate_set to 10 ms](media/odrivesetup/INSPECTOR_pwrs_msg_rate_set_ANNOTATED_pt1.png)

!!!  success
    ![Save powers_msg_rate_set configuration](media/odrivesetup/INSPECTOR_save_configuration_ANNOTATED.png)

#### Congratulations 