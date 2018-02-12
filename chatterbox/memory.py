import abc
import json
import redis
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


class RedisMemory(BaseMemory):
    def __init__(self):
        self.r = redis.StrictRedis()

    def user(self, user_key):
        obj = self.r.get(user_key)
        if obj is not None:
            user = User.from_json(obj)
            return user
        return None

    def create(self, user_key, home_name):
        user = User(user_key, home_name)
        self.save(user)
        return user

    def save(self, user):
        self.r.set(user.user_key, user.to_json())

    def delete(self, user):
        self.r.delete(user.user_key)


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


class Context:
    def __init__(self):
        self.generator = None
        self.destination = None
