# Autor: Rubén Sahuquillo Redondo

# Descripción:
# - Este módulo define la clase CAMARA_HQ, que se encarga de manejar la cámara HQ de Raspberry Pi
#   para medir el diámetro del filamento en tiempo real.

# Flujo del programa:
# 1. Se inicializa la cámara y se configuran los parámetros.

# 2. Se lanzan tres hilos:
#    - Hilo de captura: Captura frames continuamente de la cámara y los guarda en self.frame_actual.
#    - Hilo de medición: Mide el diámetro del filamento usando la ROI vertical del láser y actualiza
#      self.diametro_mm, self.diametro_y1, self.diametro_y2.
#    - Hilo de preparación web: Prepara el JPEG para la web en segundo plano, dibujando la ROI del láser
#      y el diámetro detectado, y lo guarda en self.jpeg_actual.

# 3. La función generate_frames() es un generador que produce los frames JPEG formateados para el streaming web,
#   accediendo a self.jpeg_actual.

# 4. El método __calculate_diameter_from_roi() procesa la ROI del láser para detectar el diámetro del filamento,
#   devolviendo el diámetro en mm y las coordenadas verticales detectadas.

# 5. El método __send_diameter() se encarga de imprimir el diámetro calculado si verbose es True.

# Nota: Se han implementado locks para proteger el acceso a las variables compartidas entre hilos y evitar condiciones de carrera.


#------------------#
#---- Módulos -----#
#------------------#
from picamera2 import Picamera2
import time
import cv2
import numpy as np
import threading


