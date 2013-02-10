#! /usr/bin/env python

#     
#     gst2paje : this program allows to convert a gstreamer debug trace to paje trace format 
#    
#     Copyright (C) 2012 Damien Dosimont <damien.dosimont@gmail.com>
#    
#     This program is free software; you can redistribute it and/or modify it
#     under the terms of the GNU General Public License as published by the Free
#     Software Foundation; either version 3 of the License, or (at your option)
#     any later version.
#    
#     This program is distributed in the hope that it will be useful, but WITHOUT
#     ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#     FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#     more details.
#    
#     You should have received a copy of the GNU General Public License along with
#     this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import csv, math
import ctypes
from ctypes import *

class Function:
  def __init__(self, name):
    self.name =name

class Thread:
  def __init__(self, name):
    self.name =name
    self.function ={}
    self.currentfunction =0
    
class Process:
  def __init__(self, name):
    self.name =name
    self.thread ={}


#Parameters checking
if (len(sys.argv) < 3):
    print ("Usage : " + sys.argv[0] + " gstreamertrace.csv pajetrace.pj")
    exit(-1)

#Getting the inputs
csvfile = sys.argv[1]
pajefile = sys.argv[2]

csvstream = open(csvfile, 'r')
csvstreammod = csv.reader(csvstream, delimiter=',')
pajestream = open(pajefile, 'w')

#First, dump the pajeheader
#First parameter is a boolean indicating a basic header or not
#Second parameter is a boolean indicating an old header or not

ctypes.CDLL('./poti.so').poti_header(0, 0);

#Defining my types
ctypes.CDLL('./poti.so').poti_DefineContainerType("Root", "0", "Root")
ctypes.CDLL('./poti.so').poti_DefineContainerType("ProcessID", "Root", "ProcessID")
ctypes.CDLL('./poti.so').poti_DefineContainerType("ThreadID", "ProcessID", "ThreadID")
#ctypes.CDLL('./poti.so').poti_DefineContainerType("DebugLevel", "ThreadID", "DebugLevel")
#ctypes.CDLL('./poti.so').poti_DefineContainerType("Source_file", "ThreadID", "Source_file")
ctypes.CDLL('./poti.so').poti_DefineContainerType("Function", "ThreadID", "Function")
ctypes.CDLL('./poti.so').poti_DefineStateType("State", "Function", "State")

#Define values and color for the STATE type
ctypes.CDLL('./poti.so').poti_DefineEntityValue("r", "State", "running", "0.0 1.0 0.0")#TODO manage debug lvl
ctypes.CDLL('./poti.so').poti_DefineEntityValue("i", "State", "idle", "0.3 0.3 0.3")

ctypes.CDLL('./poti.so').poti_CreateContainer(c_double(0.00), "Machiiiiine", "Root", "0", "Machiiiiine")

#Parsing de la trace

process_dict={}
threadid=[]
firstline=1

for line in csvstreammod:
  if firstline:
    firstline=0
  elif line:
    if not process_dict.has_key(line[1]):
      ctypes.CDLL('./poti.so').poti_CreateContainer(c_double(float(line[0])), line[1], "ProcessID", "Machiiiiine", line[1])
      process_dict[line[1]]= Process(line[1])
    if not process_dict[line[1]].thread.has_key(line[2]): 
      ctypes.CDLL('./poti.so').poti_CreateContainer(c_double(float(line[0])), line[2], "ThreadID", line[1], line[2])
      process_dict[line[1]].thread[line[2]] = Thread(line[2])
    if not process_dict[line[1]].thread[line[2]].function.has_key(line[8]): 
      ctypes.CDLL('./poti.so').poti_CreateContainer(c_double(float(line[0])), line[8], "Function", line[2], line[8])
      process_dict[line[1]].thread[line[2]].function[line[8]] = Function(line[8])
    if process_dict[line[1]].thread[line[2]].currentfunction:
      ctypes.CDLL('./poti.so').poti_PushState(c_double(float(line[0])), process_dict[line[1]].thread[line[2]].currentfunction, "State", "i")
    process_dict[line[1]].thread[line[2]].currentfunction=line[8]
    ctypes.CDLL('./poti.so').poti_PushState(c_double(float(line[0])), line[8], "State", "r")

  #Closing containers
csvstream.close()
pajestream.close()
