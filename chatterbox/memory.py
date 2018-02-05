class BaseMemory:
    def user(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        raise NotImplementedError


class DictionaryMemory(BaseMemory):
    def __init__(self):
        self.user_list = dict()

    def user(self, user_key):
        return self.user_list.get(user_key)

    def create(self, user_key, current_state):
        self.user_list[user_key] = User(current_state)
        return self.user(user_key)


class User:
    def __init__(self, current=None):
        self.previous = None
        self.current = current
        self.context = None

    def move(self, dest):
        self.previous = self.current
        self.current = dest
        return self
