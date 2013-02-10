gst2paje
========

A script to convert GStreamer debug traces to Pajé file format

###Some components are required

- gstparser.py, written by Serge Emteu and modified by myself to fit to Pajé timestamps, and provided here.
  It allows to transform a gst debug stream in a readable csv file.

- poti C library, written by Lucas Schnorr, providing some functions to generate paje trace files.
  You need to download it and compile it before launching gst2paje.py:

        $ git clone https://github.com/schnorr/poti.git
        $ cd poti       
        $ mkdir build       
        $ cd build       
        $ cmake ..       
        $ make       
        $ cp libpoti.so.4.2 ../../libpoti.so

###Generate a csv file

- when you launch your gst-debug application, redirect the std stream to a file
- then, execute gstparser.py:

        $ ./gstparser.py gst-stream gst-trace.csv
        
- then, execute gst2paje.py:

        $ ./gst2paje.py gst-trace.csv > gst-trace.pj

