import socket
import json
import threading

HEADER_LENGTH = 10

HOST = (socket.gethostname(), 10000)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(HOST)
print('Connected to', HOST)

stop = True


def receive():
    while not stop:
        message = client_socket.recv(1024).decode('utf-8')
        print(message)


def send():
    data = {"request_type": "registration",
            "name": "Kirill",
            "password": "password"}

    msg = json.dumps(data).encode('UTF-8')
    header = f"{len(msg):<{HEADER_LENGTH}}".encode('UTF-8')

    client_socket.sendall(header + msg)

    ######

    data = {"request_type": "join_to_chat",
            "chat_name": "Chat1",
            "chat_password": "password"}

    msg = json.dumps(data).encode('UTF-8')
    header = f"{len(msg):<{HEADER_LENGTH}}".encode('UTF-8')

    client_socket.sendall(header + msg)


receive_thread = threading.Thread(target=receive)
receive_thread.start()

send()

input()

stop = False

client_socket.close()
