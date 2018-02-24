import abc
import atexit
import contextlib
import json
import pathlib
import sqlite3
import tempfile
from datetime import datetime
from functools import wraps
from types import SimpleNamespace


def count(func):
    call_count = 0

    @wraps(func)
    def decorator(*args, **kwargs):
        nonlocal call_count
        self = args[0]

        call_count += 1
        if call_count > self.frequency:
            self.collect()
            call_count = 0

        result = func(*args, **kwargs)
        return result
    return decorator


def now():
    return int(datetime.utcnow().timestamp())


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

    @abc.abstractmethod
    def collect(self):
        pass


class DictionaryMemory(BaseMemory):
    TIMEOUT = 10 * 60

    def __init__(self, frequency):
        self.user_list = dict()
        self.frequency = frequency

    def user(self, user_key):
        if user_key in self.user_list:
            return self.user_list.get(user_key).get('user')
        return None

    @count
    def create(self, user_key, current_state):
        self.user_list[user_key] = {
            'user': User(user_key, current_state),
            'last_time': now(),
        }
        return self.user(user_key)

    @count
    def save(self, user):
        self.user_list[user.user_key] = {
            'user': user,
            'last_time': now(),
        }

    @count
    def delete(self, user):
        self.user_list.pop(user.user_key)

    def collect(self):
        utcnow = now()

        def check(key):
            user = self.user_list.get(key)
            last_time = user.get('last_time')
            return utcnow - last_time > self.TIMEOUT

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
        return json.dumps(self.__dict__, ensure_ascii=False)

    @classmethod
    def from_json(cls, obj):
        user = User(**json.loads(obj))
        return user
