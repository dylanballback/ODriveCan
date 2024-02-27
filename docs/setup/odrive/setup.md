# ODriveCan

This is a tutorial page on how to configure your O-Drive S1 or Pro in order to use this package. If this is your first time using your O-Drive, I strongly recommend to see the [O-Drive Documentation](https://docs.odriverobotics.com/v/latest/guides/getting-started.html) and start with their tutorial and using the web GUI to get your motor spinning for the first time.

In this example I will be using a Raspberry Pi 2 Zero W with the WaveShare RS485 CAN HAT.

!!! Tip 
    If you have not already set up your Raspberry Pi with the WaveShare RS485 CAN HAT, please visit this page: [Raspberry Pi CAN Hat Setup](./piCANHatSetup.md)

## O-Drive GUI configuration 

??? warning "O-Drive Firmware >= v0.6.9 to use the pyodrivecan package."
     
    You can check your O-Drive Firmware when connected to the GUI on the bottom left corner:
    ![O-Drive Version >= v0.6.9](images/10.png)

### 1. Power source
![Power Source Configuration](images/01.png)

### 2. Motor 
![Motor Configuration](images/02.png)

### 3. Encoder 
![Encoder Configuration](images/03.png)

### 4. Control mode
![Control Mode Configuration](images/04.png)

### 5. Interfaces 
![CAN Interface Configuration](images/05.png)

### 6. Apply and calibrate 

??? warning "If you have your O-Drive powered by a power supply/battery and want to plug in the USB, you need to have a [USB Isolator](https://odriverobotics.com/shop/usb-isolator)."

    ![DC_Undervoltage_warning](images/06.png)


!!! success

    ![O-Drive Version >= v0.6.9](images/07.png)


### 7. Powers message rate
Set `powers_msg_rate_ms` in Inspector Tab
![Set powers_msg_rate_set to 10 ms](images/08.png)


### Congratulations 
!!! success

    ![Save powers_msg_rate_set configuration](images/09.png)