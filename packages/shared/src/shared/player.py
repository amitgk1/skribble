from dataclasses import dataclass, field
from uuid import UUID, uuid4

NAME_FALLBACK = "anonymous"


@dataclass
class Player:
    name: str
    id: UUID = field(default_factory=uuid4)
    score: int = 0
    is_owner: bool = False
    is_player_turn: bool = False

    def get_player_name(self, my_player_id: UUID):
        name = self.name or NAME_FALLBACK
        return name if self.id != my_player_id else f"{name} (you)"
