from picamera2 import Picamera2
import time
import cv2
import base64

class CAMERA_HQ:
    def __init__(self):
        self.__getstate__picam2 = Picamera2()

        self.video_config = self.picam2.create_video_configuration(
            main={"size": (1280, 720), "format": "RGB888"},
            controls={
                "AeEnable": True,
                "AwbEnable": True,
                "Brightness": 0.0,
                "Contrast": 1.0,
                "Sharpness": 2.0,
                "Saturation": 1.0
            }
        )

        self.picam2.configure(self.video_config)
        self.picam2.start()
        time.sleep(1)

    def capture_frame_base64(self):
        frame = self.picam2.capture_array()
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ret:
            return None
        
        encoded = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded}"