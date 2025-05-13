from dataclasses import dataclass
from uuid import UUID

from shared.actions import Action


@dataclass
class GameOverAction(Action):
    score: int
    winners: list[UUID]
