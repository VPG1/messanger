class User:
    def __init__(self, name, password):
        self.__name = name
        self.__password = password
        self.__chats = []

    def set_name(self, name):
        self.__name = name

    def get_name(self):
        return self.__name

    def get_password(self):
        return self.__password

    def join_to_chat(self, chat_name):
        self.__chats.append(chat_name)

    def to_json_object(self):
        return {"name": self.__name,
                "password": self.__password,
                "chats": self.__chats}

    @staticmethod
    def from_json_object(json_object):
        user = User("", "")
        user.__name = json_object["name"]
        user.__password = json_object["password"]
        user.__chatsId = json_object["chats"]

        return user
