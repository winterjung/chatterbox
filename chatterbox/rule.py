from types import SimpleNamespace

from chatterbox.utils import listify


class RuleBook:
    def __init__(self, rules=None):
        self._rules = []

        if rules is not None:
            self.add_rules(rules)

    def add_rules(self, rules):
        for rule in listify(rules):
            if isinstance(rule, list):
                self.add_rule(*rule)
            if isinstance(rule, dict):
                self.add_rule(**rule)
            if isinstance(rule, Rule):
                self._rules.append(rule)

    def add_rule(self, action, src, dest, func):
        self._rules.append(Rule(action, src, dest, func))

    def _filter(self, category, name):
        return [rule for rule in self._rules
                if getattr(rule, category) == name]

    def action(self, name):
        return RuleBook(rules=self._filter('action', name))

    def src(self, name):
        return RuleBook(rules=self._filter('src', name))

    def dest(self, name):
        return RuleBook(rules=self._filter('dest', name))

    def first(self):
        if self._rules:
            return self._rules[0]
        return None

    def one(self):
        length = len(self._rules)
        if length == 1:
            return self._rules[0]
        if length == 0:
            raise Exception('No rule was found')
        raise Exception('Multiple rules were found')

    def all(self):
        return self._rules[:]


class Rule(SimpleNamespace):
    def __init__(self, action, src, dest, func):
        self.action = action
        self.src = src
        self.dest = dest
        self.func = func
