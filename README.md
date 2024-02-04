# Bode Plot with DHO800/900
A python support package plots a Bode plot with gain and phase. The program is tested with DHO914 as Oscilloscope and DG1022Z as function generator.


![Bode setup](/doc/bode.jpg)

## Test setup
Connect the DG1000Z and the DHO800/900 with same Ethernet as the computer. 

### Two Pin Component Frequency Characterisation 
Generator CH1 should be connected to the oscilloscope CH1 via a BNC or SMA cable. Same connection for CH2 but the channel 2 has a T-connector in between and the component is between plus and minus of the stub. The wire length of CH1 and CH2 should be the same and the cable at the end of the oscilloscope should be terminated with 50 Ohm.

### Circuit Transfer Function
Generator CH1 should be connected to the oscilloscope CH1 via a BNC or SMA cable.  
The generator CH2 is connected to the circuit input and the circuit output directly to oscilloscope CH2.
The wire length of CH1 and CH2 should be the same and the cable at the end of the oscilloscope should be terminated with 50 Ohm.

## Python Requirements
This package needs numpy/scipy/matplotlib/pylabdevs/pydg1000z/pydho800 environment. 

## Installing 

There is a Python and PyPi packages that can be installed using

```
pip install  numpy scipy matplotlib pylabdevs pydho800 pydg1000z pybode
```

## Usage
The basic syntax is `python bode.py MIN_FREQ MAX_FREQ [FREQ_COUNT]`, so if you, for example, want to test your DUT between 1kHz and 2.2Mhz, with 100 steps (default is 50),
you can do it like this: `python bode.py 1e3 2.2e6 100`.

By default only the Amplitude diagram is measured and plotted. If you also want to get the Phase diagram, you will have to specify the `--phase` flag.

If you want to use the measured data in another software like OriginLab or Matlab, you can export it to a semicolon-seperated CSV file with the `--output` option.

So a typical command line would like this: ```python bode.py 1e3 2.2e6 100 --osc_ip 10.0.0.123 --awg_ip 10.0.0.124  --phase --output out.csv```
To see the full list of possible options call `python bode.py --help`.

## License
This program is licensed under the MIT License. See [LICENSE](https://github.com/pmschueler/pybode/blob/main/LICENSE) file for more info.

## Acknowledgements
Based on the original work by [DS1054_BodePlotter](https://github.com/jbtronics/DS1054_BodePlotter) I have re-used code parts and the method of the measurement.