from __future__ import print_function
import sys
import time
from datetime import datetime
import RPi.GPIO as GPIO
from pad4pi import rpi_gpio
#import face_recognition
import subprocess
import paho.mqtt.client as mqtt
import signal
import zbarlight
import PIL
import qrcode
from datetime import timedelta

import os
import re
import face_recognition.api as face_recognition
import multiprocessing
import itertools
import sys
import PIL.Image
import numpy as np

def scan_known_people(known_people_folder):
    known_names = []
    known_face_encodings = []

    for file in image_files_in_folder(known_people_folder):
        basename = os.path.splitext(os.path.basename(file))[0]
        img = face_recognition.load_image_file(file)
        encodings = face_recognition.face_encodings(img)

        if len(encodings) > 1:
            click.echo("WARNING: More than one face found in {}. Only considering the first face.".format(file))

        if len(encodings) == 0:
            click.echo("WARNING: No faces found in {}. Ignoring file.".format(file))
        else:
            known_names.append(basename)
            known_face_encodings.append(encodings[0])

    return known_names, known_face_encodings


face_name=""

def print_result(filename, name, distance, show_distance=False):
	global face_name
	face_name=name
	if show_distance:
		print("{},{},{}".format(filename, name, distance))
	else:
		print("{},{}".format(filename, name))


def test_image(image_to_check, known_names, known_face_encodings, tolerance=0.6, show_distance=False):
    unknown_image = face_recognition.load_image_file(image_to_check)

    # Scale down image if it's giant so things run a little faster
    if max(unknown_image.shape) > 1600:
        pil_img = PIL.Image.fromarray(unknown_image)
        pil_img.thumbnail((1600, 1600), PIL.Image.LANCZOS)
        unknown_image = np.array(pil_img)

    unknown_encodings = face_recognition.face_encodings(unknown_image)

    for unknown_encoding in unknown_encodings:
        distances = face_recognition.face_distance(known_face_encodings, unknown_encoding)
        result = list(distances <= tolerance)

        if True in result:
            [print_result(image_to_check, name, distance, show_distance) for is_match, name, distance in zip(result, known_names, distances) if is_match]
        else:
            print_result(image_to_check, "unknown_person", None, show_distance)

    if not unknown_encodings:
        # print out fact that no faces were found in image
        print_result(image_to_check, "no_persons_found", None, show_distance)


def image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]


def process_images_in_process_pool(images_to_check, known_names, known_face_encodings, number_of_cpus, tolerance, show_distance):
    if number_of_cpus == -1:
        processes = None
    else:
        processes = number_of_cpus

    # macOS will crash due to a bug in libdispatch if you don't use 'forkserver'
    context = multiprocessing
    if "forkserver" in multiprocessing.get_all_start_methods():
        context = multiprocessing.get_context("forkserver")

    pool = context.Pool(processes=processes)

    function_parameters = zip(
        images_to_check,
        itertools.repeat(known_names),
        itertools.repeat(known_face_encodings),
        itertools.repeat(tolerance),
        itertools.repeat(show_distance)
    )

    pool.starmap(test_image, function_parameters)



def main(known_people_folder, image_to_check, cpus, tolerance, show_distance):
    known_names, known_face_encodings = scan_known_people(known_people_folder)

    # Multi-core processing only supported on Python 3.4 or greater
    if (sys.version_info < (3, 4)) and cpus != 1:
        click.echo("WARNING: Multi-processing support requires Python 3.4 or greater. Falling back to single-threaded processing!")
        cpus = 1

    if os.path.isdir(image_to_check):
        if cpus == 1:
            [test_image(image_file, known_names, known_face_encodings, tolerance, show_distance) for image_file in image_files_in_folder(image_to_check)]
        else:
            process_images_in_process_pool(image_files_in_folder(image_to_check), known_names, known_face_encodings, cpus, tolerance, show_distance)
    else:
        test_image(image_to_check, known_names, known_face_encodings, tolerance, show_distance)




