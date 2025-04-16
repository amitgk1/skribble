import threading


class ThreadSafeSet[T]:
    def __init__(self):
        self._set = set[T]()
        self._lock = threading.Lock()

    def add(self, item: T):
        with self._lock:
            self._set.add(item)

    def remove(self, item: T):
        with self._lock:
            self._set.remove(item)

    def discard(self, item: T):
        with self._lock:
            self._set.discard(item)

    def contains(self, item: T):
        with self._lock:
            return item in self._set

    def copy(self):
        with self._lock:
            return self._set.copy()

    def __iter__(self):
        with self._lock:
            return iter(self._set.copy())

    def __len__(self):
        with self._lock:
            return len(self._set)
