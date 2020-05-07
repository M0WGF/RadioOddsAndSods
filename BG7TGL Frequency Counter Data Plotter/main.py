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
import matplotlib.pyplot as plt

version = '1.0'

# setup the commandline argument handler
parser = argparse.ArgumentParser(
    description='''This software will collect data from the BG7TGL FA-2 Frequency counter over a set period of time. 
    The data will be displayed using a line chart or can be saved to CSV with time stamp.  To have a chart displayed
    you'll need to have matplotlib installed. ''',
    epilog='''If you have modifications to this program please email me, thanks. Mark M0WGF (mhorn71 (at) gmail (dot) com) ''')

# command line argument to take the input path where the .dat files are
parser.add_argument('-s', dest='port', help='Serial Port')
parser.add_argument('-b', dest='baudrate', help='Baudrate. Default : 9600')
parser.add_argument('-p', dest='period', help='Period over which to sample data in seconds. Default : If -p'
                                              'isn\'t set the script will run until the user calls Ctrl-C '
                                              'and interrupts. The script will still create a csv file, graph or both.')
parser.add_argument('-c', dest='csv', action='store_true', help='Save collected data to CSV file.')
parser.add_argument('-g', dest='graph', action='store_true', help='Show chart of collected data, you can save the chart from the pop-up window.')
parser.add_argument('-G', dest='graph_save', action='store_true', help='Saves created chart to file without showing the chart.')
parser.add_argument('-l', dest='stdout', action='store_true', help='Print data to stdout.')
parser.add_argument('-d', dest='destination',
                    help='Full path where the CSV data is to be saved. Default : Where this script resides.')
parser.add_argument('-f', dest='file_name', help='Filename of saved CSV and Graph. ')
parser.add_argument('-a', dest='append_file', action='store_true', help='Append data to already created csv file.')
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

    # User supplied filename
    if args.file_name:
        file = str(args.file_name) + '.csv'
        chart_file = str(args.file_name) + '.png'
    else:
        file = 'bg7tgl.csv'
        chart_file = 'bg7tgl.png'

    # Create the file and path variable so we can use them later.
    if args.destination:
        filename = os.path.join(args.destination, file)
        chartname = os.path.join(args.destination, chart_file)
    else:
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
        chartname = os.path.join(os.path.dirname(os.path.abspath(__file__)), chart_file)

    # Are we appending csv data to an already existing file?
    if args.append_file:
        # Append to file and if it doesn't exist create it.
        format = 'a+'
    else:
        # Create file.
        format = 'x'

    # check we can open the file and write to it.
    if args.csv:
        try:
            test = open(filename, format)
        except Exception as msg:
            print('ERROR :- %s' % msg)
            exit(1)
        else:
            test.close()

    if args.graph_save:
        if os.path.isfile(chartname):
            print('ERROR :- Chart already exists you must use unique file names.')
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

                # Read 22 bytes from serial port.
                try:
                    data_from_bg7tgl = BG7TGL.read(27)
                except Exception:
                    pass

                # Format data we first remove the 3 spaces and F: from start of string and strip the \r\n
                bg7tgl_formatted_data = data_from_bg7tgl.decode()[5:].strip('\r\n')

                # If data is long enough then append it to the data list along with a time stamp.
                if len(bg7tgl_formatted_data) == 20:

                    # Format data ready for printing and appending to data list and remove leading zeros.
                    pre_data = datetime.datetime.now(), bg7tgl_formatted_data.lstrip('0')

                    # Append date and formatted data to data list as tuple.
                    data.append(pre_data)

                    # If we're printing to stdout then we don't show the cursor spinner.
                    if args.stdout:
                        print('%s %s' % (pre_data[0].strftime("%d/%m/%Y %H:%M:%S"), pre_data[1]))
                    else:
                        # Show cursor indicator
                        sys.stdout.write(next(spinner))
                        sys.stdout.flush()
                        sys.stdout.write('\b')

            else:
                # If the current time exceeds the start time plus the period then break the while loop.
                break
        except KeyboardInterrupt:
            # If user hit's ctrl-c then break while loop and continue.
            break

    # Close serial port
    try:
        BG7TGL.close()
        print('Serial port closed ....')
    except Exception:
        pass

    # Save csv data.
    if args.csv:
        with open(filename, 'a+', newline='\n', encoding='utf-8') as csv_outfile:
            csv_out = csv.writer(csv_outfile, dialect='excel')
            csv_out.writerows(data)

    # Create plot of data.
    if args.graph:

        formatted_data = [(elem1, elem2) for elem1, elem2 in data]

        plt.plot(*zip(*formatted_data))
        plt.title(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        plt.xlabel('time')
        plt.ylabel('frequency')
        plt.show()
    elif args.graph_save:

        formatted_data = [(elem1, elem2) for elem1, elem2 in data]

        plt.plot(*zip(*formatted_data))
        plt.title(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        plt.xlabel('time')
        plt.ylabel('frequency')
        plt.savefig(chartname)

    print('Process finished ....')


data_collector()