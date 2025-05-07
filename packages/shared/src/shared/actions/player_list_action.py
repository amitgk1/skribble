from dataclasses import dataclass
from uuid import UUID

from shared.actions import Action
from shared.player import Player


@dataclass
class PlayerListAction(Action):
    players_list: list[Player]
    you: UUID
