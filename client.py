import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import socket
import json
from lib_for_messanger import *
import threading

chats = {}

current_chat = None


def receive_answers(sock):
    while True:
        try:
            answer = receive_msg(sock)
            if not answer:
                print('Соединение с сервером разорвано.')
                break
            elif answer["request_type"] == "registration":
                if answer["answer"] == "success":
                    messagebox.showinfo("Регистрация", "Регистрация успешна!")
                    show_main_page()
                elif answer["answer"] == "user_exist":
                    messagebox.showinfo("Регистрация", "Пользователь уже существует")
                else:
                    messagebox.showerror("Ошибка", "!!!!!!!")
            elif answer["request_type"] == "entrance":
                if answer["answer"] == "success":
                    print(type(answer["user"]))
                    user = User.from_json_object(answer["user"])

                    chats_info = answer["chats_info"]

                    for chat_name, _messages in chats_info.items():
                        messages_text = []
                        for _message in _messages:
                            message_object = Message.from_json_object(_message)
                            if message_object.get_sender_name() == user.get_name():
                                messages_text.append("You: " + message_object.get_message_text())
                            else:
                                messages_text.append(message_object.get_sender_name() + ": "
                                                     + message_object.get_message_text())
                        chats[chat_name] = messages_text
                        chat_listbox.insert(tk.END, chat_name)

                    show_main_page()
                elif answer["answer"] == "wrong_password":
                    messagebox.showinfo("Вход", "Неправильный пароль")
                elif answer["answer"] == "user_does_not_exist":
                    messagebox.showinfo("Вход", "Пользователя не существует")
                else:
                    messagebox.showerror("Ошибка", "!!!!!!!")
            elif answer["request_type"] == "send_message":
                chats[answer["chat_name"]].append(answer["message"]["sender_name"] + ": "
                                                  + answer["message"]["message_text"])
                if current_chat == answer["chat_name"]:
                    listbox.delete(0, tk.END)
                    for message_text in chats[current_chat]:
                        listbox.insert(tk.END, message_text)

                    listbox.see(tk.END)  # Прокрутка списка в самый низ
            elif answer["request_type"] == "create_new_chat":
                if answer["answer"] == "success":
                    messagebox.showinfo("Создание новго чата", "Новый чат создан!")
                    chats[answer["chat_name"]] = []
                    update_chat_listbox()
                    show_main_page()
                elif answer["answer"] == "chat_exist":
                    messagebox.showinfo("Создание новго чата", "Чат с таким именем уже существует")
                else:
                    messagebox.showerror("Ошибка", "!!!!!!!")
            elif answer["request_type"] == "join_to_chat":
                if answer["answer"] == "success":
                    chat_messages_text = []
                    for message_json_object in answer["messages"]:
                        message_object = Message.from_json_object(message_json_object)
                        chat_messages_text.append(message_object.get_sender_name() + ": "
                                                  + message_object.get_message_text())

                    chats[answer["chat_name"]] = chat_messages_text
                    update_chat_listbox()
                    show_main_page()
                elif answer["answer"] == "user_in_chat":
                    messagebox.showinfo("Вход в чат", "Пользователь уже в чате")
                elif answer["answer"] == "wrong_password":
                    messagebox.showinfo("Вход в чат", "Неправлильный пароль")
                elif answer["answer"] == "chat_does_not_exist":
                    messagebox.showinfo("Вход в чат", "Чата не существует")
                else:
                    messagebox.showerror("Ошибка", "!!!!!!!")
        except ConnectionResetError:
            print('Соединение с сервером разорвано.')
            break


def send_msg(client, json_object):
    msg = json.dumps(json_object).encode('UTF-8')
    header = f"{len(msg):<{HEADER_LENGTH}}".encode('UTF-8')
    client.sendall(header + msg)


def receive_msg(client):
    msg_header = client.recv(HEADER_LENGTH)
    if msg_header.decode('UTF-8') == "":
        return None
    msg_length = int(msg_header.decode('UTF-8').strip())
    return json.loads(client.recv(msg_length).decode('UTF-8'))


def login():
    username = login_entry_username.get()
    password = login_entry_password.get()

    # Проверка успешного входа

    registration_request = {"request_type": "entrance",
                            "name": username,
                            "password": password}
    send_msg(client_socket, registration_request)


