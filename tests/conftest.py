import pytest

from chatterbox import Chatter
from chatterbox.response import Keyboard, Message, MessageButton, Photo, Text


@pytest.fixture(scope='class')
def response_dict(request):
    text = {
        'text': '안녕!',
    }
    photo = {
        'url': 'https://photo.src',
        'width': 640,
        'height': 480,
    }
    message_button = {
        'label': '안녕!',
        'url': 'https://button/url',
    }
    input_keyboard = {
        'type': 'text',
    }
    button_keyboard = {
        'type': 'buttons',
        'buttons': ['버튼1', '버튼2'],
    }
    data_dict = dict(
        input_keyboard={
            'keyboard': input_keyboard,
        },
        button_keyboard={
            'keyboard': button_keyboard,
        },
        text={
            'message': text,
        },
        photo={
            'message': {
                'photo': photo,
            },
        },
        message_button={
            'message': {
                'message_button': message_button,
            },
        },
        full={
            'message': {
                **text,
                'photo': photo,
                'message_button': message_button,
            },
        },
    )
    data_instance = dict(
        text=Text(**text),
        photo=Photo(**photo),
        message_button=MessageButton(**message_button),
        input_keyboard=Keyboard(**input_keyboard),
        button_keyboard=Keyboard(**button_keyboard),
    )
    request.cls.response = data_dict
    request.cls.response_ins = data_instance


@pytest.fixture(scope='function')
def chatter():
    return Chatter()


@pytest.fixture(scope='class')
def registered_chatter(request, handler):
    chatter = Chatter()
    chatter.add_base('홈', handler['home_keyboard'])
    chatter.add_rule('자기소개', '홈', '소개', handler['intro'])
    chatter.add_rule('오늘의 날씨', '소개', '홈', handler['weather'])
    chatter.add_rule('사이트로 이동하기', '홈', '홈', handler['web'])
    chatter.add_rule('취소', '*', '홈', handler['cancel'])
    request.cls.chatter = chatter


@pytest.fixture(scope='function')
def data():
    data = {
        'user_key': 'encryptedUserKey',
        'type': 'text',
        'content': None,
    }
    return data


@pytest.fixture(scope='module')
def handler():
    handlers = {
        'home_keyboard': home_keyboard,
        'intro': intro,
        'weather': weather,
        'web': web,
        'cancel': cancel,
    }
    return handlers


def home_keyboard():
    home_buttons = ['자기소개', '사이트로 이동하기']
    return Keyboard(home_buttons)


def intro(data):
    message = '안녕하세요! 무엇을 도와드릴까요?'
    buttons = ['오늘의 날씨', '취소']
    return Text(message) + Keyboard(buttons)


def weather(data):
    text = Text('오늘은 하루종일 맑겠습니다.')
    sunny_image_url = 'http://images/test.jpg'
    photo = Photo(url=sunny_image_url, width=600, height=401)
    keyboard = home_keyboard()
    return text + photo + keyboard


def web(data):
    text = Text('자세한 정보를 보고싶으면 사이트로 이동해주세요!')
    msg_button = MessageButton(label='이동하기',
                               url='https://github.com/jungwinter/chatterbox')
    keyboard = home_keyboard()
    return Message(text=text, message_button=msg_button) + keyboard


def cancel(data):
    message = '취소하셨습니다.'
    return Text(message) + home_keyboard()
