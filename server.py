import socket
import select
import json

from lib_for_messanger import *

HEADER_LENGTH = 10
HOST = (socket.gethostname(), 10000)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind(HOST)
server.listen()
print("Listening")

socket_list = [server]
processed_client_list = {}

users_list = []
users_file_path = "users.json"
users_file_service = FileService(users_file_path, users_list, user.User)

chats_list = []
chats_file_path = "chats.json"
chats_file_service = FileService(chats_file_path, chats_list, chat.Chat)

messages_list = []
messages_file_path = "message.json"
messages_file_service = FileService(messages_file_path, messages_list, message.Message)


def receive_msg(client):
    msg_header = client.recv(HEADER_LENGTH)
    if msg_header.decode('UTF-8') == "":
        return None
    msg_length = int(msg_header.decode('UTF-8').strip())
    return json.loads(client.recv(msg_length).decode('UTF-8'))


def send_msg(client, json_object):
    print("message send: ", json_object)
    msg = json.dumps(json_object).encode('UTF-8')
    header = f"{len(msg):<{HEADER_LENGTH}}".encode('UTF-8')
    client.sendall(header + msg)


def find_user_by_name(user_name):
    for _user in users_list:
        if _user.get_name() == user_name:
            return _user

    return None


def find_chat_by_name(chat_name):
    for _chat in chats_list:
        if _chat.get_chat_name() == chat_name:
            return _chat

    return None


def handle_new_client(server_socket):
    client_socket, client_address = server_socket.accept()
    print("Connected -", client_address)

    socket_list.append(client_socket)


def process_new_client(new_client_socket):
    request_data = receive_msg(new_client_socket)

    if request_data is None:
        socket_list.remove(new_client_socket)
        new_client_socket.close()
        print("client disconnect")
        return

    if request_data["request_type"] == "registration":
        # new_user = users_file_service.find_element_in_file_by_name(request_data["name"])
        new_user = find_user_by_name(request_data["name"])

        if new_user is None:
            new_user = user.User(request_data["name"], request_data["password"])
            # users_file_service.add_new_element(new_user)
            users_list.append(new_user)

            users_file_service.save_data()

            processed_client_list[new_client_socket] = new_user

            answer = {"request_type": request_data["request_type"],
                      "answer": "success"}
            send_msg(new_client_socket, answer)

            print("new user in system")
            print("new user online")
        else:
            answer = {"request_type": request_data["request_type"],
                      "answer": "success"}
            send_msg(new_client_socket, answer)

            print("user already exist")
    elif request_data["request_type"] == "entrance":
        new_user = find_user_by_name(request_data["name"])
        # new_user = users_file_service.find_element_in_file_by_name(request_data["name"])

        if new_user is not None:
            if request_data["password"] == new_user.get_password():
                processed_client_list[new_client_socket] = new_user

                answer = {"request_type": request_data["request_type"],
                          "answer": "success",
                          "user": new_user.to_json_object()}

                send_msg(new_client_socket, answer)

                users_file_service.save_data()

                print("user online")
            else:
                answer = {"request_type": request_data["request_type"],
                          "answer": "wrong_password"}
                send_msg(new_client_socket, answer)

                print("wrong password")
        else:
            answer = {"request_type": request_data["request_type"],
                      "answer": "user_does_not_exist"}
            send_msg(new_client_socket, answer)

            print("no such user exists")

    else:
        print("invalid request type")


def process_request_from_client(client_socket):
    request_data = receive_msg(client_socket)

    if request_data is None:
        del processed_client_list[client_socket]
        socket_list.remove(client_socket)
        client_socket.close()
        print("client disconnect")
        return

    if request_data["request_type"] == "create_new_chat":
        new_chat = find_chat_by_name(request_data["chat_name"])
        # new_chat = chats_file_service.find_element_in_file_by_name(request_data["name"])

        if new_chat is None:
            new_chat = chat.Chat(request_data["chat_name"], request_data["chat_password"],
                                 processed_client_list[client_socket].get_name())

            chats_list.append(new_chat)
            processed_client_list[client_socket].join_to_chat(new_chat.get_chat_name())

            users_file_service.save_data()
            chats_file_service.save_data()

            # chats_file_service.add_new_element(new_chat)

            print("chat created")
        else:
            print("chat with the same name already exists")
    elif request_data["request_type"] == "join_to_chat":
        chat_object = find_chat_by_name(request_data["chat_name"])
        # chat_object = chats_file_service.find_element_in_file_by_name((request_data["name"]))

        if chat_object is not None:
            if request_data["chat_password"] == chat_object.get_chat_password():
                print(processed_client_list[client_socket].get_name())
                if processed_client_list[client_socket].get_name() not in chat_object.get_members():
                    chat_object.add_new_member(processed_client_list[client_socket].get_name())
                    processed_client_list[client_socket].join_to_chat(chat_object.get_chat_name())

                    users_file_service.save_data()
                    chats_file_service.save_data()

                    print("user joined to chat")
                else:
                    print("user is already in the chat")
            else:
                print("wrong password")
        else:
            print("chat doesn't exist")
    elif request_data["request_type"] == "send_message":
        chat_object = find_chat_by_name(request_data["chat_name"])

        if chat_object is not None:
            user_object = processed_client_list[client_socket]

            if user_object.get_name() in chat_object.get_members():
                new_message = message.Message(user_object.get_name(), request_data["message_text"])

                messages_list.append(new_message)
                chat_object.add_new_message_id(len(messages_list) - 1)

                chats_file_service.save_data()
                messages_file_service.save_data()

                for receiver_socket, user_object in processed_client_list.items():
                    if user_object.get_name() in chat_object.get_members() and client_socket != receiver_socket:
                        send_msg(receiver_socket, new_message.to_json_object())
            else:
                print("user not in chat")
        else:
            print("chat doesn't exist")
    else:
        print("invalid request type")


while True:
    rs, _, _ = select.select(socket_list, [], socket_list)
    for socket in rs:
        if socket == server:
            handle_new_client(socket)
        else:
            if socket not in processed_client_list.keys():
                print("process new client")
                process_new_client(socket)
            else:
                print("process request from client")
                process_request_from_client(socket)
