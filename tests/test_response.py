import pytest
import json
from chatterbox.response import Keyboard, Text, Photo, MessageButton, Message


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
        with pytest.raises(Exception):
            Keyboard(['버튼1'], type='text')
        with pytest.raises(Exception):
            Keyboard('버튼1')
        with pytest.raises(Exception):
            Keyboard(type='buttons')

    def test_text(self):
        text = Text('안녕!')
        assert self.response['text'] == text

    def test_photo(self):
        photo = Photo('https://photo.src', 640, 480)
        photo_with_kwargs = Photo(url='https://photo.src',
                                  width=640,
                                  height=480)
        assert self.response['photo'] == photo == photo_with_kwargs

    def test_message_button(self):
        message_button = MessageButton(label='안녕!',
                                       url='https://button/url')
        assert self.response['message_button'] == message_button

    def test_message(self):
        assert self.response_ins['text'] == Message(text='안녕!')

        message_photo = Message(photo={
                                    'url': 'https://photo.src',
                                    'width': 640,
                                    'height': 480,
                                })
        assert self.response_ins['photo'] == message_photo

        message_button = Message(message_button={
                                    'label': '안녕!',
                                    'url': 'https://button/url',
                                })
        assert self.response_ins['message_button'] == message_button

        message_full = Message(text='안녕!',
                               photo={
                                   'url': 'https://photo.src',
                                   'width': 640,
                                   'height': 480,
                               },
                               message_button={
                                   'label': '안녕!',
                                   'url': 'https://button/url',
                               })
        assert self.response['full'] == message_full
        assert message_full == Message(**self.response['full']['message'])

    def test_message_combination(self):
        text = self.response_ins['text']
        photo = self.response_ins['photo']
        button = self.response_ins['message_button']
        message_full = Message(**self.response['full']['message'])

        assert text + photo + button == self.response['full']
        assert text + photo + button == message_full
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
        assert text + photo_dict + button_dict == self.response['full']
        assert text_dict + photo + button_dict == self.response['full']
        with pytest.raises(TypeError):
            assert text_dict + photo_dict + button == self.response['full']
