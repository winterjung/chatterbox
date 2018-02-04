import pytest
from chatterbox.response import Response


@pytest.mark.usefixtures('registered_chatter')
class TestChatterRoute:
    def test_initialized_chatter(self):
        assert self.chatter is not None
        assert len(self.chatter.rules) > 0
        assert callable(self.chatter.rules['자기소개_홈_소개'])
        assert callable(self.chatter.rules['오늘의 날씨_소개_홈'])
        assert callable(self.chatter.rules['사이트로 이동하기_홈_홈'])
        assert callable(self.chatter.rules['취소_*_홈'])
        assert self.chatter.home.name == '홈'
        assert callable(self.chatter.home)

    def test_valid_scenario(self, data):
        user_key = data['user_key']
        check = Checker().init(self.chatter).user(user_key)
        check_text = check.msg(['text'])
        check_home = check_text.dest('홈').home()

        data['content'] = '자기소개'
        res = self.chatter.route(data)
        check_text.src('홈').dest('소개').do(res)

        data['content'] = '오늘의 날씨'
        res = self.chatter.route(data)
        check_home.src('소개').msg(['photo']).do(res)

        data['content'] = '사이트로 이동하기'
        res = self.chatter.route(data)
        check_home.src('홈').msg(['message_button']).do(res)

        data['content'] = '자기소개'
        res = self.chatter.route(data)
        data['content'] = '취소'
        res = self.chatter.route(data)
        check_home.src('소개').do(res)

    def test_invalid_content(self, data):
        with pytest.raises(ValueError) as excinfo:
            data['content'] = '오늘의 날씨'
            self.chatter.route(data)
        assert 'there is no matching function' in str(excinfo.value)


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
        assert self.chatter.previous_state(self.user_key) == src
        return self

    def dest(self, dest):
        assert self.chatter.current_state(self.user_key) == dest
        return self

    def msg(self, messages):
        for msg in messages:
            assert msg in self.response['message']
        return self

    def home(self):
        home_keyboard = self.chatter.home()
        assert self.response['keyboard'] == home_keyboard['keyboard']
        return self


class Checker:
    def __init__(self, wrapper=None):
        if wrapper is None:
            wrapper = Asserter()
        self._wrapper = wrapper

    def do(self, response):
        if isinstance(self._wrapper, CheckerWrapper):
            self._wrapper.response = response
            self._wrapper = self._wrapper.unwrap()
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
