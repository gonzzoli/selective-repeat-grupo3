import socket
import threading
import time
import random
import hashlib

# Hace el selective repeat

host_receptor = 'localhost'
puerto_receptor = 12001

socket_emisor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
acknowledged = set()
temporizadores = {}

# Valores asignados en el __main__, estos son por defecto
mensajes = []
TAMANO_VENTANA = 4
TIMEOUT = 2
PROBABILIDAD_PERDIDA = 0.2
PROBABILIDAD_CORRUPCION = 0.2


def iniciar_temporizador(numero_trama):
    temporizadores[numero_trama] = time.time()

def temporizador_vencido(numero_trama):
    if numero_trama in temporizadores and time.time() - temporizadores[numero_trama] > TIMEOUT:
        return True
    return False

def simular_trama_perdida():
    aleatorio = random.random()
    if aleatorio > PROBABILIDAD_PERDIDA:
        return False
    return True

def simular_trama_corrupta():
    aleatorio = random.random()
    if aleatorio > PROBABILIDAD_CORRUPCION:
        return False
    return True

def enviar_trama(numero_trama):
    mensaje_con_secuencia = mensajes[numero_trama]
    # Generamos un hash como checksum, sobre el payload del mensaje, y solo tomamos 6 caracteres para no hacerla tan larga
    mensaje_con_checksum = f"{hashlib.md5(mensaje_con_secuencia.split(":")[1].encode()).hexdigest()[:6]}:{mensaje_con_secuencia}"
    # Solo se envian mensajes que no han sido enviados o cuyo temporizador venció, por eso los string posibles del print
    print(f"Enviando trama {"por primera vez " if numero_trama not in temporizadores else 'vencida '} {numero_trama}: {mensaje_con_checksum}")
    iniciar_temporizador(numero_trama)
    if simular_trama_perdida():
        print(f"Trama {numero_trama} perdida")
        return
    
    if simular_trama_corrupta():
        print(f"Trama {numero_trama} corrompida")
        # Si se corrompió, modificamos algo en el payload para simular ese error, y el checksum sera distinto en el receptor
        socket_emisor.sendto((f"{mensaje_con_checksum}" + "a").encode(), (host_receptor, puerto_receptor))
    else:
        socket_emisor.sendto(mensaje_con_checksum.encode(), (host_receptor, puerto_receptor))

def recibir_ack():
    while len(mensajes) > len(acknowledged):
        print("Esperando ACK")
        try:
            ack, _ = socket_emisor.recvfrom(2048)
            ack_num = int(ack.decode())
            print(f"Recibido ACK para trama {ack_num}")
            acknowledged.add(ack_num) # Marcamos el paquete como recibido
            temporizadores.pop(ack_num) # Eliminamos el temporizador del paquete recibido
        except socket.timeout:
            print("TIMEOUT")
        except Exception as e:
            print(f"Error al recibir ACK: {e}")

def emisor():
    secuencia_base = 0
    socket_emisor.settimeout(TIMEOUT)

    # Hilo para manejar los ACKs
    receptor_ack = threading.Thread(target=recibir_ack)
    receptor_ack.start()

    # Se ejecuta mientras queden tramas por enviar
    while secuencia_base < len(mensajes):
        print(f"Secuencia base: {secuencia_base}")
        print(f"Nro mensajes: {len(mensajes)} - Recibidos: {len(acknowledged)}")
        print(acknowledged)
        time.sleep(1)

        # Por cada trama dentro de la ventana actualmente analiza su estado y las envia o no dependiendo de ello
        for numero_trama in range(secuencia_base, min(secuencia_base + TAMANO_VENTANA, len(mensajes))):
            if numero_trama not in acknowledged and( numero_trama not in temporizadores.keys() or temporizador_vencido(numero_trama)):
                # Condiciones que generan un envío de la trama
                enviar_trama(numero_trama)
                time.sleep(1)

        while secuencia_base in acknowledged:
            # Si se han recibido los ACK de paquetes en la secuencia base, se desplaza la ventana
            # hasta el primer paquete no ACK desde la base
            secuencia_base += 1
            print(f"Secuencia base incrementada: {secuencia_base}")

    socket_emisor.close()

if __name__ == "__main__":
    cantidad_mensajes = int(input("Ingrese la cantidad de mensajes a enviar: "))
    PROBABILIDAD_PERDIDA = float(input("Ingrese la probabilidad de perdida de trama: "))
    PROBABILIDAD_CORRUPCION = float(input("Ingrese la probabilidad de corrupcion de trama: "))
    TIMEOUT = int(input("Ingrese el timeout de las tramas: "))
    TAMANO_VENTANA = int(input("Ingrese el tamaño de la ventana: "))

    for i in range(cantidad_mensajes):
        mensajes.append(f"{i}:mensaje {i}")
    print(f"Mensajes generados: {mensajes}")
    emisor()
