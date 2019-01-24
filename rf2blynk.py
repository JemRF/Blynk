#!/usr/bin/env python
"""
rf2blynk.py v1 JemRF Sensor Interface to Blynk 
---------------------------------------------------------------------------------
 Works conjunction with host at www.Blynk.cc
 Visit https://www.jemrf.com/pages/documentation for full details                                 
																				  
 J. Evans October 2019
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
 WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
 CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                                                       

 Revision History                                                                  
 V1.00 - Release
 
 Instructions:
 =============
 
 Serial to Blynk 
 ===============
 Messages received through the serial port from JemRF wireless sensors are transformed
 and sent to the Blynk server using the blynk.virtual_write(ID, Value) function.
 
 Mulithreading
 =============
 The Blynk python library is a blokcing library so this is a multithreaded application
 that runs the Blync processing in one thread and serial data processing in another.
 
 Device ID Mapping
 ==================
 JemRF sensors can perform multiple functions (e.g. 3 temperature sensors, humidity, door switch, relay control, LED control)
 ) all using the same Device ID of the sensor. The Bylnk widgets need unique ID's threfore it is neccessary to
 ensure a unique ID is assigned to each JemRF function. This program uses the following logic to try allocate a
 unique Device ID to each function:
 
 TMPA    - DeviceID
 TMPB    - DeviceID + 10
 TMPC    - DeviceID + 20
 BUTTON  - DeviceID + 30
 ANAA    - DeviceID + 40
 ANAB    - DeviceID + 50
 HUM     - DeviceID + 60
 BATT    - DeviceID + 70
 
 The above is not perfect and might overlap with device ID's if you have many JemRF Radio modules deployed. 
 You might need to chnage your device ID'same  so that the above deivice ID allocations work, or adjust 
 the code in this program accordingly. 
 
 Relay Support
 ==============
 The Bylnk app allows you to create buttons that can be mapped to JemRF relays. This allows you to 
 remote control relay switches wires to the JemRF radio module (see here for more details:
 https://www.jemrf.com/pages/how-to-use-the-flex-module-for-remote-control) . 
 
 We have added code for two remote switches to this application but you can add more as follows. 
 Below you will see some configuration items for relay switches explained below:
 
 button1=13               - This is the Virtual ID of the Blynk button
 button1RFRelayID=3       - This is the JemRF Device ID of the radio module
 button1RFRelay="A"       - This is the Relay Port. JemRF modules support two relays per device (RELAYA and RELAYB)
 
 If you want to add more than two Blynk buttons then add the following code at the bottom of this application source. 
 Make sure you change the "def v13_...." to the virtual device of the button in Blynk. Also create three new global variables
 (described above) to the new button (e.g. button3=15...). Lastly make susre you modify the below code replaying "button1"
 with "button3" or whatever name you gave to the global variable. 
 
 ##=======================================================================
 # Register virtual pin handler
 @blynk.VIRTUAL_WRITE(button1)
 def v13_write_handler(value):
	 dprint('Current button value: {}'.format(value))
	 if value=="0":
                 #sensorID,         rfPort,   wirelessMessage, wCommand
	 	SwitchRF(button1RFRelayID, button1RFRelay, "RELAY", "ON")
	 else:
	 	SwitchRF(button1RFRelayID, button1RFRelay, "RELAY", "OFF")
 ##=======================================================================
 
 
  -----------------------------------------------------------------------------------
"""

import serial
import BlynkLib
import time
from time import sleep
global blynk
import thread
global measure
global PrintToScreen
global Farenheit
global AllowExternalControl
global terminalID

#Once you have signed up for the Bylmk App you will receive a token which you insert here
#BLYNK_AUTH = 'YourTokenHere'

# Remote Control
#===============================================================================================
# Support for two Blynk buttons has been included that you can use to control JemRF relays. 
# See above for how to add more than two buttons.
# Relay button 1 configuration
button1=13           ##This is the Blynk virtual ID
button1RFRelayID=3   ##This is the JemRF module ID
button1RFRelay="A"   ##"A" for RELAYA, "B" for RELAYB

button2=14
button2RFRelayID=3
button2RFRelay="B"

#================================================================================================

PrintToScreen=True         #Set to True initially whiile testing. Set to False once it's working 
Farenheit=False            #Set to True to convert all temperature readings from Celciud to Fahrenheit
AllowExternalControl=False #This is a security setting. Set to True to allow external control of relays
                           #on the JEMRF modules.  

terminalID=59              #This is for a Blynk termial widget. All messages will get sent to the terminal widget
                           #that must have an ID of 59.

# No more config needed...you are good to go!
                           
blynk = BlynkLib.Blynk(BLYNK_AUTH)

def dprint(message):
	global PrintToScreen
	if (PrintToScreen):
		print message

#if you want to add code that is run on a timer
# (period must be a multiple of 50 ms)
#def my_user_task():
	# do any non-blocking operations
	# This works if you need it
			
def BlynkLoop():
	global blynk
	dprint("Blynk thread Started")
	#blynk.set_user_task(my_user_task, 1000) #un-comment this line to enable the my_user_task function
	blynk.run()

def DoFahrenheitConversion(value):
	global measure
	global Farenheit
	
	if Farenheit:
		value = float(value)*1.8+32
		value = round(value,2)
		measure = '1'
	else:
		measure='0'
	return(value)	
	
