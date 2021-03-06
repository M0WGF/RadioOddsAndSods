# QO100uplinkVFO - Version 2.0
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
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QApplication
from widget2 import Ui_Form

class RigVFO(QThread):

    # Emit current K3s VFO frequency.
    hertz = pyqtSignal(object)
    # Emit serial port disconnect.
    RigDisconnect = pyqtSignal()

    def __init__(self):
        QThread.__init__(self)

        # Default VFO get settings.
        self.VFO = 1  # Simple switch to tell later on if rig is Elecraft.
        self.VFO_CMD = b'FA;'  # VFO Command that is sent to the radio.
        self.VFO_DATA_LENGTH = 14  # The expected length of the response.

        # Initiate the serial port.
        self.serial_port = serial.Serial()

        # Set the poll rate.
        self.poll = 0.01

        # Set the class serial port
        self.port = 'COM1'

        # Set the class serial baudrate
        self.baud = 9600

    def run(self):

        # This section will house the serial port connection and get the current VFO reading from the K3s.

        while True:

            try:
                if self.serial_port.is_open:

                    if self.VFO == 1:
                        self.VFO_CMD = b'FA;'  # VFO Command that is sent to the radio.
                        self.VFO_DATA_LENGTH = 14  # The expected length of the response.
                    else:
                        self.VFO_CMD = b'\x00\x00\x00\x00\x03'
                        self.VFO_DATA_LENGTH = 5  # The expected length of the response.

                    self.serial_port.write(self.VFO_CMD)  # Get VFO frequency from radio

                    data = self.serial_port.read(self.VFO_DATA_LENGTH)  # Reads Bytes which is the max number
                    # of bytes the radio should respond with.

                    # Set result to none so we can bypass emit if no data is received.
                    result = None

                    if self.VFO == 1:
                        data = data.decode('ascii')  # Decode bytes to ascii
                        result = sub('[^0-9]', '', data)  # strip all characters unless it's numeric
                    elif self.VFO == 2:
                        data = data[0], data[1], data[2], data[3]
                        result = "%02x%02x%02x%02x0" % data

                    # Emit the vfo reading.
                    if result is not None:
                        self.hertz.emit(int(result))
                    else:
                        pass

                    # Sleep for time stated by poll.
                    time.sleep(self.poll)
                else:
                    self.RigDisconnect.emit()
            except serial.SerialException:
                self.RigDisconnect.emit()

    def connect(self):

        # Set the baud rate.
        self.serial_port.baudrate = int(self.baud)

        # Set the serial port.
        self.serial_port.port = self.port

        try:
            self.serial_port.open()
        except serial.SerialException:
            self.RigDisconnect.emit()


