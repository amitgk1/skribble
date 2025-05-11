from dataclasses import dataclass

from shared.actions import Action


@dataclass
class WordPickedAction(Action):
    picked_word: str
