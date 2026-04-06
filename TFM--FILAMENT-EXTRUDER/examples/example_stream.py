from picamera2 import Picamera2, Preview
from libcamera import Transform

picam2 = Picamera2()
picam2.start_preview(Preview.QTGL, transform=Transform(hflip=True))
picam2.start()
while True:
    pass
#time.sleep(60)
#picam2.close()