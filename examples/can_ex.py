import can
import time
import threading

# --- Configuración del bus CAN ---
bus = can.interface.Bus(channel='can0', bustype='socketcan')

# --- Función para enviar mensajes periódicamente ---
def enviar_mensajes():
    contador = 0
    while True:
        msg = can.Message(
            arbitration_id=0x123,          # ID del mensaje
            data=[0xDE, 0xAD, 0xBE, contador % 256],  # 4 bytes, último byte cambia
            is_extended_id=False
        )
        try:
            bus.send(msg)
            print(f"Mensaje enviado: ID 0x123, Data {[hex(b) for b in msg.data]}")
        except can.CanError:
            print("Error enviando mensaje")
        contador += 1
        time.sleep(1)  # enviar cada segundo

# --- Función para recibir mensajes ---
def recibir_mensajes():
    print("Escuchando mensajes CAN...")
    while True:
        mensaje = bus.recv(timeout=1.0)
        if mensaje is not None:
            print(f"Recibido: ID {hex(mensaje.arbitration_id)}, Data {[hex(b) for b in mensaje.data]}")

# --- Ejecutar envío y recepción en hilos separados ---
if __name__ == "__main__":
    hilo_envio = threading.Thread(target=enviar_mensajes, daemon=True)
    hilo_recepcion = threading.Thread(target=recibir_mensajes, daemon=True)

    hilo_envio.start()
    hilo_recepcion.start()

    try:
        while True:
            time.sleep(0.1)  # Mantener el programa vivo
    except KeyboardInterrupt:
        print("Programa terminado")
