import pytest
from chatterbox import Chatter


class TestChatter:

    @classmethod
    def setup_class(cls):
        pass

    def test_create_chatter(self):
        chatter = Chatter()
        assert chatter is not None

    @classmethod
    def teardown_class(cls):
        pass
