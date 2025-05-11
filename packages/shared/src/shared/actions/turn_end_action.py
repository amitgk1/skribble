from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from shared.actions.player_list_action import PlayerListAction


class TurnEndReason(StrEnum):
    TIMEOUT = "times up!"
    EVERYONE_GUESSED_CORRECTLY = "everyone guessed the word!"


@dataclass
class TurnEndAction(PlayerListAction):
    word: str
    reason: TurnEndReason
    player_score_update: dict[UUID, int]
