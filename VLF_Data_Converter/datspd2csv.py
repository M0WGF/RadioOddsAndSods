# VLF Data Converter Tool - Version 2.4
# Copyright (C) 2020  Mark Horn (M0WGF) mhorn71 (at) gmail (dot) com
#
# This file is part of VLF Data Converter Tool.
#
# VLF Data Converter Tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# VLF Data Converter Tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with VLF Data Converter Tool.  If not, see <http://www.gnu.org/licenses/>.

import struct
import os
import datetime
import re
from math import *
import argparse
from pathlib import Path
from shutil import copyfile

version = '2.4'

# Set your default paths here, note if the paths are specified at the cmdline these will be ignored.
input_path = '/Users/mark/PyCharmProjects/RadioOddsAndSods/VLF_Data_Converter'  # e.g '/Home/mark'
output_path = '/Users/mark/Data_Converter'
transverse = None  # transverse

# setup the commandline argument handler
parser = argparse.ArgumentParser()

# command line argument to take the input path where the .dat files are
parser.add_argument('-i', '--i', dest='indir', help='Input files directory. This will override the hardcoded path.')

# command line argument that takes the path where the output files go
parser.add_argument('-o', '--o', dest='outdir', help='Output files directory. This will override the hardcoded path.')

# command line argument that takes the path where the output files go
parser.add_argument('-p', '--p', action='store_true', help='Save output files to original input directory.')

# command line argument to transverse the input path.
parser.add_argument('-t', '--t', action='store_true', help='transverse input path subdirectories.')

# command line argument to enable debugging
parser.add_argument('-v', '--v', action='count', help='Enable debugging -v or -vv for really verbose debugs. \n\r '
                                                      'You may want to redirect stdout to a file as -vv is '
                                                      'very verbose')

# command line argument to transverse the input path.
parser.add_argument('-V', '--V', action='store_true', help='Print version number.')

# create the argument handler object
args = parser.parse_args()

if args.V:
    print('VLF data converter, version %s' % version)
    exit(0)

# Set debugging from command line.
if args.v is not None and args.v == 1:
    debug = 1
    rsp_debug = True
    jc_debug = True
    metadata_debug = True
elif args.v is not None and args.v >= 2:
    debug = 2
    rsp_chunk_debug = True
    jc_chunk_debug = True
else:
    debug = 0


def dd2dms(type, dd):
    # Quick and nasty degrees decimal to degrees minutes and seconds.
    # Based on the following blog post https://rextester.com/BRMA94677
    # type must be either 'long' or 'lat'

    # make sure type is lower case.
    type = type.lower()

    # Make sure dd is float
    dd = float(dd)

    mins = dd % 1.0 * 60
    secs = mins % 1.0 * 60

    if type == 'long':
        deg = str(int(floor(dd))).zfill(3)  # zfill make sure deg is always three digits long by prefixing zeros.
        min = str(int(floor(mins))).zfill(2)
        sec = str(floor(secs)).zfill(2)
    else:
        deg = str(int(floor(dd))).zfill(2)  # zfill make sure deg is always three digits long by prefixing zeros.
        min = str(int(floor(mins))).zfill(2)
        sec = str(floor(secs)).zfill(2)

    return ('+%s:%s:%s' % (deg, min, sec))  # This might not be the best way of doing things as + is hard coded.


def doubledt_2_stddt(dd_date):
    # Quick and nasty VB double type date to standard format date this may or may not always yield the correct result!!
    # Skypipe stores the time as a double. e.g 43872.38966576389 and we want to convert that to standard time e.g \
    # 2020-02-11 09:21:07

    # Radio Skypipe is written in VB and uses double date which are calculated from 1899-12-30 at midnight.
    # So here we set our double_date_base date to this date and time.
    double_date_base = datetime.datetime(1899, 12, 30, 0, 0, 0)  # The base date double uses to find the current date.

    # Check the parameter that is passed to this function is a float.
    if type(dd_date) != 'float':
        dd_date = float(dd_date)

    # Set the date to be the double_date_base plus the amount of time that has passed as denoted by the double we have
    # been passed.
    dt = double_date_base + datetime.timedelta(days=float(dd_date))

    # Return the resulting date but round to the nearest second.
    return dt - datetime.timedelta(microseconds=dt.microsecond)  # This timedelta rounds to the nearest second.


def stardata(filename, debug):
    '''
    Translates Stardata to CSV

    This function will decode date encoded in the Stardata format as used in Starbase.

    :param filename: including full path.
    :param debug: integer 0 - 2 with 0 being no debugs, 1 debugging on and 2 verbose debugs.
    :return: tuple <boolean, list>
    '''
    pass