def register():
    username = register_entry_username.get()
    password = register_entry_password.get()
    confirm_password = register_entry_confirm_password.get()

    # Проверка соответствия паролей
    if password == confirm_password:
        registration_request = {"request_type": "registration",
                                "name": username,
                                "password": password}
        send_msg(client_socket, registration_request)
        # answer = receive_msg(client_socket)
    else:
        messagebox.showerror("Ошибка", "Пароли не совпадают.")


def join_to_chat():
    chat_name = login_entry_chat_name.get()
    chat_password = login_entry_chat_password.get()

    join_to_chat_request = {"request_type": "join_to_chat",
                            "chat_name": chat_name,
                            "chat_password": chat_password}

    send_msg(client_socket, join_to_chat_request)

def create_new_chat():
    chat_name = register_entry_chat_name.get()
    chat_password = register_entry_chat_password.get()
    confirm_chat_password = register_entry_confirm_chat_password.get()

    if chat_password == confirm_chat_password:
        create_new_chat_request = {"request_type": "create_new_chat",
                                   "chat_name": chat_name,
                                   "chat_password": chat_password}
        send_msg(client_socket, create_new_chat_request)
    else:
        messagebox.showerror("Ошибка", "Пароли не совпадают.")


def send_message():
    message_text = entry.get()
    if message_text:
        chats[current_chat].append("You: " + message_text)
        listbox.insert(tk.END, "You:" + message_text)
        entry.delete(0, tk.END)

        request = {"request_type": "send_message",
                   "chat_name": current_chat,
                   "message_text": message_text}

        send_msg(client_socket, request)
        listbox.see(tk.END)  # Прокрутка списка в самый низ


def change_chat(event):
    global current_chat
    selected_indices = chat_listbox.curselection()
    if selected_indices:
        selected_index = selected_indices[0]
        selected_chat = chat_listbox.get(selected_index)
        current_chat = selected_chat
        listbox.delete(0, tk.END)
        for message_text in chats[current_chat]:
            listbox.insert(tk.END, message_text)

        listbox.see(tk.END)  # Прокрутка списка в самый низ

        chat_frame.pack(fill=tk.BOTH, expand=True)

        # Подсветка выбранного чата
        for i in range(chat_listbox.size()):
            if chat_listbox.get(i) == current_chat:
                chat_listbox.itemconfig(i, background="#D3D3D3")
            else:
                chat_listbox.itemconfig(i, background="white")


def update_chat_listbox():
    chat_listbox.delete(0, tk.END)
    for chat_name in chats:
        chat_listbox.insert(tk.END, chat_name)


def show_login_page():
    main_frame.pack_forget()
    register_frame.pack_forget()
    create_new_chat_frame.pack_forget()
    join_to_chat_frame.pack_forget()

    login_frame.pack()


def show_register_page():
    main_frame.pack_forget()
    login_frame.pack_forget()
    create_new_chat_frame.pack_forget()
    join_to_chat_frame.pack_forget()

    register_frame.pack()


def show_main_page():
    login_frame.pack_forget()
    register_frame.pack_forget()
    create_new_chat_frame.pack_forget()
    join_to_chat_frame.pack_forget()

    main_frame.pack()


def show_create_new_chat_page():
    login_frame.pack_forget()
    register_frame.pack_forget()
    main_frame.pack_forget()
    join_to_chat_frame.pack_forget()

    create_new_chat_frame.pack()


def show_join_to_chat_page():
    login_frame.pack_forget()
    register_frame.pack_forget()
    create_new_chat_frame.pack_forget()
    main_frame.pack_forget()

    join_to_chat_frame.pack()


HEADER_LENGTH = 10

HOST = (socket.gethostname(), 10000)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(HOST)
print('Connected to', HOST)

root = tk.Tk()
root.title("Mecceнджер")

# Создание фреймов
login_frame = tk.Frame(root)
register_frame = tk.Frame(root)

create_new_chat_frame = tk.Frame(root)
join_to_chat_frame = tk.Frame(root)

main_frame = tk.Frame(root)

# Фрейм входа
label_username = ttk.Label(login_frame, text="Имя пользователя:")
label_username.pack()
login_entry_username = ttk.Entry(login_frame)
login_entry_username.pack()

label_password = ttk.Label(login_frame, text="Пароль:")
label_password.pack()
login_entry_password = ttk.Entry(login_frame, show="•")
login_entry_password.pack()

button_login = ttk.Button(login_frame, text="Войти", command=login)
button_login.pack()

button_show_register = ttk.Button(login_frame, text="Зарегистрироваться", command=show_register_page)
button_show_register.pack()

# Фрейм регистрации
label_username = ttk.Label(register_frame, text="Имя пользователя:")
label_username.pack()
register_entry_username = ttk.Entry(register_frame)
register_entry_username.pack()