GPIO.setwarnings(False)

val=0.36

    # Rotating STEPPER 

def Exit_gracefully(signal,frame):
	open_gate(1,0)
	GPIO.cleanup()
	client.publish("Door/joystick2", None, 0, True)
	client.publish("Hatch/control", None, 0, True)
	client.publish("Door/msg", None, 0, True)
	client.publish("Rfid/add", None, 0, True)
	client.publish("Rfid/delete", None, 0, True)
	client.publish("Door/count",None,0,True)
	client.disconnect()
	print("Smart Door: Stoping services")
		
	sys.exit(0)

signal.signal(signal.SIGINT,Exit_gracefully)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.publish("Door/open_stats","10")
    client.publish("Door/hatch_stat","Close")
    client.publish("Door/count","0")
    client.publish("Door/auto","1")
 
    # Subscribing in on_connect() - if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("Door/joystick2")
    client.subscribe("Door/camera2")
    client.subscribe("Door/msg")
    client.subscribe("Hatch/control")
    client.subscribe("Door/qr")
    client.subscribe("Door/open_stats")
    client.subscribe("Door/hatch_stat")
    client.subscribe("Door/message")
    client.subscribe("Door/camera3")
    client.subscribe("Rfid/add")
    client.subscribe("Rfid/delete")
    client.subscribe("Door/stats")
    client.subscribe("Door/count")
    client.subscribe("Door/auto")
 
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global open_time,close_time,hatch_open,hatch_time,auto_mode
    print(msg.topic+" "+str(msg.payload))
    #print(msg.payload)
    str3=str(msg.payload)

    res3=str3.split("'")

    if (msg.topic== "Door/camera2"):

        
        print("MQTT: Capturing Image")
        subprocess.call(["fswebcam","--no-banner","-r","400x400","-F","8","-q","./test1/unknown_image.jpg"])
        
        now=datetime.now()
        dt=now.strftime("%d:%m:%y_%H:%M:%S")

        subprocess.call(["cp","./test1/unknown_image.jpg","./log/"+dt+".jpg"])
    
        print("Saved in logs")
        subprocess.call(["cp","./test1/unknown_image.jpg","./gdrive/"+dt+".jpg"])
        
        print("Uploading to cloud...")
        subprocess.call(["drive","push","-no-prompt","-quiet","./gdrive"])
        print("Uploaded successfully!")
	
    if (msg.topic== "Door/joystick2") :
        res4=int(res3[1])
        print("MQTT: Joystick control")
        open_gate(1,10-res4)

    if(msg.topic== "Door/msg"):
        print(res3[1])
        subprocess.call(["say",res3[1]])
    if(msg.topic== "Hatch/control"):
        print(res3[1])
        if(res3[1]=="Open" and hatch_open==0):
                print("Hatch Access: Opening")
                motor_func2(1,open_time)
                hatch_time=time.time()
                hatch_open=1
        elif(res3[1]=="Close" and hatch_open==1):
                print("Hatch Access: Closing")
                motor_func2(-1,close_time)
                hatch_time=time.time()
                hatch_open=0
    if(msg.topic== "Door/qr"):
        
        print(res3[1])
        res4=res3[1].split(" ")
        now=datetime.now()
        now1=datetime.now() + timedelta(hours=int(res4[1]))
        now2=datetime.now() + timedelta(hours=int(res4[2])+int(res4[1]))
     
        no=now.strftime("%d-%m-%y %H:%M:%S")
        
        no2=now1.strftime("%y-%m-%d %H:%M:%S")
        no3=now2.strftime("%y-%m-%d %H:%M:%S")
        
        print(no)
        print(no2)
        print(no3)
        dt=now.strftime("%d:%m:%y_%H:%M:%S")
        img=qrcode.make(res4[0]+dt)
	
        img.save("./qr_code/QR_"+dt+".png")
        img.save("./gdrive/QR_"+dt+".png")
        f=open('./qr_code/code.txt','a')
        x=str(res4[0])+dt+" "+no2+" "+no3+" \n"
        print(x)
        f.write(x)
        f.close()
        
        print("Uploading to cloud...")
        subprocess.call(["drive","push","-no-prompt","-quiet","./gdrive"])
        print("Uploaded successfully!")

    if(msg.topic== "Rfid/add"):
        print(res3[1])
        f=open('./rfid/rfid.txt','a')
        f.write(str(res3[1])+"\n")
        f.close()
        client.publish("Door/stats","Added "+str(res3[1]))
    if(msg.topic== "Rfid/delete"):
        subprocess.call(["rm","-r","./rfid/rfid.txt"])
        os.mknod("./rfid/rfid.txt")
        client.publish("Door/stats","Deleted all enteries")
    if(msg.topic== "Door/auto"):
        print(res3[1])
        if(str(res3[1])=="0"):
                auto_mode=0
                client.publish("Door/stats","Auto Mode Off")
        else:
                auto_mode=1
                client.publish("Door/stats","Auto Mode On")
        
		
        

  
 
