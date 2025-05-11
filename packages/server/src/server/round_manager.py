import socket
import threading
import time
from itertools import cycle
from math import floor

from shared.actions.choose_word_action import ChooseWordAction
from shared.actions.game_over_action import GameOverAction
from shared.actions.player_list_action import PlayerListAction
from shared.actions.turn_end_action import TurnEndAction, TurnEndReason
from shared.actions.turn_start_action import TurnStartAction
from shared.protocol import ActionProtocol

from server.server_state import ServerState
from server.turn import Turn
from server.words import WordManager, drawable_words


class RoundManager:
    def __init__(self, state: ServerState, max_rounds: int = 3, turn_timeout: int = 60):
        self.state = state
        self.max_rounds = max_rounds
        self.turn_timeout = turn_timeout
        self.word_manager = WordManager(drawable_words)
        self.round = 0
        self.players = self._player_iter()
        self.turn: Turn = None

    def set_turn_word(self, word: str):
        self.word_manager.pick_word(word)
        self.turn.word = word
        placeholder = " ".join(["_" for i in word])
        for sock, p in self.state.players.items():
            action = TurnStartAction(placeholder, self.round, self.turn_timeout)
            if sock == self.turn.active_player:
                action.word = word
            ActionProtocol.send_batch(sock, action)
        self.turn.timer.start()
        self.turn.start_time = time.time()

    def check_guess(self, sock: socket.socket, guess: str) -> bool:
        if guess == self.turn.word:
            self.turn.player_score_update[sock] = self._calculate_score()
            if self.is_turn_finished():
                self.turn.timer.cancel()
            return True
        return False

    def is_turn_finished(self):
        return len(self.turn.player_score_update) == len(self.state.players) - 1

    def build_turn_end(self, reason: TurnEndReason):
        self.turn.player_score_update[self.turn.active_player] = min(
            self.turn_timeout, len(self.turn.player_score_update) * 10
        )
        self._apply_score_updates()
        threading.Timer(5, self._post_turn_end).start()
        return TurnEndAction(
            self.state.get_player_list(),
            self.turn.word,
            reason,
            player_score_update={
                self.state.players[sock].id: score
                for sock, score in self.turn.player_score_update.items()
            },
        )

    def _post_turn_end(self):
        if not next(self.players, None):
            for s in self.state.players.keys():
                ActionProtocol.send_batch(s, GameOverAction())

    def _calculate_score(self):
        """
        player turn score is calculated based on the remaining time from the turn clock
        """
        return self.turn_timeout - floor(time.time() - self.turn.start_time)

    def _apply_score_updates(self):
        for s, p in self.state.players.items():
            p.score += self.turn.player_score_update.get(s, 0)

    def _on_timeout(self):
        turn_end_action = self.build_turn_end(TurnEndReason.TIMEOUT)
        print("sending turn end action", turn_end_action)
        for s, p in self.state.players.items():
            ActionProtocol.send_batch(s, turn_end_action)

    def _player_iter(self):
        for i, p in enumerate(cycle(self.state.players.items())):
            self.round = (i // len(self.state.players)) + 1
            if self.round > self.max_rounds:
                return

            for s, player in self.state.players.items():
                player.is_player_turn = p[0] == s
            self.turn = Turn(timer=threading.Timer(self.turn_timeout, self._on_timeout))
            self.turn.active_player = p[0]
            self._sendChooseWordAction()
            yield p

    def _sendChooseWordAction(self):
        choose_word_action = ChooseWordAction(self.word_manager.get_word_options())
        player_list_action = PlayerListAction(self.state.get_player_list())
        for s, p in self.state.players.items():
            actions = [player_list_action]
            if s == self.turn.active_player:
                actions.append(choose_word_action)
            ActionProtocol.send_batch(s, actions)
