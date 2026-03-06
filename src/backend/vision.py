# Autor: Rubén Sahuquillo Redondo

from picamera2 import Picamera2
import base64
import io
import cv2
import time


class Vision:
    """Módulo de visión para capturar imágenes utilizando la cámara del Raspberry Pi
    Atributos:
        picam2 (Picamera2): Instancia de la cámara Picamera2
    Métodos:
        __init__: Constructor para inicializar la cámara
        __del__: Destructor para liberar recursos de la cámara
        capture_image: Método para capturar una imagen y convertirla a base64
    """
    # Constructor para inicializar la cámara
    def __init__(self):
        """
        Inicializa la cámara utilizando Picamera2
        Args:            None
        Returns:         None
        """
        try:
            self.picam2 = Picamera2()
            self.picam2.start()
            print("Cámara inicializada correctamente")

        except Exception as e:
            print(f"Error al inicializar la cámara: {e}")
            self.picam2 = None


    # Destructor para liberar recursos de la cámara
    def __del__(self):
        """
        Detiene la cámara y libera los recursos asociados
        Args:            None
        Returns:         None
        """
        if self.picam2 is not None:
            self.picam2.stop()
            print("Cámara detenida y recursos liberados")


    # Método para capturar una imagen y convertirla a base64 para web
    def capture_image_web(self):
        """
        Captura una imagen utilizando la cámara y la convierte a formato base64
        Args:            None
        Returns:         str: Imagen en formato base64 o None si no se pudo capturar la imagen
        """
        if self.picam2 is None:
            return None
            
        try:
            frame = self.picam2.capture_array()
            buf = io.BytesIO()
            self.picam2.capture_file(buf, format='jpeg')
            base64_image = base64.b64encode(buf.getvalue()).decode('utf-8')
            return base64_image

        except Exception as e:
            print(f"Error al capturar la imagen: {e}")
            return None


    # Método para capturar una imagen y devolverla como un array para procesamiento
    def capture_image(self):
        """
        Captura una imagen utilizando la cámara y la devuelve como un array
        Args:            None
        Returns:         numpy.ndarray: Imagen capturada como un array o None si no se pudo capturar la imagen
        """
        if self.picam2 is None:
            return None
            
        try:
            frame = self.picam2.capture_array()
            return frame

        except Exception as e:
            print(f"Error al capturar la imagen: {e}")
            return None

    
    def process_image(self, image, mode='laser', filament_position='horizontal'):
        """
        Procesa la imagen capturada para detectar el diámetro de filamento usando línea láser:
        1 - Convertir la imagen a espacio de color HSV para detectar el color rojo de la línea láser
        2 - Crear máscaras para los rangos de color rojo y combinarlas
        3 - Aplicar operaciones morfológicas para limpiar la máscara y eliminar ruido
        4 - Encontrar contornos en la máscara de color rojo y filtrar por área para eliminar ruido
        5 - Calcular el diámetro basado en la distancia entre los extremos de los contornos válidos
        6 - Convertir el diámetro de píxeles a milímetros usando una relación de conversión predefinida
        Args:       image (numpy.ndarray): Imagen capturada como un array
        Returns:    float: Diámetro de filamento detectado en mm o None si no se pudo procesar la imagen
        """
        if mode == 'laser':
            try:
                # Convertir a espacio de color HSV para mejor detección de color rojo
                hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
                # Rangos de color rojo en HSV 
                lower_red1 = (0, 120, 70)
                upper_red1 = (10, 255, 255)
                lower_red2 = (170, 120, 70)
                upper_red2 = (180, 255, 255)

                # Crear máscaras para ambos rangos de rojo y combinarlas en una sola máscara
                mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
                mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
                red_mask = cv2.bitwise_or(mask1, mask2)

                # Aplicar operaciones morfológicas para limpiar la máscara y eliminar ruido
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
                red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
                red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)

                # Deteccion de contornos en la máscara de color rojo (laser)
                contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Si se encuentran contornos, filtrar por área para eliminar ruido y calcular el diámetro
                if contours:
                    min_area = 10
                    max_area = 500
                    valid_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area and cv2.contourArea(cnt) < max_area]

                    # Si hay contornos válidos, calcular el diámetro basado en la distancia entre los extremos de los contornos
                    if valid_contours:
                        # Si hay múltiples contornos calcular la distancia entre los extremos y encontrar el diámetro máximo
                        if len(valid_contours) > 1:
                            all_points = []
                            for cnt in valid_contours:
                                all_points.extend(cnt.reshape(-1, 2).tolist())

                            # Si hay puntos válidos, calcular la bounding box que los contiene a todos
                            if all_points:
                                x_coords = [pt[0] for pt in all_points]
                                y_coords = [pt[1] for pt in all_points]
                                min_x, max_x = min(x_coords), max(x_coords)
                                min_y, max_y = min(y_coords), max(y_coords)

                                # Calcular el diámetro basado en la posición del filamento (horizontal o vertical)
                                if filament_position == 'horizontal':
                                    diameter_pixels = max_y - min_y

                                elif filament_position == 'vertical':
                                    diameter_pixels = max_x - min_x

                                else:
                                    return None

                            else:
                                return None

                        # Si solo hay un contorno válido, calcular el ancho del bounding box de ese contorno
                        else:
                            x, y, w, h = cv2.boundingRect(valid_contours[0])
                            diameter_pixels = w

                        # Convertir píxeles a mm
                        pixel_to_mm = 0.01
                        diameter_mm = diameter_pixels * pixel_to_mm
                        return round(diameter_mm, 3)
                return None

            except Exception as e:
                print(f"Error al procesar la imagen: {e}")
                return None


    def get_diameter(self):
        """
        Captura una imagen y procesa el diámetro del filamento usando línea láser
        Returns:
            float: Diámetro del filamento en mm o None si no se pudo medir
        """
        image = self.capture_image()
        if image is not None:
            return self.process_image(image, mode='laser', filament_position='horizontal')
        return None

    
    def get_processed_image_web(self):
        """
        Captura una imagen, procesa el diámetro y devuelve la imagen con visualización del diámetro en base64
        Returns:
            str: Imagen procesada en base64 con diámetro dibujado, o imagen original si no se pudo procesar
        """
        if self.picam2 is None:
            return None
            
        try:
            image = self.capture_image()
            if image is None:
                return None
            
            # Procesar para obtener el diámetro
            diameter_mm = self.process_image(image, mode='laser', filament_position='horizontal')
            
            # Dibujar el diámetro en la imagen
            processed_image = self.draw_diameter_on_image(image, diameter_mm)
            
            # Convertir a BGR para codificar correctamente
            processed_image_bgr = cv2.cvtColor(processed_image, cv2.COLOR_RGB2BGR)
            
            # Convertir a base64
            _, buffer = cv2.imencode('.jpg', processed_image_bgr)
            base64_image = base64.b64encode(buffer).decode('utf-8')
            return base64_image
            
        except Exception as e:
            print(f"Error procesando imagen con diámetro: {e}")
            # Devolver imagen original si falla
            try:
                image = self.capture_image()
                if image is not None:
                    # Convertir RGB a BGR para codificar
                    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    _, buffer = cv2.imencode('.jpg', image_bgr)
                    return base64.b64encode(buffer).decode('utf-8')
            except:
                pass
            return None


    def draw_diameter_on_image(self, image, diameter_mm):
        """
        Dibuja el diámetro detectado en la imagen para visualización
        Args:
            image (numpy.ndarray): Imagen original capturada
            diameter_mm (float): Diámetro del filamento en mm para dibujar en la imagen
        Returns:
            numpy.ndarray: Imagen con el diámetro dibujado
        """
        if diameter_mm is not None:
            # Dibujar un rectángulo y el texto del diámetro en la imagen
            cv2.rectangle(image, (10, 10), (200, 60), (255, 0, 0), 2)
            cv2.putText(image, f"Diametro: {diameter_mm} mm", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        return image


# Prueba del módulo Vision
if __name__ == "__main__":
    vision = Vision()
    while True:
        image = vision.capture_image()
        if image is not None:
            diameter = vision.get_diameter()
            print(f"Diámetro del filamento: {diameter} mm")
            image_with_diameter = vision.draw_diameter_on_image(image, diameter)
            cv2.imshow("Filament Diameter Detection", image_with_diameter)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        time.sleep(0.1)