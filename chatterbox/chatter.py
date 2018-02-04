class Chatter:
    def __init__(self):
        self.rules = {}
        self._home = HomeBase()
        self._memory = {}

    def add_rule(self, action, src, dest, func):
        rule_name = '{}_{}_{}'.format(action, src, dest)
        self.rules[rule_name] = func

    def rule(self, action, src, dest):
        def decorator(func):
            self.add_rule(action, src, dest, func)
            return func
        return decorator

    def add_base(self, name, func):
        self._home.name = name
        self._home.func = func

    def base(self, name):
        def decorator(func):
            self.add_base(name, func)
            return func
        return decorator

    @property
    def home(self):
        return self._home

    def route(self, data):
        # TODO: valid check
        user_key = data['user_key']
        action = data['content']

        # Default user setting
        if user_key not in self._memory:
            src = self.home.name
            self._memory[user_key] = State(src)

        # Get src
        src = self.current_state(user_key)

        # Search rule
        rule_name = '{}_{}_'.format(action, src)
        dest = None
        func = None
        for key in self.rules:
            if key.startswith(rule_name):
                dest = key.replace(rule_name, '')
                func = self.rules[key]

        # Search when src is *
        if func is None:
            rule_name = '{}_*_'.format(action)
            for key in self.rules:
                if key.startswith(rule_name):
                    dest = key.replace(rule_name, '')
                    func = self.rules[key]

        # Not match
        if func is None:
            raise ValueError('there is no matching function')
        # Execute function
        response = func(data)
        # TODO: check coroutine

        # Update state
        self._memory[user_key].move(dest)

        return response

    def previous_state(self, user_key):
        # TODO: check exist
        return self._memory[user_key].previous

    def current_state(self, user_key):
        # TODO: check exist
        return self._memory[user_key].current


class State:
    def __init__(self, current_state):
        self.previous = None
        self.current = current_state

    def move(self, dest):
        self.previous = self.current
        self.current = dest
        return self


class HomeBase:
    def __init__(self, name=None, func=None):
        self.name = name
        self.func = func

    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, value):
        setattr(self, name, value)

    def __call__(self):
        return self.func()
