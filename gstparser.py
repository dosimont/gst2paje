#! /usr/bin/env python

#     
#     gstparser : this program allows to convert a gstreamer debug flow to a readable trace 
#    
#     Original Author : Serge Emteu
#     Modified by : Damien Dosimont <damien.dosimont@gmail.com>
#

"""
Runtime script for processing a file a script and using a program to extract progressively pattern from the stream
"""
import commands
#import pdb;pdb.set_trace()
import shlex, subprocess
import sys
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.pyplot import *
from numpy import *


#main

if (len(sys.argv) < 3):
    print ("Usage : " + sys.argv[0] + " input_file output_file")
    exit(-1)


#Getting the inputs
input_file = sys.argv[1]
output_file = sys.argv[2]

input_stream = open(input_file, 'r')
output_stream = open(output_file, 'w')

#line = input_stream.readline().rstrip('\r\n').split(' ')

output = "#timestamp,processID,ThreadID,DebugCategory,UnknowInfo,DebugLevel,source_file,line,function,object,message\n"
output_stream.write(output)

for line in input_stream:
    line = line.rstrip('\r\n').split('\x1b')
    #print line
    timestamp = line[0].strip().split(':')
    if(timestamp[0].isdigit() and timestamp[1].isdigit()):
        tmp = timestamp[2].split('.')
        ts = (int(tmp[0]))
        ts = ts + (int(timestamp[1]) * 60)
        ts = ts + (int(timestamp[0]) * 3600)
        time = (str(ts)+'.'+str(tmp[1])
        
        #Getting process ID
        process_id = line[1][line[1].find('m') + 1 : len(line[1])].strip()
        
        #Getting thread ID
        thread_id = line[2][line[2].find('m') + 1 : len(line[2])].strip()

        #Getting DebugCategory
        debugCategory = line[3][line[3].find('m') + 1 : len(line[3])].strip()

        #Getting unknow info (Not interessant information)
        unknownInfo = line[4][line[4].find('m') + 1 : len(line[4])].strip()

        #Getting DebugLevel and source file
        data = line[5][line[5].find('m') + 1 : len(line[5])].strip().split(' ', 1)
        debugLevel = data[0].strip()
        sdata = data[1].split(':')
        src = sdata[0]
        _line = sdata[1]
        _function = sdata[2]
        _object = sdata[3].lstrip('<').rstrip('>')

        #Getting message
        message = line[6][line[6].find('m') + 1 : len(line[6])].strip()
        
        output_stream.write(time + ',' + process_id + ',' + thread_id + ',' + debugCategory + ',' + unknownInfo + ',' + debugLevel + ',' +
                            src + ',' + _line + ',' + _function + ',' + _object + ',' + '\'' + message + '\'' + '\n')
        #print time, process_id, thread_id, debugCategory, unknownInfo, debugLevel, src, _line, _function, _object, message
       
    
input_stream.close()
output_stream.close()