def john_cook_data(filename, debug):
    '''
    # John Cooks data file get the date from the filename.

    This function doesn't require any function other than what's provided by the standard python libraries.

    # Please read the Starbase JohnCook datatranslator on how John encodes his datafiles.
    # https://isbd.uk/repo/starbase/trunk/Starbase/src/org/lmn/fc/common/datatranslators/johncook/

    :param filename: including full path.
    :param debug: integer 0 - 2 with 0 being no debugs, 1 debugging on and 2 verbose debugs.
    :return: tuple <boolean, list>
    '''

    # set up debugging ...
    if debug == 1:
        jc_debug = True
        jc_chunk_debug = False
    elif debug == 2:
        jc_debug = True
        jc_chunk_debug = True
    else:
        jc_debug = False
        jc_chunk_debug = False

    # CSV Data list
    csv_data = []

    if jc_debug: print('DEBUG : John Cook Dat Converter')

    print('INFO : Processing file %s' % filename)

    # Split filename on system path delimiter
    filename_split = filename.split(str(os.path.sep))

    # Get last item from split list which should be the filename
    filename_date = filename_split[-1]

    # Strip the period and suffix from the filename.
    filename_date = filename_date.rstrip('.dat')

    # JC file can be in three known filename formats YYYYMMDD.dat , UTYYMMDD*.dat or UTYYYYMMDD*.dat

    # Check to see if file starts with UT
    if filename_date.startswith('UT'):
        # Get only digits from the filename we'll make the assumption that it's the observation date.
        filename_date = ''.join(filter(str.isdigit, filename_date))
        # Check we have a 6 or 8 digit anything else mean we can't makesense of it.
        if len(filename_date) == 6 or len(filename_date) == 8:
            # If we have a 6 digit date we'll need to add two digits.
            if len(filename_date) == 6:
                # Ok prefix with 20 so we have a four digit year date.
                filename_date = '20' + filename_date
        else:
            # Date length isn't correct to return False.
            print('ERROR : Unable to decipher the date for %s' % filename_split[-1])
            return False

    # Find the year and store as observation year we'll need this when creating the CSV file.
    try:
        observation_year = int(filename_date[:4])
    except ValueError:
        return False, None

    if jc_debug: print('DEBUG : observation_year = ', observation_year)

    # Insert a dash between the year and month.
    filename_date = filename_date[:4] + '-' + filename_date[4:]

    # Insert a dash between month and day and assign to observation date.
    observation_date = filename_date[:7] + '-' + filename_date[7:]

    if jc_debug: print('DEBUG : observation_date = ', observation_date)

    # Open dat data file in binary mode.
    with open(filename, 'rb') as dat_file:

        # Set the current position in the file at zero the beginning of the file.
        dat_file.seek(0, 0)

        '''
        John cooks data files come in two versions, variable and fixed formats.

        The easiest method to distinguish the 2 formats is to check the msb of the first byte in the file.
        If the most significant bit is high, then it is the time stamp of a fixed format file.
        If it is low, then it is the channel number of a variable format file.
        '''

        # Read first byte so we can check if first byte bit order is high or low.
        # JC sets the first bytes high for his old file format and low for the new format.

        first_byte = dat_file.read(1)

        # Low bit manipulation =  0x01
        # High bit manipulation = 0x80

        if (first_byte[0] & 0x80) == 0x80:
            if jc_debug: print('DEBUG : First byte bit order is set High. -- Fixed File Format!')
            bit_order = 'HIGH'
        else:
            if jc_debug: print('DEBUG : First byte bit order is set Low. -- Variable File Format!')
            bit_order = 'LOW'

        if bit_order == 'HIGH':
            number_of_channels = 3
            sample_interval = 5

            # set seek to beginning of file.
            dat_file.seek(0, 0)

        else:

            # start from beginning of file.
            dat_file.seek(0, 0)

            # read the first bytes this is the number of channels.
            number_of_channels_byte = dat_file.read(1)

            # number of channels
            number_of_channels = int(number_of_channels_byte[0])

            if number_of_channels > 0:
                pass
            else:
                print('ERROR : Number or channels is missing!!')
                return False

            # Seek from the current file position.
            dat_file.seek(0, 1)

            # read the first bytes this is the sample interval.
            sample_interval_byte = dat_file.read(1)

            # sample interval
            sample_interval = int(sample_interval_byte[0])

        if jc_debug:
            print('DEBUG : number_of_channels = ', number_of_channels)
            print('DEBUG : sample_interval = ', sample_interval)

        # Chunk size is the number of channels plus the second indentifier.
        chunk_size = 1 + number_of_channels

        # Create Metadata

        csv_data.append('Instrument.Importer.Format,JohnCook Data File')

        csv_data.append('Observer.Name,John Cook')

        csv_data.append('Observatory.Name,John Cook Observatory')

        csv_data.append('Observation.Notes,Replace this text with information about your observatory.')

        csv_data.append('Observation.Channel.Count,' + str(number_of_channels))

        n = 0
        for i in range(0, number_of_channels):
            csv_data.append('Observation.Channel.Name.%s,%s %s' % (str(n), 'Channel', str(n)))
            n += 1

        n = 0
        for i in range(0, number_of_channels):
            csv_data.append('Observation.Axis.Label.Y.%s,%s %s' % (str(n), 'Y Axis', str(n)))
            n += 1

        csv_data.append('Observation.Axis.Label.X,Time UTC')

        # Data sample string
        data_samples = ','

        # Simple way to break loop without errors.
        main_loop = True

        # Set hourly timestamp to none so we can use it to skip data if we haven't seen a timestamp
        hourly_timestamp = None

        # CSV_DATA line counter.
        csv_line_counter = 0

        # Main loop
        while main_loop:

            # Seek from the current file position.
            dat_file.seek(0, 1)

            # Read the first byte if it's bit order is high then we have a date stamp otherwise it's data or maybe EOF.
            byte_one = dat_file.read(1)

            # If byte_one is 0xFF and bit_order is LOW then we could have the end of the file.
            # The old data format doesn't use this it has a \r\n at EOF ....
            try:
                if byte_one[0] == 0xFF:

                    # if the byte is 0xFF we could be at the end of the file so we'll check the next three bytes for 0xFF.
                    dat_file.seek(0, 1)
                    chunk = dat_file.read(3)

                    if jc_chunk_debug:
                        print('DEBUG : EOF byte_one ', byte_one)
                        print('DEBUG : EOF chunk ', chunk)

                    # if the chunk is null then we have probably reach EOF and even if we haven't we can't continue.
                    if not chunk:
                        break

                    # Fixed format may end with '\r\n>' but maybe not?? Otherwise we probably have Variable Format data so
                    # we look for the additonal 3 x 0xFF that indicate EOF.
                    if chunk == b'\r\n>':
                        if jc_chunk_debug: print('DEBUG : EOF!')
                        break
                    elif chunk[0] == 0xFF and chunk[1] == 0xFF and chunk[2] == 0xFF:
                        if jc_chunk_debug: print('DEBUG : EOF!')
                        break

                elif (byte_one[0] & 0x80) == 0x80:

                    dat_file.seek(0,1)
                    chunk = dat_file.read(3)

                    date_stamp_minute = int(byte_one[0] & 0x7F)  # Encoded Most Significant Bit First.
                    date_stamp_hour = int(chunk[0])
                    date_stamp_day = int(chunk[1])
                    date_stamp_month = int(chunk[2])

                    if jc_debug:
                        print('DEBUG : =========================================')
                        print('DEBUG : date_stamp_minute = ', date_stamp_minute)
                        print('DEBUG : date_stamp_hour = ', date_stamp_hour)
                        print('DEBUG : date_stamp_day = ', date_stamp_day)
                        print('DEBUG : date_stamp_month = ', date_stamp_month)

                    # We store the hourly timestamp so we can increment the sample date and time later.
                    hourly_timestamp = datetime.datetime(observation_year, date_stamp_month, date_stamp_day,
                                                         date_stamp_hour, date_stamp_minute)

                else:

                    if hourly_timestamp is not None:
                        # As we got this far then we expect byte_one to be the seconds identifier.
                        time_seconds = int(byte_one[0])

                        # Check we actually have the seconds identifier if not we'll bail as
                        # whatever we have doesn't make sense.
                        if time_seconds > 59:
                            break

                        # Convert our hourly_timestamp to string format so we can append the current second identifier to it and
                        # prefix any single digit second identifier with zero.
                        data_datetime = hourly_timestamp.strftime('%Y-%m-%d,%H:%M:') + str(time_seconds).zfill(2)

                        # Now let's convert our above timestamp back to a datetime object.
                        data_datetime_object = datetime.datetime.strptime(data_datetime, '%Y-%m-%d,%H:%M:%S')

                        # Increment the data_datatime_object by sample_interval
                        data_datetime_object += datetime.timedelta(seconds=sample_interval)

                        # If minutes of data_datatime_object is greater than hourly_timestamp then increase hourly_timestamp
                        # minutes by one minute.
                        if hourly_timestamp.minute < data_datetime_object.minute:
                            hourly_timestamp += datetime.timedelta(seconds=60)

                        # Now read the next n bytes as denoted by the number of channels from the current position in the file.
                        dat_file.seek(0,1)

                        chunk = dat_file.read(number_of_channels)

                        # Check chunk is the correct size, if it isn't we've probably reached the EOF!
                        if len(chunk) != number_of_channels:
                            break
                        else:
                            # Get the actual channel samples.
                            for i in range(0, number_of_channels):
                                data_samples = data_samples + str(chunk[i]) + ','

                            # strip final comma as it's unwanted.
                            data_samples = data_samples.rstrip(',')

                            # prefix csv_datetime to data_samples.
                            data_samples = data_datetime + data_samples

                            if jc_chunk_debug: print('DEBUG : data_sample = ', data_samples)

                            # Append data_samples to csv_data which is were our process data is stored.
                            csv_data.append(data_samples)

                            # Set data samples ready to accept next csv_datetime and samples.
                            data_samples = ','

                            # increment csv_line_counter
                            csv_line_counter += 1

            except(IndexError, ValueError) as err:
                break

    dat_file.close()

    # The total length of the expected metadata keys.
    metadata_len = number_of_channels * 2 + 6
    # The total length of the CSV data plus the metadata
    calculated_csv_data_length = csv_line_counter + metadata_len

    if jc_debug:
        print('DEBUG : Calculated CVS data length : %s' % calculated_csv_data_length)
        print('DEBUG : CVS data list length : %s' % len(csv_data))

    # If csv_data length is not zero then we look like we have some data so we return True
    if len(csv_data) == calculated_csv_data_length:
        return True, csv_data
    else:
        print('ERROR : Calculated CVS data length is not equal to list length')
        return False, None


