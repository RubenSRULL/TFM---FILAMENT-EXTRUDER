from gpiozero import LED


class LASER:
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