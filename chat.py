class Chat:
    seed = 0

    def __init__(self, chat_name: str, chat_password: str, chat_admin_name: str):
        self.__chat_name = chat_name
        self.__chat_admin_name = chat_admin_name
        self.__chat_password = chat_password
        self.__members = [chat_admin_name]
        self.__messages_id = []

    def get_chat_name(self):
        return self.__chat_name

    def get_chat_password(self):
        return self.__chat_password

    def add_new_member(self, member_name):
        self.__members.append(member_name)

    def get_members(self):
        return self.__members

    def add_new_message_id(self, message_id):
        self.__messages_id.append(message_id)

    def to_json_object(self):
        return {"chat_name": self.__chat_name,
                "chat_admin_name": self.__chat_admin_name,
                "chat_password": self.__chat_password,
                "members": self.__members,
                "messages_id": self.__messages_id}

    @staticmethod
    def from_json_object(json_object):
        chat = Chat("", "", "")

        chat.__chat_name = json_object["chat_name"]
        chat.__chat_admin_name = json_object["chat_admin_name"]
        chat.__chat_password = json_object["chat_password"]
        chat.__members = json_object["chat_admin_name"]
        chat.__messages_id = json_object["message_id"]

        return chat
