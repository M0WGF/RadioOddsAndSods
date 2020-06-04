# BG7TBL Frequency Counter Data Decimator Tool - Version 1.0
# Copyright (C) 2020  Mark Horn (M0WGF) mhorn71 (at) gmail (dot) com
#
# This file is part of BG7TBL Frequency Counter Data Decimator Tool.
#
# BG7TBL Frequency Counter Data Decimator Tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# BG7TBL Frequency Counter Data Decimator Tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BG7TBL Frequency Counter Data Decimator Tool.  If not, see <http://www.gnu.org/licenses/>.

import csv
import matplotlib.pyplot as plt
from datetime import datetime
import argparse

# setup the commandline argument handler
parser = argparse.ArgumentParser(
    description='''This software will plot data collected from the BG7TBL FA-2 Frequency counter as created by the BG7TBL Frequency Counter Data Collection Tool.''',
    epilog='''If you have modifications to this program please email me, thanks. Mark M0WGF (mhorn71 (at) gmail (dot) com) ''')

# command line argument to take the input path where the .dat files are
parser.add_argument('-f', dest='filename', help='Filename.')
parser.add_argument('-t', dest='title', help='Chart title.')
parser.add_argument('-n', dest='decimate', help='Plot ever n number of samples.')
parser.add_argument('-c', dest='cut', help='Ignore first n number of samples.')
parser.add_argument('-i', dest='invert', help='Invert Y axis.')
parser.add_argument('-d', dest='dec', help='Number of decimal places to plot between 1 to 9')

# create the argument handler object
args = parser.parse_args()

if args.filename:
    filename = args.filename
else:
    print('No filename specified!!')
    exit(1)

if args.title:
    title = args.title
else:
    title = 'BG7TBL FA-2 Freq Counter'

if args.decimate:
    decimate = int(args.decimate)
else:
    decimate = 0  # Plot ever n number of samples

if args.cut:
    cut_head = int(args.cut)
else:
    cut_head = 0 # Ignore first n number of samples.

if args.invert:
    invertYaxis = True
else:
    invertYaxis = False # invert Y axis

if args.dec:
    decimals = int(args.dec)
else:
    decimals = 1 # Can be set between 1 - 9

data = []

def data_dec():

    if decimals == 1:
        dec = "%.1f"
    elif decimals == 2:
        dec = "%.2f"
    elif decimals == 3:
        dec = "%.3f"
    elif decimals == 4:
        dec = "%.4f"
    elif decimals == 5:
        dec = "%.5f"
    elif decimals == 6:
        dec = "%.6f"
    elif decimals == 7:
        dec = "%.7f"
    elif decimals == 8:
        dec = "%.8f"
    elif decimals == 9:
        dec = "%.9f"
    else:
        dec = "%.3f"

    with open(filename, 'r', newline='\n', encoding='utf-8') as csvfile:
        csv_stream = csv.reader(csvfile)

        timer = 0
        cut_counter = 0

        for row in csv_stream:

            if cut_counter < cut_head:
                pass
                cut_counter += 1
            else:

                if timer == 10:
                    dt_obj = datetime.strptime(row[0], '%Y\%m\%d %H:%M:%S')

                    timer = 0
                else:
                    timer += 1

    csvfile.close()

    formatted_data = [(elem1, elem2) for elem1, elem2 in data]

    plt.plot(*zip(*formatted_data))
    plt.xlabel('Time')
    plt.ylabel('Frequency')

    if invertYaxis:
        plt.gca().invert_yaxis()

    if title is not None:
        plt.title(title)

    plt.grid()
    plt.show()

data_dec()