label_password = ttk.Label(register_frame, text="Пароль:")
label_password.pack()
register_entry_password = ttk.Entry(register_frame, show="•")
register_entry_password.pack()

label_confirm_password = ttk.Label(register_frame, text="Подтвердите пароль:")
label_confirm_password.pack()
register_entry_confirm_password = ttk.Entry(register_frame, show="•")
register_entry_confirm_password.pack()

button_register = ttk.Button(register_frame, text="Зарегистрироваться", command=register)
button_register.pack()

button_show_login = ttk.Button(register_frame, text="Войти", command=show_login_page)
button_show_login.pack()

# Создание фрейма для выбора чатов (слева)
chat_panel = tk.Frame(main_frame, width=200, bg="#E6E6FA")
chat_panel.pack(side=tk.LEFT, fill=tk.Y)

chat_listbox = tk.Listbox(chat_panel, height=20, width=20, bg="#E6E6FA", font=("Arial", 12))
update_chat_listbox()
chat_listbox.pack(side=tk.LEFT, padx=10, pady=10)

chat_listbox.bind("<<ListboxSelect>>", change_chat)  # Связывание функции change_chat с событием выбора элемента списка

button1 = ttk.Button(chat_panel, text="Создать новый чат", command=show_create_new_chat_page)
button1.pack()

button2 = ttk.Button(chat_panel, text="Войти в чат", command=show_join_to_chat_page)
button2.pack()

# Создание фрейма для отображения чата (справа)
chat_frame = tk.Frame(main_frame)
# chat_frame.pack(fill=tk.BOTH, expand=True)

# Создание списка сообщений
listbox = tk.Listbox(chat_frame, height=15, width=50)
listbox.pack(padx=10, pady=10, expand=True)

# Создание поля ввода текста
entry = tk.Entry(chat_frame, width=50)
entry.pack(padx=10, pady=10, expand=True)

# Создание кнопки отправки сообщения
send_button = tk.Button(chat_frame, text="Отправить", command=send_message)
send_button.pack(padx=10, pady=10)

# Фрейм входа в чат
label_chat_name = ttk.Label(join_to_chat_frame, text="Имя чата:")
label_chat_name.pack()
login_entry_chat_name = ttk.Entry(join_to_chat_frame)
login_entry_chat_name.pack()

label_chat_password = ttk.Label(join_to_chat_frame, text="Пароль:")
label_chat_password.pack()
login_entry_chat_password = ttk.Entry(join_to_chat_frame, show="•")
login_entry_chat_password.pack()

button_join_to_chat = ttk.Button(join_to_chat_frame, text="Войти в чат", command=join_to_chat)
button_join_to_chat.pack()

button_show_create_new_chat = ttk.Button(join_to_chat_frame, text="Создать новый чат",
                                         command=show_create_new_chat_page)
button_show_create_new_chat.pack()

button_back_to_main_frame1 = ttk.Button(join_to_chat_frame, text="Назад", command=show_main_page)
button_back_to_main_frame1.pack()

# Фрейм создания нового чата
label_chat_name = ttk.Label(create_new_chat_frame, text="Имя чата:")
label_chat_name.pack()
register_entry_chat_name = ttk.Entry(create_new_chat_frame)
register_entry_chat_name.pack()

label_chat_password = ttk.Label(create_new_chat_frame, text="Пароль:")
label_chat_password.pack()
register_entry_chat_password = ttk.Entry(create_new_chat_frame, show="•")
register_entry_chat_password.pack()

label_confirm_chat_password = ttk.Label(create_new_chat_frame, text="Подтвердите пароль:")
label_confirm_chat_password.pack()
register_entry_confirm_chat_password = ttk.Entry(create_new_chat_frame, show="•")
register_entry_confirm_chat_password.pack()

button_create_new_chat = ttk.Button(create_new_chat_frame, text="Создать новый чат", command=create_new_chat)
button_create_new_chat.pack()

button_show_join_to_chat = ttk.Button(create_new_chat_frame, text="Войти в чат", command=show_join_to_chat_page)
button_show_join_to_chat.pack()

button_back_to_main_frame2 = ttk.Button(create_new_chat_frame, text="Назад", command=show_main_page)
button_back_to_main_frame2.pack()

# Показать страницу входа при запуске
show_login_page()

receive_thread = threading.Thread(target=receive_answers, args=(client_socket,))
receive_thread.start()

root.mainloop()

client_socket.close()