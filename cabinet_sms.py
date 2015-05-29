#!/usr/bin/python

import pygame, sys, time
from pygame.locals import *

import RPi.GPIO as GPIO
import serial

import os

#*************************************************************************************
#
# USER SETTINGS
#
# set up cabinet unlocked period in seconds
CABINETTIMEOUT = 300
#
# set up location
LOCATION = '#AAD-702 Demo Unit, Royal Cornwall Show'  # note use of single quotes
#
# set up phone number to SMS
SMSNUMBER='07xxxxxxxxx'   # note use of single quotes
#
#*************************************************************************************

# set SMS on or off
SMS = True
#SMS = False

# set debug on or off
#debug = True
debug = False

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# set global variables
cabinetUnlocked = False
doorOpen = False
defibRemoved = False
bouncetimedoorclosed = time.time()
bouncetimedooropen = time.time()
bouncetimedefibremoved = time.time()
bouncetimedefibreplaced = time.time()
cabinetTimer = time.time()

def reset():
	global cabinetUnlocked
	global doorOpen
	global cabinetTimer
	global defibRemoved

	cabinetUnlocked = False
	state = ''
	if GPIO.input(20) and (not GPIO.input(8)):
		doorOpen = True
		state += 'Door Open '
	else:
		doorOpen = False
	if GPIO.input(21) and (not GPIO.input(25)):
		defibRemoved = True
		state += 'Defibrillator Missing'
	else:
		defibRemoved = False		
	cabinetTimer = time.time()
	GPIO.output(LIGHTPIN, False)
	pygame.mouse.set_pos(0,0)
	pygame.mouse.set_visible(0)
	message('Cabinet Locked', BLACK)
	if state.strip():
		smallMessage(state, RED)

def message(msgText, colour):
	windowSurface.fill(colour)
	basicFont = pygame.font.SysFont(None, 180)
	text = basicFont.render(msgText, True, WHITE, colour)
	textRect = text.get_rect()
	textRect.centerx = windowSurface.get_rect().centerx
	textRect.centery = windowSurface.get_rect().centery
	windowSurface.blit(text, textRect)
	pygame.display.update()
	if debug:
		print(msgText)


def smallMessage(smallText, colour):
	basicFont = pygame.font.SysFont(None, 30)
	text = basicFont.render(smallText, True, WHITE, colour)
	textRect = text.get_rect()
	textRect.centerx = windowSurface.get_rect().centerx
	textRect.centery = windowSurface.get_rect().centery+100
	windowSurface.blit(text, textRect)
	pygame.display.update()
	if debug:
		print(smallText)


def sms(msgText, colour):
	global LOCATION

	if(not SMS):
		return 1

	smsText = ''

	try:
		smsdongle = serial.Serial('/dev/sms_dongle', 115200, timeout=1)
		smsText = msgText+' '+LOCATION
		smsdongle.write("AT^CURC=0\r") # disable periodic status reports
		response = smsdongle.readline()
		if ("error" in response): 
			print response
			smsText = "ERROR SENDING SMS"
		response = smsdongle.readline()
		if ("error" in response): 
			print response
			smsText = "ERROR SENDING SMS"
			
		smsdongle.write("AT+CMGF=1\r") # set sms to text mode
		response = smsdongle.readline()
		if ("error" in response): 
			print response
			smsText = "ERROR SENDING SMS"
		response = smsdongle.readline()
		if ("error" in response): 
			print response
			smsText = "ERROR SENDING SMS"

		smsdongle.write("AT+CSCA=\"+447785016005\",145\r") # set SMS gateway to stop ERROR 330
		response = smsdongle.readline()
		if ("error" in response): 
			print response
			smsText = "ERROR SENDING SMS"
		response = smsdongle.readline()
		if ("error" in response): 
			print response
			smsText = "ERROR SENDING SMS"

		print ("SMSing %s" %SMSNUMBER)
		smsdongle.write("AT+CMGS=\"%s\"\r" %SMSNUMBER) # set phone to send sms to
		response = smsdongle.readline()
		if ("error" in response): 
			print response
			smsText = "ERROR SENDING SMS"
		response = smsdongle.readline()
		if ("error" in response): 
			print response
			smsText = "ERROR SENDING SMS"
		smsdongle.write("%s\x1A\r" %smsText) # sent message terminated with CTRL-Z
		response = smsdongle.readline()
		if ("error" in response): 
			print response
			smsText = "ERROR SENDING SMS"
		response = smsdongle.readline()
		if ("error" in response): 
			print response
			smsText = "ERROR SENDING SMS"

		smsText = "SMS Sent - "+smsText
	except:
		print("There was an error opening the sms_dongle serial port")
		if smsText.split():
			smsText = "ERROR SENDING SMS"

	smallMessage(smsText, colour)


