from chatterbox import Chatter
from chatterbox.chatter import HomeBase
from chatterbox.response import Keyboard


class TestChatter:
    def test_create_chatter(self):
        chatter = Chatter()
        assert chatter is not None

    def test_handler_functions(self, handler):
        assert isinstance(handler, dict)

        for func_name in handler:
            assert callable(handler[func_name])

    def test_add_rule(self, chatter, handler):
        chatter.add_rule(action='자기소개',
                         src='홈',
                         dest='소개',
                         func=handler['intro'])

        rule = chatter.rules.action('자기소개').one()
        assert rule is not None
        assert rule.src == '홈'
        assert rule.dest == '소개'
        assert callable(rule.func)

    def test_add_rule_decorator(self, chatter):
        @chatter.rule(action='자기소개', src='홈', dest='소개')
        def intro(data):
            pass

        rule = chatter.rules.action('자기소개').one()
        assert rule is not None
        assert rule.src == '홈'
        assert rule.dest == '소개'
        assert callable(rule.func)

    def test_add_rule_multiple_action(self, chatter, handler):
        actions = ['자기소개', '소개하기', '안내']
        chatter.add_rule(action=actions,
                         src='홈',
                         dest='소개',
                         func=handler['intro'])

        rule = chatter.rules.action('자기소개').src('홈').first()
        assert rule.dest == '소개'
        assert callable(rule.func)

        rules = chatter.rules.src('홈').dest('소개').all()
        for rule in rules:
            assert rule.action in actions

        funcs = [rule.func for rule in rules]
        assert len(set(funcs)) == 1

    def test_add_base(self, chatter, handler):
        chatter.add_base(name='홈', func=handler['home_keyboard'])

        assert chatter.home.name == '홈'
        assert callable(chatter.home.func)
        assert isinstance(chatter.home(), Keyboard)
        assert isinstance(chatter.home, HomeBase)

    def test_add_base_decorator(self, chatter):
        @chatter.base('홈')
        def home_keyboard():
            pass

        assert chatter.home.name == '홈'
        assert callable(chatter.home.func)


class TestHomeBase:
    def test_homebase_with_args(self):
        def keyboard():
            return Keyboard(['버튼'])
        home = HomeBase()
        home.register('홈', keyboard)

        assert home.name == '홈'
        assert callable(home.func)
        assert callable(home)
        assert home() == home.func()

    def test_homebase_without_args(self):
        home = HomeBase()
        home.name = '홈'
        home.func = lambda: Keyboard(['버튼'])
        assert home() == home.func()