# Create an MQTT client and attach our routines to it.
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
 
client.connect_async("broker.hivemq.com", 1883, 60)

# Process network traffic and dispatch callbacks. This will also handle
# reconnecting. Check topen_gate(dir,val2)he documentation at
# https://github.com/eclipse/paho.mqtt.python
# for information on how to use other loop*() functions
client.loop_start()

auto_mode=1
check=0






#******************************************#
KEYPAD = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]

ROW_PINS = [5, 6, 13, 19] # BCM numbering
COL_PINS = [14,18,7,26] # BCM numbering

factory = rpi_gpio.KeypadFactory()
keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)

from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

#******************************************#

#******************************************#
matrix=-1
matrix_time=time.time()

d = ['0','0','0','0']
matrix_count=0

password = ['0','0','0','0']
hatch_time=time.time()
hatch_open=0
open_time=0.35
close_time=0.315
h_time=8
attempt=3
block=0
block_time=time.time()
block_val=1800
door_time=time.time()

pin1=17
pin2=22

door_loops=10

GPIO.setup(pin1,GPIO.OUT)
GPIO.setup(pin2,GPIO.OUT)
GPIO.output(pin1,GPIO.LOW)
GPIO.output(pin2,GPIO.LOW)

def open_gate(dir,val2):
	global door_open,val
	#print("Initial %d"%door_open)
	if(door_open<val2):
		#print("here")
		while (door_open<val2):
			motor_func(-1,val,1)
			#print("came here")
			time.sleep(0.2)
			door_open+=1
			client.publish("Door/open_stats",str(10-door_open))
			#print(door_open)
	else:
		while (door_open>val2):
			dist1=distance(GPIO_TRIGGER,GPIO_ECHO)
			dist5=distance(GPIO_TRIGGER,GPIO_ECHO)
    
		
			if(dist1<12 and dist5<12):
				time.sleep(0.1)
			dist6=distance(GPIO_TRIGGER,GPIO_ECHO)
			if(dist1<12 and dist5<12 and dist6<12):
				client.publish("Door/stats","Obstruction in closing")
				continue
			motor_func(1,val+0.4,1)
			#print("came here")
			time.sleep(0.2)
			door_open-=1
			client.publish("Door/open_stats",str(10-door_open))
			if(door_open==0):		
				client.publish("Door/stats","Door Closed")




