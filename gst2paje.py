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

libpoti='./libpoti.so'

class Function:
  def __init__(self, name):
    self.name =name

class DebugLevel:
  def __init__(self, name):
    self.name =name
    self.function ={}

class Thread:
  def __init__(self, name):
    self.name =name
    self.debuglevel ={}
    self.currentfunction =0#TODO think about multicore management
    
class Process:
  def __init__(self, name):
    self.name =name
    self.thread ={}

class Container:
  def __init__(self, name, containerType):
    self.name =name
    self.containerType =containerType

#Parameters checking
if (len(sys.argv) < 2):
    print ("Usage : " + sys.argv[0] + " gstreamertrace.csv > pajetrace.pj")
    exit(-1)

#Getting the inputs
csvfile = sys.argv[1]

csvstream = open(csvfile, 'r')
csvstreammod = csv.reader(csvstream, delimiter=',')

#ctypes.CDLL(libpoti).poti_open(pajefile)
#ctypes.CDLL(libpoti).poti_init('w')
#Dump the pajeheader
#First parameter is a boolean indicating a basic header or not
#Second parameter is a boolean indicating an old header or not

ctypes.CDLL(libpoti).poti_header(0, 0)

#Defining the types
ctypes.CDLL(libpoti).poti_DefineContainerType("Root", "0", "Root")
ctypes.CDLL(libpoti).poti_DefineContainerType("ProcessID", "Root", "ProcessID")
ctypes.CDLL(libpoti).poti_DefineContainerType("ThreadID", "ProcessID", "ThreadID")
ctypes.CDLL(libpoti).poti_DefineContainerType("DebugLevel", "ThreadID", "DebugLevel")
ctypes.CDLL(libpoti).poti_DefineContainerType("Function", "DebugLevel", "Function")
ctypes.CDLL(libpoti).poti_DefineStateType("State", "Function", "State")

#Define values and color for the State type
ctypes.CDLL(libpoti).poti_DefineEntityValue("ERROR", "State", "Error", "1.0 0.0 0.0")#red
ctypes.CDLL(libpoti).poti_DefineEntityValue("WARNING", "State", "Warning", "1.0 0.4 0.")#orange
ctypes.CDLL(libpoti).poti_DefineEntityValue("FIXME", "State", "Fixme", "0.0 0.0 1.0")#blue
ctypes.CDLL(libpoti).poti_DefineEntityValue("INFO", "State", "Info", "0.0 1.0 0.0")#green
ctypes.CDLL(libpoti).poti_DefineEntityValue("DEBUG", "State", "Debug", "1.0 0.8 0.0")#yellow
ctypes.CDLL(libpoti).poti_DefineEntityValue("LOG", "State", "Log", "0.4 0.4 0.4")#dark gray
ctypes.CDLL(libpoti).poti_DefineEntityValue("TRACE", "State", "Trace", "0.0 0.0 0.0")#black
ctypes.CDLL(libpoti).poti_DefineEntityValue("IDLE", "State", "Idle", "0.7 0.7 0.7")#light gray


#Create Container Machiiiiine = Root
ctypes.CDLL(libpoti).poti_CreateContainer(c_double(0.00), "Machiiiiine", "Root", "0", "Machiiiiine")
container=[]
container.append(Container("Machiiiiine", "Root"))

#Parsing de la trace

process={}
firstline=1
previousfunction=0

for line in csvstreammod:
  if firstline:
    firstline=0
  elif line:
    if not process.has_key(line[1]):
      ctypes.CDLL(libpoti).poti_CreateContainer(c_double(float(line[0])), line[1], "ProcessID", "Machiiiiine", line[1])
      container.append(Container(line[1], "ProcessID"))
      process[line[1]]= Process(line[1])
    if not process[line[1]].thread.has_key(line[2]): 
      ctypes.CDLL(libpoti).poti_CreateContainer(c_double(float(line[0])), line[2], "ThreadID", line[1], line[2])
      container.append(Container(line[2], "ThreadID"))
      process[line[1]].thread[line[2]] = Thread(line[2])
    if not process[line[1]].thread[line[2]].debuglevel.has_key(line[5]): 
      ctypes.CDLL(libpoti).poti_CreateContainer(c_double(float(line[0])), line[5] + "_on_" + line[2], "DebugLevel", line[2], line[5] + "_on_" + line[2])
      container.append(Container(line[5] + "_on_" + line[2], "DebugLevel"))
      process[line[1]].thread[line[2]].debuglevel[line[5]] = DebugLevel(line[5])
    if not process[line[1]].thread[line[2]].debuglevel[line[5]].function.has_key(line[8]): 
      ctypes.CDLL(libpoti).poti_CreateContainer(c_double(float(line[0])), line[8] + "_dbg_" + line[5] + "_on_" + line[2], "Function", line[5], line[8] + "_dbg_" + line[5] + "_on_" + line[2])
      container.append(Container(line[8] + "_on_" + line[2], "Function"))
      process[line[1]].thread[line[2]].debuglevel[line[5]].function[line[8]] = Function(line[8])
#    if process[line[1]].thread[line[2]].currentfunction:
#/!\We admit only one core is used for the application and only one thread is running at the same time
    if previousfunction:
#      ctypes.CDLL(libpoti).poti_SetState(c_double(float(line[0])), process[line[1]].thread[line[2]].currentfunction + "_on_" + line[2], "State", "IDLE")
      ctypes.CDLL(libpoti).poti_SetState(c_double(float(line[0])), previousfunction, "State", "IDLE")
#    process[line[1]].thread[line[2]].currentfunction=line[8]
    previousfunction= line[8] + "_dbg_" + line[5] + "_on_" + line[2]
    ctypes.CDLL(libpoti).poti_SetState(c_double(float(line[0])), line[8] + "_dbg_" + line[5] + "_on_" + line[2], "State" , line[3])
    timestamp=float(line[0])

container.reverse()
#Closing containers
for i in container:
  ctypes.CDLL(libpoti).poti_DestroyContainer(c_double(timestamp+0.000000001), i.containerType, i.name)

#Closing files
csvstream.close()
