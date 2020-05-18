"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-19

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
from dwfconstants import *
import math
import time
import matplotlib.pyplot as plt
import sys
import numpy as np

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

#declare ctype variables
hdwf = c_int()
sts = c_byte()
rgdSamples = (c_double*16384)()
channel = c_int(0)
pulse = 300e-5
secPosition = 0.0185

print("rgdSamples: ", rgdSamples)

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

#open device
print("Opening first device")
# dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))
dwf.FDwfDeviceConfigOpen(c_int(-1), c_int(1), byref(hdwf))

print("hdwf.value", hdwf.value)

if hdwf.value == hdwfNone.value:
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(szerr.value)
    print("failed to open device")
    quit()

cBufMax = c_int()
dwf.FDwfAnalogInBufferSizeInfo(hdwf, 0, byref(cBufMax))

print("Device buffer size: "+str(cBufMax.value)) 

#set up acquisition
print("Setting up acquisition")
dwf.FDwfAnalogInFrequencySet(hdwf, c_double(800000.0))
dwf.FDwfAnalogInBufferSizeSet(hdwf, c_int(16384))
dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(-1), c_bool(True))
dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(-1), c_double(0.2))
dwf.FDwfAnalogInChannelFilterSet(hdwf, c_int(-1), filterDecimate)

#set up trigger
print("Setting up trigger")
dwf.FDwfAnalogInTriggerAutoTimeoutSet(hdwf, c_double(0)) #disable auto trigger
dwf.FDwfAnalogInTriggerSourceSet(hdwf, trigsrcExternal1) #one of the external channels
dwf.FDwfAnalogInTriggerTypeSet(hdwf, trigtypeEdge)
dwf.FDwfAnalogInTriggerChannelSet(hdwf, c_int(0)) # first channel
dwf.FDwfAnalogInTriggerLevelSet(hdwf, c_double(0.5)) # 0.5V
dwf.FDwfAnalogInTriggerConditionSet(hdwf, trigcondRisingPositive)
dwf.FDwfAnalogInTriggerPositionSet(hdwf, c_double(secPosition))

# #wait at least 2 seconds for the offset to stabilize
# time.sleep(2)

# Set up pulse out
print("Setting up analog out pulse")
dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(0))

dwf.FDwfAnalogOutNodeEnableSet(hdwf, channel, AnalogOutNodeCarrier, c_bool(True))
dwf.FDwfAnalogOutIdleSet(hdwf, channel, DwfAnalogOutIdleOffset)
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, channel, AnalogOutNodeCarrier, funcSquare)
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, channel, AnalogOutNodeCarrier, c_double(0)) # low frequency
dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, channel, AnalogOutNodeCarrier, c_double(5))
dwf.FDwfAnalogOutNodeOffsetSet(hdwf, channel, AnalogOutNodeCarrier, c_double(0))
dwf.FDwfAnalogOutRunSet(hdwf, channel, c_double(pulse)) # pulse length
dwf.FDwfAnalogOutWaitSet(hdwf, channel, c_double(0)) # wait
dwf.FDwfAnalogOutRepeatSet(hdwf, channel, c_int(1)) # repeat once

for capture in range(100):
    print("Starting oscilloscope")
    dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(1))

    # Wait for scope to be ready
    time.sleep(0.0001)

    print("Generating pulse")
    dwf.FDwfAnalogOutConfigure(hdwf, channel, c_bool(True))

    while True:
        dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
        if sts.value == DwfStateDone.value:
            break
        time.sleep(0.0001)
    print("Acquisition done")

    dwf.FDwfAnalogInStatusData(hdwf, 0, rgdSamples, 16384) # get channel 1 data


    #plot window
    dc = sum(rgdSamples)/len(rgdSamples)
    print("DC: "+str(dc)+"V")

    test_array = np.fromiter(rgdSamples, dtype = np.float)

    savefilename = str('Captures/') + str(capture) + '.txt'

    np.savetxt(savefilename, test_array, delimiter=',')

    print(test_array.shape)
    plt.plot(np.fromiter(rgdSamples, dtype = np.float))
    # plt.show()

    # Briefly show plot
    plt.pause(0.001)
    plt.clf()

dwf.FDwfDeviceCloseAll()
