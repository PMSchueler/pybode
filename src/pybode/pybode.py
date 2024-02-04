# pybode.py
# Program to plot bode diagrams using DHO800/DHO900 and  JDS6600 or DG1000Z

# Jan Böhmer (c) 2019
# published under MIT license. See file "LICENSE" for full license text

# Derived from https://github.com/jbtronics/DS1054_BodePlotter

# Peter Matthias Schueler (c) 2023
# added DHO800/DHO900 support using pydho800 and pyserial

import numpy as np
import time
    
import argparse

import matplotlib.pyplot as plt

import scipy.signal

from pydho800.pydho800 import PYDHO800
from pydg1000z.pydg1000z import PYDG1000Z

from labdevices.scpi import SCPIDeviceEthernet
from labdevices.functiongenerator import FunctionGenerator, FunctionGeneratorWaveform, FunctionGeneratorModulation

    
parser = argparse.ArgumentParser(
    description="This program plots Bode Diagrams of a DUT using an Rigol DG1000Z and Rigol DHO800/DHO900")

parser.add_argument('MIN_FREQ', metavar='min', type=float, help="The minimum frequency for which should be tested")
parser.add_argument('MAX_FREQ', metavar='max', type=float, help="The maximum frequency for which should be tested")
parser.add_argument('COUNT', metavar='N', nargs="?", default=50, type=int,
                    help='The number of frequencies for which should be probed')
parser.add_argument("--osc_ip", default="None", dest="OSC_IP",
                    help="The IP address of the DHO800. ")
parser.add_argument("--awg_ip", default="None", dest="AWG_IP",
                    help="The IP address of the DG1000Z.")
parser.add_argument("--awg_voltage", dest="VOLTAGE", default=5, type=float,
                    help="The amplitude of the signal used for the generator")
parser.add_argument("--step_time", dest="TIMEOUT", default=0.00, type=float,
                    help="The pause between to measurements in ms.")
parser.add_argument("--use_manual_settings", dest="MANUAL_SETTINGS", action="store_true",
                    help="When this option is set, the options on the oscilloscope for voltage and time base are not changed by this program.")
parser.add_argument("--output", dest="file", type=argparse.FileType("w"),
                    help="Write the measured data to the given CSV file.")
parser.add_argument("--no_plots", dest="PLOTS", action="store_false",
                    help="When this option is set no plots are shown. Useful in combination with --output")

args = parser.parse_args()

if args.OSC_IP == "None":
    exit("No OSC address in command line")
else:
    OSC_IP = args.OSC_IP
    
if args.AWG_IP == "None":
    exit("No AWG address in command line")
else:        
    AWG_IP = args.AWG_IP
    
DEFAULT_PORT = args.AWG_PORT
MIN_FREQ = args.MIN_FREQ
MAX_FREQ = args.MAX_FREQ
STEP_COUNT = args.COUNT

# Do some validity checs
if MIN_FREQ < 0 or MAX_FREQ < 0:
    exit("Frequencies has to be greater 0!")

if MIN_FREQ >= MAX_FREQ:
    exit("MAX_FREQ has to be greater then min frequency")

if STEP_COUNT <= 0:
    exit("The step count has to be positive")

TIMEOUT = args.TIMEOUT

AWG_CHANNEL1 = 1
AWG_CHANNEL2 = 2
AWG_VOLT = args.VOLTAGE

print("Init AWG")

