from chatterbox import Chatter


class TestChatter:

    @classmethod
    def setup_class(cls):
        pass

    def test_create_chatter(self):
        chatter = Chatter()
        assert chatter is not None

    def test_handler_functions(self, handler):
        assert isinstance(handler, dict)

        for func_name in handler:
            assert callable(handler[func_name])

    def test_add_rule_with_kwargs(self, handler):
        chatter = Chatter()

        chatter.add_rule(action='자기소개',
                         src='홈',
                         dest='소개',
                         func=handler['intro'])

        assert chatter.rules is not None
        assert chatter.rules['자기소개_홈_소개'] is not None

    def test_add_rule_without_kwargs(self, handler):
        chatter = Chatter()

        chatter.add_rule('자기소개', '홈', '소개', handler['intro'])

        assert chatter.rules is not None
        assert chatter.rules['자기소개_홈_소개'] is not None

    def test_add_rule_decorator(self):
        chatter = Chatter()

        @chatter.rule(action='자기소개', src='홈', dest='소개')
        def intro(data):
            pass

        assert chatter.rules is not None
        assert chatter.rules['자기소개_홈_소개'] is not None

    @classmethod
    def teardown_class(cls):
        pass
