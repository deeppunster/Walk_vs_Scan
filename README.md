# Walk_vs_Scan
Sample program to compare how to use Python’s os.walk vs. os.scandir to
traverse a directory structure and time each method.

This is a self-contained program in Python to demonstrate how to use os
.walk and os.scandir.

Included in this program are:
-   How to exclude directories (e.g. .git)
-   A simplified timer class based on the context manager.



Usage: NewWalkVsScan.py [-h] [-d ROOTDIR] [-o OUTPUT]

Test using os.walk vs. using os.scandir to traverse a directory structure.

optional arguments:
  -h, --help            show this help message and exit
  -d ROOTDIR, --rootdir ROOTDIR
                        root directory of tree to be traversed
  -o OUTPUT, --output OUTPUT
                        output file to contain the results of walk vs. scan