with PYDG1000Z(address=AWG_IP) as awg:
    
    awg.set_channel_enabled(0, True)
    awg.set_channel_enabled(1, True)

    # We use sine for sweep
    awg.set_channel_frequency(0, 600000)
    awg.set_channel_waveform(channel=0, waveform=FunctionGeneratorWaveform.SINE)
    awg.set_channel_waveform(channel=1, waveform=FunctionGeneratorWaveform.SINE)
    
    # Set amplitude
    awg.set_channel_amplitude(0, AWG_VOLT)
    awg.set_coupling(True)

    # Init scope

    with PYDHO800(address=OSC_IP) as scope:
        # Set some options for the oscilloscope
        scale_ch1 = (AWG_VOLT / 2.5)
        scale_ch2 = (AWG_VOLT / 2.5)
        
        scope.set_channel_bandwidth(channel=0, bandwidth="OFF")
        scope.set_channel_bandwidth(channel=1, bandwidth="OFF")
        
        if not args.MANUAL_SETTINGS:
            # Center vertically
    
            # Set the sensitivity according to the selected voltage
            scope.set_channel_scale(0, scale_ch1)
            # Be a bit more pessimistic for the default voltage, because we run into problems if it is too confident
            scope.set_channel_scale(1, scale_ch2)
    
        freqs = np.logspace(np.log10(MIN_FREQ), np.log10(MAX_FREQ), num=STEP_COUNT)
    
        
        volts = list()
        phases = list()
            
        time.sleep(0.05)
    
    
        for freq in freqs:    
            awg.set_channel_frequency(0, freq)
            time.sleep(TIMEOUT)
    
            # Use a better timebase and scale
            
            if not args.MANUAL_SETTINGS:
                # Display one period in 3 divs
                period = (1 / freq) / 3
                scope.set_timebase_scale(period)
                
            time.sleep((1 / freq) * 10)
            volt_ch2 = float(scope.get_channel_measurement(type='VPP', channel=1))
        
            # Optimize voltage scale of Channel 2, signal should be 2 times scale
            while ((volt_ch2 >= 10.0) or (float(scale_ch2 * 2) > volt_ch2 )):
                if (volt_ch2 >= 10.0):
                    # out of limit, scale to low
                    scale_ch2 = scale_ch2 * 3
                else:
                    scale_ch2 = scale_ch2 / 2
                scope.set_channel_scale(1, scale_ch2)
                time.sleep(0.2)
                # wait 10 cycles
                time.sleep((1 / freq) * 10)
                
            volt_ch2 = float(scope.get_channel_measurement(type='VPP', channel=1))                    
            volt_ch1 = float(scope.get_channel_measurement(type='VPP', channel=0))
            volts.append(volt_ch2 / volt_ch1)
    
            # Measure phase
            time.sleep(0.5)
            phase = float(scope.get_channel_measurement(type='RRPH', refchannel=0 ,channel=1))
            print("phase", phase)
            if phase:
                phase = -phase
            phases.append(phase)
    
# Write data to file if needed
if args.file:

    args.file.write("Frequency in Hz; Amplitude in V; Phase in Degree\n")

    for n in range(0, len(freqs)):
        if volts[n]:
            volt = volts[n]
        else:
            volt = float("nan")

        if phases[n]:
            phase = phases[n]
        else:
            phase = phases[n]

        args.file.write("%f;%f;%f \n" % (freqs[n], volt, phase))

    args.file.close()

# Plot graphics

if not args.PLOTS:
    exit()

plt.figure()
plt.subplot(211)
plt.axis([MIN_FREQ, MAX_FREQ, 0.001, 10.0])
plt.plot(freqs, volts, label="Measured data")

plt.title("Amplitude diagram (N=%d)" % STEP_COUNT)
plt.xlabel("Frequency [Hz]")
plt.ylabel("Voltage Peak-Peak [V]")
plt.legend()
plt.subplots_adjust(left=0.15, bottom=0.1, right=0.9, top=0.9, wspace=0.2, hspace=0.5)

# Set log x axis
plt.xscale("log")
plt.yscale("log")
plt.magnitude_spectrum(volts, scale='dB') 

plt.subplot(212)
plt.plot(freqs, phases, 'r--')
plt.grid(True)
plt.title("Phase diagram (N=%d)" % STEP_COUNT)
plt.ylabel("Phase [°]")
plt.xlabel("Frequency [Hz]")

plt.show()
