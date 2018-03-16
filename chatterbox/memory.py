import abc
import atexit
import contextlib
import hashlib
import inspect
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


class SqliteMemory(BaseMemory):
    TIMEOUT = 10 * 60

    def __init__(self, frequency):
        self.path = SqliteMemory.db_path()
        self.init_db()
        self.frequency = frequency

        atexit.register(SqliteMemory.remove_db, self.path)

    @staticmethod
    def db_path(name=None):
        if name is None:
            frame = inspect.stack()[-1]
            file = frame.frame.f_locals.get('__file__', '.')
            path = str(pathlib.Path(file).resolve())
            name = hashlib.md5(path.encode()).hexdigest()
        temp = tempfile.gettempdir()
        path = pathlib.Path(temp, name)
        return path

    @staticmethod
    def remove_db(db=None):
        if db is None:
            db = SqliteMemory.db_path()
        try:
            db.unlink()
        except FileNotFoundError:
            pass

    @contextlib.contextmanager
    def cursor(self):
        con = sqlite3.connect(str(self.path))
        with contextlib.closing(con):
            with con:
                yield con.cursor()

    def init_db(self):
        SqliteMemory.remove_db(self.path)

        with self.cursor() as cur:
            cur.execute('''CREATE TABLE if not exists UserList (
                user_key text PRIMARY KEY,
                user text,
                last_time integer
            )''')

    def user(self, user_key):
        value = (user_key, )
        with self.cursor() as cur:
            cur.execute('''SELECT user
                FROM UserList
                WHERE user_key = ?
            ''', value)
            user = cur.fetchone()

        if user is not None:
            user = User.from_json(user[0])
        return user

    @count
    def create(self, user_key, current_state):
        value = (
            user_key,
            User(user_key, current_state).to_json(),
            now(),
        )
        with self.cursor() as cur:
            cur.execute('INSERT INTO UserList VALUES (?, ?, ?)', value)

        return self.user(user_key)

    @count
    def save(self, user):
        value = (
            user.to_json(),
            now(),
            user.user_key,
        )
        with self.cursor() as cur:
            cur.execute('''UPDATE UserList
                SET user = ?,
                    last_time = ?
                WHERE user_key = ?
            ''', value)

    @count
    def delete(self, user):
        value = (
            user.user_key,
        )
        with self.cursor() as cur:
            cur.execute('''DELETE FROM UserList
                WHERE user_key = ?
            ''', value)

    def collect(self):
        utcnow = now()
        value = (
            utcnow,
            self.TIMEOUT,
        )

        with self.cursor() as cur:
            cur.execute('''DELETE FROM UserList
                WHERE ? - last_time > ?
            ''', value)


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


available = {  # pylint: disable=invalid-name
    'dict': DictionaryMemory,
    'sqlite': SqliteMemory,
}
