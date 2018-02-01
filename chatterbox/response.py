class Message(dict):
    def __init__(self, text=None, photo=None, message_button=None):
        message_dict = dict()

        if text:
            message_dict['text'] = text
        if photo:
            message_dict['photo'] = photo
        if message_button:
            message_dict['message_button'] = message_button

        super().__init__(self, message=message_dict)

    def __add__(self, other):
        return Message(**self['message'], **other['message'])

    def __radd__(self, other):
        return self.__add__(other)


class Keyboard(dict):
    def __init__(self, buttons=None, type='buttons'):
        self._buttons = buttons
        self._type = type
        self._check_validity()

        button_mapping = {
            'text': self._text_type_keyboard(),
            'buttons': self._buttons_type_keyboard(),
        }
        super().__init__(self, keyboard=button_mapping[self._type])

    def _check_validity(self):
        if not isinstance(self._buttons, list) and self._type == 'buttons':
            raise TypeError('buttons must be list in buttons type')
        if self._buttons is not None and self._type == 'text':
            raise TypeError('buttons must be None in text type')

    def _text_type_keyboard(self):
        return dict(type='text')

    def _buttons_type_keyboard(self):
        return dict(type='buttons', buttons=self._buttons)


class Text(Message):
    def __init__(self, text):
        self._text = text

        text_dict = {
            'text': self._text
        }
        super().__init__(**text_dict)


class Photo(Message):
    def __init__(self, url, width, height):
        self._url = url
        self._width = width
        self._height = height

        photo_dict = {
            'photo': {
                'url': self._url,
                'width': self._width,
                'height': self._height,
            }
        }
        super().__init__(**photo_dict)


class MessageButton(Message):
    def __init__(self, label, url):
        self._label = label
        self._url = url

        message_button_dict = {
            'message_button': {
                'label': self._label,
                'url': self._url,
            }
        }
        super().__init__(**message_button_dict)
