import abc
import json
from datetime import datetime
from types import SimpleNamespace


class BaseMemory(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def user(self, user_key):
        pass

    @abc.abstractmethod
    def create(self, user_key, current_state):
        pass

    @abc.abstractmethod
    def save(self, user):
        pass

    @abc.abstractmethod
    def delete(self, user):
        pass


class DictionaryMemory(BaseMemory):
    def __init__(self):
        self.user_list = dict()

    def user(self, user_key):
        return self.user_list.get(user_key)

    def create(self, user_key, home_name):
        self.user_list[user_key] = User(user_key, home_name)
        return self.user(user_key)

    def save(self, user):
        self.user_list[user.user_key] = user

    def delete(self, user):
        self.user_list.pop(user.user_key)


class TimeoutDictionaryMemory(BaseMemory):
    TIMEOUT = 10 * 60

    def __init__(self):
        self.user_list = dict()

    def user(self, user_key):
        if user_key in self.user_list:
            return self.user_list.get(user_key).get('user')
        return None

    def create(self, user_key, home_name):
        self.user_list[user_key] = {
            'user': User(user_key, home_name),
            'last_time': datetime.utcnow().timestamp(),
        }
        return self.user(user_key)

    def save(self, user):
        self.user_list[user.user_key] = {
            'user': user,
            'last_time': datetime.utcnow().timestamp(),
        }

    def delete(self, user):
        self.user_list.pop(user.user_key)

    def collect(self):
        now = datetime.utcnow().timestamp()

        def check(key):
            user = self.user_list.get(key)
            last_time = user.get('last_time')
            return now - last_time > self.TIMEOUT

        targets = filter(check, self.user_list)

        for key in list(targets):
            self.user_list.pop(key, None)


class User(SimpleNamespace):
    def __init__(self, user_key, current=None, previous=None):
        self.user_key = user_key
        self.previous = previous
        self.current = current

    def move(self, dest):
        self.previous = self.current
        self.current = dest
        return self

    def to_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, obj):
        user = User(**json.loads(obj))
        return user