def rfRequest(request, retry):
	# sends the message and waits for a reply, retires if no reply retry times
	
	port = '/dev/ttyAMA0'
	baud = 9600

	# open a serial connection using the variables above
	ser = serial.Serial(port=port, baudrate=baud)

	# wait for a moment before doing anything else
	sleep(0.2)
	#sensorID=globals.RelayPin #currently limited to only one RF module
	n = 0
	while (n < retry):
		ser.flushInput()    # clear input buffer
		dprint ('sending     : ' + request)
		ser.write(request)  # see if our device is online
		timeout=15;
		while ser.inWaiting() == 0 and timeout!=0:
			sleep(0.05)
			timeout = timeout - 1
		
		if timeout==0:
				response="No response"
		else:
			response=""
			while ser.inWaiting():
				#sleep(0.01)
				if (ser.inWaiting()): response+=ser.read(1)
				if (response==request):
					n=retry
			dprint( "response is : "+response)
		n = n + 1
	ser.close
	return
	
def SwitchRF(sensorID, rfPort, wirelessMessage, wCommand):
	global AllowExternalControl
	if (AllowExternalControl==False): return
	rfRequest('a{0:02}{1}{2}{3}'.format(sensorID, wirelessMessage, rfPort, wCommand),5)
	
def main():
  global measure

  thread.start_new_thread(BlynkLoop,() )
  sensordata=''
  currdevid=''
  # loop until the serial buffer is empty

  start_time = time.time()

  #try:
  while True:
      # declare to variables, holding the com port we wish to talk to and the speed
      port = '/dev/ttyAMA0'
      baud = 9600

      # open a serial connection using the variables above
      ser = serial.Serial(port=port, baudrate=baud)

      # wait for a moment before doing anything else
      sleep(0.2)        
      while ser.inWaiting():
          # read a single character
          char = ser.read()
          # check we have the start of a LLAP message
          if char == 'a':
              sleep(0.01)
              start_time = time.time()
              
              # start building the full llap message by adding the 'a' we have
              llapMsg = 'a'

              # read in the next 11 characters form the serial buffer
              # into the llap message
              llapMsg += ser.read(11)

              # now we split the llap message apart into devID and data
              devID = llapMsg[1:3]
              data = llapMsg[3:]
              
              dprint(time.strftime("%c")+ " " + llapMsg)
                              
              if data.startswith('BUTTONON') or data.startswith('STATEON'):
                  devID=str(int(devID)+30)
                  sensordata=255
                  PEPFunction=26

              if data.startswith('BUTTONOFF') or data.startswith('STATEOFF'):
                  devID=str(int(devID)+30)
                  sensordata=1
                  PEPFunction=26

              if data.startswith('TMPA'):
                  sensordata=DoFahrenheitConversion(str(data[4:].rstrip("-")))
                  PEPFunction=37
              
              if data.startswith('ANAA'):
                  devID=str(int(devID)+40)
                  sensordata=str(data[4:].rstrip("-"))
                    #convert it to a reading between 1(light) and 48 (dark)
                  sensordata=str(sensordata)
                  PEPFunction=37
                  measure='2'
              
              if data.startswith('ANAB'):
                  devID=str(int(devID)+50)
                  sensordata=str(data[4:].rstrip("-"))
                  # if float(sensordata) < 1300: sensordata=1300
                  sensordata=float(sensordata)/2300*50#convert it to a reading between 1(light) and 48 (dark)
                  sensordata=str(sensordata)
                  measure='2'
                  PEPFunction=37
              
              if data.startswith('TMPC'):
                  devID=str(int(devID)+20)
                  sensordata=DoFahrenheitConversion(str(data[4:].rstrip("-")))
                  PEPFunction=37
              
              if data.startswith('TMPB'): 
                  devID=str(int(devID)+10)
                  sensordata=DoFahrenheitConversion(str(data[4:].rstrip("-")))
                  PEPFunction=37
                                      
              if data.startswith('HUM'):
                  devID=str(int(devID)+60)
                  sensordata=str(data[3:].rstrip("-"))								
                  PEPFunction=37
                  measure='2'
                  
              if data.startswith('BATT'):
                    devID=str(int(devID)+70)
                    sensordata=data[4:].strip('-')
                    PEPFunction=22
                                    
              if ((currdevid==devID) and (currvalue==sensordata)) or (sensordata==""): #ignore duplicates
                  dprint("Ignoring message");
              else:
                  currvalue=sensordata
                  currdevid=devID              
                  dprint("Sending data to Blynk:"+str(devID)+","+str(currvalue))
                  blynk.virtual_write(str(devID), str(currvalue))
                  blynk.virtual_write(terminalID, str(devID)+" - "+str(currvalue)+" - "+time.strftime('%X %x\n'))
                
          measure=''
          sensordata=''
        
      elapsed_time = time.time() - start_time
      if (elapsed_time > 2):
          currvalue=""
          sensordata=""
          currdevid=""

# Register virtual pin handler
@blynk.VIRTUAL_WRITE(button1)
def v13_write_handler(value):
	dprint('Current button value: {}'.format(value))
	if value=="0":
                #sensorID,         rfPort,   wirelessMessage, wCommand
		SwitchRF(button1RFRelayID, button1RFRelay, "RELAY", "ON")
	else:
		SwitchRF(button1RFRelayID, button1RFRelay, "RELAY", "OFF")


@blynk.VIRTUAL_WRITE(button2)
def v14_write_handler(value):
	dprint('Current button value: {}'.format(value))
	if value=="0":
		SwitchRF(button2RFRelayID, button2RFRelay, "RELAY", "ON")
	else:
		SwitchRF(button2RFRelayID, button2RFRelay, "RELAY", "OFF")

#@blynk.VIRTUAL_READ(2)
#def v62_read_handler():
    # This widget will show some time in seconds..
#    blynk.virtual_write(62, "RESET")	
	
if __name__ == "__main__":
	main()
