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
import serial
import datetime
import csv
import os
import matplotlib

version = '1.0'

# setup the commandline argument handler
parser = argparse.ArgumentParser(
    description='''This software will collect data from the BG7TGL FA-2 Frequency counter over a set period of time. 
    The data will be displayed using a line chart or can be saved to CSV with time stamp.  To have a chart displayed
    you'll need to have matplotlib installed. ''',
    epilog='''If you have modifications to this program please email me thanks Mark M0WGF mhorn71 (at) gmail (dot) com ''')

# command line argument to take the input path where the .dat files are
parser.add_argument('-s', dest='port', help='Serial Port')
parser.add_argument('-b', dest='baudrate', help='Baudrate. Default : 9600')
parser.add_argument('-p', dest='period', help='Period over which to sample data in seconds. Default : If no time period '
                                              'is set the script will run until the user calls ctrl-c '
                                              'at which point the script will create a csv file, graph or both.')
parser.add_argument('-c', dest='csv', action='store_true', help='Save collected data to CSV file.')
parser.add_argument('-d', dest='dest',
                    help='Full path where the CSV data is to be saved. Default : Where this script resides.')
parser.add_argument('-g', dest='graph', action='store_true', help='Show chart of collected data.')
parser.add_argument('-v', dest='version', action='store_true', help='Show version number.')

# create the argument handler object
args = parser.parse_args()

if args.version:
    print('BG7TGL Frequency Counter Data Collection Tool - Version %s' % version)
    print('By Mark Horn M0WGF - mhorn (at) gmail (dot) com')
    exit(0)


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
        end_time = datetime.datetime.now() + datetime.timedelta(days=2)

    print("Reading serial port .... ")

    while True:
        try:
            if datetime.datetime.now() <= end_time:
                # Show cursor indicator
                sys.stdout.write(next(spinner))
                sys.stdout.flush()
                sys.stdout.write('\b')

                # Read 22 bytes from serial port.
                try:
                    data_from_bg7tgl = BG7TGL.read(27)
                except Exception:
                    pass

                # Format data we first remove the 3 spaces and F: from start of string and strip the \r\n
                bg7tgl_formatted_data = data_from_bg7tgl.decode()[5:].strip('\r\n')

                # If data is long enough then append it to the data list along with a time stamp.
                if len(bg7tgl_formatted_data) == 20:
                    # Append date and formatted data to data list as tuple.
                    data.append((datetime.datetime.now(), bg7tgl_formatted_data))

            else:
                break
        except KeyboardInterrupt:
            break

    # Close serial port
    try:
        BG7TGL.close()
        print('Serial port closed ....')
    except Exception:
        pass

    # If save to csv is true then lets do it.
    if args.dest:
        filename = os.path.join(args.dest, 'bg7tgl.csv')
        print('Saving CSV to : %s' % filename)
    else:
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bg7tgl.csv')
        print('Saving CSV to : %s' % filename)

    # Save csv data.
    if args.csv:
        with open(filename, 'w', newline='\n', encoding='utf-8') as csv_outfile:
            csv_out = csv.writer(csv_outfile, dialect='excel')
            csv_out.writerows(data)

    # Create plot of data.
    if args.graph:
        pass


data_collector()