def printKey(key):
    global matrix,matrix_count,matrix_time,password,d, hatch_open, hatch_time,attempt,block_time,block_val,block,face_name,door_open,auto_mode,door_time
    print("Pressed: "+key)
    #print(matrix)
    if(door_open==10 and door_time + 10 < time.time() and auto_mode==1):
        print('Door Access: Closing (Auto)')
        open_gate(1,0)
        door_open=0
        check=0
    if(matrix_time + 10 <time.time() and matrix==1 and block==0):
        print('Door Access: Press * again to enter password (auto reset)')
        matrix=-1
    if(hatch_time + h_time <time.time() and hatch_open==1):
        print('Hatch Access: Closing (Auto)')
        hatch_open=0
        motor_func2(-1,close_time)
    if(block_time + block_val <time.time() and block==1):
        print('Door Access: Password access unblocked')
        block=0
        attempt=3
    if(key=='*' and matrix==-1 and block==0):
        print('Door Access: Enter Password')
        matrix=1
        matrix_time=time.time()
    elif(key=='*' and matrix==1 and block==0):
        print("Door Access: Press again * to enter password (manual reset)")
        matrix=-1
        matrix_count=0
    elif(matrix==1 and key == 'C' and block==0):
        print('Door Access: Password Cleared')
        matrix_count=0
    elif(key.isdigit() and matrix==1 and block==0):
        d[matrix_count]=key
        matrix_count=matrix_count+1
        if(matrix_count==4):
            subprocess.call(["fswebcam","--no-banner","-r","400x400","-F","8","-q","./test1/unknown_image.jpg"])
            now=datetime.now()
            dt=now.strftime("%d:%m:%y_%H:%M:%S")
            if(d==password):
                subprocess.call(["cp","./test1/unknown_image.jpg","./log/door_password_open_"+dt+".jpg"])
                print("Door Access: Opening")
                open_gate(-1,10)
                door_time=time.time()
            else:
                subprocess.call(["cp","./test1/unknown_image.jpg","./log/door_password_Incorrect_"+dt+".jpg"])
                
                attempt-=1
                print("Door Access: Wrong Password! (%d attempts left)"%attempt)
                if(attempt==0):
                        print("Door Access: Password access has been blocked for %d seconds"%block_val)
                        block=1
                        block_time=time.time()
            matrix=-1
            matrix_count=0
    elif(key == '#' and matrix==-1):

    	



    	print("Door Access: Be Ready for Image capture")
    	subprocess.call(["fswebcam","--no-banner","-r","400x400","-F","8","-q","./test1/unknown_image.jpg"])
        
    	now=datetime.now()
    	dt=now.strftime("%d:%m:%y_%H:%M:%S")
      
    	print("Processing...")
    	main("./test","./test1/unknown_image.jpg",1,0.4,False)        

    	
    	res3="A person is waiting outside"
    	if(face_name=="unknown_person"):
                subprocess.call(["say",res3])
                subprocess.call(["cp","./test1/unknown_image.jpg","./log/door_unknown_person_"+dt+".jpg"])
                print("Door Access: No Match")  
    	elif(face_name=="no_persons_found"):
                subprocess.call(["cp","./test1/unknown_image.jpg","./log/door_noone_detected_"+dt+".jpg"])
                print("Door Access: No Face Found")                
    	else:
                subprocess.call(["say",face_name,"has","arrived"])
                subprocess.call(["cp","./test1/unknown_image.jpg","./log/door_"+face_name+"_"+dt+".jpg"])
                print("Door Access: Opening")
                open_gate(-1,10)
                door_time=time.time()
    	time.sleep(1)
    	matrix=-1
    	matrix_count=0

    elif(key == 'A' and matrix==-1):
      
        print("Door Access: Reading RFID")
        id, text = reader.read()
        subprocess.call(["fswebcam","--no-banner","-r","400x400","-F","8","-q","./test1/unknown_image.jpg"])
        now=datetime.now()
        dt=now.strftime("%d:%m:%y_%H:%M:%S")
        subprocess.call(["cp","./test1/unknown_image.jpg","./log/door_"+text+"_"+dt+".jpg"])
        print(id)

        f=open('rfid/rfid.txt','r')
        f.seek(0)
        line=f.readline()
        while line:
                if(line==str(id)+"\n"):
                        print("Welcome "+text+ " !")
                        subprocess.call(["say",text,"has","arrived"])
                        print("Door Access: Opening")
                        open_gate(-1,10)
                        door_time=time.time()
                line=f.readline()
        f.close()


        
    elif(key == 'B' and matrix==-1):
        if(hatch_open==0):
                print("Hatch Access: Be Ready for Image capture")
                subprocess.call(["fswebcam","--no-banner","-r","400x400","-F","8","-q","./test1/unknown_image.jpg"])
	        
                now=datetime.now()
                dt=now.strftime("%d:%m:%y_%H:%M:%S")
                #print(dt)
              
                
                print("Processing...")
                main("./hatch","./test1/unknown_image.jpg",1,0.4,False) 
         
	        
                if(face_name=="unknown_person"):
                        print("Hatch Access: No Match")  
                        subprocess.call(["cp","./test1/unknown_image.jpg","./log/hatch_unknown_person_"+dt+".jpg"])
                elif(face_name=="no_persons_found"):
                        print("Hatch Access: No Face Found") 
                        subprocess.call(["cp","./test1/unknown_image.jpg","./log/hatch_noone_detected_"+dt+".jpg"])               
                else:
                        subprocess.call(["cp","./test1/unknown_image.jpg","./log/hatch_"+face_name+"_"+dt+".jpg"])
                        print("Hatch Access: Opening")
                        motor_func2(1,open_time)
                        hatch_open=1
                        hatch_time=time.time()
                        print("Hatch Access: hatch will automatically close after %d (Press B again to close manually)"%h_time)
        else:
                hatch_open=0
                print("Hatch Access: Closing (Manual)")
                motor_func2(-1,close_time)
        time.sleep(1)
        matrix=-1
        matrix_count=0
    elif(key == '1'):
        
               
        print("Hatch Access: Opening")
        motor_func2(1,open_time)

        
        time.sleep(0.5)
        matrix=-1
        matrix_count=0
    elif(key == '2' and matrix==-1):
        
                
        print("Hatch Access: Closing")
        motor_func2(-1,close_time)

        
        time.sleep(0.5)
        matrix=-1
        matrix_count=0

    elif(key == 'D' and matrix==-1):
        
                
        print("Door Access: Image capture (QR code)")
        subprocess.call(["fswebcam","--no-banner","-r","1280x720","-F","4","-q","./qr_code/qr_image.jpg"])
        print ('Scanning Image..')
        f = open('./qr_code/qr_image.jpg','rb')
        qr = PIL.Image.open(f);
        qr.load()

        codes = zbarlight.scan_codes('qrcode',qr)
    	
        if(codes==None):
       
        	print ('No QR code found')

        else:
        	print ('QR code(s):')
        	print (codes)
        	res2=str(codes[0]).split("'")
        	print(res2)
        	f=open('./qr_code/code.txt','r+')
        	line = f.readline()
        	cnt=1
        	target=-1
        	while line:
                        res=line.split(" ")
			
                        if(str(res2[1])==str(res[0])):
                            	target=cnt
                            	now=datetime.now()
				
                            	format="%y-%m-%d %H:%M:%S"
                            	n=now.strftime(format)
                            	print(res)
                            	now1=datetime.strptime(str(res[1])+" "+str(res[2]),format)
                            	now2=datetime.strptime(str(res[3])+" "+str(res[4]),format)
                            	now=datetime.strptime(n,format)
                            	print(now1)
                            	print(now2)
                            	print(now)
                            	if(now>=now1 and now<=now2):
                            	    	print("Door Access: Opening")
                            	    	open_gate(-1,10)
                            	    	door_time=time.time()			
                        line=f.readline()
                        cnt+=1  
        	f.close()
        	if(target!=-1):
                        f=open('./qr_code/code.txt','r')
                        f.seek(0)
                        line = f.readline()
                        cnt=1
                        f2=open('./qr_code/temp.txt','w')
                        
                        while line:
                            	if(cnt!=target):
                            	    	f2.write(line)
                            	line = f.readline()
				
                            	cnt+=1
                        f.close()
                        f2.close()
                        subprocess.call(["rm","-r","./qr_code/code.txt"])
                        subprocess.call(["mv","./qr_code/temp.txt","./qr_code/code.txt"])
		


	
        
        

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
  #print ("Setup pins")
  GPIO.setup(pin,GPIO.OUT)
  GPIO.output(pin, False)
  
