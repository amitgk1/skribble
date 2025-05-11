from dataclasses import dataclass

from shared.actions import Action


@dataclass
class PickWordAction(Action):
    options: list[str]
