import socket
import threading
import time
import random

# Hace el selective repeat

nombreServidor = 'localhost'
puertoServidor = 12000
TAMANO_VENTANA = 4
TIMEOUT = 2

socketCliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mensajes = ["0:mensaje", "1:mensaje", "2:mensaje", "3:mensaje"]
acknowledged = set()

proximaSecuencia = 0
temporizadores = {}

def iniciar_temporizador(numero_marco):
    temporizadores[numero_marco] = time.time()

def verificar_temporizador(numero_marco):
    if time.time() - temporizadores[numero_marco] > TIMEOUT:
        return True
    return False

def simular_marco_perdido():
    aleatorio = random.random()
    if aleatorio > 0.5:
        return False
    return True

def enviar_marco(numero_marco):
    mensaje = mensajes[numero_marco]
    print(f"Enviando marco {numero_marco}: {mensaje}")
    iniciar_temporizador(numero_marco)
    if simular_marco_perdido():
        print(f"Marco {numero_marco} perdido")
        return
    socketCliente.sendto(mensaje.encode(), (nombreServidor, puertoServidor))

def recibir_ack():
    while len(mensajes) != len(acknowledged):
        try:
            ack, _ = socketCliente.recvfrom(2048)
            ack_num = int(ack.decode())
            print(f"Recibido ACK para marco {ack_num}")
            acknowledged.add(ack_num)
        except socket.timeout:
            break
        except Exception as e:
            print(f"Error al recibir ACK: {e}")
            break

def cliente():
    
    global proximaSecuencia
    socketCliente.settimeout(TIMEOUT)

    # Hilo para manejar los ACKs
    ack_handler = threading.Thread(target=recibir_ack)
    ack_handler.start()

    while proximaSecuencia < len(mensajes):
        for numero_marco in range(proximaSecuencia, min(proximaSecuencia + TAMANO_VENTANA, len(mensajes))):
            if numero_marco not in acknowledged:
                time.sleep(1)
                enviar_marco(numero_marco)

        for numero_marco in range(proximaSecuencia, min(proximaSecuencia + TAMANO_VENTANA, len(mensajes))):
            if numero_marco not in acknowledged and verificar_temporizador(numero_marco):
                print(f"Retransmitiendo marco {numero_marco}")
                time.sleep(1)
                enviar_marco(numero_marco)

        proximaSecuencia = min(proximaSecuencia + TAMANO_VENTANA, len(mensajes))
        time.sleep(1)

    socketCliente.close()

if __name__ == "__main__":
    cliente()