#set GPIO Pins for ultrasonic sensor
GPIO_TRIGGER = 16
GPIO_ECHO = 12

#set GPIO direction (IN / OUT) for ultrasonic
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)


GPIO.setup(15, GPIO.OUT)
GPIO.setup(12, GPIO.IN)

def distance(trigger,echo):
    # set Trigger to HIGH
    GPIO.output(trigger, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(trigger, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    x=time.time()
    del2=1
    while (GPIO.input(echo) == 0 and x+del2>time.time()) :
        StartTime = time.time()
 
    x=time.time()
    # save time of arrival
    while (GPIO.input(echo) == 1 and x+del2>time.time()):
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

pin3=20
pin4=21
GPIO.setup(pin3,GPIO.OUT)
GPIO.setup(pin4,GPIO.OUT)
GPIO.output(pin3,GPIO.LOW)
GPIO.output(pin4,GPIO.LOW)

ir1=27
ir2=4
GPIO.setup(ir1,GPIO.IN)
GPIO.setup(ir2,GPIO.IN)


def stepper_func(direction,total_max,wait_time2):
	# Start main loop
	StepDir=direction
	# Initialise variables
	StepCounter = 0
	# Initialise variables
	total = 0
	x=True
	while x:
	
	  print (StepCounter)
	  print (Seq[StepCounter])
	
	  for pin in range(0, 4):
	    xpin = StepPins[pin]
	    if Seq[StepCounter][pin]!=0:
	      print (" Enable GPIO %i" %(xpin))
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

def motor_func(direction,t,loops):
	
	i=0
	while (i<loops):
		if(direction== -1):
			print("left")
		
			GPIO.output(pin1,GPIO.HIGH)
			GPIO.output(pin2,GPIO.LOW)
			time.sleep(t)
			GPIO.output(pin1,GPIO.LOW)
			GPIO.output(pin2,GPIO.LOW)
		else:
			print("right")
			GPIO.output(pin1,GPIO.LOW)
			GPIO.output(pin2,GPIO.HIGH)
			time.sleep(t)
			GPIO.output(pin1,GPIO.LOW)
			GPIO.output(pin2,GPIO.LOW)
		i+=1
	

def motor_func2(direction,t):
	
	
	if(direction== -1):
		print("DOWN")
		client.publish("Door/hatch_stat","Close")
		
		GPIO.output(pin3,GPIO.HIGH)
		GPIO.output(pin4,GPIO.LOW)
		time.sleep(t)
		GPIO.output(pin3,GPIO.LOW)
		GPIO.output(pin4,GPIO.LOW)
	else:
		print("UP")
		client.publish("Door/hatch_stat","Open")
		GPIO.output(pin3,GPIO.LOW)
		GPIO.output(pin4,GPIO.HIGH)
		time.sleep(t)
		GPIO.output(pin3,GPIO.LOW)
		GPIO.output(pin4,GPIO.LOW)
		

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
print ('Smart Door: Joystick, Password, Face recognition and MQTT Controls On')
#print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*range(4)))
print('-' * 70)


auto_trigger=23
auto_echo=24
GPIO.setup(auto_trigger,GPIO.OUT)
GPIO.setup(auto_echo,GPIO.IN)
GPIO.output(auto_trigger,GPIO.LOW)



person_count=0
sensor1=0
sensor2=0
read1=0
read2=0
tot=time.time()
gap=6
door_open=0	
# Main loop.
while True:
    if(tot + gap<time.time()):
        #print("Smart Door: Running")
        tot=time.time()
    # Read all the ADC channel values in a list.
    values = [0]*4
    for i in range(4):
        # Read the specified ADC channel using the previously set gain value.
        values[i] =adc.read_adc(i, gain=GAIN)
        # Note you can also pass in an optional data_rate parameter that controls
        # the ADC conversion time (in samples/second). Each chip has a different
        # set of allowed data rate values, see datasheet Table 9 config register
        # DR bit values.
        #values[i] = adc.read_adc(i, gain=GAIN, data_rate=128)
        # Each value will be a 12 or 16 bit signed integer value depending on the
        # ADC (ADS1015 = 12-bit, ADS1115 = 16-bit).
    # Print the ADC values.
    #if(matrix==-1):
       #print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*values))
      
    
    # Rotating STEPPER 
    dist1=distance(GPIO_TRIGGER,GPIO_ECHO)
    dist5=distance(GPIO_TRIGGER,GPIO_ECHO)
    a1=distance(auto_trigger,auto_echo)
    a2=distance(auto_trigger,auto_echo)
    #print(a1)
    #print(a2)
    if(auto_mode==1 and a1 < 25 and a2<25 and door_open<=5):
        check=1
        print('Door Access: Opening (Auto)')
        open_gate(-1,10)
        door_open=10
        door_time=time.time()
		
    if(dist1<12 and dist5<12):
        time.sleep(0.1)
    dist6=distance(GPIO_TRIGGER,GPIO_ECHO)
    #print("came here 3")
    #dist2=distance(27,4)
    #dist3=distance(15,12)

    #dist1=100
    dist2=100
    dist3=100
    
    #if(matrix==-1):
    	#print("first %f"%dist2)
    #if(matrix==-1):
    	#print("second %f"%dist3)

    if(matrix==-1):
        if(GPIO.input(ir1)==0):
            print("IR1")
            if(sensor2==0):
                sensor1=1
                
            else:
                person_count-=1
                if(check==1):		
                    print('Door Access: Closing (Auto)')
                    open_gate(1,0)
                    door_open=0
                    check=0
                print(person_count)
                client.publish("Door/count",str(person_count))
                time.sleep(2)
                print("Person Count: sleep UP")
                sensor2=0
                sensor1=0
           
        
        if( GPIO.input(ir2)==0):
            print("IR2")
            if(sensor1==0):
                sensor2=1
                	
            else:
                person_count+=1
                print(person_count)
                client.publish("Door/count",str(person_count))
                time.sleep(2)
                print("Person Count: sleep UP")
                sensor1=0
                sensor2=0
            
        
     
    	
    
    #if(matrix==-1):
       #print("dist1: %f"%dist1)
       #print(dist5)
       #print(dist6)	
    stop=1
    #dist5=10   #shit
    if(dist1<10 or dist5<10 or dist6<10):
        stop=0
    
    if(values[0]<15000 and values[0]>7000 and matrix ==-1 and door_open<10):
        motor_func(-1,val,1)
        door_open+=1
        client.publish("Door/open_stats",str(10-door_open))
        print(door_open)
    if(values[0]>25000 and values[0]<32000 and (stop or door_open<=1) and matrix==-1 and door_open>0):
        motor_func(1,val+0.4,1)
        door_open-=1
        client.publish("Door/open_stats",str(10-door_open))
        print(door_open)
    if(matrix_time + 10 <time.time() and matrix==1):
        print('Door Access: Press * again to enter password (auto reset)')
        matrix=-1
    if(hatch_time + h_time <time.time() and hatch_open==1):
        print('Hatch Access: Closing (Auto)')
        hatch_open=0
        motor_func2(-1,close_time)

    if(door_open==10 and door_time + 10 < time.time() and auto_mode==1):
        print('Door Access: Closing (Auto)')
        open_gate(1,0)
        door_open=0
        check=0

    if(block_time + block_val <time.time() and block==1):
        print('Door Access: Password access unblocked')
        block=0
        attempt=3
    # Pause for some time.
    time.sleep(0.01)
