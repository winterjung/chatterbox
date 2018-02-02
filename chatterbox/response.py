class Response(dict):
    def __init__(self, message=None, keyboard=None):
        self._message = message
        self._keyboard = keyboard
        response = dict()

        if self._message:
            response['message'] = self._message
        if self._keyboard:
            response['keyboard'] = self._keyboard

        super().__init__(**response)

    def __add__(self, other):
        if isinstance(other, Keyboard):
            raise TypeError('unsupported operand: Response + Keyboard')
        if type(other) is Response:
            raise TypeError('unsupported operand: Response + Response')
        return Response(message={**self['message'], **other['message']},
                        keyboard=self['keyboard'])

    def __radd__(self, other):
        return self.__add__(other)


class Message(Response):
    def __init__(self, text=None, photo=None, message_button=None):
        self._text = text
        self._photo = photo
        self._message_button = message_button

        message_dict = dict()

        if self._text:
            message_dict['text'] = self._text
        if self._photo:
            message_dict['photo'] = self._photo
        if self._message_button:
            message_dict['message_button'] = self._message_button

        super().__init__(message=message_dict)

    def __add__(self, other):
        if isinstance(other, Keyboard):
            return Response(**self, **other)
        return Message(**self['message'], **other['message'])


class Keyboard(Response):
    def __init__(self, buttons=None, type='buttons'):
        self._buttons = buttons
        self._type = type
        self._check_validity()

        button_mapping = {
            'text': self._text_type_keyboard(),
            'buttons': self._buttons_type_keyboard(),
        }
        super().__init__(keyboard=button_mapping[self._type])

    def _check_validity(self):
        if not isinstance(self._buttons, list) and self._type == 'buttons':
            raise TypeError('buttons must be list in buttons type')
        if self._buttons is not None and self._type == 'text':
            raise TypeError('buttons must be None in text type')

    def _text_type_keyboard(self):
        return dict(type='text')

    def _buttons_type_keyboard(self):
        return dict(type='buttons', buttons=self._buttons)

    def __add__(self, other):
        if isinstance(other, Keyboard):
            raise TypeError('unsupported operand: Keyboard + Keyboard')
        return Response(**other, **self)


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
