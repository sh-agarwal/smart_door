#Libraries
import RPi.GPIO as GPIO
import time
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BOARD)
 
#set GPIO Pins
GPIO_TRIGGER = 16
GPIO_ECHO = 12
 
p1=19
p2=21
p3=23
p4=22
p5=24

GPIO.setup(p1,GPIO.OUT )
GPIO.setup(p2,GPIO.OUT )
GPIO.setup(p3,GPIO.OUT )
GPIO.setup(p4,GPIO.OUT )
GPIO.setup(p5,GPIO.OUT )

#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.OUT)
 
def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
if __name__ == '__main__':
    try:
        GPIO.output(p1, True)
    	GPIO.output(p2, True)
	GPIO.output(p3, True)
	GPIO.output(p4, True)
	GPIO.output(p5, True)
        time.sleep(1000)
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