#----------------#
#---- Clase -----#
#----------------#
class CAMARA_HQ:
    # -----Constructor que inicializa la cámara-----#
    def __init__(self, factor_mm_por_pixel=1.00, x_laser=640, ancho_roi=80, web_fps=15, web_width=640, web_height=360, jpeg_quality=50, verbose=False):
        """
        Descripción:
        Inicializa la cámara, configura los parámetros y lanza los hilos de captura, medición y preparación web.
        Parametros:
            - factor_mm_por_pixel: Factor de conversión de píxeles a mm.
            - x_laser: Coordenada X de la línea láser vertical.
            - ancho_roi: Ancho de la ROI vertical alrededor de la línea láser.
            - web_fps: FPS objetivo para el streaming web.
            - web_width: Ancho del frame para la web.
            - web_height: Alto del frame para la web.
            - jpeg_quality: Calidad del JPEG para la web (0-100).
            - verbose: Si es True, imprime el diámetro calculado. Si es False, no imprime nada.
        Retorna:
            - No retorna nada, pero inicia la cámara y los hilos de captura, medición y preparación web.
        """
        # Factor de conversión de píxeles a mm.
        self.factor_mm_por_pixel = factor_mm_por_pixel

        # Coordenada X de la línea láser vertical y ancho de la ROI.
        self.x_laser = x_laser
        self.ancho_roi = ancho_roi

        # Variables compartidas entre hilos.
        self.frame_actual = None
        self.diametro_mm = None
        self.diametro_y1 = None
        self.diametro_y2 = None
        self.jpeg_actual = None
        self.running = True

        # Locks para proteger variables compartidas.
        self.lock_frame = threading.Lock()
        self.lock_diametro = threading.Lock()
        self.lock_jpeg = threading.Lock()

        # Parámetros del streaming web.
        self.web_fps = web_fps
        self.web_width = web_width
        self.web_height = web_height
        self.jpeg_quality = jpeg_quality

        # Control para no imprimir miles de veces por segundo.
        self.verbose = verbose
        self._ultimo_print = 0
        self.print_interval = 0.20

        try:
            # Inicialización de la cámara
            self.picam2 = Picamera2()

            config = {
                "main": {"size": (1280, 720), "format": "RGB888"},
                "controls": {
                    "AeEnable": True,
                    "AwbEnable": True,
                    "Brightness": 0.0,
                    "Contrast": 1.0,
                    "Sharpness": 1.0,
                    "Saturation": 1.0
                }
            }
            self.__configurar(config)

            self.picam2.start()
            time.sleep(2)

            # Hilo único que toca la cámara.
            self.hilo_captura = threading.Thread(target=self.__capture_loop, daemon=True)

            # Hilo de medición del diámetro.
            self.hilo_medicion = threading.Thread( target=self.__diameter_loop, daemon=True)

            # Hilo que prepara el JPEG para la web.
            self.hilo_web = threading.Thread(target=self.__web_encoder_loop, daemon=True)

            self.hilo_captura.start()
            self.hilo_medicion.start()
            self.hilo_web.start()

            print("Cámara iniciada correctamente")

        except Exception as e:
            print("Camara no conectada")
            print(e)


    # -----Configuración de la cámara-----#
    def __configurar(self, config):
        """
        Descripción:
            Configura la cámara con una resolución de 1280x720 y ajustes automáticos de exposición e iluminación.
        Parametros:
            - config: Diccionario con la configuración de la cámara.
        Retorna:
            - No retorna nada, pero deja la cámara lista para capturar frames con la configuración adecuada
        """
        video_config = self.picam2.create_video_configuration(
            main=config["main"],
            controls=config["controls"]
        )
        self.picam2.configure(video_config)


    # -----Hilo de captura-----#
    def __capture_loop(self):
        """
        Descripción:
            Captura frames continuamente de la cámara y los guarda en self.frame_actual.
        Parametros:
            - No recibe parámetros, pero actualiza self.frame_actual con el último frame capturado.
        Retorna:
            - No retorna nada, pero mantiene self.frame_actual siempre con el último frame capturado de la cámara.
        """
        while self.running:
            try:
                frame = self.picam2.capture_array()

                with self.lock_frame:
                    self.frame_actual = frame

            except Exception as e:
                print("Error capturando frame:", e)
                time.sleep(0.01)


    # -----Hilo de medición-----#
    def __diameter_loop(self):
        """
        Descripción:
            Mide el diámetro del filamento usando la ROI vertical del láser.
        Parametros:
            - No recibe parámetros, pero actualiza self.diametro_mm con el diámetro calculado y self.diametro_y1, self.diametro_y2 con
            las coordenadas verticales detectadas.
        Retorna:
            - No retorna nada, pero mantiene self.diametro_mm siempre con el último diámetro calculado a partir de la ROI del láser,
            y self.diametro_y1, self.diametro_y2 con las coordenadas verticales detectadas para poder pintarlas en la web.
        """
        # Bucle de ejecución del hilo de medición.
        while self.running:
            # Protección del acceso a self.frame_actual para evitar condiciones de carrera con el hilo de captura.
            with self.lock_frame:
                if self.frame_actual is None:
                    roi = None

                else:
                    # Recortamos la ROI vertical alrededor de la línea láser. Nos aseguramos de no salirnos de los límites de la imagen.
                    _, w, _ = self.frame_actual.shape
                    x1 = self.x_laser - self.ancho_roi // 2
                    x2 = self.x_laser + self.ancho_roi // 2

                    x1 = max(0, x1)
                    x2 = min(w, x2)

                    if x2 <= x1:
                        roi = None
                    else:
                        roi = self.frame_actual[:, x1:x2].copy()

            if roi is None:
                time.sleep(0.001)
                continue

            # Calculo del diámetro a partir de la ROI del láser.
            resultado = self.__calculate_diameter_from_roi(roi)

            if resultado is not None:
                diametro, y_inicio, y_fin = resultado

                # Protección del acceso a self.diametro_mm, self.diametro_y1, self.diametro_y2 para evitar
                # condiciones de carrera con el hilo web.
                with self.lock_diametro:
                    self.diametro_mm = diametro
                    self.diametro_y1 = y_inicio
                    self.diametro_y2 = y_fin

                self.__send_diameter(diametro)

            time.sleep(0.001)


    # -----Hilo de codificación web-----#
    def __web_encoder_loop(self):
        """
        Descripción:
            Prepara el JPEG para la web en segundo plano.
        Parametros:
            - No recibe parámetros, pero actualiza self.jpeg_actual con el último JPEG preparado para la web, que incluye los dibujos de depuración
            y el diámetro detectado.
        Retorna:
            - No retorna nada, pero mantiene self.jpeg_actual siempre con el último JPEG preparado para la web.
        """
        # Intervalo entre frames para la web según el FPS objetivo
        # Ej: si web_fps=15, entonces intervalo=0.0666 segundos entre frames
        intervalo = 1.0 / self.web_fps

        # Bucle de ejecución del hilo de preparación web
        while self.running:
            inicio = time.perf_counter()

            # Protección del acceso a self.frame_actual para evitar condiciones de carrera con el hilo de captura.
            with self.lock_frame:
                frame = self.frame_actual

            if frame is None:
                time.sleep(0.01)
                continue

            frame_web = frame

            # Redimensionamos el frame para la web
            frame_web = cv2.resize(frame_web,(self.web_width, self.web_height),interpolation=cv2.INTER_AREA)

            # Protección del acceso a self.diametro_mm, self.diametro_y1, self.diametro_y2 para evitar condiciones de carrera
            # con el hilo de medición.
            with self.lock_diametro:
                diametro = self.diametro_mm
                diametro_y1 = self.diametro_y1
                diametro_y2 = self.diametro_y2

            escala_x = self.web_width / 1280
            x_laser_web = int(self.x_laser * escala_x)
            ancho_roi_web = max(2, int(self.ancho_roi * escala_x))
            x1_web = x_laser_web - ancho_roi_web // 2
            x2_web = x_laser_web + ancho_roi_web // 2

            cv2.rectangle(frame_web, (x1_web, 0), (x2_web, frame_web.shape[0] - 1), (0, 255, 255), 1)

            if diametro is not None:
                if diametro_y1 is not None and diametro_y2 is not None:
                    escala_y = self.web_height / 720
                    y1_diam_web = int(diametro_y1 * escala_y)
                    y2_diam_web = int(diametro_y2 * escala_y)

                    # Línea vertical del láser
                    cv2.line(frame_web,(x_laser_web, y1_diam_web), (x_laser_web, y2_diam_web), (0, 255, 0), 4)

                    # Marcas superior e inferior del diámetro.
                    cv2.line(frame_web, (x1_web, y1_diam_web), (x2_web, y1_diam_web), (255, 0, 255), 2)
                    cv2.line(frame_web, (x1_web, y2_diam_web), (x2_web, y2_diam_web),(255, 0, 255), 2)

                cv2.putText(frame_web, f"Diametro: {diametro:.2f} mm", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Codificamos el frame con los dibujos para la web en formato JPEG.
            ok, buffer = cv2.imencode(".jpg",frame_web,[cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality])

            if ok:
                # Protección del acceso a self.jpeg_actual para evitar condiciones de carrera con el hilo de generación de frames web.
                with self.lock_jpeg:
                    self.jpeg_actual = buffer.tobytes()

            tiempo = time.perf_counter() - inicio
            pausa = intervalo - tiempo

            if pausa > 0:
                time.sleep(pausa)


    # -----Generador de frames para la web-----#
    def generate_frames(self):
        """
        Descripción:
            Genera los frames JPEG para el streaming web.
        Parametros:
            - No recibe parámetros, pero accede a self.jpeg_actual para obtener el último JPEG preparado para la web.
        Retorna:
            - Retorna un generador que produce los frames JPEG formateados para el streaming web
        """
        # Bucle de generación de frames para la web
        while True:
            # Protección del acceso a self.jpeg_actual para evitar condiciones de carrera con el hilo de preparación web.
            with self.lock_jpeg:
                jpeg = self.jpeg_actual

            if jpeg is None:
                time.sleep(0.01)
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                jpeg +
                b"\r\n"
            )

            time.sleep(1.0 / self.web_fps)


    # ----Cálculo del diámetro desde ROI-----#
    def __calculate_diameter_from_roi(self, roi, medir_rojo=True):
        """
        Descripción:
            Calcula el diámetro del filamento a partir de la ROI vertical del láser.
        Parametros:
            - roi: Imagen recortada alrededor de la línea láser, con forma (alto, ancho_roi, 3) y formato BGR.
            - medir_rojo: Si es False, mide la ausencia/interrupción del rojo. Si es True, mide directamente la zona roja detectada.
        Retorna:
            - Retorna una tupla (diametro_mm, y_inicio, y_fin) donde diametro_mm es el diámetro calculado en mm, y y_inicio, y_fin son las coordenadas verticales detectadas del filamento para poder dibujarlas en la web. Si no se detecta un diámetro válido, retorna None.
        """

        r = roi[:, :, 2].astype(np.int16)
        g = roi[:, :, 1].astype(np.int16)
        b = roi[:, :, 0].astype(np.int16)

        # Máscara para detectar píxeles rojos
        mascara_rojo = ((r > 120) & (r > g + 40) & (r > b + 40))

        # Sumamos la cantidad de píxeles rojos en cada fila de la ROI.
        suma_rojo = mascara_rojo.sum(axis=1)

        # Si la suma de rojo en una fila supera el umbral, consideramos que esa fila tiene rojo
        umbral_rojo_fila = 2
        filas_con_rojo = suma_rojo >= umbral_rojo_fila

        # Si medir_rojo es True, buscamos la mayor secuencia de filas con rojo. Si es False, buscamos la mayor secuencia de filas sin rojo.
        if medir_rojo:
            filas_a_medir = filas_con_rojo
        else:
            filas_a_medir = ~filas_con_rojo

        mejor_inicio = None
        mejor_fin = None
        inicio_actual = None

        # Iteración para encontrar la mayor secuencia de filas válidas (con rojo o sin rojo según medir_rojo).
        for i, fila_valida in enumerate(filas_a_medir):
            if fila_valida:
                if inicio_actual is None:
                    inicio_actual = i
            else:
                if inicio_actual is not None:
                    fin_actual = i - 1

                    if (mejor_inicio is None or (fin_actual - inicio_actual) > (mejor_fin - mejor_inicio)):
                        mejor_inicio = inicio_actual
                        mejor_fin = fin_actual

                    inicio_actual = None

        if inicio_actual is not None:
            fin_actual = len(filas_a_medir) - 1

            if (mejor_inicio is None or (fin_actual - inicio_actual) > (mejor_fin - mejor_inicio)):
                mejor_inicio = inicio_actual
                mejor_fin = fin_actual

        if mejor_inicio is None:
            return None

        diametro_pixeles = mejor_fin - mejor_inicio + 1

        # Filtro contra ruido.
        if diametro_pixeles < 5:
            return None

        diametro_mm = diametro_pixeles * self.factor_mm_por_pixel

        # Devolvemos también las coordenadas verticales detectadas para poder pintarlas en la web.
        return diametro_mm, mejor_inicio, mejor_fin


    # -----Envío del diámetro al microcontrolador-----#
    def __send_diameter(self, diametro_mm):
        """
        Descripción:
            Imprime el diámetro calculado si verbose es True.
        Parametros:
            - diametro_mm: El diámetro calculado en mm que se desea imprimir.
        Retorna:
            - No retorna nada, pero si verbose es True, imprime el diámetro calculado en mm
        """
        if not self.verbose:
            return
        print(f"Diametro: {diametro_mm:.2f} mm")


    # -----Parar cámara e hilos-----#
    def stop(self):
        """
        Descripción:
            Detiene la cámara y los hilos de captura, medición y preparación web.
        Parametros:
            - No recibe parámetros, pero detiene la cámara y los hilos de captura, medición y preparación web.
        Retorna:
            - No retorna nada, pero deja la cámara y los hilos detenidos.
        """
        self.running = False
        time.sleep(0.1)

        try:
            self.picam2.stop()
        except Exception:
            pass


# -----Main de prueba-----#
if __name__ == "__main__":
    camera = CAMARA_HQ()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        camera.stop()
        print("Cámara detenida")
