"""
J. Evans Jan 2019
Blynk is a platform with iOS and Android apps to control
Arduino, Raspberry Pi and the likes over the Internet.
You can easily build graphic interfaces for all your
projects by simply dragging and dropping widgets.
  Downloads, docs, tutorials: http://www.blynk.cc
  Sketch generator:           http://examples.blynk.cc
  Blynk community:            http://community.blynk.cc
  Social networks:            http://www.fb.com/blynkapp
                              http://twitter.com/blynk_app
This example shows how to perform periodic actions and
update the widget value on demand.
In your Blynk App project:
  Add two Value Display widgets, bind it to Virtual Pin V2 and V3
  Add a Button Wdget and bind it to V13
  set reading all frequencies to 'PUSH' 
  Run the App (green triangle in the upper right corner).
"""
import BlynkLib
import time
from time import sleep
import thread
global blynk

BLYNK_AUTH = 'yourtokenhere'

blynk = BlynkLib.Blynk(BLYNK_AUTH)

# (period must be a multiple of 50 ms)
def my_user_task():
	# do any non-blocking operations
	blynk.virtual_write(3, time.ticks_ms() // 1000)
			
def BlynkLoop():
	global blynk
	print("Blynk thread Started")
	blynk.set_user_task(my_user_task, 1000) 
	blynk.run()

#Virtual Button V13
@blynk.VIRTUAL_WRITE(13)
def v13_write_handler(value):
	print 'Current button value: {}'.format(value)
	
def main():
	#This statement puts Blynk into a thread of its own 
	thread.start_new_thread(BlynkLoop,() )

	#Put your code here without the need to call blynk.run, 
	#it's already running in a thread of it's own
	value=0
	while True:	
		#You can call Blynk functions from within your code!
		blynk.virtual_write(2, str(value))
		value = value + 1
		sleep(1)
			
if __name__ == "__main__":
	main()
