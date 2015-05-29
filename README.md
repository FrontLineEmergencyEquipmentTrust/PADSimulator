# PADSimulator

## File locations

/home/pi/cabinet_sms.py

/home/pi/shutdown.py

/home/pi/Desktop/launcher.desktop

/home/pi/Desktop/shutdown.desktop

## Setup

### Initial setup

Enable SSH

### Linux setup

```sudo apt-get install picocom```

Setup the sms usb dongle as below

Copy the above programs to the correct directories

```nano cabinet_sms.py``` 

Change User Settings at the beginning of the program - especially the mobile number to SMS

```Ctrl+x``` followed by ```y``` and ```enter``` to exit and save

```nano /etc/xdg/lxsession/LXDE-pi/autostart```

Add ```@sudo python /home/pi/cabinet_sms.py``` to end of the autostart file

```Ctrl+x``` followed by ```y``` and ```enter``` to exit and save

### Things to do in LXDE desktop

Disable Screen Sleep

## Operation

Boot up the Pi and it will automatically start cabinet_sms.py in full screen mode.

The unlock/lock input (radio doorbell) toggles between the two.

If the cabinet is unlocked, it will lock after CABINETTIMEOUT which is set at 300 by default.

To shutdown the Pi, press and hold the shutdown button for more than 2 seconds.

To disable sending SMSes when the cabinet is Unlocked, Door Opened or Defibrillator Removed, disconnect the SMS USB Dongle.

## Testing

If a mouse is connected, you can left click to close the full screen and return to the LXDE desktop.

To test the USB dongle, type the following in a terminal:

```picocom /dev/ttyUSB0 -b 115200 -l```

Typing ```at``` in picocom should return ```ok```

To exit picocom press ```Ctrl+a``` followed by ```Ctrl+x```

If a keyboard is connected, you can simulate the inputs:

u = unlock cabinet

l = lock cabinet

o = open door

c = close door

r = remove defibrillator

q = replace defibrillator


## IO

GPIO BCM 7  Physical Pin 26 = Lock and Unlock input

GPIO BCM 8  Physical Pin 24 = Door Open       input (goes low)

GPIO BCM 20 Physical Pin 38 = Door Closed     input (goes low)

GPIO BCM 25 Physical Pin 22 = Defib Removed   input (goes low)

GPIO BCM 21 Physical Pin 40 = Defib Replaced  input (goes low)

GPIO BCM 16 Physical Pin 36 = Shutdown        input (goes low)

GPIO BCM 24 Physical Pin 18 = Lights On       output (goes low)

## SMS USB Dongle

The code has been written for a UK Vodafone E220 Huawei dongle

Use picocom to configure the dongle:

```picocom /dev/ttyUSB0 -b 115200 -l```

Remove the CD partition with the following command:

AT^U2DIAG=0

Configure the modem for only GPRS/EDGE with the following commmand:

AT^SYSCFG=13,1,3FFFFFFF,2,4

To exit picocom press ```Ctrl+a``` followed by ```Ctrl+x```

More instructions can be found here:

https://myraspberryandme.wordpress.com/2013/09/13/short-message-texting-sms-with-huawei-e220/
