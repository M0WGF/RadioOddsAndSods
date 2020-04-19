# K3S or FT817 CAT QO-100 offset Display 

I originally wrote this of the K3s however I then expanded the software later 
to also allow it to work with the Yaesu FT817 series of radios.

Additional libraries needed are pyqt5 and pyserial.

Edit the config.ini using Vi or Wordpad and set the following:

LO = 432000000 # The frequency that the K3s shows.

PORT = COM10 # The serial port.

BAUD = 38400 # Baud rate.

POLL = 0.01 # Polling interval 0.01 should be quite fast enough. 

RIG = K3S # Set rig type to either K3S or FT817.