from flask import Flask, Response
from picamera2 import Picamera2, Preview
import cv2
import time

app = Flask(__name__)

picam2 = Picamera2()

# Configuración de video con parámetros de nitidez
video_config = picam2.create_video_configuration(
    main={"size": (1280, 720), "format": "RGB888"},
    controls={
        "AeEnable": True,          # Exposición automática
        "AwbEnable": True,         # Balance de blancos automático
        "Brightness": 0.0,
        "Contrast": 1.0,
        "Sharpness": 1.0,
        "Saturation": 1.0
    }
)



picam2.configure(video_config)
picam2.start()
time.sleep(2)  # estabilización

def generate_frames():
    while True:
        frame = picam2.capture_array()
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
        frame_bytes = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
        )

@app.route('/video')
def video_feed():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/')
def index():
    return "<h1>Streaming de cámara</h1><img src='/video'>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
