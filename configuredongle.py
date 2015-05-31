#!/usr/bin/python

import serial

def dongleIsPresent():
	try:
		smsdongle = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
		smsdongle.write("AT\r") # expect OK in response
		response = smsdongle.readline() # reads the echo
		if ("error" in response): 
			print(response)
		response = smsdongle.readline() # reads the response
		if ("error" in response): 
			print(response)
		if ("OK" in response): 
			return True
	except:
		return False



if (dongleIsPresent()):
	smsdongle = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

	smsdongle.write("AT^CURC=0\r") # disable periodic status reports
	response = smsdongle.readline()
	if ("error" in response): 
			print response
	response = smsdongle.readline()
	if ("error" in response): 
			print response

	smsdongle.write("AT^U2DIAG=0\r") # disable CD partition
	response = smsdongle.readline()
	if ("error" in response): 
			print response
	response = smsdongle.readline()
	if ("error" in response): 
			print response

	smsdongle.write("AT^SYSCFG=13,1,3FFFFFFF,2,4\r") # configure the modem for only GPRS/EDGE
	response = smsdongle.readline()
	if ("error" in response): 
			print response
	response = smsdongle.readline()
	if ("error" in response): 
			print response

	print 'Dongle Configured'

else:
	print 'No dongle found'



