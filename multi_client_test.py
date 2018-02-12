import random
import string
from chatterbox import Chatter
from chatterbox.response import Keyboard, Text


USER_KEY_LENGTH = 15
NUM_USERS = 1000
NUM_CHATTERS = 4
NUM_LOOP = 4000


def home():
    return Keyboard(['go'])


def a(data):
    return Text('going') + Keyboard(['back'])


def go_back(data):
    return Text('back') + home()


def create_chatter():
    chatter = Chatter('redis')
    chatter.add_base('home', home)
    chatter.add_rule('go', 'home', 'a', a)
    chatter.add_rule('back', 'a', 'home', go_back)
    return chatter


def generate_content(keys, user_key):
    value = keys[user_key]
    if value == 0:
        keys[user_key] = 1
        return 'go'
    if value == 1:
        keys[user_key] = 0
        return 'back'


def user_data(user_key, content):
    return dict(user_key=user_key, type='text', content=content)


def main():
    users = [''.join(random.choice(string.ascii_letters)
                     for _ in range(USER_KEY_LENGTH))
             for _ in range(NUM_USERS)]

    keys = {key: 0 for key in users}
    chatters = [create_chatter() for _ in range(NUM_CHATTERS)]
    error_counter = 0
    pass_counter = 0

    for i in range(NUM_LOOP):
        user_key = random.choice(users)
        content = generate_content(keys, user_key)
        chatter = random.choice(chatters)
        data = user_data(user_key, content)
        try:
            res = chatter.route(data)
        except ValueError:
            error_counter += 1
        else:
            pass_counter += 1

    print(f'error count: {error_counter}')
    print(f'pass count: {pass_counter}')
    print(f'error ratio: {error_counter/NUM_LOOP*100:.2f}%')


if __name__ == '__main__':
    main()
