# Blynk
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
 
 ```python
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
 ```
