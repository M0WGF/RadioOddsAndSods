# BG7TGL Frequency Counter Data Collection Tool - Version 1.0
# Copyright (C) 2020  Mark Horn (M0WGF) mhorn71 (at) gmail (dot) com
#
# This file is part of BG7TGL Frequency Counter Data Collection Tool.
#
# BG7TGL Frequency Counter Data Collection Tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# BG7TGL Frequency Counter Data Collection Tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BG7TGL Frequency Counter Data Collection Tool.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import sys
import time
import serial
import datetime

version = '1.0'

# setup the commandline argument handler
parser = argparse.ArgumentParser(
    description='''This software will collect data from the BG7TGL FA-2 Frequency counter over a set period of time. 
    The data will be displayed using a line chart or can be saved to CSV with time stamp.  To have a chart displayed
    you'll need to have matplotlib installed.''',
    epilog='''If you have modifications to this program please email me thanks Mark M0WGF mhorn71 (at) gmail (dot) com ''')

# command line argument to take the input path where the .dat files are
parser.add_argument('-s', dest='port', help='Serial Port')
parser.add_argument('-b', dest='baudrate', help='Baudrate. Default : 9600')
parser.add_argument('-p', dest='period', help='Period over which to sample data in seconds. Default : 60')
parser.add_argument('-c', dest='csv', action='store_true', help='Save collected data to CSV file.')
parser.add_argument('-d', dest='dest', help='Full path where the CSV data is to be saved.')
parser.add_argument('-g', dest='graph', action='store_true', help='Show chart of collected data.')

# create the argument handler object
args = parser.parse_args()


def spinning_cursor():
    # Got this piece of code from :
    # https://stackoverflow.com/questions/4995733/how-to-create-a-spinning-command-line-cursor

    while True:
        for cursor in '|/-\\':
            yield cursor


def data_collector():

    # A quick check we have one of the default output options selected.
    if args.csv != True and args.graph != True:
        print('ERROR :- You must supply specify CSV or Graph output or both not NONE!')
        print('main.py -h for help.')
        exit(1)

    # Simple list to hold out collected data
    data = []

    # Initialise spinner
    spinner = spinning_cursor()

    # Initialise serial port.
    BG7TGL = serial.Serial()

    if args.port:
        BG7TGL.port = args.port
    else:
        BG7TGL.port = 'COM1'

    if args.baudrate:
        BG7TGL.baudrate = int(args.baudrate)
    else:
        BG7TGL.baudrate = 9600

    # Open the serial port
    try:
        BG7TGL.open()
    except Exception as msg:
        print('ERROR : - %s' % msg)
        exit(1)

    # Calculate end time.
    if args.period:
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=int(args.period))
    else:
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=60)

    print("Processing .... ")

    while True:
        if datetime.datetime.now() <= end_time:
            # Show cursor indicator
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write('\b')

            # Read 22 bytes from serial port.
            data_from_bg7tgl = BG7TGL.read(22)
            # Get item 0 from above read and remove the first two chars which are F:
            bg7tgl_formatted_data = data_from_bg7tgl[0][2:]

            # If data is long enough then append it to the data list along with a time stamp.
            if len(bg7tgl_formatted_data) > 19:
                data.append(datetime.datetime.now(), bg7tgl_formatted_data)

        else:
            break

    print('Processing finished ...')

    for i in data:
        print(i)

data_collector()
