import socket
import json
import threading

HEADER_LENGTH = 10

HOST = (socket.gethostname(), 10000)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(HOST)
print('Connected to', HOST)

stop = False


def receive():
    while not stop:
        msg_header = client_socket.recv(HEADER_LENGTH)
        msg_length = int(msg_header.decode('UTF-8').strip())
        print(json.loads(client_socket.recv(msg_length).decode('UTF-8')))


def send():
    data = {"request_type": "registration",
            "name": "Alex",
            "password": "password"}

    msg = json.dumps(data).encode('UTF-8')
    header = f"{len(msg):<{HEADER_LENGTH}}".encode('UTF-8')

    client_socket.sendall(header + msg)

    ######

    data = {"request_type": "join_to_chat",
            "chat_name": "Chat2",
            "chat_password": "password"}
    msg = json.dumps(data).encode('UTF-8')
    header = f"{len(msg):<{HEADER_LENGTH}}".encode('UTF-8')

    client_socket.sendall(header + msg)

    ######

    data = {"request_type": "send_message",
            "chat_name": "Chat2",
            "message_text": "ffff"}

    msg = json.dumps(data).encode('UTF-8')
    header = f"{len(msg):<{HEADER_LENGTH}}".encode('UTF-8')

    client_socket.sendall(header + msg)


receive_thread = threading.Thread(target=receive)
receive_thread.start()

send()

input()

stop = True

client_socket.close()
