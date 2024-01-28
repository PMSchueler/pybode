# bode.py
# Program to plot bode diagrams using a DHO800/DHO900 and a JDS6600

# Jan Böhmer (c) 2019
# published under MIT license. See file "LICENSE" for full license text

# Derived from https://github.com/jbtronics/DS1054_BodePlotter

# Peter Matthias Schueler (c) 2023
# added DHO800/DHO900 support using pydho800 and pyserial

from pydg1000 import *


from labdevices.scpi import SCPIDeviceEthernet

    

with PYDG1000(address="192.168.10.142") as awg:
    
    awg.set_model()
    
    print("Press Key")
    input()
    
    awg.set_serial_number("DG1ZA253504071")

