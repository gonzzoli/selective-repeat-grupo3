import socket
import hashlib

puerto_receptor = 12001
socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

socket_cliente.bind(("", puerto_receptor))

trama_esperada = 0
buffer = {}

def enviar_ack(numero_trama, direccion_servidor):
    print("ENVIANDO ACK", numero_trama)
    socket_cliente.sendto(f"{numero_trama}".encode(), direccion_servidor)

while True:
    print("~ESPERANDO ALGÚN MENSAJE...~")
    mensaje, direccion_servidor = socket_cliente.recvfrom(2048)
    print(f"RECIBIDO DESDE {direccion_servidor}")
    checksum, nro_trama_recibida, mensaje = mensaje.decode().split(":")
    nro_trama_recibida = int(nro_trama_recibida)

    print(f"Recibida trama {nro_trama_recibida}: {checksum}:{nro_trama_recibida}:{mensaje}")

    # Si el checksum no coincide, ignoramos la trama y esperamos la proxima
    if hashlib.md5(mensaje.encode()).hexdigest()[:6] != checksum:
        print("Checksum incorrecto")
        continue

    # Si es la trama que esperamos, la procesamos
    if nro_trama_recibida == trama_esperada:
        print(f"Procesando trama {nro_trama_recibida}")
        # Ya recibimos y enviamos ACK, pasamos a esperar el proximo.
        trama_esperada += 1

        # Revisar buffer por tramas fuera de orden
        while trama_esperada in buffer:
            print(f"Procesando trama en buffer {trama_esperada}: {buffer[trama_esperada]}")
            del buffer[trama_esperada]
            # Si los hay, significa que podemos avanzarlos sin esperar por otra respuesta
            trama_esperada += 1

    # Si es una trama fuera de orden, la guardamos en el buffer
    elif nro_trama_recibida > trama_esperada:
        print(f"Trama fuera de orden {nro_trama_recibida}, almacenada en buffer")
        buffer[nro_trama_recibida] = mensaje
    
    enviar_ack(nro_trama_recibida, direccion_servidor)
    print("~RECEPCIÓN FINALIZADA~")

