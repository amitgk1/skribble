from dataclasses import dataclass
from uuid import UUID

from shared.actions.player_list_action import PlayerListAction
from shared.chat_message import ChatMessage


@dataclass
class InitGameStateAction(PlayerListAction):
    you: UUID
    chat_messages: list[ChatMessage]
    max_rounds: int
