import zbarlight
import os
import sys
import PIL
import subprocess

print ('Taking picture..')
subprocess.call(["fswebcam","--no-banner","-r","1280x720","-F","4","-q","./qr_code/qr_image.jpg"])
f=1
if(f):
    print 'Scanning image..'
    f = open('./qr_code/qr_image.jpg','rb')
    qr = PIL.Image.open(f);
    qr.load()

    codes = zbarlight.scan_codes('qrcode',qr)
    if(codes==None):
       
        print 'No QR code found'
    else:
        print 'QR code(s):'
        print codes
       