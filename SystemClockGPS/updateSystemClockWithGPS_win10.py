""" Module for Setting the system clock for Windows 10 based on GPS.

      Used setup: - Adafruit 's Ultimate GPS Breakout Board
                  - USB to TTL Serial Cable
                  - Laptop that runs Windows 10

"""

import serial
import time
import sys
import threading
import datetime
import win32api


def autodetect_serial_gps_device():
    """ Auto detecting the COM port of GPS module

     Configuring the COM port of GPS module automtically by looking all possible COM port
    number with valid GPS messages. COM port is running at 9600.

    :param none: No parameter is required.
    """

    print("Searching for serial GPS device...")

    global sPort, baudrate, found
    found = 0
    temp = 0
    try_attempt = 100
    baudrate = 9600

    for i in range(256):
        try:
            sPort = serial.Serial()
            portNo = int(i)  # this refers to which port your usb is inserted into
            sPort.port = "COM{}".format(portNo)
            sPort.timeout = 10
            sPort.baudrate = baudrate
            sPort.open()
            while try_attempt:
                line = sPort.readline()
                line_str = str(line)
                try_attempt -= 1
                # if (line_str[5] == 'G'):  # $GPGGA
                if ('$GPRMC' in line_str):
                    found = 1
                    temp = i
                    break
            sPort.close()
        except serial.SerialException:
            pass

    comnum = 'COM' + str(temp)  # concatenate COM and the port number to define serial port

    # configure the serial connections
    sPort = serial.Serial()
    sPort.baudrate = baudrate
    sPort.port = comnum
    sPort.timeout = 1

    if (found):
        print('GPS device found and opening port ' + sPort.name)
        sPort.open()
        sPort.isOpen()
        print('Creating background process for Listening...')
        thread()
    else:
        print('No Serial GPS device is connected...')
        print('Please connect GPS device and retry...')
        exit()

def background_process():
    """ Background process for listening  the GPS module.

     This process looks for the GPRMC sentence to extract date and time info and evaluate
    the valdity of GPS signal.

    :param none: No parameter is required.
    """

    # Filters $GPRMC sentence and extract date and time info in background
    global newDateTime, valid
    while 1:
        line = sPort.readline()
        line_str = str(line)
        #if (line_str[5] == 'G'):  # $GPGGA
        if ('$GPRMC' in line_str):
            time_utc = int(float(line_str.split(',')[1]))
            valid = (line_str.split(',')[2] == 'A')

            #print('Time is: ', time)
            if time_utc is not None:
                hours = time_utc // 10000
                mins = (time_utc // 100) % 100
                secs = time_utc % 100
                mSec = int((line_str.split(',')[1]).split('.')[1])
                #print('HH: ' + str(hours) + ' MM: ' + str(mins) + ' SS: ' + str(secs))

            date = (line_str.split(',')[9])
            #print('Date is: ', date)
            if date is not None:
                dd = int(date[0:2])
                mm = int(date[2:4])
                yy = 2000 + int(date[4:6])
                #print('DD: ' + str(dd) + ' MM: ' + str(mm) + ' YYYY: ' + str(yy))

            newDateTime = datetime.datetime(yy, mm, dd, hours, mins, secs,(mSec *1000))#,tzinfo=pytz.UTC)

def thread():
    """ Wrapup function of background process.

    :param none: No parameter is required.
    """
    # threads - run idependent of main loop
    thread1 = threading.Thread(target=background_process)  # Read the GPS and filtering $GPRMC sentence
    thread1.start()


if __name__ == '__main__':
    """Our Application code to set the system clock for Windows 10 based on GPS module

    As this is a headless application and uses win32 api, execute the following command "python updateSystemClockWithGPS_win10.py" with admin privilege.
    
    Procedure of the application:
    
     1. Detect the connected COM port of the GPS module as follows:
     
      1.1. Assign port number as 1 to 255 and look for incoming valid GPS NMEA sentences especially $GPRMC which holds time and date info.
      
       1.1.1. If it matches close the current port by remembering that COM port number.
      
        1.1.1.1. Create a backgroung process that listens in the detected port.
        
       1.1.2. If it does not match with any of the number from 1 to 255, then end the program with user prompt message.

     2. Background process is responsibe for extracting the timer and info GPS NMEA.
     
       2.1. Read the serial port line by line.
       
       2.2. Filter out the NMEA sentence of $GPRMC.
       
       2.3. Extract the date and time info and store it in global variable.
       
    3. Setting the system clock with win32api SetSystemTime funtion.
    
       3.1. Look for validity of GPS data and if so then only set the time.


    :param args: No input arguments.
    """

    """ Entry point """
    print('!!!!!! System Clock update with GPS Data  !!!!!!!')
    print('Checking for port availability')

    autodetect_serial_gps_device()

    while 1:
        time.sleep(10)
        if (valid == True):
            print('Synchronizing time ' + str(newDateTime.hour) + ':' + str(newDateTime.minute) + ':' + str(newDateTime.second) + '-' + str(int(newDateTime.microsecond/1000))+ ' with GPS data...')
            win32api.SetSystemTime(newDateTime.year, newDateTime.month, newDateTime.weekday(), newDateTime.day,
                               newDateTime.hour, newDateTime.minute, newDateTime.second, int(newDateTime.microsecond/1000))
        else:
            print('GPS data is invalid...')

    sPort.close()
