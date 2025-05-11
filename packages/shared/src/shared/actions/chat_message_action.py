from dataclasses import dataclass

from shared.actions import Action
from shared.chat_message import ChatMessage


@dataclass
class ChatMessageAction(Action):
    message: ChatMessage
