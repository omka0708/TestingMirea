import csv
from datetime import datetime

from vk_api import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.utils import get_random_id

vk_session = vk_api.VkApi(token="13c403991e7cf080abc0a32a6450e4552feb9457bb646c174eda48342bddb1adb486ae4a78fa465a48c33")
longpoll = VkBotLongPoll(vk_session, '197126596')
vk = vk_session.get_api()
category = ["id", "firstname", "lastname", "regisration data", "nickname", "section"]  # для работы с DictWriter
users = {}  # словарь с ключами - id пользователя, со значениями объектов User, поля которого выгружаются из users.csv


class User:
    def __init__(self, id_, firstname_, lastname_, registration_data_, nickname_, section_):
        self.id = id_
        self.firstname = firstname_
        self.lastname = lastname_
        self.registration_data = registration_data_
        self.nickname = nickname_
        self.section = section_

    def set_nickname(self, nickname_):
        self.nickname = nickname_

    def get_stats(self):
        return f"Имя: {self.firstname}\n" \
               f"Фамилия: {self.lastname}\n" \
               f"Ник: {self.nickname}\n" \
               f"Дата регистрации: {self.registration_data}"


def register(_users):  # регистрация пользователя (если он не зарегистрирован)
    with open("users.csv", "a", encoding='utf8') as w_file:
        writer = csv.DictWriter(w_file, lineterminator="\r", fieldnames=category)
        is_registered = False
        with open("users.csv", "r", encoding='utf8') as r_file:
            for r_row in r_file:
                if str(r_row.strip().split(",")[0]) == str(_users["id"]):
                    is_registered = True
                    break
        if not is_registered:
            _users["regisration data"] = str(datetime.now()).replace('-', '.')[:-7]
            _users["nickname"] = _users["firstname"] + ' ' + _users["lastname"]
            _users["section"] = "none"
            users[str(_users["id"])] = User(str(_users["id"]),
                                            _users["firstname"],
                                            _users["lastname"],
                                            _users["regisration data"],
                                            _users["nickname"],
                                            _users["section"])
            writer.writerow(_users)


def download_users_from_file():  # выгрузка данных о пользователе из users.csv в виде объектов класса User
    with open("users.csv", "r", encoding='utf8') as file:
        for row in file:
            _id, _firstname, _lastname, _registration_data, _nickname, _section = row.strip().split(",")
            if _id != 'id':
                print(_id)
                users[_id] = User(_id, _firstname, _lastname, _registration_data, _nickname, _section)
                print(users[_id])
        print("Все зарегистрированные пользователи загружены!")


def upload_user_to_file():  # загрузка данных о пользователе в файл (обновление users.csv)
    with open("users.csv", "w", encoding='utf8') as file:
        writer = csv.DictWriter(file, lineterminator="\r", fieldnames=category)
        for value in users.values():
            writer.writerow({"id": value.id,
                             "firstname": value.firstname,
                             "lastname": value.lastname,
                             "regisration data": value.registration_data,
                             "nickname": value.nickname,
                             "section": value.section})


def send_message(event, message, attachment=None):
    vk.messages.send(
        key='abe17c7a950a294d1298e7703846b9220a139e37',
        server='https://lp.vk.com/wh197126596',
        ts='3164',
        random_id=get_random_id(),
        chat_id=event.chat_id,
        message=message,
        attachment=attachment
    )


def main():
    download_users_from_file()
    for event in longpoll.listen():
        if event.from_chat:
            user_dict = {"id": event.obj.from_id, "firstname": vk.users.get(user_id=event.obj.from_id)[0]['first_name'],
                         "lastname": vk.users.get(user_id=event.obj.from_id)[0]['last_name']}
            register(user_dict)
            message = str(event.obj.text)
            user_id = str(event.obj.from_id)

            print(f'{user_id}: {message}')
            upload_user_to_file()


if __name__ == '__main__':
    main()
