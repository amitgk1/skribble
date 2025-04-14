import pickle
from typing import Self


class Action:
    def serialize(self):
        return pickle.dumps(self)

    def deserialize(msg: str) -> Self:
        return pickle.loads(msg)
