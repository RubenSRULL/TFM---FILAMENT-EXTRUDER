# Autor: Rubén Sahuquillo Redondo

# Descripción:
# - Este módulo define la clase LASER, que proporciona una interfaz para controlar un láser conectado a un pin GPIO de la
#   Raspberry Pi utilizando la biblioteca gpiozero.

# Flujo del programa:
# 1. Se inicializa la clase LASER.
# 2. La clase tiene métodos para encender y apagar el láser.
# 3. Los mensajes recibidos se almacenan en una cola, y se pueden obtener mediante el método get_mensaje.
# 4. Para enviar mensajes, se utiliza el método enviar_mensaje, que acepta un ID de arbitraje y una cadena de datos.
#   Si está en modo simulado, simplemente imprime el mensaje en la consola.
# 5. La clase maneja errores de conexión y envío, y proporciona información sobre el estado de la comunicación CAN.


#------------------#
#---- Módulos -----#
#------------------#
from gpiozero import LED


# ------------------- #
#---- Clase LASER --- #
# ------------------- #
class LASER:
    # ----Constructor de la clase LASER-----#
    def __init__(self, pin=4):
        """
        Descripción:
            Inicializa el láser conectado al pin especificado.
        Parámetros:
            pin (int): Número del pin GPIO al que está conectado el láser (por defecto 4).
        Retorno:
            None
        """
        self.laser = LED(pin, initial_value=False)


    # -----Método para encender el láser-----#
    def on(self):
        """
        Descripción:
            Enciende el láser.
        Parámetros:
            None
        Retorno:
            None
        """
        self.laser.on()


    # -----Método para apagar el láser-----#
    def off(self):
        """
        Descripción:
            Apaga el láser.
        Parámetros:
            None
        Retorno:
            None
        """
        self.laser.off()