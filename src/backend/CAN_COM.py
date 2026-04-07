# Autor: Ruben Sahuquillo Redondo


#-----------------------------------------#
#--- Importación de módulos necesarios ---#
#-----------------------------------------#
import can
import threading


#-------------------------------------------#
#--- Clase CAN_COM para comunicación CAN ---#
#-------------------------------------------#
class CAN_COM:
    #-----Constructor que inicializa el bus CAN-----#
    def __init__(self, channel='can0', bustype='socketcan'):
        """
        Descripción:
            Inicializa el bus CAN utilizando la biblioteca python-can.
            Maneja posibles errores durante la inicialización.
            Establece variables para controlar la recepción de mensajes en un hilo separado.
        Parámetros:
            channel (str): El canal del bus CAN a utilizar (por defecto 'can0').
            bustype (str): El tipo de bus CAN a utilizar (por defecto 'socketcan').
        Retorno:
            None
        """
        # Intentar inicializar el bus CAN y manejar posibles errores
        try:
            self.bus = can.interface.Bus(channel=channel, bustype=bustype)
            print(f"Bus CAN inicializado en {channel}")
        except Exception as e:
            print(f"Error inicializando bus CAN: {e}")
            self.bus = None

        # Variable para controlar el hilo de recepción
        self._running = False
        self._thread = None


    #-----Envio de mensajes CAN-----#
    def enviar_mensaje(self, arbitration_id, data_str):
        """
        Descripción:
            Envía un mensaje CAN con un ID de arbitraje y datos codificados.
            Maneja posibles errores durante el envío.
        Parámetros:
            arbitration_id (int): El ID de arbitraje del mensaje CAN.
            data_str (str): Los datos a enviar, que serán codificados a bytes.
        Retorno:
            None
        """
        # Si el bus no se ha inicializado correctamente, no se puede enviar mensajes
        if self.bus is None:
            return
        # Si los datos son una cadena, convertir a bytes
        if isinstance(data_str, str):
            data_codificado = data_str.encode('utf-8')
        # Limitar los datos a 8 bytes (tamaño máximo de un mensaje CAN)
        data_codificado = data_codificado[:8]
        # Crear el mensaje CAN
        msg = can.Message(arbitration_id=arbitration_id,data=data_codificado,is_extended_id=False)
        # Intentar enviar el mensaje y manejar posibles errores
        try:
            self.bus.send(msg)
            print(f"[TX] {hex(arbitration_id)} -> {data_codificado} - {data_str}")
        except can.CanError as e:
            print(f"Error enviando: {e}")


    #-----Recepción de mensajes CAN-----#
    def recepcion_mensajes(self):
        """
        Descripción:
            Función que se ejecuta en un hilo separado para recibir mensajes CAN de forma continua.
            Imprime los mensajes recibidos en la consola, decodificando los datos a texto cuando sea posible.
            Maneja posibles errores durante la recepción.
        Parámetros:
            None
        Retorno:
            None
        """
        # Si el bus no se ha inicializado correctamente, no se puede recibir mensajes
        while self._running:
            # Intentar recibir un mensaje con un timeout para evitar bloqueos indefinidos
            try:
                msg = self.bus.recv(timeout=1.0)
                if msg:
                    texto = msg.data.decode('utf-8', errors='ignore')
                    print(f"[RX] {hex(msg.arbitration_id)} -> {msg.data} ({texto})")
            except can.CanError as e:
                print(f"Error recibiendo: {e}")


    #-----Métodos para iniciar y detener la recepción en un hilo separado-----#
    def iniciar_recepcion(self):
        """
        Descripción:
            Inicia la recepción de mensajes CAN en un hilo separado.
            Si la recepción ya está en ejecución, no hace nada.
        Parámetros:
            None
        Retorno:
            None
        """
        # Si la recepción ya está en ejecución, no hacer nada
        if self._running:
            return
        # Iniciar el hilo de recepción
        self._running = True
        self._thread = threading.Thread(target=self.recepcion_mensajes, daemon=True)
        self._thread.start()


    #----Detener la recepción y esperar a que el hilo termine-----#
    def detener_recepcion(self):
        """
        Descripción:
            Detiene la recepción de mensajes CAN y espera a que el hilo de recepción termine.
        Parámetros:
            None
        Retorno:
            None
        """
        self._running = False
        if self._thread:
            self._thread.join()


    #----Cerrar el bus CAN y limpiar recursos-----#
    def cerrar_bus(self):
        """
        Descripción:
            Detiene la recepción de mensajes y cierra el bus CAN, liberando los recursos asociados.
            Maneja posibles errores durante el cierre del bus.
        Parámetros:
            None
        Retorno:
            None
        """
        self.detener_recepcion()
        if self.bus:
            self.bus.shutdown()
            print("Bus cerrado")


#--- Programa principal para probar la clase CAN_COM ---#
if __name__ == "__main__":
    # Crear instancia de CAN_COM y manejar la comunicación CAN
    can_com = CAN_COM()
    # Iniciar la recepción de mensajes y permitir al usuario enviar mensajes desde la consola
    try:
        can_com.iniciar_recepcion()
        while True:
            cmd = input("Escribe mensaje (o 'salir'): ")
            if cmd.lower() == "salir":
                break
            can_com.enviar_mensaje(0x123, cmd)
    except KeyboardInterrupt:
        print("\nInterrumpido por usuario")
    finally:
        can_com.cerrar_bus()