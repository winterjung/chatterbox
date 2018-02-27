import abc
from collections import ChainMap


class Addable(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __add__(self, other):
        pass

    def __radd__(self, other):
        return self.__add__(other)


class MessageAddMixin(Addable):
    def __add__(self, other):
        if isinstance(other, Keyboard):
            return Response(self.message, other.keyboard)
        return Message(**ChainMap(self.message, other.message))


class KeyboardAddMixin(Addable):
    def __add__(self, other):
        if isinstance(other, Keyboard):
            raise TypeError('unsupported operand: Keyboard + Keyboard')
        return Response(other.message, self.keyboard)


class ResponseAddMixin(Addable):
    def __add__(self, other):
        if isinstance(other, Keyboard):
            raise TypeError('unsupported operand: Response + Keyboard')
        if type(other) is Response:
            raise TypeError('unsupported operand: Response + Response')
        message = dict(ChainMap(self.message.message, other.message))
        keyboard = self.keyboard.keyboard
        return Response(message=message,
                        keyboard=keyboard)


class Response(dict, ResponseAddMixin):
    def __init__(self, message=None, keyboard=None):
        self.message = None
        self.keyboard = None

        if message:
            self.message = Message(**message)
        if keyboard:
            self.keyboard = Keyboard(**keyboard)

        self.response = self.frame()
        super().__init__(**self.response)

    def frame(self):
        response = ChainMap()
        if self.message:
            response = response.new_child(self.message)
        if self.keyboard:
            response = response.new_child(self.keyboard)
        return dict(response)


class Message(dict, MessageAddMixin):
    def __init__(self, text=None, photo=None, message_button=None):
        self.text = None
        self.photo = None
        self.message_button = None

        if isinstance(text, Text):
            self.text = text
        elif text:
            self.text = Text(text)

        if isinstance(photo, Photo):
            self.photo = photo
        elif photo:
            self.photo = Photo(**photo)

        if isinstance(message_button, MessageButton):
            self.message_button = message_button
        elif message_button:
            self.message_button = MessageButton(**message_button)

        self.message = self.frame()
        super().__init__(message=self.message)

    def frame(self):
        messages = (self.text, self.photo, self.message_button)
        not_none_messages = (msg.message for msg in messages if msg)
        return dict(ChainMap(*not_none_messages))


class Keyboard(dict, KeyboardAddMixin):
    def __init__(self,
                 buttons=None,
                 type='buttons'):  # pylint: disable=redefined-builtin
        self.buttons = buttons
        self.type = type
        self.validate()

        self.keyboard = self.frame()
        super().__init__(keyboard=self.keyboard)

    def validate(self):
        if not isinstance(self.buttons, list) and self.type == 'buttons':
            raise TypeError('buttons must be list in buttons type')
        if self.buttons is not None and self.type == 'text':
            raise TypeError('buttons must be None in text type')

    def frame(self):
        mapping = {
            'text': self.generate_text_keyboard(),
            'buttons': self.generate_buttons_keyboard(self.buttons),
        }
        return mapping.get(self.type)

    def items(self):
        return dict(**self.keyboard).items()

    @classmethod
    def generate_text_keyboard(cls):
        return dict(type='text')

    @classmethod
    def generate_buttons_keyboard(cls, buttons):
        return dict(type='buttons', buttons=buttons)


class Text(dict, MessageAddMixin):
    def __init__(self, text):
        self.text = text

        self.message = self.frame()
        super().__init__(message=self.message)

    def frame(self):
        return {
            'text': self.text
        }


class Photo(dict, MessageAddMixin):
    def __init__(self, url, width, height):
        self.url = url
        self.width = width
        self.height = height
        self.validate()

        self.message = self.frame()
        super().__init__(message=self.message)

    def validate(self):
        if not isinstance(self.width, int):
            raise TypeError('width must be int')
        if not isinstance(self.height, int):
            raise TypeError('height must be int')

    def frame(self):
        return {
            'photo': {
                'url': self.url,
                'width': self.width,
                'height': self.height,
            }
        }


class MessageButton(dict, MessageAddMixin):
    def __init__(self, label, url):
        self.label = label
        self.url = url

        self.message = self.frame()
        super().__init__(message=self.message)

    def frame(self):
        return {
            'message_button': {
                'label': self.label,
                'url': self.url,
            }
        }
