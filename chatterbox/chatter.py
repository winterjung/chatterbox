from inspect import isgeneratorfunction

from chatterbox.memory import DictionaryMemory
from chatterbox.rule import RuleBook
from chatterbox.utils import listify


class Chatter:
    WAITING_STATE = '__waiting_input'

    def __init__(self, memory='dict'):
        self.rules = RuleBook()
        self.home = HomeBase()
        try:
            memory_type = self._lookup_memory(memory)
        except KeyError:
            raise KeyError('Unsupported memory type: {}'.format(memory))
        self.memory = memory_type()

    def _lookup_memory(self, memory):
        table = {
            'dict': DictionaryMemory,
        }
        return table[memory]

    def add_rule(self, action, src, dest, func):
        actions = listify(action)
        for act in actions:
            self.rules.add_rule(act, src, dest, func)

    def rule(self, action, src, dest):
        def decorator(func):
            self.add_rule(action, src, dest, func)
            return func
        return decorator

    def add_base(self, name, func):
        self.home.register(name, func)

    def base(self, name):
        def decorator(func):
            self.add_base(name, func)
            return func
        return decorator

    def user(self, user_key):
        user = self.memory.user(user_key)
        if user is None:
            user = self.memory.create(user_key, self.home.name)
        return user

    def route(self, data):
        user_key = data['user_key']
        action = data['content']
        user = self.user(user_key)
        current_state = user.current

        if self._is_waiting_state(current_state):
            response = self._get_response_from_generator(user, data)
            return response

        rule = self._find_rule(action, current_state)

        if isgeneratorfunction(rule.func):
            gen = rule.func(data)
            response = gen.send(None)

            user.context.generator = gen
            user.context.destination = rule.dest
            dest = self.WAITING_STATE
        else:
            response = rule.func(data)
            dest = rule.dest

        user.move(dest)
        self._update_user(user)
        return response

    def _update_user(self, user):
        if user.current == self.home.name:
            self._delete_user(user)
        else:
            self._save_user(user)

    def _delete_user(self, user):
        self.memory.delete(user)

    def _save_user(self, user):
        self.memory.save(user)

    def _is_waiting_state(self, state):
        return state == self.WAITING_STATE

    def _get_response_from_generator(self, user, data):
        gen = user.context.generator
        dest = user.context.destination

        try:
            response = gen.send(data)
            user.context.generator = gen
        except StopIteration as excinfo:
            response = excinfo.value
            user.move(dest)
        self._update_user(user)
        return response

    def _find_rule(self, action, current_state):
        rule = self.rules.action(action).src(current_state).first()
        if rule is None:
            rule = self.rules.action(action).src('*').first()
        if rule is None:
            raise ValueError('there is no matching function')
        return rule


class HomeBase:
    def __init__(self):
        self.name = None
        self.func = None

    def __call__(self):
        return self.func()

    def register(self, name=None, func=None):
        self.name = name
        self.func = func
