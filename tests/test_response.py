import json
from functools import partial, reduce
from itertools import chain, combinations, permutations, product
from operator import add

import pytest

from chatterbox.response import (Keyboard, Message, MessageButton, Photo,
                                 Response, Text)


@pytest.mark.usefixtures('response_dict')
class TestResponse:
    def test_keyboard(self):
        input_keyboard = Keyboard(type='text')
        assert self.response['input_keyboard'] == input_keyboard

        button_keyboard = Keyboard(['버튼1', '버튼2'])
        assert self.response['button_keyboard'] == button_keyboard

        serialized = '{"keyboard": {"type": "buttons", "buttons": ["버튼1"]}}'
        keyboard = Keyboard(['버튼1'])
        assert json.dumps(keyboard, ensure_ascii=False) == serialized

    def test_invalid_keyboard(self):
        with pytest.raises(TypeError) as excinfo:
            Keyboard(['버튼1'], type='text')
        assert 'buttons must be None' in str(excinfo.value)
        with pytest.raises(TypeError) as excinfo:
            Keyboard('버튼1')
        assert 'buttons must be list' in str(excinfo.value)
        with pytest.raises(TypeError) as excinfo:
            Keyboard(type='buttons')
        assert 'buttons must be list' in str(excinfo.value)
        with pytest.raises(TypeError) as excinfo:
            Keyboard()
        assert 'buttons must be list' in str(excinfo.value)

    def test_text(self):
        text = Text('안녕!')
        assert isinstance(text, Text)
        text_with_kwargs = Text(text='안녕!')
        assert self.response['text'] == text == text_with_kwargs

    def test_photo(self):
        photo = Photo('https://photo.src', 640, 480)
        assert isinstance(photo, Photo)
        photo_with_kwargs = Photo(url='https://photo.src',
                                  width=640,
                                  height=480)
        assert self.response['photo'] == photo == photo_with_kwargs

    def test_message_button(self):
        button = MessageButton('안녕!', 'https://button/url')
        assert isinstance(button, MessageButton)
        button_with_kwargs = MessageButton(label='안녕!',
                                           url='https://button/url')
        assert self.response['message_button'] == button == button_with_kwargs

    def test_message(self):
        full = Message(text='안녕!',
                       photo={
                           'url': 'https://photo.src',
                           'width': 640,
                           'height': 480,
                       },
                       message_button={
                           'label': '안녕!',
                           'url': 'https://button/url',
                       })
        full_dict = self.response['full']
        assert full_dict == full
        assert full == Message(**full_dict['message'])

    def test_message_combination_with_dict(self):
        text = self.response_ins['text']
        photo = self.response_ins['photo']
        button = self.response_ins['message_button']

        assert text + photo + button == self.response['full']
        assert text + photo == {
            'message': {
                **self.response['text']['message'],
                **self.response['photo']['message']
            }
        }
        assert text + button == {
            'message': {
                **self.response['text']['message'],
                **self.response['message_button']['message']
            }
        }
        assert photo + button == {
            'message': {
                **self.response['photo']['message'],
                **self.response['message_button']['message']
            }
        }

    def test_message_combination_with_instance(self):
        text = self.response_ins['text']
        photo = self.response_ins['photo']
        button = self.response_ins['message_button']

        messages = (text, photo, button)

        repeats = range(1, len(messages)+1)
        combination = (combinations(messages, r) for r in repeats)
        flatten = chain(*combination)
        adder = partial(reduce, add)
        messages = map(adder, flatten)

        for message in messages:
            assert message == Message(**message['message'])

    def test_advanced_message_combination(self):
        text = self.response_ins['text']
        photo = self.response_ins['photo']
        button = self.response_ins['message_button']

        text_dict = self.response['text']
        photo_dict = self.response['photo']
        button_dict = self.response['message_button']

        assert text_dict + photo + button == self.response['full']
        assert text + photo_dict + button == self.response['full']
        assert text + photo + button_dict == self.response['full']

    def test_message_keyboard_combination(self):
        text = self.response_ins['text']
        photo = self.response_ins['photo']
        button = self.response_ins['message_button']
        input_keyboard = self.response_ins['input_keyboard']
        button_keyboard = self.response_ins['button_keyboard']

        keyboards = (input_keyboard, button_keyboard)
        messages = (text, photo, button)

        repeats = range(1, len(messages)+1)
        combination = (combinations(messages, r) for r in repeats)
        flatten = chain(*combination)
        adder = partial(reduce, add)
        messages = map(adder, flatten)
        matrix = product(messages, keyboards)

        for message, keyboard in matrix:
            assert message + keyboard == {**message, **keyboard}

        combination = permutations((text, photo, button_keyboard))
        for combo in combination:
            assert adder(combo) == Response(**(text+photo), **button_keyboard)

    def test_supported_operand(self):
        text = self.response_ins['text']
        photo = self.response_ins['photo']
        button = self.response_ins['message_button']
        keyboard = self.response_ins['button_keyboard']

        assert isinstance(text + photo, Message)
        assert isinstance(text + button, Message)
        assert isinstance(photo + button, Message)
        assert isinstance(text + photo + button, Message)

        assert type(text + keyboard) is Response
        assert type(photo + keyboard) is Response
        assert type(button + keyboard) is Response
        assert type(Message() + keyboard) is Response

        assert type(keyboard + text) is Response
        assert type(keyboard + photo) is Response
        assert type(keyboard + button) is Response
        assert type(keyboard + Message()) is Response

    def test_unsupported_operand(self):
        with pytest.raises(TypeError) as excinfo:
            Keyboard([]) + Keyboard([])
        assert 'Keyboard + Keyboard' in str(excinfo.value)

        with pytest.raises(TypeError) as excinfo:
            Response() + Keyboard([])
        assert 'Response + Keyboard' in str(excinfo.value)

        with pytest.raises(TypeError) as excinfo:
            Response() + Response()
        assert 'Response + Response' in str(excinfo.value)
