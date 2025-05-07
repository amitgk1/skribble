from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Player:
    name: str
    id: UUID = field(default_factory=uuid4)
    score: int = 0
    is_owner: bool = False
    is_player_turn: bool = False
