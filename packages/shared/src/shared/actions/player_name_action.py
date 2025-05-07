from dataclasses import dataclass

from shared.actions import Action


@dataclass
class PlayerNameAction(Action):
    name: str
