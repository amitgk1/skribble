from dataclasses import dataclass

from shared.actions import Action


@dataclass
class UpdateWordAction(Action):
    word: str
