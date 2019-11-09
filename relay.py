import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)

pin1=19


GPIO.setup(pin1,GPIO.OUT)

GPIO.output(pin1,GPIO.LOW)



try:
	
	print("forward")
	
	GPIO.output(pin1,GPIO.HIGH)
	time.sleep(100)



except KeyboardInterrupt:
	GPIO.cleanup()
	pass