class QO100uplinkVFO(QWidget, Ui_Form):
    def __init__(self):
        super(QO100uplinkVFO, self).__init__()

        # Initiate the rig_vfo class
        self.rig_vfo = RigVFO()

        # Initiate the config parser.
        config = configparser.RawConfigParser()

        try:
            # Open and read the config.ini file.
            config.read('config.ini')
            # Get the configuration from the ini file.
            comport = config.get('CONFIG', 'PORT')
            baud = int(config.get('CONFIG', 'BAUD'))
            poll = float(config.get('CONFIG', 'POLL'))
            rig = config.get('CONFIG', 'RIG')
            band1_name = config.get('CONFIG', 'IF1_BAND_NAME')
            band2_name = config.get('CONFIG', 'IF2_BAND_NAME')
            self.band1_IF_RX = int(config.get('CONFIG', 'IF1_RX_IF'))
            self.band1_IF_TX = int(config.get('CONFIG', 'IF1_TX_IF'))
            self.band2_IF_RX = int(config.get('CONFIG', 'IF2_RX_IF'))
            self.band2_IF_TX = int(config.get('CONFIG', 'IF2_TX_IF'))
        except configparser.NoSectionError:  # If the file or configuration is missing set some defaults.
            # print('Error Config Missing - See http://m0wgf.blogspot.com')
            comport = 'COM1'
            baud = 38400
            poll = 0.01
            rig = 'K3S'
            band1_name = 'Band 1'
            band2_name = 'Band 2'
            self.band1_IF_RX = 10489500000
            self.band1_IF_TX = 2400000000
            self.band2_IF_RX = 10489500000
            self.band2_IF_TX = 2400000000

        # Setup the Ui_Form display.
        self.setupUi(self)

        # Initiate the rig_vfo class
        self.rig_vfo = RigVFO()

        # Initialise RigVFO class parameters.
        self.rig_vfo.port = comport
        self.rig_vfo.baud = int(baud)
        self.rig_vfo.poll = float(poll)

        if rig.lower() == 'k3s':
            self.rig_vfo.VFO = 1
        else:
            self.rig_vfo.VFO = 2

        # Set the RigVFO class parameters.

        if self.rig_vfo.VFO == 1:
            # Set the window title.
            self.setWindowTitle('K3s VFO Display')
        else:
            # Set the window title.
            self.setWindowTitle('FT817 VFO Display')

        # Connect the connect button to the k3s_vfo class serial port connect function.
        self.connectButton.clicked.connect(self.rig_vfo.connect)

        # Connect the XIT button to XIT function.
        self.xit.clicked.connect(self.xit_clarifier)

        # Connect the XIT QDial to XIT Offset function.
        self.xit_offset.valueChanged.connect(self.xit_offset_dial)
        # Set offset dial to zero.
        self.xit_offset.setValue(0)
        # Set offset lcd to zero.
        self.xit_lcd.display(0)
        # Disable offset dial as default state.
        self.xit_offset.setDisabled(True)

        # Connect Band1 and Band2 RadioButton to function.
        self.bandButtonGroup.buttonClicked[int].connect(self.band)
        # Set the ID of each button in the QRadioButton Group.
        self.bandButtonGroup.setId(self.band1, 1)
        self.bandButtonGroup.setId(self.band2, 2)

        # Set RadioButton label text
        self.band1.setText(band1_name)
        self.band2.setText(band2_name)

        # Set Band1 RadioButton as checked.
        self.band1.setChecked(True)

        # Control states so we can switch between band and not lose XIT offset.
        self.selected_band1 = True
        self.selected_xit_band1 = False
        self.selected_xit_offset_band1 = 0

        self.selected_band2 = False
        self.selected_xit_band2 = False
        self.selected_xit_offset_band2 = 0

        # Variable to hold the current VFO frequency.
        self.freq = 0

        # Variable to hold the current uplink and downlink frequencies.
        self.uplink_data = 144300000
        self.downlink_data = 144300000

        # Define thread list.
        self.thread = []

    def start(self):

        # This function starts the thread to run the serial port K3s poller.
        self.rig_vfo.hertz.connect(self.updater)
        self.rig_vfo.RigDisconnect.connect(self.error)
        self.thread.append(self.rig_vfo)
        self.rig_vfo.start()

    def data_list(self, data):

        # a list to hold the individual chars in the data when converted to a string.
        data_list = []

        # Add the XIT offset to the frequency data we have received from the rig.
        if self.selected_band1:
            data = int(data) + self.selected_xit_offset_band1
        else:
            data = int(data) + self.selected_xit_offset_band2

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

    def data_list_offset_updater(self, data):

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
        # This function gets called when the rig_vfo hertz slot emits data.

        # data is int, but data_list will return a list of strings with 3 chars in each element.
        freq_list = self.data_list(data)
        # Join the list with periods between each element
        freq = '.'.join(freq_list)
        # Update display with frequency.
        self.vfo.display(freq)

        # add uplink IF to the rigs frequency
        if self.selected_band1:
            self.uplink_data = data + self.band1_IF_TX
        else:
            self.uplink_data = data + self.band2_IF_TX

        freq_list = self.data_list(self.uplink_data)
        freq = '.'.join(freq_list)
        self.uplink.display(freq)

        # add downlink offset to the rigs frequency
        if self.selected_band1:
            self.downlink_data = data + self.band1_IF_RX
        else:
            self.downlink_data = data + self.band2_IF_RX

        freq_list = self.data_list(self.downlink_data)
        freq = '.'.join(freq_list)
        self.downlink.display(freq)

    def xit_clarifier(self):

        # If XIT button is pressed set up XIT for the band selected.

        if self.selected_band1:
            # Check if xit button is checked.
            if self.xit.isChecked():
                # Enable the offset dial.
                self.xit_offset.setDisabled(False)
                # Set the band1 xit selected to True.
                self.selected_xit_band1 = True
            else:
                # Set the xit offset dial to disabled.
                self.xit_offset.setDisabled(True)
                # Set the band1 xit selected to False.
                self.selected_xit_band1 = False
                # Set the xit offset value to zero.
                self.xit_offset.setValue(0)
                self.selected_xit_offset_band1 = 0
        elif self.selected_band2:
            if self.xit.isChecked():
                self.xit_offset.setDisabled(False)
                self.selected_xit_band2 = True
            else:
                self.xit_offset.setDisabled(True)
                self.selected_xit_band2 = False
                self.xit_offset.setValue(0)
                self.selected_xit_offset_band2 = 0

    def xit_offset_dial(self):
        # Read the value of the XIT dial as it's turned.
        value = self.xit_offset.value()
        self.xit_lcd.display(value)

        # Depending on which band is set update that bands offset variable value.
        if self.selected_band1:
            self.selected_xit_offset_band1 = value
        elif self.selected_band2:
            self.selected_xit_offset_band2 = value

        # Update the current Downlink and Uplink Frequencies.  We don't modify the exciters frequency readout.
        updated_rx = self.downlink_data + int(value)
        freq_list = self.data_list_offset_updater(updated_rx)
        self.freq = '.'.join(freq_list)
        self.downlink.display(self.freq)

        updated_tx = self.uplink_data + int(value)
        freq_list = self.data_list_offset_updater(updated_tx)
        freq = '.'.join(freq_list)
        self.uplink.display(freq)

    def band(self, id):
        # for each button in the QRadioButton group get the id and set which band is selected
        # to True and the other band to False.
        for button in self.bandButtonGroup.buttons():
            if button is self.bandButtonGroup.button(id):
                if id == 1:
                    self.selected_band1 = True
                    self.selected_band2 = False
                elif id == 2:
                    self.selected_band1 = False
                    self.selected_band2 = True

        if self.selected_band1:
            # If band 1 is selected and xit is enabled
            if self.selected_xit_band1:
                # Set the xit lcd to the save band 1 offset value.
                self.xit_lcd.display(self.selected_xit_offset_band1)
                # Reset the XIT button to be checked.
                self.xit.setChecked(True)
                # Enable the XIT offset dial.
                self.xit_offset.setDisabled(False)
                # Reset the XIT dial to the value is was last set too.
                self.xit_offset.setValue(self.selected_xit_offset_band1)
            else:
                # set the xit lcd back to displaying zero.
                self.xit_lcd.display(0)
                # Set the xit dial to disabled.
                self.xit_offset.setDisabled(True)
                # Set the xit dial back to zero.
                self.xit_offset.setValue(0)
                # Set the bands XIT offset value back to zero.
                self.selected_xit_offset_band1 = 0
                # Set the xit button to be unchecked or we'll interfere with the operation on the next selected band.
                self.xit.setChecked(False)
        elif self.selected_band2:
            if self.selected_xit_band2:
                self.xit_lcd.display(self.selected_xit_offset_band2)
                self.xit.setChecked(True)
                self.xit_offset.setDisabled(False)
                self.xit_offset.setValue(self.selected_xit_offset_band2)
            else:
                self.xit_lcd.display(0)
                self.xit_offset.setDisabled(True)
                self.xit_offset.setValue(0)
                self.selected_xit_offset_band2 = 0
                self.xit.setChecked(False)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = QO100uplinkVFO()
    window.show()
    window.start()  # starts the serial port thread.
    sys.exit(app.exec_())
