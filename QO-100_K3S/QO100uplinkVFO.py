# QO100uplinkVFO - Version 1.0
# Copyright (C) 2020  Mark Horn (M0WGF) mhorn71 (at) gmail (dot) com
#
# This file is part of QO100uplinkVFO.
#
# QO100uplinkVFO is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# QO100uplinkVFO is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with QO100uplinkVFO.  If not, see <http://www.gnu.org/licenses/>.

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
            rig = config.get('CONFIG', 'RIG')
        except configparser.NoSectionError:  # If the file or configuration is missing set some defaults.
            print('Error Config Missing - See http://m0wgf.blogspot.com')
            self.lo = 432000000
            port = 'COM1'
            baud = 38400
            self.poll = 0.01
            rig = 'K3S'

        rig = rig.lower()

        if rig == 'k3s':
            self.VFO = 1  # Simple switch to tell later on if rig is Elecraft.
            self.VFO_CMD = b'FA;'  # VFO Command that is sent to the radio.
            self.VFO_DATA_LENGTH = 14  # The expected length of the response.
        else:
            self.VFO = 0  # Simple switch to tell later on if rig is Yaesu.
            self.VFO_CMD = b'\x00\x00\x00\x00\x03'
            self.VFO_DATA_LENGTH = 5  # The expected length of the response.


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

                    print('Port is open')

                    self.k3s_port.write(self.VFO_CMD)  # Get VFO frequency from radio

                    data = self.k3s_port.read(self.VFO_DATA_LENGTH)  # Reads Bytes which is the max number of bytes the radio should respond with.

                    print(data)

                    if self.VFO == 1:
                        data = data.decode('ascii')  # Decode bytes to ascii
                        result = sub('[^0-9]', '', data)  # strip all characters unless it's numeric
                    elif self.VFO == 0:
                        print('FT817')
                        data = data[0], data[1], data[2], data[3]
                        result = "%02x%02x%02x%02x0" % data
                        print(result)

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

        # Initiate the k3s_vfo class
        self.k3s_vfo = getK3sVFO()

        if self.k3s_vfo.VFO == 1:
            # Set the window title.
            self.setWindowTitle('K3s, QO100 (Uplink, Downlink) VFO Display')
        else:
            # Set the window title.
            self.setWindowTitle('FT817, QO100 (Uplink, Downlink) VFO Display')

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
