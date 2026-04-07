# Autor: Ruben Sahuquillo Redondo


#-----------------------------------------#
#--- Importación de módulos necesarios ---#
#-----------------------------------------#
from picamera2 import Picamera2
import time
import cv2


#----------------------------------------------#
#--- Clase CAMERA_HQ para captura de imagen ---#
#----------------------------------------------#
class CAMERA_HQ():
    #-----Constructor que inicializa la cámara-----#
    def __init__(self):
        """
        Descripción:
            Inicializa la cámara utilizando la biblioteca picamera2.
        Parámetros:
            None
        Retorno:
            None
        """
        try:
            self.picam2 = Picamera2()
            self.configurar()
            self.picam2.start()
            time.sleep(2)

        except Exception as e:
            print("Camara no conectada")


    #-----Configuración de la cámara-----#
    def configurar(self):
        """
        Descripción:
            Establece una configuración para la cámara
        Parámetros:
            None
        Retorno:
            None
        """
        video_config = self.picam2.create_video_configuration(
            main={"size": (1280, 720), "format": "RGB888"},
            controls={
                "AeEnable": True,
                "AwbEnable": True,
                "Brightness": 0.0,
                "Contrast": 1.0,
                "Sharpness": 1.0,
                "Saturation": 1.0
            }
        )
        self.picam2.configure(video_config)
        

    #-----Generador de frames de la cámara-----#
    def generate_frames(self):
        """
        Descripción:
            Generador que provee un frame capturado por la cámara cada vez que es llamado
        Parámetros:
            None
        Retorno:
            frame
        """
        while True:
            frame = self.picam2.capture_array()
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            _, buffer = cv2.imencode('.jpg', frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


#-----Main-----#
if __name__ == "__main__":
    camera = CAMERA_HQ()
    camera.generate_frames()