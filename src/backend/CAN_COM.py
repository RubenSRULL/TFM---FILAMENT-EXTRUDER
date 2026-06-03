import can
from queue import Queue, Empty
import threading
import time
import subprocess


class CAN_COM:
    def __init__(self, channel='can0', interface='socketcan', modo_simulado=True):
        """
        Descripción:
            Inicializa la comunicación CAN. Si la interfaz no está disponible, puede entrar en modo simulado.
        Parámetros:
            channel (str): Nombre de la interfaz CAN (por defecto 'can0').
            interface (str): Tipo de interfaz CAN (por defecto 'socketcan').
            modo_simulado (bool): Si True, activa el modo simulado si la interfaz no está disponible (por defecto True).
        Retorno:
            None
        """
        self.channel = channel
        self.interface = interface
        self.bus = None
        self._running = False
        self.queue = Queue()
        self._thread = None
        self.modo_simulado = False

        if not self._existe_interfaz_can(channel):
            if modo_simulado:
                self.modo_simulado = True
                print(f"Interfaz {channel} no encontrada. CAN en modo SIMULADO.")

            else:
                print(f"Interfaz {channel} no encontrada. CAN desactivado.")

            return

        try:
            # Intentar abrir la interfaz CAN
            self.bus = can.interface.Bus(channel=channel, interface=interface)
            print(f"CAN inicializado correctamente en {channel}")

        except Exception as e:
            if modo_simulado:
                self.modo_simulado = True
                print(f"No se pudo abrir {channel}. CAN en modo SIMULADO. Detalle: {e}")
            else:
                print(f"Error al inicializar CAN: {e}")


    # Método privado para verificar si la interfaz CAN existe
    def _existe_interfaz_can(self, channel):
        """
        Descripción:
            Verifica si la interfaz CAN especificada existe en el sistema.
        Parámetros:
            channel (str): Nombre de la interfaz CAN a verificar.
        Retorno:
            bool: True si la interfaz existe, False en caso contrario.
        """
        # Utiliza el comando 'ip link show <channel>' para verificar la existencia de la interfaz
        resultado = subprocess.run(
            ["ip", "link", "show", channel],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return resultado.returncode == 0


    # Método para recibir mensajes CAN en un hilo separado
    def recepcion_mensajes(self):
        """
        Descripción:
            Método que se ejecuta en un hilo separado para recibir mensajes CAN de forma continua.
        Parámetros:
            None
        Retorno:
            None
        """
        while self._running:
            if self.modo_simulado:
                time.sleep(0.1)
                continue

            if self.bus is None:
                time.sleep(0.1)
                continue

            try:
                msg = self.bus.recv(timeout=1)
                if msg:
                    texto = msg.data.decode('utf-8', errors='ignore')
                    self.queue.put((msg.arbitration_id, texto))

            except Exception as e:
                print(f"Error recibiendo mensaje CAN: {e}")


    # Método para obtener mensajes recibidos
    def get_mensaje(self, timeout=1):
        """
        Descripción:
            Obtiene un mensaje recibido de la cola de mensajes.
        Parámetros:
            timeout (float): Tiempo máximo de espera para obtener un mensaje.
        Retorno:
            tuple: Una tupla con el ID de arbitraje y el texto del mensaje, o None si no hay mensajes disponibles.
        """
        try:
            return self.queue.get(timeout=timeout)
        except Empty:
            return None


    # Método para enviar mensajes CAN
    def enviar_mensaje(self, arbitration_id, data_str):
        """
        Descripción:
            Envía un mensaje por la red CAN.
        Parámetros:
            arbitration_id (int): ID de arbitraje del mensaje.
            data_str (str): Datos del mensaje como cadena de texto.
        Retorno:
            bool: True si el mensaje se envió correctamente, False en caso contrario.
        """
        if self.modo_simulado:
            print(f"[CAN SIMULADO] ID: {hex(arbitration_id)} DATA: {data_str}")
            # En modo simulado, simplemente se imprime el mensaje y se agrega a la cola como si fuera recibido
            self.queue.put((arbitration_id, "OK"))
            return True

        if self.bus is None:
            print("Error: CAN no disponible")
            return False

        try:
            # Asegurarse de que los datos no excedan los 8 bytes permitidos por CAN
            data_bytes = data_str.encode('utf-8')[:8]
            # Construir el mensaje CAN y enviarlo
            msg = can.Message(arbitration_id=arbitration_id, data=data_bytes, is_extended_id=False)
            self.bus.send(msg)
            return True

        except Exception as e:
            print(f"Error enviando mensaje CAN: {e}")
            return False


    # Métodos para iniciar y detener la recepción de mensajes
    def iniciar_recepcion(self):
        """
        Descripción:
            Inicia la recepción de mensajes CAN en un hilo separado. Si ya está en ejecución, no hace nada.
        Parámetros:
            None
        Retorno:
            None
        """
        if self._running:
            return

        if self.bus is None and not self.modo_simulado:
            print("No se puede iniciar recepción: CAN no disponible")
            return

        self._running = True
        # Iniciar el hilo de recepción de mensajes
        self._thread = threading.Thread(target=self.recepcion_mensajes,daemon=True)
        self._thread.start()


    # Método para detener la recepción de mensajes
    def detener_recepcion(self):
        """
        Descripción:
            Detiene la recepción de mensajes CAN y espera a que el hilo termine.
        Parámetros:
            None
        Retorno:
            None
        """
        self._running = False

        if self._thread:
            self._thread.join()
            self._thread = None