def shutdownEventHandler(gpioPin):
	time.sleep(2) # debounce needed for next test
	
	if GPIO.input(gpioPin):
		return 1#

	message("Shutting Down", BLUE)
	os.system("sudo halt")

def lockEventHandler(gpioPin):
	global cabinetUnlocked
	global cabinetTimer
	if (not cabinetUnlocked):
		cabinetUnlocked = True
		cabinetTimer = time.time()
		GPIO.output(LIGHTPIN, True)
		message('Cabinet Unlocked', BLACK)
		sms('CABINET UNLOCKED', BLACK)
	else:
		reset()


def doorOpenEventHandler(gpioPin):
	global doorOpen
	global cabinetUnlocked
	global bouncetimedooropen

	time_now = time.time()

	if (time_now - bouncetimedooropen) >= 0.5:
		bouncetimedooropen = time_now

		time.sleep(0.3) # debounce needed for next test
	
		if GPIO.input(gpioPin):
			return 1

		if ((GPIO.input(20)) and (not GPIO.input(8)) and (not doorOpen)):
			doorOpen = True

			if(cabinetUnlocked):
				message('Door Opened', BLACK)
				sms('DOOR OPENED', BLACK)	
			else:
				message('Unauthorised Access', RED)


def doorClosedEventHandler(gpioPin):
	global doorOpen
	global bouncetimedoorclosed

	time_now = time.time()

	if (time_now - bouncetimedoorclosed) >= 0.5:
		bouncetimedoorclosed = time_now

		time.sleep(0.3) # debounce needed for next test
	
		if GPIO.input(gpioPin):
			return 1

		if ((GPIO.input(8)) and (not GPIO.input(20)) and (doorOpen)):
			doorOpen = False
			message('Door Closed', BLACK)



def defibRemovedEventHandler(gpioPin):
	global doorOpen
	global cabinetUnlocked
	global defibRemoved
	global bouncetimedefibremoved

	time_now = time.time()

	if (time_now - bouncetimedefibremoved) >= 2:
		bouncetimedefibremoved = time_now

		time.sleep(0.3) # debounce needed for next test
	
		if GPIO.input(gpioPin):
			return 1

		if ((GPIO.input(21)) and (not GPIO.input(25)) and (not defibRemoved)): 
			defibRemoved = True

			if (cabinetUnlocked and doorOpen):
				message('Defibrillator Removed', BLACK)
				sms('DEFIBRILLATOR REMOVED', BLACK)
			else:
				message('Unauthorised Removal', RED)


def defibReplacedEventHandler(gpioPin):
	global defibRemoved
	global bouncetimedefibreplaced

	time_now = time.time()


	if (time_now - bouncetimedefibreplaced) >= 2:
		bouncetimedefibreplaced = time_now

		time.sleep(0.3) # debounce needed for next test
	
		if GPIO.input(gpioPin):
			return 1

		if ((GPIO.input(25)) and (not GPIO.input(21)) and (defibRemoved)):
			defibRemoved = False
			message('Defibrillator Replaced', BLACK)


