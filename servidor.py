import socket
import threading
import time
import random

# Hace el selective repeat

nombreServidor = 'localhost'
puertoServidor = 12000
TAMANO_VENTANA = 4
TIMEOUT = 3

socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

mensajes = ["0:mensaje", "1:mensaje", "2:mensaje", "3:mensaje"]
acknowledged = set()

temporizadores = {}

def iniciar_temporizador(numero_marco):
    temporizadores[numero_marco] = time.time()

def temporizador_vencido(numero_marco):
    if numero_marco in temporizadores and time.time() - temporizadores[numero_marco] > TIMEOUT:
        return True
    return False

def simular_marco_perdido():
    aleatorio = random.random()
    if aleatorio > 0.2:
        return False
    return True

def enviar_marco(numero_marco):
    mensaje = mensajes[numero_marco]
    print(f"Enviando marco {numero_marco}: {mensaje}")
    iniciar_temporizador(numero_marco)
    if simular_marco_perdido():
        print(f"Marco {numero_marco} perdido")
        return
    socket_servidor.sendto(mensaje.encode(), (nombreServidor, puertoServidor))

def recibir_ack():
    while len(mensajes) > len(acknowledged):
        try:
            ack, _ = socket_servidor.recvfrom(2048)
            ack_num = int(ack.decode())
            print(f"Recibido ACK para marco {ack_num}")
            acknowledged.add(ack_num) # Marcamos el paquete como recibido
            temporizadores.pop(ack_num) # Eliminamos el temporizador del paquete recibido
        except socket.timeout:
            break
        except Exception as e:
            print(f"Error al recibir ACK: {e}")
            break

def cliente():
    secuencia_base = 0
    socket_servidor.settimeout(TIMEOUT)

    # Hilo para manejar los ACKs
    receptor_ack = threading.Thread(target=recibir_ack)
    receptor_ack.start()

    while secuencia_base < len(mensajes):
        time.sleep(1)
        print(f"Secuencia base: {secuencia_base}")
        print(f"Nro mensajes: {len(mensajes)} - Recibidos: {len(acknowledged)}")
        print(acknowledged)

        for numero_marco in range(secuencia_base, min(secuencia_base + TAMANO_VENTANA, len(mensajes))):
            if numero_marco not in acknowledged and numero_marco not in temporizadores.keys():
                # Condiciones que cumplen los paquetes que aun no se envian ni por 1era vez
                print(f"1era vez: {numero_marco}")
                enviar_marco(numero_marco)
                time.sleep(1)
            
            for numero_marco in temporizadores.keys():
                # Paquetes que ya se enviaron (tienen temporizador)
                if temporizador_vencido(numero_marco) and numero_marco not in acknowledged:
                    print(f"Marco {numero_marco} vencido")
                    enviar_marco(numero_marco)

        while secuencia_base in acknowledged:
            # Si se han recibido los ACK de paquetes en la secuencia base, se desplaza la ventana
            # hasta el primer paquete no ACK desde la base
            secuencia_base += 1
        print(acknowledged)

    socket_servidor.close()

if __name__ == "__main__":
    cliente()
