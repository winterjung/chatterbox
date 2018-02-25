import pytest

from chatterbox import Chatter
from chatterbox.rule import RuleBook


@pytest.mark.usefixtures('registered_chatter')
class TestRuleBook:
    def test_exist_rule_book(self):
        assert isinstance(self.chatter.rules, RuleBook)

    def test_exist_rule_in_rule_book(self):
        rules = self.chatter.rules.all()
        assert len(rules) == 4
        for rule in rules:
            assert callable(rule.func)

    def test_no_rule(self):
        chatter = Chatter()
        rule = chatter.rules.first()
        assert rule is None

        with pytest.raises(Exception) as excinfo:
            chatter.rules.one()
        assert 'No rule was found' in str(excinfo.value)

        rules = chatter.rules.all()
        assert rules == []

    def test_many_rule(self):
        with pytest.raises(Exception) as excinfo:
            self.chatter.rules.dest('홈').one()
        assert 'Multiple rules were found' in str(excinfo.value)
