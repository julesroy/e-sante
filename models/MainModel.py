class MainModel:
    def __init__(self):
        self._counter = 0

    @property  # permet d'accéder à counter comme une propriété (model.counter au lieu de model.counter())
    def counter(self):
        return self._counter

    def increment_counter(self):
        self._counter += 1

    def reset_counter(self):
        self._counter = 0
