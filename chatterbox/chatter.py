from types import GeneratorType
from chatterbox.memory import DictionaryMemory


class Chatter:
    WAITING_STATE = '__waiting_input'

    def __init__(self, memory=DictionaryMemory):
        self.rules = {}
        self._home = HomeBase()
        self._memory = memory()

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
        user_key = data['user_key']
        action = data['content']
        user = self.user(user_key)

        current_state = user.current

        if self._is_waiting_state(current_state):
            # Side effect
            response = self._get_response_from_generator(user, data)
            return response

        rule_name = self._find_rule_name(action, current_state)

        dest = self._extract_dest(rule_name)
        func = self._finc_handle_func(rule_name)

        response = func(data)

        if isinstance(response, GeneratorType):
            gen = response
            response = gen.send(None)
            # user.update_context(gen=response, dest=dest)
            user.context = {
                'generator': gen,
                'destination': dest,
            }
            dest = self.WAITING_STATE

        user.move(dest)
        return response

    def _is_waiting_state(self, state):
        return state == self.WAITING_STATE

    def _get_response_from_generator(self, user, data):
        context = user.context
        gen = context['generator']
        dest = context['destination']

        try:
            response = gen.send(data)
            user.context['generator'] = gen  # Side effect
            # user.update_context(gen=gen)
        except StopIteration as excinfo:
            response = excinfo.value
            user.move(dest)  # Side effect
        return response

    def _find_rule_name(self, action, current_state):
        rule_name = '{}_{}_'.format(action, current_state)
        for name in self.rules:
            if name.startswith(rule_name):
                return name

        if current_state == '*':
            raise ValueError('there is no matching function')

        name = self._find_rule_name(action, '*')
        return name

    def _finc_handle_func(self, rule_name):
        func = self.rules[rule_name]
        return func

    def _extract_dest(self, rule_name):
        return rule_name.split('_')[-1]

    def user(self, user_key):
        user = self._memory.user(user_key)
        if user is None:
            user = self._memory.create(user_key, self.home.name)
        return user


class HomeBase:
    def __init__(self, name=None, func=None):
        self.name = name
        self.func = func

    def __call__(self):
        return self.func()
