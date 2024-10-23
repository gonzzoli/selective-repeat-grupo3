import socket

puertoServidor = 12000
socketServidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

socketServidor.bind(("", puertoServidor))

expected_frame = 0
received_buffer = {}

while True:
    mensaje, direccionCliente = socketServidor.recvfrom(2048)
    frame_num, data = mensaje.decode().split(":")
    frame_num = int(frame_num)

    print(f"Recibido marco {frame_num}: {data}")

    # Si es el marco que esperamos, lo procesamos
    if frame_num == expected_frame:
        print(f"Procesando marco {frame_num}")
        expected_frame += 1

        # Revisar buffer por marcos fuera de orden
        while expected_frame in received_buffer:
            print(f"Procesando marco en buffer {expected_frame}: {received_buffer[expected_frame]}")
            del received_buffer[expected_frame]
            expected_frame += 1

    # Si es un marco fuera de orden, lo guardamos en el buffer
    elif frame_num > expected_frame:
        print(f"Marco fuera de orden {frame_num}, almacenado en buffer")
        received_buffer[frame_num] = data

    # Enviar ACK para el marco actual
    print("ENVIANDO ACK", expected_frame)
    socketServidor.sendto(f"{expected_frame}".encode(), direccionCliente)

