import socket
import threading
import serial
from collections import deque

arduino = serial.Serial('COM6', 9600)  
HOST = '192.168.68.228'
PORT = 65432
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print(f"Servidor escuchando en {HOST}:{PORT}")

def handle_client_connection(client_socket):
    print(f"Conexión establecida con {client_socket.getpeername()}")

    buffer_size = 10
    humidity_values = deque([0] * buffer_size, maxlen=buffer_size)

    while True:
        try:
            data = arduino.readline().decode().strip()
            try:
                humidity = int(data.split(':')[1])
                humidity_values.append(humidity)
                client_socket.sendall(f"{humidity}\n".encode())

                if humidity < 600:
                    response = client_socket.recv(1024).decode().strip()
                    if response == 'A':
                        arduino.write(b'A')
                    elif response == 'D':
                        arduino.write(b'D')
            except (IndexError, ValueError):
                pass
        except serial.SerialException:
            print("Error en la conexión serial con Arduino")
            break

    client_socket.close()

while True:
    client_socket, addr = server.accept()
    client_handler = threading.Thread(target=handle_client_connection, args=(client_socket,))
    client_handler.start()
