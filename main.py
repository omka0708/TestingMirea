import csv
import os
import re
import random
from threading import Timer

from vk_api import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
from datetime import datetime
import requests
from vk_api.utils import get_random_id
from gtts import gTTS

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


def weather(city):
    """c0c4a4b4047b97ebc5948ac9c48c0559"""
    app_id = "8a2e9f9bcd7dd4d44acc6320ae687a76"
    country_code = "ru"
    res = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?q={city},{0},{country_code}&appid={app_id}&units"
        f"=metric&lang=ru")
    data = res.json()
    smiles = {'01': '☀', '02': '⛅', '03': '☁', '04': '☁', '09': '🌧', '10': '🌦', '11': '🌩', '13': '❄', '50': '🌫'}
    if data['cod'] == 200:
        smile_code = data['weather'][0]['icon'][:2]
        description = data['weather'][0]['description']
        temp = round(data['main']['temp'])
        return city.capitalize() + ' ' + smiles[smile_code] + '\n' + str(temp) + '°C, ' + description
    else:
        return 'Город не найден'


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


def voice_acting(event, message):
    text = message[7:]
    try:
        if len(text) > 100:
            send_message(event, "Слишком большой текст, допустимая длина - 100 символов")
        else:
            language = "ru"
            speech = gTTS(text=text, lang=language, slow=False)
            speech.save("text.mp3")
            a = vk.docs.getMessagesUploadServer(
                type="audio_message",
                peer_id=2000000000 + event.chat_id
            )
            b = requests.post(a['upload_url'], files={'file': open("text.mp3", 'rb')}).json()
            c = vk.docs.save(
                file=b["file"]
            )
            d = 'doc{}_{}'.format(c['audio_message']['owner_id'], c['audio_message']['id'])
            send_message(event, '', d)
            os.remove("text.mp3")
    except AssertionError:
        send_message(event, "Введите что-то помимо символов")


def guess_the_melody(event):
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


def change_nickname(event, message):
    if len(message[8:].lower()) > 20:
        send_message(event, "Слишком длинный ник, допустимая длина - 20 символов")
    else:
        print(f"Пользователь {users[str(event.obj.from_id)].nickname} (id {str(event.obj.from_id)}) сменил "
              f"ник на {message[8:]}")
        users[str(event.obj.from_id)].set_nickname(message[8:])
        send_message(event, f"Вы сменили ник на \"{message[8:]}\"!")


def main():
    download_users_from_file()  # выгружаю данные из users.csv
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
            if message[:7].lower() == 'погода ':
                print(f"Пользователь {users[user_id].nickname} узнаёт погоду")
                send_message(event, weather(str(event.obj.text).lower()[7:]))
            if message[:8].lower() == 'никнейм ':
                change_nickname(event, message)
            if message[:7].lower() == 'озвучь ':
                print(f"Пользователь {users[user_id].nickname} использует озвучку")
                voice_acting(event, message)
            if str(message[message.find('id') + 2:message.find('|')]) in users:  # отметка пользователя через @
                replied_id = str(message[message.find('id') + 2:message.find('|')])
                print(f"{users[user_id].nickname} отметил {users[replied_id].nickname}")
                command = re.sub(r"\[.*]", "", message).lower().replace(' ', '')
                if command == 'удар' or command == 'ударить':
                    send_message(event,
                                 f"{users[user_id].nickname} ударил [id{replied_id}|{users[replied_id].nickname}]")
                if command == 'чмок' or command == 'поцеловать' or command == 'цем':
                    send_message(event,
                                 f"{users[user_id].nickname} поцеловал [id{replied_id}|{users[replied_id].nickname}]")
            if (message.lower() == 'угадай мелодию' or message.lower() == 'угадать мелодию' or message.lower() == 'угадай трек' or message.lower() == 'угадать трек') and not gameMELODY:
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
