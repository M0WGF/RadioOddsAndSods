# BG7TGL Frequency Counter Data Plotter

usage: main.py [-h] [-s PORT] [-b BAUDRATE] [-p PERIOD] [-c] [-g] [-G] [-l]
               [-d DESTINATION] [-f FILE_NAME] [-a] [-v]

This software will collect data from the BG7TGL FA-2 Frequency counter over a
set period of time. The data will be displayed using a line chart or can be
saved to CSV with time stamp. To have a chart displayed you'll need to have
matplotlib installed.

optional arguments:

  -h, --help      show this help message and exit
  
  -s PORT         Serial Port
  
  -b BAUDRATE     Baudrate. Default : 9600
  
  -p PERIOD       Period over which to sample data in seconds. Default : If -p
                  isn't set the script will run until the user calls Ctrl-C and 
                  interrupts. The script will still create a csv file, graph or both.
                  
  -c              Save collected data to CSV file.
  
  -g              Show chart of collected data, you can save the chart from the pop-up window.
  
  -G              Saves created chart to file without showing the chart.
  
  -l              Print data to stdout.
  
  -d DESTINATION  Full path where the CSV data is to be saved. Default : Where
                  this script resides.
                  
  -f FILE_NAME    Filename of saved CSV and Graph.
  
  -a              Append data to already created csv file.
  
  -v              Show version number.
  

If you have modifications to this program please email me, thanks. Mark M0WGF
(mhorn71 (at) gmail (dot) com)
