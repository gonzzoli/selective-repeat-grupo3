import socket

puerto_cliente = 12000
socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

socket_cliente.bind(("", puerto_cliente))

marco_esperado = 0
buffer = {}

def enviar_ack(numero_marco, direccion_servidor):
    print("ENVIANDO ACK", numero_marco)
    socket_cliente.sendto(f"{numero_marco}".encode(), direccion_servidor)

while True:
    mensaje, direccion_servidor = socket_cliente.recvfrom(2048)
    nro_marco_recibido, mensaje = mensaje.decode().split(":")
    nro_marco_recibido = int(nro_marco_recibido)

    print(f"Recibido marco {nro_marco_recibido}: {mensaje}")

    # Si es el marco que esperamos, lo procesamos
    if nro_marco_recibido == marco_esperado:
        print(f"Procesando marco {nro_marco_recibido}")
        # Ya recibimos y enviamos ACK, pasamos a esperar el proximo.
        marco_esperado += 1

        # Revisar buffer por marcos fuera de orden
        while marco_esperado in buffer:
            print(f"Procesando marco en buffer {marco_esperado}: {buffer[marco_esperado]}")
            del buffer[marco_esperado]
            # Si los hay, significa que podemos avanzarlos sin esperar por otra respuesta
            marco_esperado += 1

    # Si es un marco fuera de orden, lo guardamos en el buffer
    elif nro_marco_recibido > marco_esperado:
        print(f"Marco fuera de orden {nro_marco_recibido}, almacenado en buffer")
        buffer[nro_marco_recibido] = mensaje
    
    enviar_ack(nro_marco_recibido, direccion_servidor)

