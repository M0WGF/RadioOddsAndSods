# VLF Data Converter Tool

**VLF Data Converter Tool Overview :** 

The tool will convert John Cook data files and Radio Skypipe data files to CSV.

It can convert all .spd and .dat files in the current directory or sub-directories.

The processed files can either be saved to a defined folder or in the original location of the unprocessed file.

The following four parameters can be set in the top of the python file under the copyright notice.

input_path : The folder or base folder where the files to be processed reside.
output_path : The output folder where processed files will be saved unless preserve is set.
preserve : Save the processed files to the location of the original file.
transverse : Follow directory structure beneath the base folder.

The above parameter can also be set from the command line. 

usage: datspd2csv.py [-h] [-i INDIR] [-o OUTDIR] [-p] [-t] [-v] [-V]

optional arguments:

  -h, --help            show this help message and exit
  
  -i INDIR, --i INDIR   Input files directory. Can be made persistent by
                        editing the parameter input_path in the code.
                        
  -o OUTDIR, --o OUTDIR Output files directory. Can be made persistent by
                        editing the parameter output_path in the code
                        
  -p, --p               Set the output path to the same as input path. Can be
                        set persistent by setting the parameter preserve to
                        True in the code.
                        
  -t, --t               Transverse input path subdirectories. Can be set to
                        bepersistent by setting parameter transverse to True in
                        the code.
                        
  -v, --v               Enable debugging -v or -vv for really verbose
                        debugs.You may want to redirect stdout to a file as
                        -vv is very verbose.
                        
  -V, --V               Print version number.
