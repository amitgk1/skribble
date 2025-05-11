from dataclasses import dataclass

from shared.actions import Action


@dataclass
class TurnStartAction(Action):
    """
    for the active player the word will be as is, for others it will be a placeholder
    """

    word: str
    round: int
    time: int
