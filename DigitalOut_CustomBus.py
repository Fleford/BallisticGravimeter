"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-19

   Requires:                       
       Python 2.7, 3
   Description:
   Generates a custom pattern on 16 channels with 16 samples
   Captures 32 samples having the generated data in middle
"""

from ctypes import *
from dwfconstants import *
import math
import sys
import time
import matplotlib.pyplot as plt
import numpy

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

hdwf = c_int()

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

print("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == 0:
    print("failed to open device")
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    quit()

print("Configuring Digital Out")

hzRate = 5e2    # frequency
cChannels = 16
cSamples = 4
cBytes = int(math.ceil(cSamples/8))
rgSamples = [0x0003,0x0006,0x000C,0x0009]
# rgSamples = [0x0009,0x000C,0x0006,0x0003]

hzDO = c_double()
dwf.FDwfDigitalOutInternalClockInfo(hdwf, byref(hzDO))

for channel in range(cChannels): # configure output channels
    rgBits = (cBytes*c_byte)() # custom bit array for each channel
    for sample in range(cSamples): # using the bits from samples array construct the bit array for the channel
        if(1&(rgSamples[int(sample)]>>channel)) : rgBits[int(sample/8)] |= 1<<(sample&7)
        else : rgBits[int(sample/8)] &= ~(1<<(sample&7))
    dwf.FDwfDigitalOutEnableSet(hdwf, c_int(channel), c_int(1))
    dwf.FDwfDigitalOutTypeSet(hdwf, c_int(channel), DwfDigitalOutTypeCustom)
    dwf.FDwfDigitalOutDividerSet(hdwf, c_int(channel), c_int(int(hzDO.value/hzRate))) # set sample rate
    dwf.FDwfDigitalOutDataSet(hdwf, c_int(channel), byref(rgBits), c_int(cSamples))

dwf.FDwfDigitalOutRunSet(hdwf, c_double(cSamples/hzRate)) # 160ns = 2*8 bits /100MHz = 16 bits * 10ns
dwf.FDwfDigitalOutRepeatSet(hdwf, c_int(100)) # once

print("outputting time baby!")
dwf.FDwfDigitalOutConfigure(hdwf, c_int(1))
sts = c_byte()
while True:
    dwf.FDwfDigitalOutStatus(hdwf, byref(sts))
    if sts.value == stsDone.value:
        break

dwf.FDwfDeviceCloseAll()

