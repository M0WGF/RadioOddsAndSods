# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(500, 282)
        Form.setStyleSheet("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 9px;\n"
"    margin-top: 0.5em;\n"
"    color: rgb(255, 255, 255);\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 10px;\n"
"    padding: 0px 3px 0px 3px;\n"
"}\n"
"\n"
"QWidget {\n"
" background-color: rgb(53, 54, 55);\n"
"}\n"
"\n"
"QLCDNumber{\n"
"background-color: rgb(240, 201, 93);\n"
"}\n"
"\n"
"QLabel{\n"
"color: rgb(255, 255, 255);\n"
"}\n"
"\n"
"QComboBox{\n"
"background-color: rgb(240, 201, 93);\n"
"}\n"
"\n"
"QRadioButton{\n"
"color: rgb(255, 255, 255);\n"
"}")
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 351, 81))
        self.groupBox.setStyleSheet("")
        self.groupBox.setObjectName("groupBox")
        self.downlink = QtWidgets.QLCDNumber(self.groupBox)
        self.downlink.setGeometry(QtCore.QRect(10, 20, 301, 51))
        self.downlink.setFrameShadow(QtWidgets.QFrame.Raised)
        self.downlink.setLineWidth(1)
        self.downlink.setSmallDecimalPoint(False)
        self.downlink.setDigitCount(14)
        self.downlink.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.downlink.setObjectName("downlink")
        self.downlinkLabel = QtWidgets.QLabel(self.groupBox)
        self.downlinkLabel.setGeometry(QtCore.QRect(320, 30, 21, 21))
        self.downlinkLabel.setObjectName("downlinkLabel")
        self.groupBox_2 = QtWidgets.QGroupBox(Form)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 100, 351, 81))
        self.groupBox_2.setStyleSheet("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.uplink = QtWidgets.QLCDNumber(self.groupBox_2)
        self.uplink.setGeometry(QtCore.QRect(10, 20, 301, 51))
        self.uplink.setFrameShadow(QtWidgets.QFrame.Raised)
        self.uplink.setLineWidth(1)
        self.uplink.setSmallDecimalPoint(False)
        self.uplink.setDigitCount(14)
        self.uplink.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.uplink.setObjectName("uplink")
        self.uplinkLabel = QtWidgets.QLabel(self.groupBox_2)
        self.uplinkLabel.setGeometry(QtCore.QRect(320, 30, 21, 21))
        self.uplinkLabel.setObjectName("uplinkLabel")
        self.groupBox_3 = QtWidgets.QGroupBox(Form)
        self.groupBox_3.setGeometry(QtCore.QRect(10, 190, 351, 81))
        self.groupBox_3.setStyleSheet("")
        self.groupBox_3.setObjectName("groupBox_3")
        self.vfo = QtWidgets.QLCDNumber(self.groupBox_3)
        self.vfo.setGeometry(QtCore.QRect(10, 20, 301, 51))
        self.vfo.setFrameShadow(QtWidgets.QFrame.Raised)
        self.vfo.setLineWidth(1)
        self.vfo.setSmallDecimalPoint(False)
        self.vfo.setDigitCount(14)
        self.vfo.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.vfo.setObjectName("vfo")
        self.vfoLabel = QtWidgets.QLabel(self.groupBox_3)
        self.vfoLabel.setGeometry(QtCore.QRect(320, 30, 21, 21))
        self.vfoLabel.setObjectName("vfoLabel")
        self.connectButton = QtWidgets.QPushButton(Form)
        self.connectButton.setGeometry(QtCore.QRect(370, 240, 121, 32))
        self.connectButton.setStyleSheet("QPushButton{\n"
"    background-color: rgb(30, 30, 31);\n"
"    color: rgb(255, 255, 255);\n"
"    border-style: inset;\n"
"    border-radius: 5px;\n"
"    border-color: rgb(195, 195, 195);\n"
"    border-width: 1px;\n"
"}\n"
"\n"
"QPushButton::pressed {\n"
"    background-color: rgb(144, 145, 146);\n"
"}")
        self.connectButton.setObjectName("connectButton")
        self.groupBox_4 = QtWidgets.QGroupBox(Form)
        self.groupBox_4.setGeometry(QtCore.QRect(370, 60, 121, 171))
        self.groupBox_4.setObjectName("groupBox_4")
        self.splitter = QtWidgets.QSplitter(self.groupBox_4)
        self.splitter.setGeometry(QtCore.QRect(10, 20, 100, 141))
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.xit_lcd = QtWidgets.QLCDNumber(self.splitter)
        self.xit_lcd.setMinimumSize(QtCore.QSize(100, 32))
        self.xit_lcd.setDigitCount(5)
        self.xit_lcd.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.xit_lcd.setProperty("intValue", 1000)
        self.xit_lcd.setObjectName("xit_lcd")
        self.xit_offset = QtWidgets.QDial(self.splitter)
        self.xit_offset.setMinimum(-5000)
        self.xit_offset.setMaximum(5000)
        self.xit_offset.setOrientation(QtCore.Qt.Horizontal)
        self.xit_offset.setInvertedAppearance(False)
        self.xit_offset.setInvertedControls(True)
        self.xit_offset.setWrapping(False)
        self.xit_offset.setNotchTarget(50.0)
        self.xit_offset.setNotchesVisible(True)
        self.xit_offset.setObjectName("xit_offset")
        self.xit = QtWidgets.QPushButton(self.splitter)
        self.xit.setStyleSheet("QPushButton{\n"
"    background-color: rgb(30, 30, 31);\n"
"    color: rgb(255, 255, 255);\n"
"    border-style: inset;\n"
"    border-radius: 5px;\n"
"    border-color: rgb(195, 195, 195);\n"
"    border-width: 1px;\n"
"}\n"
"\n"
"QPushButton::pressed {\n"
"    background-color: rgb(144, 145, 146);\n"
"}")
        self.xit.setCheckable(True)
        self.xit.setObjectName("xit")
        self.band1 = QtWidgets.QRadioButton(Form)
        self.band1.setGeometry(QtCore.QRect(380, 10, 100, 20))
        self.band1.setObjectName("band1")
        self.bandButtonGroup = QtWidgets.QButtonGroup(Form)
        self.bandButtonGroup.setObjectName("bandButtonGroup")
        self.bandButtonGroup.addButton(self.band1)
        self.band2 = QtWidgets.QRadioButton(Form)
        self.band2.setGeometry(QtCore.QRect(380, 30, 100, 20))
        self.band2.setObjectName("band2")
        self.bandButtonGroup.addButton(self.band2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "QO-100 VFO Converter"))
        self.groupBox.setTitle(_translate("Form", "RX"))
        self.downlinkLabel.setText(_translate("Form", "Hz"))
        self.groupBox_2.setTitle(_translate("Form", "TX"))
        self.uplinkLabel.setText(_translate("Form", "Hz"))
        self.groupBox_3.setTitle(_translate("Form", "K3s VFO"))
        self.vfoLabel.setText(_translate("Form", "Hz"))
        self.connectButton.setText(_translate("Form", "Connect"))
        self.groupBox_4.setTitle(_translate("Form", "Display Offset"))
        self.xit.setText(_translate("Form", "Offset"))
        self.band1.setText(_translate("Form", "Band 1"))
        self.band2.setText(_translate("Form", "Band 2"))

