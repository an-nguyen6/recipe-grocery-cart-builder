class DataBase():

    def __init__(self):
        self._data = {}

    def get(self, key):
        return self._data[key]

    def put(self, key, value):
        self._data[key] = value

    def all(self):
        return self._data

    def delete(self, key):
        del self._data[key]