import json
import os


class FileService:
    def __init__(self, file_path, data_list, object_class):
        path = os.path.join(file_path)

        self.__file_path = file_path
        self.__data_list = data_list

        if not os.path.isfile(path):
            my_file = open(file_path, "w+")
            my_file.write("[]")
            my_file.close()
        else:
            with open(self.__file_path, "r") as file:
                json_array = json.load(file)
                for json_object in json_array:
                    self.__data_list.append(object_class.from_json_object(json_object))

                print(self.__data_list)

    def save_data(self):
        with open(self.__file_path, "r+") as file:
            json_array = []
            for el in self.__data_list:
                json_array.append(el.to_json_object())
            print(json_array)
            json.dump(json_array, file)
