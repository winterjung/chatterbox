from functools import wraps

from chatterbox.memory import DictionaryMemory
from chatterbox.rule import RuleBook
from chatterbox.utils import listify


class Chatter:
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

    def add_rule(self, action=None, src=None, dest=None, func=None):
        @wraps(func)
        def wrapper(data):
            result = func(data)
            user = self.user(data['user_key'], False)
            if dest is not None:
                user.move(dest)
                self._update_user(user)
            return result

        actions = listify(action)
        for act in actions:
            self.rules.add_rule(act, src, dest, wrapper)
        return wrapper

    def rule(self, action=None, src=None, dest=None):
        def decorator(func):
            wrapper_func = self.add_rule(action, src, dest, func)
            return wrapper_func
        return decorator

    def add_base(self, name, func):
        self.home.register(name, func)

    def base(self, name):
        def decorator(func):
            self.add_base(name, func)
            return func
        return decorator

    def user(self, user_key, create_when_not_exist=True):
        user = self.memory.user(user_key)
        if user is None and create_when_not_exist:
            user = self.memory.create(user_key, self.home.name)
        return user

    def route(self, data):
        user_key = data['user_key']
        action = data['content']
        user = self.user(user_key)
        current_state = user.current

        rule = self._find_rule(action, current_state)
        response = rule.func(data)

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

    def _find_rule(self, action, current_state):
        rule = self.rules.action(action).src(current_state).first()
        if rule is None:
            rule = self.rules.action('*').src(current_state).first()
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
