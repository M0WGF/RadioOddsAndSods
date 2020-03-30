import sys
import time
import serial
from re import sub
import configparser
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QApplication
from widget import Ui_Form


class getK3sVFO(QThread):

    # Emit current K3s VFO frequency.
    hertz = pyqtSignal(object)
    # Emit serial port disconnect.
    k3sDisconnect = pyqtSignal()

    def __init__(self):
        QThread.__init__(self)

        # Initiate the config parser.
        config = configparser.RawConfigParser()

        try:
            # Open and read the config.ini file.
            config.read('config.ini')
            # Get the configuration from the ini file.
            self.lo = int(config.get('CONFIG', 'LO'))
            port = config.get('CONFIG', 'PORT')
            baud = int(config.get('CONFIG', 'BAUD'))
            self.poll = float(config.get('CONFIG', 'POLL'))
        except configparser.NoSectionError:  # If the file or configuration is missing set some defaults.
            print('Error Config Missing - See http://m0wgf.blogspot.com')
            self.lo = 432000000
            port = 'COM1'
            baud = 38400
            self.poll = 0.01

        # TODO remove pause it's just for testing.
        self.pause = False

        # Initiate the serial port.
        self.k3s_port = serial.Serial()

        # Set the baud rate.
        self.k3s_port.baudrate = baud

        # Set the serial port.
        self.k3s_port.port = port

    def run(self):

        # This section will house the serial port connection and get the current VFO reading from the K3s.

        while True:

            try:
                if self.k3s_port.is_open:
                    self.k3s_port.write(b'FA;')  # Get VFO frequency from radio

                    data = self.k3s_port.read(14)  # Reads 14 Bytes which is the max number of bytes the radio should respond with.
                    data = data.decode('ascii')  # Decode bytes to ascii
                    result = sub('[^0-9]', '', data)  # strip all characters unless it's numeric

                    # Emit the vfo reading.
                    self.hertz.emit(int(result))

                    # Sleep for time stated by poll.
                    time.sleep(self.poll)
                else:
                    self.k3sDisconnect.emit()
            except Exception:
                self.k3sDisconnect.emit()

    def connect(self):
        try:
            self.k3s_port.open()
        except Exception:
            self.k3sDisconnect.emit()


class QO100uplinkVFO(QWidget, Ui_Form):
    def __init__(self):
        super(QO100uplinkVFO, self).__init__()

        # Setup the Ui_Form display.
        self.setupUi(self)

        # Set the window title.
        self.setWindowTitle('K3s, QO100 (Uplink, Downlink) VFO Display')

        # Initiate the k3s_vfo class
        self.k3s_vfo = getK3sVFO()

        # Connect the connect button to the k3s_vfo class serial port connect function.
        self.connectButton.clicked.connect(self.k3s_vfo.connect)

        # Define the uplink and downlink IF's using the LO parameter from the k3s_vfo class.
        self.uplink_if = 2400000000 - self.k3s_vfo.lo

        self.downlink_if = 10489500000 - self.k3s_vfo.lo

    def start(self):

        # This function starts the thread to run the serial port K3s poller.

        self.thread = []
        self.k3s_vfo.hertz.connect(self.updater)
        self.k3s_vfo.k3sDisconnect.connect(self.error)
        self.thread.append(self.k3s_vfo)
        self.k3s_vfo.start()

    def data_list(self, data):

        # a list to hold the individual chars in the data when converted to a string.
        data_list = []

        # Ensure data is 12 chars long so fill space to the left of the data with zeros.
        data = str(data).zfill(12)

        # Simple counter so we can cut the data up into 3 char chunks
        n = 0

        # While n is less than 12 cut another 3 chars from data and append to data_list.
        # Ok this is a bit barmy as I originally wrote this whole function in another way
        # but I can't be bothered to rewrite it now!!
        while n < 12:
            next_string = data[(12 - n) - 3: (12 - n)]
            # Increase where we are in the data by 3
            n += 3

            # Append the data to the data_list this will be in reverse order e.g Hz first then kHz ... etc.
            data_list.append(next_string)

        # send the data list back in reverse order that we stored it in the list.
        # e.g GHz -> Hz
        return reversed(data_list)

    def error(self):
        self.vfo.display('Error')
        self.uplink.display('Error')
        self.downlink.display('Error')

    def updater(self, data):
        # This function gets called when the k3s_vfo hert slot emits data.

        # data is int, but data_list will return a list of strings with 3 chars in each element.
        freq_list = self.data_list(data)
        # Join the list with periods between each element
        freq = '.'.join(freq_list)
        # Update display with frequency.
        self.vfo.display(freq)

        # add uplink offset to the K3s frequency
        uplink_data = data + self.uplink_if
        freq_list = self.data_list(uplink_data)
        freq = '.'.join(freq_list)
        self.uplink.display(freq)

        # add downlink offset to the K3s frequency
        downlink_data = data + self.downlink_if
        freq_list = self.data_list(downlink_data)
        freq = '.'.join(freq_list)
        self.downlink.display(freq)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QO100uplinkVFO()
    window.show()
    window.start()  # starts the serial port thread.
    sys.exit(app.exec_())
