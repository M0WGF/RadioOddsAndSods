# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

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

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(491, 282)
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
        self.connectButton.setGeometry(QtCore.QRect(370, 20, 113, 32))
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

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "QO-100 VFO Converter"))
        self.groupBox.setTitle(_translate("Form", "RTL Downlink"))
        self.downlinkLabel.setText(_translate("Form", "Hz"))
        self.groupBox_2.setTitle(_translate("Form", "DxPatrol Uplink"))
        self.uplinkLabel.setText(_translate("Form", "Hz"))
        self.groupBox_3.setTitle(_translate("Form", "K3s VFO"))
        self.vfoLabel.setText(_translate("Form", "Hz"))
        self.connectButton.setText(_translate("Form", "Connect"))