# set up pygame
pygame.init()

# set up the window
if (debug):
	windowSurface = pygame.display.set_mode((1360, 768), 0,32)
else:
	windowSurface = pygame.display.set_mode((1360, 768), pygame.FULLSCREEN)

# set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# debounce disables the interrupt for X msec

LOCKPIN = 7 # physical pin 26 controlled by remote doorbell switch (idle = high, goes low on pressing doorbell)
GPIO.setup(LOCKPIN, GPIO.IN)
GPIO.add_event_detect(LOCKPIN, GPIO.FALLING, callback=lockEventHandler)

DOOROPENPIN = 8 # physical pin 24 connected to door switch (goes low when door open)
GPIO.setup(DOOROPENPIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.add_event_detect(DOOROPENPIN, GPIO.FALLING, callback=doorOpenEventHandler)

DOORCLOSEDPIN = 20 # physical pin 38 connected to door switch (goes low when door closed)
GPIO.setup(DOORCLOSEDPIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.add_event_detect(DOORCLOSEDPIN, GPIO.FALLING, callback=doorClosedEventHandler)  

DEFIBREMOVEDPIN = 25 # physical pin 22 connected to defibrillator switch (goes low when defib removed)
GPIO.setup(DEFIBREMOVEDPIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.add_event_detect(DEFIBREMOVEDPIN, GPIO.FALLING, callback=defibRemovedEventHandler)

DEFIBREPLACEDPIN = 21 # physical pin 40 connected to defibrillator switch (goes low when defib replaced)
GPIO.setup(DEFIBREPLACEDPIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.add_event_detect(DEFIBREPLACEDPIN, GPIO.FALLING, callback=defibReplacedEventHandler)

SHUTDOWNPIN = 16 # physical pin 36 connected to shutdown switch (goes low to shutdown - need to hold for 2 seconds)
GPIO.setup(SHUTDOWNPIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.add_event_detect(SHUTDOWNPIN, GPIO.FALLING, callback=shutdownEventHandler)

LIGHTPIN = 24 # physical pin 18 connected to lights
GPIO.setup(LIGHTPIN, GPIO.OUT)
GPIO.output(LIGHTPIN, False)

# set cabinet locked
reset()

# run the loop
while True:
	time.sleep(0.1)

	key=pygame.key.get_pressed() # keypress is for debugging as should use event handlers for GPIO triggers

	if key[pygame.K_u]: # unlock cabinet
		cabinetUnlocked = True
		cabinetTimer = time.time()
		GPIO.output(LIGHTPIN, True)
		message('Cabinet Unlocked', BLACK)
		sms('CABINET UNLOCKED', BLACK)

	if key[pygame.K_o]: # open door
		if(cabinetUnlocked):
			doorOpen = True
			message('Door Opened', BLACK)
			sms('DOOR OPENED', BLACK)	
		else:
				message('Unauthorised Access', RED)
				sms('UNAUTHORISDED ACCESS', RED)
				doorOpen = True	

	if key[pygame.K_c]: # close door
		doorOpen = False
		message('Door Closed', BLACK)

	if key[pygame.K_r]: # remove defibrillator
		if (cabinetUnlocked and doorOpen):
			message('Defibrillator Removed', BLACK)
			sms('DEFIBRILLATOR REMOVED', BLACK)
		else:
				message('Unauthorised Removal', RED)
				sms('UNAUTHORISDED REMOVAL', RED)

	if key[pygame.K_q]: # replace defibrillator
		message('Defibrillator Replaced', BLACK)

	if key[pygame.K_l]: # cabinet locked:
		cabinetUnlocked = False
		GPIO.output(LIGHTPIN, False)
		message('Cabinet Locked', BLACK)

	if(cabinetUnlocked and (cabinetTimer+CABINETTIMEOUT < time.time())):
		reset()

	for event in pygame.event.get():
		if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
			pygame.mouse.set_visible(1)
			pygame.quit()
			sys.exit()
