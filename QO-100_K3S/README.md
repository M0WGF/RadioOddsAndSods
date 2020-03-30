# K3S CAT QO-100 offset Display 

Additional libraries needed are pyqt5 and pyserial.

Edit the config.ini using Vi or Wordpad and set the following:

LO = 432000000   # The frequency that the K3s shows

PORT = COM10 # The serial port

BAUD = 38400

POLL = 0.01 # Polling interval 0.01 should be quite fast enough. 