def radio_sky_pipe(filename, debug):
    '''
    # Translates Radio Sky Pipe SPD file to CSV

    #  NOTE :
    #  This function can not handle files with no timestamps.
    #  Timezone information can not be decoded as Jim Sky won't tell me how it relates to real timezones,
    #  so UTC is assumed.
    #  Only rudimentary metadata is saved using the Starbase metadata naming convention.

    # To run this function in another program you'll will need to include the doubledt_2_stddt and dd2dms functions.

    :param filename: including full path.
    :param debug: integer 0 - 2 with 0 being no debugs, 1 debugging on and 2 verbose debugs.
    :return: tuple <boolean, list>
    '''

    # Set up debugging
    if debug == 1:
        rsp_debug = True
        rsp_chunk_debug = False
    elif debug == 2:
        rsp_debug = True
        rsp_chunk_debug = True
    else:
        rsp_debug = False
        rsp_chunk_debug = False

    # CSV Data list
    csv_data = []

    # Channel labels list
    channel_labels = []

    # Y Axis Labels list
    y_axis_labels = []

    if rsp_debug: print('DEBUG : Radio Sky Pipe Converter')

    print('INFO : Processing file %s' % filename)

    try:

        # Open spd data file in binary mode.
        with open(filename, 'rb') as spd_file:

            # Set the current position in the file at zero at the beginning of the file.
            spd_file.seek(0, 0)

            # Read first 10 bytes which holds the skypipe version number.
            version = spd_file.read(10)

            # Unpack the first 10 bytes as a string.
            data = struct.unpack("10s", version)

            # Struct will unpack the bytes as tuple so we join each tuple item into one string.
            version = ''.join(str(i.decode()) for i in data)  # Skypipe Version Number.

            if rsp_debug: print("DEBUG : Version = ", version)

            # Seek from the current file position.
            spd_file.seek(0, 1)

            # Read the next eight bytes which holds the sample data start datetime.
            start_bytes = spd_file.read(8)

            '''  
            NOTE all doubles are unpacked little endian. 
            '''

            # Unpack the eight bytes as double.
            start_double = struct.unpack('<d', start_bytes)[0]

            ''' NOTE: Start / Finish times are not currently saved in csv file! '''

            # Call double to standard time function to convert double to normal time conventions.
            start_time = doubledt_2_stddt(start_double)  # Data Start Time

            if rsp_debug: print('DEBUG : Start Double = ', start_double)
            if rsp_debug: print('DEBUG : Start Time = ', start_time)

            # TODO Use the start data to create the filename ....  observation_date

            # Seek from the current file position.
            spd_file.seek(0, 1)

            # Read the next eight bytes which holds the sample data finish datetime.
            finish_bytes = spd_file.read(8)

            # Unpack the eight bytes as double.
            finish_double = struct.unpack('<d', finish_bytes)[0]

            # Call double to standard time function to convert double to normal time conventions.
            finish_time = doubledt_2_stddt(finish_double)  # Data Finish Time

            if rsp_debug:
                print('DEBUG : Finish Double = ', finish_double)
                print('DEBUG : Finish Time = ', finish_time)

            # Seek from the current file position.
            spd_file.seek(0, 1)

            # Read the next eight bytes which holds the latitude data.
            latitude_bytes = spd_file.read(8)

            # Unpack the eight bytes as double.
            latitude_double = struct.unpack('<d', latitude_bytes)[0]

            # Call degree decimal to degree, minutes, seconds function.
            latitude = dd2dms('lat', latitude_double)  # Data Finish Time

            if rsp_debug: print('DEBUG : Latitude Double = ', latitude_double)
            if rsp_debug: print('DEBUG : Latitude = ', latitude)

            # Seek from the current file position.
            spd_file.seek(0, 1)

            # Read the next eight bytes which holds the longitude data.
            longitude_bytes = spd_file.read(8)

            # Unpack the eight bytes as double.
            longitude_double = struct.unpack('<d', longitude_bytes)[0]

            # Call degree decimal to degree, minutes, seconds function.
            longitude = dd2dms('long', longitude_double)  # Data Finish Time

            if rsp_debug: print('DEBUG : Longitude Double = ', longitude_double)
            if rsp_debug: print('DEBUG : Longitude = ', longitude)

            # Seek from the current file position.
            spd_file.seek(0, 1)

            ''' NOTE: Max / Min Y are unused, so not currently saved in csv file! '''

            # Read the next eight bytes which holds the Max Y data.
            max_y_bytes = spd_file.read(8)

            # Unpack the eight bytes as double.
            max_y_double = struct.unpack('<d', max_y_bytes)[0]  # Max Y

            if rsp_debug: print('DEBUG : Max Y = ', max_y_double)

            # Seek from the current file position.
            spd_file.seek(0, 1)

            # Read the next eight bytes which holds the Min Y data.
            min_y_bytes = spd_file.read(8)

            # Unpack the eight bytes as double.
            min_y_double = struct.unpack('<d', min_y_bytes)[0]  # Min Y

            if rsp_debug: print('DEBUG : Min Y = ', min_y_double)

            # Seek from the current file position.
            spd_file.seek(0, 1)

            '''
            Note:   Timezone is not saved in CSV file as we don't know how to decode it currently.
                    The Skypipe documentation says the timezone is stored as a integer however VB stores integers
                    four bytes long which this isn't so I assumed integer stored as two bytes little endian as doubles
                    are stored little endian.
            '''

            # Read the next two bytes which holds the timezone data.
            timezone_bytes = spd_file.read(2)

            # Convert the two bytes to integer using little endian.
            timezone = int.from_bytes(timezone_bytes, byteorder='little')  # Timezone as int ???

            if rsp_debug: print('DEBUG : Timezone = ', timezone)

            # Seek from the current file position.
            spd_file.seek(0, 1)

            # Read the next ten bytes which holds the data source.
            source_bytes = spd_file.read(10)

            # Unpack the first 10 bytes as a string.
            source_strings = struct.unpack('10s', source_bytes)

            # Struct will unpack the bytes as tuple so we join each tuple item into one string.
            source = ''.join(str(i.decode()) for i in source_strings)  # Data Source

            if rsp_debug: print("DEBUG : Source  = ", source)

            # Seek from the current file position.
            spd_file.seek(0, 1)

            # Read the next twenty bytes which holds the author name.
            author_bytes = spd_file.read(20)

            # Unpack the first 20 bytes as a string.
            author_strings = struct.unpack('20s', author_bytes)

            # Struct will unpack the bytes as tuple so we join each tuple item into one string.
            author = ''.join(str(i.decode()) for i in author_strings)  # Author

            if rsp_debug: print("DEBUG : Author  = ", author)

            # Seek from the current file position.
            spd_file.seek(0, 1)

            # Read the next twenty bytes which holds the local name.
            localname_bytes = spd_file.read(20)

            # Unpack the first 20 bytes as a string.
            localname_strings = struct.unpack('20s', localname_bytes)

            # Struct will unpack the bytes as tuple so we join each tuple item into one string.
            localname = ''.join(str(i.decode()) for i in localname_strings)  # Local Name

            if rsp_debug: print("DEBUG : Local Name  = ", localname)

            # Seek from the current file position.
            spd_file.seek(0, 1)

            # Read the next forty bytes which holds the location name.
            location_bytes = spd_file.read(40)

            # Unpack the first 40 bytes as a string.
            location_strings = struct.unpack('40s', location_bytes)

            # Struct will unpack the bytes as tuple so we join each tuple item into one string.
            location = ''.join(str(i.decode()) for i in location_strings)  # Location

            if rsp_debug: print("DEBUG : Location  = ", location)

            # Seek from the current file position.
            spd_file.seek(0, 1)

            # Read the next two bytes which holds the number of channels starting from 1.
            channels_bytes = spd_file.read(2)

            ''' Again note I've made the assumption integers bytes are stored little endian.'''

            # Convert the two bytes to integer using little endian.
            number_of_channels = int.from_bytes(channels_bytes, byteorder='little')  # Number of Channels

            if number_of_channels > 0:
                pass
            else:
                print('ERROR : Number or channels is missing!!')
                return False

            if rsp_debug: print("DEBUG : Number of Channels  = ", str(number_of_channels))

            # Seek from the current file position.
            spd_file.seek(0, 1)

            # Read the next four bytes which is the length of the notes field stored as a long.
            note_length_bytes = spd_file.read(4)

            ''' 
            NOTE :  We need to check to see how many bytes the machine this code is running on implements longs as we 
                    need a longs to be four bytes long. 
            '''

            if struct.calcsize('@L') == 4:
                nl = '@L'
            elif struct.calcsize('=L') == 4:
                nl = '=L'

            # Unpack the note_length_bytes, number of bytes as long.
            note_length = struct.unpack(nl, note_length_bytes)[0]  # Note Length

            if rsp_debug: print("DEBUG : Note Length  = ", str(note_length))

            # Seek from the current file position.
            spd_file.seek(0, 1)

            # Read the next n bytes as determined by note_length which is skypipe metadata data notes.
            note_metadata_bytes = spd_file.read(note_length)

            if rsp_debug:
                print("DEBUG : Note Metadata Length  = ", len(note_metadata_bytes))
                print("DEBUG : Note Metadata Raw = ", str(note_metadata_bytes))

            # Struct will unpack the bytes as tuple however the metadata string with be at location 0
            # so we get that item only.
            note_metadata_strings = str(struct.unpack(str(note_length) + 's', note_metadata_bytes)[0])

            ''' 
            WARNING : The RSP Note field is horrendous to decode but we'll give our best shot.
            '''

            # We now split the note_metadata_strings up usign the the delimiters '*[[*' and '*]]*'
            RawNoteSplit = re.split('((\*\[\[\*)|(\*\]\]\*))', note_metadata_strings)

            '''
            # Next we remove '*[[*', '*]]*', NoneTypes, Blank Items, and Odd Characters from the RawNoteSplit list.
            # This a bit nasty but I can't see a better way of doing it at present.
            # We have to do a loop the loop to make sure everything is removed successfully.  
            '''

            for i in RawNoteSplit:
                for i in RawNoteSplit:
                    if i is None:
                        RawNoteSplit.remove(i)

                for i in RawNoteSplit:
                    if i == '*]]*':
                        RawNoteSplit.remove(i)

                for i in RawNoteSplit:
                    if i == '*[[*':
                        RawNoteSplit.remove(i)

                for i in RawNoteSplit:
                    if i == '':
                        RawNoteSplit.remove(i)

                for i in RawNoteSplit:
                    if i == "',)":
                        RawNoteSplit.remove(i)

            if rsp_debug:
                n = 0
                for i in RawNoteSplit:
                    print("item # %s %s %s" % (n, i, type(i)))
                    n += 1

            # Now we check the list we have has at least two items
            if len(RawNoteSplit) >= 2:
                pass
            else:
                if rsp_debug: print('DEBUG : Error - Unable to make sense of SPD metadata')
                return False

            # We should now have a list of where item one should be the observation note text if not we create string.
            if len(RawNoteSplit[0]) > 1:
                # Strip off unwanted (b' from start of string and convert all \r\n to single space.
                observation_note = str(RawNoteSplit[0]).strip("(b'").replace('\\r\\n', ' ')

                if rsp_debug: print('DEBUG : Observation Note = ', observation_note)

            '''
            Split item 1 in RawNoteSplit on \xff  there maybe more than two items in RawNoteSplit however
            those extra elements always appear to be a duplicate of item 1
            '''
            note_list = RawNoteSplit[1].split('\\xff')

            # Integer save variable.  Skypipe can store data sample in one of two ways as doubles or as integers.
            # Initial we assume data is stored as double so integer_save is set to False.
            integer_save = False

            # Iterate though the note_list and try and locate the metadata we want.
            for x in range(len(note_list)):
                # Look for strings starting CHL which is the channel labels.
                if note_list[x].startswith('CHL'):
                    # If channel label found subsitute CHL with space, then append name to channel_labels list.
                    channel_labels.append(re.sub(r'^CHL[0-9]', '', note_list[x]))

                y_axis_label = []
                x_axis_label = ''

                # Look for string starting with XALABEL which is the X axis label.
                if note_list[x].startswith('XALABEL'):
                    # If x axis label found subsitute XALABEL with space and set x_axis_label name.
                    x_axis_label = re.sub(r'^XALABEL', '', note_list[x])

                # Look for string starting with YALABEL which is the Y axis label.
                if note_list[x].startswith('YALABEL'):
                    # If y axis label found subsitute YALABEL with space and append to y_axis_label list.
                    y_axis_labels.append(re.sub(r'^YALABEL', '', note_list[x]))

                # Look for string starting with Integer Save and if we find it set integer_save to True.
                if note_list[x].startswith('Integer Save'):
                    integer_save = True

            if rsp_debug:
                print('DEBUG : channel labels = ', channel_labels)
                print('DEBUG : x_axis label = ', x_axis_label)
                print('DEBUG : y_axis label = ', y_axis_label)

                if integer_save:
                    print('DEBUG : Integer Save True')
                else:
                    print('DEBUG : Integer Save False')

            ''' Create Metadata ...'''

            csv_data.append('Instrument.Importer.Format,RadioSkyPipe')

            if len(version) != 0:
                csv_data.append('Rsp.Version,' + str(version))

            if len(author) == 0:
                csv_data.append('Observer.Name,UNKNOWN')
            else:
                csv_data.append('Observer.Name,' + str(author))

            if len(localname) == 0:
                csv_data.append('Observatory.Name,UNKNOWN')
            else:
                csv_data.append('Observatory.Name,' + str(localname))

            if len(location) == 0:
                csv_data.append('Observatory.Location,UNKNOWN')
            else:
                csv_data.append('Observatory.Location,' + str(location))

            if len(latitude) == 0:
                csv_data.append('Observatory.Latitude,UNKNOWN')
            else:
                csv_data.append('Observatory.Latitude,' + str(latitude))

            if len(longitude) == 0:
                csv_data.append('Observatory.Longitude,UNKNOWN')
            else:
                csv_data.append('Observatory.Longitude,' + str(longitude))

            if len(observation_note) == 0:
                csv_data.append('Observation.Notes,Replace this text with information about your observatory.')
            else:
                csv_data.append('Observation.Notes,' + str(observation_note))

            csv_data.append('Observation.Channel.Count,' + str(number_of_channels))

            n = 0
            if len(channel_labels) == 0:
                for i in range(0, number_of_channels):
                    csv_data.append('Observation.Channel.Name.%s,%s %s' % (str(n), 'Channel', str(n)))
                    n += 1
            else:
                for i in channel_labels:
                    csv_data.append('Observation.Channel.Name.%s,%s' % (str(n), str(i)))
                    n += 1

            n = 0
            if len(y_axis_labels) == 0:
                for i in range(0, number_of_channels):
                    csv_data.append('Observation.Axis.Label.Y.%s,%s %s' % (str(n), 'Y Axis', str(n)))
                    n += 1
            else:
                for i in y_axis_labels:
                    csv_data.append('Observation.Axis.Label.Y.%s,%s' % (str(n), str(i)))
                    n += 1

            if len(x_axis_label) == 0:
                csv_data.append('Observation.Axis.Label.X,Time UTC')
            else:
                csv_data.append('Observation.Axis.Label.X,' + str(x_axis_label))

            if len(source) != 0:
                csv_data.append('Rsp.source,' + str(source))

            ''' Data Parser...'''

            # Select data chunk size based on data save as integer or as double. Note: Dates are always doubles.
            # We set this here as read is at the top of the while loop.
            if integer_save:
                # Chunk size is a double followed by 2 byte integers times the number of channels.
                chunk_size = 8 + (
                        2 * number_of_channels)  # Chunk size is the total number of data bytes including date
            else:
                # Chunk size is a double followed by 2 byte integers times the number of channels.
                chunk_size = 8 + (8 * number_of_channels)

            # Simple counter for debug purposes.
            chunk_number = 1

            # Simple while loop to get each set of samples from binary data.
            while True:
                # Seek from the current file position.
                spd_file.seek(0, 1)

                # Get a chunk of data including the date.
                chunk = spd_file.read(chunk_size)

                if rsp_chunk_debug: print('DEBUG : Chunk Number = %s, Bytes = %s ' % (chunk_number, str(chunk)))

                # Check chunk is of the correct length otherwise we pass.
                if len(chunk) == chunk_size:
                    if rsp_chunk_debug: print('DEBUG : Chunk the right size')

                    if rsp_chunk_debug:
                        print('DEBUG : Chunk Item %s - Length %s ' % (chunk_number, len(chunk[0:8])))
                        print('DEBUG : Chunk Item %s - Chunk %s ' % (chunk_number, str(chunk[0:8])))

                    # Unpack the double date
                    date_double = struct.unpack('<d', chunk[0:8])[0]

                    # Chunk_slice and chunk_end_slice are always eight bytes to start with
                    chunk_slice = 8
                    chunk_end_slice = 8

                    # A simple string to hold the chunk data samples.
                    data_samples = ''

                    # Iterate over data channels
                    for i in range(number_of_channels):
                        # Process data as integer if integer_save is true.
                        if integer_save:
                            # Increase chunk_end_slice by two bytes as the channel data is a two byte integer.
                            chunk_end_slice += 2

                            # Get the data_chunk from chunk
                            data_chunk = chunk[chunk_slice:chunk_end_slice]

                            if rsp_chunk_debug:
                                print('DEBUG : chunk_slice = %s, chunk_next_slice = %s' % (
                                    str(chunk_slice), str(chunk_end_slice)))
                                print('DEBUG : Data Chunk Size = ', len(data_chunk))

                            # Get integer from two bytes encoded little endian and append to data_sample.
                            # Here we also append a comma, this of courses means we'll have one to many comma's in
                            # the data_sample however we'll remove that later with a simple rstrip.
                            data_samples = data_samples + str(
                                int.from_bytes(chunk[chunk_slice:chunk_end_slice], byteorder='little')) + ','

                            # Now we set chuck_slice to chunk_end_slice so we can increment to the next channel of data.
                            chunk_slice = chunk_end_slice

                        else:
                            # Increase chunk_end_slice by eight bytes as the channel data is double.
                            chunk_end_slice += 8

                            # Get the data_chunk from chunk
                            data_chunk = chunk[chunk_slice:chunk_end_slice]

                            if rsp_chunk_debug:
                                print('DEBUG : chunk_slice = %s, chunk_next_slice = %s' % (
                                    str(chunk_slice), str(chunk_end_slice)))
                                print('DEBUG : Data Chunk Size = ', len(data_chunk))

                            # Get double from eights bytes and append to data_sample.
                            # Here we also append a comma, this of courses means we'll have one to many comma's in
                            # the data_sample however we'll remove that later with a simple rstrip.
                            data_samples = data_samples + str(
                                struct.unpack('<d', chunk[chunk_slice:chunk_end_slice])[0]) + ','

                            # Now we set chuck_slice to chunk_end_slice so we can increment to the next channel of data.
                            chunk_slice = chunk_end_slice

                # Check we had chunk if not we have reached EOF.
                if not chunk:
                    if rsp_chunk_debug: print('DEBUG : EOF')
                    # Close the file
                    spd_file.close()
                    break
                else:

                    # Append data to csv_data set.
                    csv_data.append(
                        str(doubledt_2_stddt(date_double)).replace(' ', ',') + ',' + data_samples.rstrip(','))

                    # Increment chunk number
                    chunk_number += 1

    except FileNotFoundError as err:
        print('ERROR : File Error = ', err)
        return False, None
    except struct.error as err:
        print('ERROR : Unpack Error = ', err)
        return False, None

    # File format
    file_format = 'RadioSkyPipe'

    # If csv_data length is not zero then we look like we have some data so we return True
    if len(csv_data) != 0:
        return True, csv_data
    else:
        return False, None


