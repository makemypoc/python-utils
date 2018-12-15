## Module for Setting the system clock for Windows 10 based on GPS.

  This module is to set the system clock of Windows 10 based on extracted time and date information from NMEA sentence of GPS module. This script has to be run with admin privilege as it calls the win32 api. 

### Dependencies:
     - pyserial
     - pywin32

  These are the dependencies for this particular module.

### Used setup: 
    - Adafruit 's Ultimate GPS Breakout Board
    - USB to TTL Serial Cable
    - Laptop that runs Windows 10
    
### How to use it?

  Open the command window with admin privilege and execute the following command `python updateSystemClockWithGPS.py`.
    
    
### Procedure of the application:
    
     1. Detect the connected COM port of the GPS module as follows:
     
      1.1. Assign port number as 1 to 255 and look for incoming valid GPS NMEA sentences especially $GPRMC which holds 
      time and date info.
      
       1.1.1. If it matches close the current port by remembering that COM port number.
      
        1.1.1.1. Create a backgroung process that listens in the detected port.
        
       1.1.2. If it does not match with any of the number from 1 to 255, then end the program with user prompt message.

     2. Background process is responsibe for extracting the timer and info GPS NMEA.
     
       2.1. Read the serial port line by line.
       
       2.2. Filter out the NMEA sentence of $GPRMC.
       
       2.3. Extract the date and time info and store it in global variable.
       
    3. Setting the system clock with win32api SetSystemTime funtion.
    
       3.1. Look for validity of GPS data and if so then only set the time.
