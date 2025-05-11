from dataclasses import dataclass

from shared.actions import Action


@dataclass
class ChooseWordAction(Action):
    options: list[str]