def main():
    # Set tverse false so we can set true if transverse file system is set.
    tverse = False

    # Set the home where the files we wish to process reside either by the input_path variable or -i arg.

    if args.indir is None:
        home = input_path
    else:
        if args.indir:
            home = args.indir
        else:
            print('\r\nERROR : Please specify location where files to be processed resides - bailing!!')
            return

    # Checking the input folder exists if not bail!.
    if not os.path.exists(input_path):
        print('\r\nERROR : Files to be processed location doesn\'t exist - bailing!!')
        return

    # Set the location where the files we've processed will be stored, specified
    # either by the output_path variable or -o arg.
    if args.outdir is None:
        output = output_path
    else:
        if args.outdir:
            output = args.outdir
        else:
            print('\r\nERROR : Please specify processed file output folder - bailing!!')
            return

    # Check output folder exists.
    try:
        if not os.path.exists(output) and not args.p:
            print("\r\nWARNING : Output directory doesn't exist so creating it....")
            os.makedirs(output)
    except OSError as error:
        print('\r\nERROR : Unable to create output folder %s ' % error)
        return

    # Set transverse either or true or false based on -t arg
    if transverse is not None:
        tverse = True
    else:
        if args.t:
            tverse = True

    # a simple list to hold the files we want to process.
    files_2b_processed = []

    if not tverse:

        for file in os.listdir(input_path):
            # Check file is actually a file.  ;-)
            if os.path.isfile(os.path.join(input_path, file)):
                # Append filename and path to list.
                files_2b_processed.append(os.path.join(input_path, file))

    else:

        for dirName, subDir, fileList in os.walk(input_path, topdown=False, onerror=None, followlinks=False):
            for file in fileList:
                # Check file is actually a file.  ;-)
                if os.path.isfile(os.path.join(dirName, file)):
                    # Append filename and path to list.
                    files_2b_processed.append(os.path.join(dirName, file))

    # Check files_2b_processed isn't empty.
    if len(files_2b_processed) == 0:
        print('WARNING : No Files Found!! - Bailing.')
        return

    for i in files_2b_processed:
        # Reset the metadata and clear the csv_data list
        # metadata_creator('clear')

        # Set process_data to False
        process_data = False

        if i.endswith('.csv') or i.endswith('.txt'):
            print('WARNING : File is already in CSV format %s' % i)
            # Get original filename
            original_filename = os.path.basename(os.path.normpath(i))

            # Either output new file to new path or preserve file path.
            if not args.p:
                # prefix output path with new_filename
                out_file = os.path.join(output, original_filename)

                try:
                    copyfile(i, out_file)
                except OSError as err:
                    print('ERROR : Unable to move %s %s' % (original_filename, err))
                    print()
                else:
                    print('INFO : Moved file %s to %s' % (original_filename, out_file))

            else:
                # As the file already exists in this file path we do nothing.
                pass

        if i.endswith('.dat'):
            status, data = john_cook_data(i, debug)
            if not status:
                print('WARNING : Unable to process %s' % i)
            else:
                process_data = True
                # Get original filename
                original_filename = os.path.basename(os.path.normpath(i))
                # Rename file with new suffix
                new_filename = Path(original_filename).stem + ".csv"

                # Either output new file to new path or preserve file path.
                if not args.p:
                    # prefix output path with new_filename
                    out_file = os.path.join(output, new_filename)
                else:
                    # prefix original path with new_filename
                    out_file = os.path.join(os.path.dirname(os.path.abspath(i)), new_filename)

        if i.endswith('.spd'):
            status, data = radio_sky_pipe(i, debug)
            if not status:
                print('WARNING : Unable to process %s' % i)
            else:
                process_data = True
                # Get original filename
                original_filename = os.path.basename(os.path.normpath(i))
                # Rename file with new suffix
                new_filename = Path(original_filename).stem + ".csv"

                # Either output new file to new path or preserve file path.
                if not args.p:
                    # prefix output path with new_filename
                    out_file = os.path.join(output, new_filename)
                else:
                    # prefix original path with new_filename
                    out_file = os.path.join(os.path.dirname(os.path.abspath(i)), new_filename)

        # If process_data is true we can give it ago at creating the metadata and then creating the csv file.
        if process_data:
            # Check to see if new file already exists.
            if not os.path.exists(out_file):
                # Open new file in append mode.
                f = open(out_file, "a", newline='', encoding='utf-8')
                # for each item in data list write it to the file with linefeed and carriage return appended.
                for i in data:
                    f.write(i + '\n')

                # Close the file.
                f. close()

                print('INFO : New file created - %s' % out_file)
            else:
                print('ERROR : File exists unable to create - %s ' % out_file)


main()
