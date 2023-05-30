from datetime import datetime


class Message:
    def __init__(self, sender_name, message_text):
        self.__sender_name = sender_name
        self.__send_date = datetime.now()
        self.__message_text = message_text

    def get_sender_name(self):
        return self.__sender_name

    def get_send_date(self):
        return self.__send_date

    def get_message_text(self):
        return self.__message_text

    def to_json_object(self):
        return {"sender_name": self.__sender_name,
                "send_date": self.__send_date,
                "message_text": self.__message_text}

    @staticmethod
    def from_json_object(json_object):
        message = Message("", "")
        message.__sender_name = json_object["sender_name"]
        message.__send_date = json_object["send_date"]
        message.__message_text = json_object["message_text"]

        return message
