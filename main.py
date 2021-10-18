from vk_api import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.utils import get_random_id


vk_session = vk_api.VkApi(token="13c403991e7cf080abc0a32a6450e4552feb9457bb646c174eda48342bddb1adb486ae4a78fa465a48c33")
longpoll = VkBotLongPoll(vk_session, '197126596')
vk = vk_session.get_api()


def main():
    for event in longpoll.listen():
        if event.from_chat:
            message = str(event.obj.text)
            user_id = str(event.obj.from_id)
            print(f'{user_id}: {message}')


if __name__ == '__main__':
    main()
