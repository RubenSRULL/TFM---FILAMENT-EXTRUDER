# Autor: Ruben Sahuquillo Redondo


#-----------------------------------------#
#--- Importación de módulos necesarios ---#
#-----------------------------------------#
from picamera2 import Picamera2
import time
import cv2
import numpy as np

#----------------------------------------------#
#--- Clase CAMARA_HQ para captura de imagen ---#
#----------------------------------------------#
class CAMARA_HQ():
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
                "AeEnable": False,          # Control exposición
                "ExposureTime": 10000,      # Valor bajo para que solo brille el láser
                "AnalogueGain": 1.0,        # Evitar ruido digital
                "AwbEnable": False,         # Balance de blancos
                "AwbGains": (1.0, 1.0),     # Evitar que el color cambie solo
                "Brightness": 0.0,
                "Contrast": 1.2,            # Subir un poco para marcar bordes
                "Sharpness": 2.0,           # Ayuda a definir el borde del filamento
                "Saturation": 1.5           # Resalta el rojo del láser
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
            # Captura imagen
            frame = self.picam2.capture_array()
            # Convertir a BGR
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            # Convertir a HSV
            hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
            # Rojos
            lower_red1 = np.array([0, 120, 70])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 120, 70])
            upper_red2 = np.array([180, 255, 255])
            # Máscaras
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask_final = mask1 + mask2
            # Contornos rojo
            contornos, _ = cv2.findContours(mask_final, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in contornos:
                area = cv2.contourArea(c)
                if area > 50:
                    x, y, w, h = cv2.boundingRect(c)
                    y_top = y
                    y_bottom = y + h
                    diametro_pixeles = y_bottom - y_top
                    diametro_mm = diametro_pixeles * 1
                    cv2.line(frame_bgr, (x + w//2, y_top), (x + w//2, y_bottom), (255, 0, 0), 2)
                    cv2.putText(frame_bgr, f"{diametro_mm:.2f} mm", (x + w, y + h//2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)


            # Codificación para streaming
            _, buffer = cv2.imencode('.jpg', frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


#-----Main-----#
if __name__ == "__main__":
    camera = CAMARA_HQ()
    camera.generate_frames()