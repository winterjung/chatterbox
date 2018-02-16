import pytest

from chatterbox.response import Keyboard, Response, Text
from chatterbox.utils import listify


@pytest.mark.usefixtures('registered_chatter')
class TestChatterRoute:
    def test_valid_scenario(self, data):
        user_key = data['user_key']
        check = Checker().init(self.chatter).user(user_key)
        check_text = check.msg('text').keyboard('buttons')
        check_home = check_text.dest('홈').home()

        data['content'] = '자기소개'
        res = self.chatter.route(data)
        (check_text
            .src('홈')
            .dest('소개')
            .contain('도와드릴까요?')
            .do(res))

        data['content'] = '오늘의 날씨'
        res = self.chatter.route(data)
        (check_home
            .src('소개')
            .msg('photo')
            .contain('맑겠습니다')
            .do(res))

        data['content'] = '사이트로 이동하기'
        res = self.chatter.route(data)
        (check_home
            .src('홈')
            .msg('message_button')
            .contain('사이트로 이동')
            .do(res))

        data['content'] = '자기소개'
        res = self.chatter.route(data)
        data['content'] = '취소'
        res = self.chatter.route(data)
        (check_home
            .src('소개')
            .contain('취소하셨습니다')
            .do(res))

    def test_invalid_content(self, data):
        with pytest.raises(ValueError) as excinfo:
            data['content'] = '오늘의 날씨'
            self.chatter.route(data)
        assert 'there is no matching function' in str(excinfo.value)

    def test_endless_input_scenario(self, chatter, data):
        check = Checker().init(chatter).user(data['user_key'])
        chatter.add_base('홈', lambda: Keyboard(['숫자 맞추기']))

        @chatter.rule('숫자 맞추기', '홈', '맞추는중')
        def guess(data):
            message = '숫자 맞추기를 시작합니다.'
            return Text(message) + Keyboard(type='text')

        @chatter.rule(action='*', src='맞추는중')
        def decide(data):
            answer = data['content']

            if answer == '42':
                response = correct(data)
            else:
                response = try_again(data)
            return response

        @chatter.rule(dest='홈')
        def correct(data):
            text = Text('맞았습니다!')
            return text + chatter.home()

        @chatter.rule(dest='맞추는중')
        def try_again(data):
            text = Text('틀렸습니다.')
            keyboard = Keyboard(type='text')
            return text + keyboard

        assert chatter.rules.action('숫자 맞추기').one() is not None
        assert chatter.rules.src('맞추는중').one() is not None

        data['content'] = '숫자 맞추기'
        res = chatter.route(data)
        (check
            .src('홈')
            .dest('맞추는중')
            .msg('text')
            .contain('시작합니다')
            .keyboard('text')
            .do(res))

        data['content'] = '21'
        res = chatter.route(data)
        (check
            .src('맞추는중')
            .dest('맞추는중')
            .msg('text')
            .contain('틀렸습니다')
            .keyboard('text')
            .do(res))

        data['content'] = '42'
        res = chatter.route(data)
        (check
            .src('맞추는중')
            .dest('홈')
            .msg('text')
            .contain('맞았습니다')
            .home()
            .do(res))

    def test_once_input_scenario(self, chatter, data):
        check = Checker().init(chatter).user(data['user_key'])
        chatter.add_base('홈', lambda: Keyboard(['숫자 맞추기']))

        @chatter.rule('숫자 맞추기', '홈', '맞추는중')
        def guess(data):
            message = '숫자 맞추기를 시작합니다.'
            return Text(message) + Keyboard(type='text')

        @chatter.rule(action='*', src='맞추는중', dest='홈')
        def decide(data):
            answer = data['content']

            if answer == '42':
                text = Text('맞았습니다!')
            else:
                text = Text('틀렸습니다!')
            return text + chatter.home()

        assert chatter.rules.action('숫자 맞추기').one() is not None
        assert chatter.rules.src('맞추는중').one() is not None

        data['content'] = '숫자 맞추기'
        res = chatter.route(data)
        data['content'] = '21'
        res = chatter.route(data)
        (check
            .src('맞추는중')
            .dest('홈')
            .msg('text')
            .contain('틀렸습니다')
            .home()
            .do(res))

        data['content'] = '숫자 맞추기'
        res = chatter.route(data)
        data['content'] = '42'
        res = chatter.route(data)
        (check
            .src('맞추는중')
            .dest('홈')
            .msg('text')
            .contain('맞았습니다')
            .home()
            .do(res))


class Asserter:
    def init(self, chatter):
        self.chatter = chatter
        return self

    def user(self, user_key):
        self.user_key = user_key
        return self

    def res(self, response):
        self.response = response
        assert isinstance(self.response, Response)
        return self

    def src(self, src):
        user = self.chatter.memory.user(self.user_key)
        if user is not None:
            assert user.previous == src
        return self

    def dest(self, dest):
        user = self.chatter.memory.user(self.user_key)
        if user is not None:
            assert user.current == dest
        return self

    def msg(self, messages):
        for msg in listify(messages):
            assert msg in self.response['message']
        return self

    def home(self):
        home_keyboard = self.chatter.home()
        assert self.response['keyboard'] == home_keyboard['keyboard']
        return self

    def keyboard(self, keyboard_type):
        assert self.response['keyboard']['type'] == keyboard_type
        return self

    def contain(self, target):
        msg = self.response['message']
        text = msg.get('text', '')
        photo = msg.get('photo', {})
        button = msg.get('message_button', {})

        in_text = target in text
        in_photo = target in photo.get('url', '')
        in_button_label = target in button.get('label', '')
        in_button_url = target in button.get('url', '')

        assert any([in_text, in_photo, in_button_label, in_button_url])
        return self


class Checker:
    def __init__(self, wrapper=None):
        if wrapper is None:
            wrapper = Asserter()
        self._wrapper = wrapper

    def do(self, response):
        self._wrapper = Checker._through_to_core(self._wrapper, response)
        return self._wrapper

    def __getattr__(self, name):
        method = getattr(Asserter, name)
        return CheckerWrapper(self._wrapper, method=method)

    @staticmethod
    def _through_to_core(wrapper, response):
        if isinstance(wrapper, CheckerWrapper):
            wrapper.response = response
            wrapper = wrapper.unwrap()
        return wrapper


class CheckerWrapper:
    def __init__(self, _wrapper, method):
        self._wrapper = _wrapper
        self.method = method
        self.args = ()
        self.kwargs = {}
        self.response = None

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        return Checker(self)

    def unwrap(self):
        if isinstance(self._wrapper, CheckerWrapper):
            self._wrapper.response = self.response
            self._wrapper = self._wrapper.unwrap()
        self._wrapper.res(self.response)
        return self.method(self._wrapper, *self.args, **self.kwargs)
