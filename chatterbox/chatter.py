class Chatter:
    def __init__(self):
        self.rules = {}

    def add_rule(self, action, src, dest, func):
        rule_name = '{}_{}_{}'.format(action, src, dest)
        self.rules[rule_name] = func

    def rule(self, action, src, dest):
        def decorator(func):
            self.add_rule(action, src, dest, func)
            return func
        return decorator
