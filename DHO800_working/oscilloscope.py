from enum import Enum

from labdevices.oscilloscope import Oscilloscope

class OscilloscopeMeasurementType(Enum):
	VPP = 0
	RRPH = 1
	FFPH = 2
	VMIN = 3
	VMAX = 4
	VRMS = 5
	VAVG = 6
	OVER = 7
	FREQ = 8
	PER = 9
	
	@classmethod
	def has_value(cls, v):
		return v in cls._value2member_map_
	
class OscilloscopeBandwidthMode(Enum):
	OFF = 0
	BW20 = 1
	
	@classmethod
	def has_value(cls, v):
		return v in cls._value2member_map_
		