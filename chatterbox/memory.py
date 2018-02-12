import abc
import json
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
        del self.user_list[user.user_key]


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
