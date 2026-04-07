import can
from queue import Queue
import threading

class CAN_COM:
    def __init__(self, channel='can0', bustype='socketcan'):
        self.bus = can.interface.Bus(channel=channel, bustype=bustype)
        self._running = False
        self.queue = Queue()
        self._thread = None

    def recepcion_mensajes(self):
        while self._running:
            msg = self.bus.recv(timeout=1)
            if msg:
                texto = msg.data.decode('utf-8', errors='ignore')
                self.queue.put((msg.arbitration_id, texto))

    def get_mensaje(self, timeout=1):
        try:
            return self.queue.get(timeout=timeout)
        except:
            return None

    def enviar_mensaje(self, arbitration_id, data_str):
        data_bytes = data_str.encode('utf-8')[:8]
        msg = can.Message(arbitration_id=arbitration_id, data=data_bytes, is_extended_id=False)
        self.bus.send(msg)

    def iniciar_recepcion(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self.recepcion_mensajes, daemon=True)
        self._thread.start()

    def detener_recepcion(self):
        self._running = False
        if self._thread: self._thread.join()