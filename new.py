
import sys
import time
import RPi.GPIO as GPIO
from pad4pi import rpi_gpio

#******************************************#
KEYPAD = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]

COL_PINS = [5, 6, 13, 19] # BCM numbering
ROW_PINS = [14,15,7,26] # BCM numbering

factory = rpi_gpio.KeypadFactory()
keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)

#******************************************#

#******************************************#
matrix=-1
matrix_time=time.time()

d = ['0','0','0','0']
matrix_count=0

password = ['0','0','0','0']


def printKey(key):
    global matrix,matrix_count,matrix_time,password,d
    print(key)
    #print(matrix)
    if(matrix_time + 10 <time.time() and matrix==1):
    	print('Reset')
    	matrix=-1
    if(key=='*' and matrix==-1):
    	print('Enter Password:')
    	matrix=1
    	matrix_time=time.time()
    elif(key=='*' and matrix==1):
    	matrix=-1
    elif(matrix==1 and key == 'C'):
    	matrix_count=0
    elif(key.isdigit() and matrix==1):
    	d[matrix_count]=key
    	matrix_count=matrix_count+1
    	#print('count: ')
    	if(matrix_count==4):
    		if(d==password):
    			stepper_func(-1,30000,6/float(10000))
		else:
			print('Wrong password!')
    		matrix=-1
    		matrix_count=0
    
    #print(matrix)
    	
    	

#******************************************#

# printKey will be called each time a keypad button is pressed
keypad.registerKeyPressHandler(printKey)

# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

# Define GPIO signals to use
# Physical pins 11,15,16,18
# GPIO17,GPIO22,GPIO23,GPIO24
StepPins = [17,22,23,24]

# Set required pins as output
for pin in StepPins:
  print "Setup pins"
  GPIO.setup(pin,GPIO.OUT)
  GPIO.output(pin, False)
  
#set GPIO Pins for ultrasonic sensor
GPIO_TRIGGER = 20
GPIO_ECHO = 21

#set GPIO direction (IN / OUT) for ultrasonic
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

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
  
# Define advanced sequence
# as shown in manufacturers datasheet
Seq = [[1,0,0,1],
       [1,0,0,0],
       [1,1,0,0],
       [0,1,0,0],
       [0,1,1,0],
       [0,0,1,0],
       [0,0,1,1],
       [0,0,0,1]]
       
StepCount = len(Seq)
StepDir = -1 # Set to 1 or 2 for clockwise
            # Set to -1 or -2 for anti-clockwise

# Read wait time from command line
if len(sys.argv)>1:
  WaitTime = int(sys.argv[1])/float(10000)
else:
  WaitTime = 6/float(10000)



def stepper_func(direction,total_max,wait_time2):
	# Start main loop
	StepDir=direction
	# Initialise variables
	StepCounter = 0
	# Initialise variables
	total = 0
	x=True
	while x:
	
	  print StepCounter,
	  print Seq[StepCounter]
	
	  for pin in range(0, 4):
	    xpin = StepPins[pin]
	    if Seq[StepCounter][pin]!=0:
	      print " Enable GPIO %i" %(xpin)
	      GPIO.output(xpin, True)
	    else:
	      GPIO.output(xpin, False)
	
	  StepCounter += StepDir
	
	  # If we reach the end of the sequence
	  # start again
	  if (StepCounter>=StepCount):
	    StepCounter = 0
	  if (StepCounter<0):
	    StepCounter = StepCount+StepDir
	
	  # Wait before moving on
	  total=total+1
	  if(total>total_max):
	  	x=False
	  time.sleep(wait_time2)

# Import the ADS1x15 module.
import Adafruit_ADS1x15


# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115()

# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
GAIN = 1

print('Reading ADS1x15 values, press Ctrl-C to quit...')
# Print nice channel column headers.
print ('Joystick and matrix control On')
print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*range(4)))
print('-' * 37)
# Main loop.
while True:
    # Read all the ADC channel values in a list.
    values = [0]*4
    for i in range(4):
        # Read the specified ADC channel using the previously set gain value.
        values[i] = adc.read_adc(i, gain=GAIN)
        # Note you can also pass in an optional data_rate parameter that controls
        # the ADC conversion time (in samples/second). Each chip has a different
        # set of allowed data rate values, see datasheet Table 9 config register
        # DR bit values.
        #values[i] = adc.read_adc(i, gain=GAIN, data_rate=128)
        # Each value will be a 12 or 16 bit signed integer value depending on the
        # ADC (ADS1015 = 12-bit, ADS1115 = 16-bit).
    # Print the ADC values.
    if(matrix==-1):
    	print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*values))
    
    # Rotating STEPPER 
    dist1=distance()
    
    
    if(matrix==-1):
    	print(dist1)
    stop=1
    if(dist1<=5 ):
    	stop=0
    if(values[0]<15000 and matrix ==-1):
    	stepper_func(-1,2000,6/float(10000))
    if(values[0]>25000 and stop and matrix==-1):
    	stepper_func(1,2000,6/float(10000))
    
    if(matrix_time + 10 <time.time() and matrix==1):
    	print('Time''s Up')
    	matrix=-1
    	
    # Pause for half a second.
    time.sleep(0.01)
