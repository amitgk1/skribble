import logging
import socket
import threading
from dataclasses import dataclass, field
from itertools import groupby
from typing import Callable, Mapping

from shared.actions import Action
from shared.actions.chat_message_action import ChatMessageAction
from shared.actions.clear_canvas_action import ClearCanvasAction
from shared.actions.draw_action import DrawAction
from shared.actions.pick_word_action import PickWordAction
from shared.actions.player_list_action import PlayerListAction
from shared.actions.player_name_action import PlayerNameAction
from shared.actions.start_game_action import StartGameAction
from shared.actions.update_word_action import UpdateWordAction
from shared.chat_message import ChatMessage
from shared.colors import GREEN
from shared.constants import SYSTEM_PLAYER_ID
from shared.player import Player
from shared.protocol import ActionProtocol

from server.words import WordManager, drawable_words

type OnActionCallable = Callable[[list[Action], socket.socket], None]


@dataclass
class Turn:
    word: str = None
    draw_actions: list[DrawAction] = field(default_factory=list)
    guessed_correctly: set[socket.socket] = field(default_factory=set)


@dataclass
class ServerState:
    players: dict[socket.socket, Player] = field(default_factory=dict)
    chat_messages: list[ChatMessage] = field(default_factory=list)


class Room:
    def __init__(self):
        self.actionsMap: Mapping[Action, OnActionCallable] = {
            DrawAction: self._on_draw_action,
            PlayerNameAction: self._on_player_name_action,
            StartGameAction: self._on_start_game,
            ClearCanvasAction: self._forward,
            UpdateWordAction: self._on_update_word,
            ChatMessageAction: self._on_chat_message,
        }
        self.state = ServerState()
        self.word_manager = WordManager(drawable_words)
        self.turn: Turn = None

    def add_client(self, sock: socket.socket, addr):
        self.state.players[sock] = Player(name="", is_owner=not len(self.state.players))
        t = threading.Thread(target=self._client_thread_main, args=[sock, addr])
        t.start()

    def remove_client(self, sock: socket.socket):
        sock.close()
        del self.state.players[sock]
        if self._is_valid_state():
            self._broadcast_player_list()
        else:
            # TODO: make last player winner!
            self._broadcast_player_list()
            pass

    def _on_draw_action(self, draw_actions: list[DrawAction], sock: socket.socket):
        self.turn.draw_actions.extend(draw_actions)
        self._forward(draw_actions, sock)

    def _on_player_name_action(
        self, actions: list[PlayerNameAction], sock: socket.socket
    ):
        self.state.players[sock].name = actions[-1].name

        self._broadcast_player_list()

    def _on_start_game(self, al: list[StartGameAction], sock: socket.socket):
        if self._is_valid_state:
            first_player_sock = list(self.state.players.keys())[0]
            self.state.players[first_player_sock].is_player_turn = True
            self.turn = Turn()
            self._broadcast_player_list()
            self._forward(al, sock)
            self._sendPickWordAction()

    def _sendPickWordAction(self):
        for sock, player in filter(
            lambda t: t[1].is_player_turn, self.state.players.items()
        ):
            action = PickWordAction(self.word_manager.get_word_options())
            ActionProtocol.send_batch(sock, [action])

    def _on_update_word(self, al: list[UpdateWordAction], sock: socket.socket):
        word = al[-1].word
        self.turn.word = word
        placeholder = " ".join(["_" for i in word])
        self._forward([UpdateWordAction(placeholder)], sock)

    def _on_chat_message(self, actions: list[ChatMessageAction], sock: socket.socket):
        message = actions[-1].message
        if self.turn.word == actions[-1].message.text:
            self.state.players[sock].score += 50
            self.turn.guessed_correctly.add(sock)
            message = ChatMessage(
                SYSTEM_PLAYER_ID,
                f"{self.state.players[sock].get_player_name(None)} guessed the word!",
                GREEN,
            )
        self.state.chat_messages.append(message)
        for p_sock, player in self.state.players.items():
            ActionProtocol.send_batch(p_sock, ChatMessageAction(message))

        if len(self.turn.guessed_correctly) == len(self.state.players) - 1:
            pass  # TODO: change to ScoreReveal

    def _is_valid_state(self):
        if len(self.state.players) < 2:
            return False

    def _others(self, sock: socket.socket):
        return filter(lambda t: t[0] != sock, self.state.players.items())

    def _forward(self, actions_list: list[Action], sock: socket.socket):
        for other_sock, other_player in self._others(sock):
            ActionProtocol.send_batch(other_sock, actions_list)

    def _broadcast_player_list(self):
        plist = list(self.state.players.values())
        for sock, player in self.state.players.items():
            ActionProtocol.send_batch(
                sock,
                [
                    PlayerListAction(
                        players_list=plist,
                        you=player.id,
                    )
                ],
            )

    def _client_thread_main(self, sock: socket.socket, addr):
        logging.info("Got connection from %s", addr)
        self._broadcast_player_list()
        try:
            while True:
                actions = ActionProtocol.recv_batch(sock)
                if not actions:
                    break

                for action_type, action_iter in groupby(actions, key=lambda a: type(a)):
                    action_list = list(action_iter)
                    if action_type in self.actionsMap:
                        self.actionsMap[action_type](action_list, sock)
                    else:
                        print(action_list)
                        logging.warning("Unknown action type %s", action_type)
        except socket.error:
            logging.exception("Error handling client %s", addr)
        except (ConnectionResetError, BrokenPipeError):
            logging.exception("Client forcibly closed the connection")
        finally:
            logging.info("Connection closed from %s", addr)
            self.remove_client(sock)
