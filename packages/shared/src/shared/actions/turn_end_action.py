from dataclasses import dataclass

from shared.actions import Action


@dataclass
class TurnEndAction(Action):
    word: str
