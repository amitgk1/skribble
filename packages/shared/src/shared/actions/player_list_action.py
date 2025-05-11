from dataclasses import dataclass

from shared.actions import Action
from shared.player import Player


@dataclass
class PlayerListAction(Action):
    players_list: list[Player]
