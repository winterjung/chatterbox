import json
from functools import partial, reduce
from itertools import chain, combinations, permutations, product
from operator import add

import pytest

from chatterbox.response import (Keyboard, Message, MessageButton, Photo,
                                 Response, Text)


class TestKeyboard:
    def test_input(self, keyboard):
        input_keyboard = Keyboard(type='text')
        assert keyboard.dict.input == input_keyboard
        assert input_keyboard.type == 'text'
        assert input_keyboard.buttons is None

    def test_button(self, keyboard):
        button_keyboard = Keyboard(['버튼1', '버튼2'])
        assert keyboard.dict.button == button_keyboard
        assert button_keyboard.type == 'buttons'
        assert button_keyboard.buttons == ['버튼1', '버튼2']

    def test_invalid_input_with_button(self):
        with pytest.raises(TypeError) as excinfo:
            Keyboard(['버튼1'], type='text')
        assert 'buttons must be None' in str(excinfo.value)

    def test_invalid_button(self):
        with pytest.raises(TypeError) as excinfo:
            Keyboard('버튼1')
        assert 'buttons must be list' in str(excinfo.value)

    def test_invalid_no_button(self):
        with pytest.raises(TypeError) as excinfo:
            Keyboard(type='buttons')
        assert 'buttons must be list' in str(excinfo.value)

    def test_invalid_no_argument(self):
        with pytest.raises(TypeError) as excinfo:
            Keyboard()
        assert 'buttons must be list' in str(excinfo.value)


class TestMessage:
    def test_dict_with_instance(self, message):
        assert message.dict.text == message.ins.text
        assert message.dict.photo == message.ins.photo
        assert message.dict.button == message.ins.button
        assert message.dict.full == message.ins.full

    def test_text(self, message):
        text = Text('안녕!')
        assert isinstance(text, Text)
        assert message.dict.text == text

        assert text.text == '안녕!'
        assert text.message == {'text': '안녕!'}

    def test_photo(self, message):
        photo = Photo('https://photo.src', 640, 480)
        assert isinstance(photo, Photo)
        assert message.dict.photo == photo

        assert photo.url == 'https://photo.src'
        assert photo.width == 640
        assert photo.height == 480
        assert photo.message == {
            'photo': {
                'url': 'https://photo.src',
                'width': 640,
                'height': 480,
            }
        }

    def test_button(self, message):
        button = MessageButton('안녕!', 'https://button/url')
        assert isinstance(button, MessageButton)
        assert message.dict.button == button

        assert button.label == '안녕!'
        assert button.url == 'https://button/url'
        assert button.message == {
            'message_button': {
                'label': '안녕!',
                'url': 'https://button/url',
            }
        }

    def test_message(self, message):
        full = message.ins.full

        assert full.text == message.ins.text
        assert full.photo == message.ins.photo
        assert full.message_button == message.ins.button

    def test_response(self, message, keyboard):
        text = message.ins.text
        photo = message.ins.photo
        keyboard = keyboard.ins.button
        response = text + photo + keyboard

        assert isinstance(response, Response)
        assert response == text + photo + keyboard
        assert response.message == text + photo

        assert response.message.text == text
        assert response.message.text.text == '안녕!'

        assert response.message.photo == photo
        assert response.message.photo.url == 'https://photo.src'

        assert response.keyboard == keyboard
        assert response.keyboard.type == 'buttons'

    def test_serializable(self, message, keyboard):
        text = message.ins.text
        photo = message.ins.photo
        keyboard = keyboard.ins.button

        message = text + photo
        response = message + keyboard
        assert json.dumps(message) is not None
        assert json.dumps(response) is not None


class TestCombination:
    def test_message_instance_combination(self, message):
        text = message.ins.text
        photo = message.ins.photo
        button = message.ins.button
        messages = (text, photo, button)

        repeats = range(1, len(messages)+1)
        combination = (combinations(messages, r) for r in repeats)
        flatten = chain(*combination)

        adder = partial(reduce, add)

        messages = map(adder, flatten)
        for msg in messages:
            assert msg == Message(**msg.message)

    def test_message_instnace_and_dict_combination(self, message):
        text = message.ins.text
        photo = message.ins.photo
        button = message.ins.button

        text_dict = message.ins.text
        photo_dict = message.ins.photo
        button_dict = message.ins.button

        assert text_dict + photo + button == message.ins.full
        assert text + photo_dict + button == message.ins.full
        assert text + photo + button_dict == message.ins.full

    def test_message_keyboard_combination(self, message, keyboard):
        text = message.ins.text
        photo = message.ins.photo
        button = message.ins.button

        input_keyboard = keyboard.ins.input
        button_keyboard = keyboard.ins.button

        keyboards = (input_keyboard, button_keyboard)
        messages = (text, photo, button)

        repeats = range(1, len(messages)+1)
        combination = (combinations(messages, r) for r in repeats)
        flatten = chain(*combination)
        adder = partial(reduce, add)
        messages = map(adder, flatten)

        matrix = product(messages, keyboards)
        for msg, keyboard in matrix:
            assert msg + keyboard == Response(msg.message, keyboard.keyboard)

    def test_is_not_sensitivity_on_order(self, message, keyboard):
        text = message.ins.text
        photo = message.ins.photo
        keyboard = keyboard.ins.button

        adder = partial(reduce, add)
        combination = permutations((text, photo, keyboard))

        msg = text + photo
        response = Response(msg.message, keyboard.keyboard)
        for combo in combination:
            assert adder(combo) == response

    def test_supported_operand(self, message, keyboard):
        text = message.ins.text
        photo = message.ins.photo
        button = message.ins.button
        full = message.ins.full

        messages = (text, photo, button, full)
        keyboard = keyboard.ins.button

        for msg in messages:
            assert msg + keyboard == keyboard + msg
            assert type(msg + keyboard) is Response

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
