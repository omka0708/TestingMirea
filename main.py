import csv
import random
from datetime import datetime
from threading import Timer

import requests
from vk_api import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.utils import get_random_id

vk_session = vk_api.VkApi(token="13c403991e7cf080abc0a32a6450e4552feb9457bb646c174eda48342bddb1adb486ae4a78fa465a48c33")
longpoll = VkBotLongPoll(vk_session, '197126596')
vk = vk_session.get_api()
category = ["id", "firstname", "lastname", "regisration data", "nickname", "section"]  # для работы с DictWriter
users = {}  # словарь с ключами - id пользователя, со значениями объектов User, поля которого выгружаются из users.csv

tracks = {'lil krystalll - cardib': 'melodies/cardib.mp3',
          'ЛСП - Цветная бумага': 'melodies/cvetnayabumaga.mp3',
          'PLOHOYPAREN - Фак фейк скам': 'melodies/fuckfakescam.mp3',
          'White Punk - Крестный': 'melodies/krestniy.mp3',
          'Boulevard Depo, JEEMBO - Металлолом': 'melodies/metallolom.mp3',
          'PHARAOH - На луне': 'melodies/nalune.mp3',
          'OG Buda - Печеньки': 'melodies/pechenki.mp3',
          'PHARAOH, Big Baby Tape - Шипучка': 'melodies/shipuchka.mp3',
          'Платина - Случайна': 'melodies/sluchayna.mp3',
          'Джизус - ТЫ СТАЛА ПРОСТО СУПЕР': 'melodies/tystalaprostosuper.mp3'}


class User:
    """
    User class.
    Stores the identifier, first name, last name, date of registration in the bot,
    nickname and section parameter (possibly, it will be changed in the future),
    nickname setter and user information getter
    """
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


def register(_users):
    """
    Registration method.
    Registers the user in the users.csv file if he is not registered.
    """
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


def download_users_from_file():
    """
    A method for unloading user data from a file.
    Unloads user data from users.csv as objects of the User class
    """
    with open("users.csv", "r", encoding='utf8') as file:
        for row in file:
            _id, _firstname, _lastname, _registration_data, _nickname, _section = row.strip().split(",")
            if _id != 'id':
                print(_id)
                users[_id] = User(_id, _firstname, _lastname, _registration_data, _nickname, _section)
                print(users[_id])
        print("Все зарегистрированные пользователи загружены!")


def upload_user_to_file():
    """
    Method of loading user data file (update users.csv).
    Writes the current changes to the users.csv file.
    """
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
    """
    Method for sending messages.
    Accepts an event, message and attachment (optional) as input.
    Sends a message.
    """
    vk.messages.send(
        key='abe17c7a950a294d1298e7703846b9220a139e37',
        server='https://lp.vk.com/wh197126596',
        ts='3164',
        random_id=get_random_id(),
        chat_id=event.chat_id,
        message=message,
        attachment=attachment
    )


def change_nickname(event, message):
    """
    Nickname change method.
    Accepts an event and a message as input,
    changes the user's nickname.
    """
    if len(message[8:].lower()) > 20:
        send_message(event, "Слишком длинный ник, допустимая длина - 20 символов")
    else:
        print(f"Пользователь {users[str(event.obj.from_id)].nickname} (id {str(event.obj.from_id)}) сменил "
              f"ник на {message[8:]}")
        users[str(event.obj.from_id)].set_nickname(message[8:])
        send_message(event, f"Вы сменили ник на \"{message[8:]}\"!")


def guess_the_melody(event):
    """
    Method of guessing melodies.
    Receives an event as input,
    uploads a random melody to the VK server,
    returns the name of this melody.
    """
    random_track_name = random.choice(list(tracks.keys()))
    a = vk.docs.getMessagesUploadServer(
        type="audio_message",
        peer_id=2000000000 + event.chat_id
    )
    b = requests.post(a['upload_url'], files={'file': open(tracks[random_track_name], 'rb')}).json()
    c = vk.docs.save(
        file=b["file"]
    )
    d = 'doc{}_{}'.format(c['audio_message']['owner_id'], c['audio_message']['id'])
    send_message(event, 'Угадай мелодию (только название) за 15 секунд:', d)
    return random_track_name


def main():
    """
    The main method.
    Reading events in the chat, calls to the registration methods, download, upload, etc.
    """
    download_users_from_file()
    gameMELODY = False
    track_name = ''
    t = Timer(0.0, lambda x: None)
    for event in longpoll.listen():
        if event.from_chat:
            user_dict = {"id": event.obj.from_id, "firstname": vk.users.get(user_id=event.obj.from_id)[0]['first_name'],
                         "lastname": vk.users.get(user_id=event.obj.from_id)[0]['last_name']}
            register(user_dict)
            message = str(event.obj.text)
            user_id = str(event.obj.from_id)
            if message.lower() == 'кто я':
                print(f"Пользователь {users[user_id].nickname} узнаёт свои данные")
                send_message(event, users[user_id].get_stats())
            if message[:8].lower() == 'никнейм ':
                change_nickname(event, message)

            if (
                    message.lower() == 'угадай мелодию' or message.lower() == 'угадать мелодию' or message.lower() == 'угадай трек' or message.lower() == 'угадать трек') and not gameMELODY:
                print(f'Пользователь {users[user_id].nickname} угадывает мелодию')
                gameMELODY = True
                track_name = guess_the_melody(event)

                def end_melody():
                    send_message(event, f'Время вышло! Название трека: {track_name}')
                    nonlocal gameMELODY
                    gameMELODY = False

                t = Timer(15.0, end_melody)
                t.start()
            if gameMELODY and message.lower() == track_name.split('-')[1].strip().lower():
                t.cancel()
                send_message(event, f'[id{user_id}|{users[user_id].nickname}] ответил верно!'
                                    f'\nНазвание трека: {track_name}')
                gameMELODY = False

            upload_user_to_file()


if __name__ == '__main__':
    main()
