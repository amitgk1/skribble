import logging
import random
import socket
import threading
from itertools import groupby
from time import sleep
from typing import Callable, Mapping

from shared.actions import Action
from shared.actions.chat_message_action import ChatMessageAction
from shared.actions.clear_canvas_action import ClearCanvasAction
from shared.actions.draw_action import DrawAction
from shared.actions.game_over_action import GameOverAction
from shared.actions.init_game_state_action import InitGameStateAction
from shared.actions.player_list_action import PlayerListAction
from shared.actions.player_name_action import PlayerNameAction
from shared.actions.start_game_action import StartGameAction
from shared.actions.turn_end_action import TurnEndReason
from shared.actions.work_picked_action import WordPickedAction
from shared.chat_message import ChatMessage
from shared.colors import GREEN
from shared.constants import SYSTEM_PLAYER_ID
from shared.player import Player
from shared.protocol import ActionProtocol

from server.round_manager import RoundManager
from server.server_state import ServerState

type OnActionCallable = Callable[[list[Action], socket.socket], None]


class Room:
    def __init__(self):
        """
        Initializes an actionsMap to associate specific action types with corresponding handler methods and calls the _init_room() method to set up the room
        """
        self.actionsMap: Mapping[Action, OnActionCallable] = {
            DrawAction: self._on_draw_action,
            PlayerNameAction: self._on_player_name_action,
            StartGameAction: self._on_start_game,
            ClearCanvasAction: self._forward,
            WordPickedAction: self._on_word_picked,
            ChatMessageAction: self._on_chat_message,
        }
        self._init_room()

    def _init_room(self):
        """
        Initializes the server's game state and round manager, and sets up the callback for handling game over events
        """
        self.state = ServerState()
        self.round_manager = RoundManager(self.state, self._on_game_over)

    def add_client(self, sock: socket.socket, addr):
        """
        Adds a new player to the game, sends the updated player list to them, and starts a new thread to handle their messages
        """
        self.state.players[sock] = Player(name="", is_owner=not len(self.state.players))
        self._forward(
            [PlayerListAction(players_list=self.state.get_player_list())], sock
        )
        t = threading.Thread(target=self._client_thread_main, args=[sock, addr])
        t.start()

    def remove_client(self, sock: socket.socket):
        """
        Disconnects a player, reassigns owner if needed, updates player list or ends game if state is invalid
        """
        sock.close()
        if sock in self.state.players:
            was_owner = self.state.players[sock].is_owner
            del self.state.players[sock]
            if was_owner and self.state.get_player_list():
                player = random.choice(self.state.get_player_list())
                player.is_owner = True
            if self._is_valid_state() or not self.state.is_playing:
                self._broadcast_player_list()
            else:
                self._on_game_over()

    def _on_draw_action(self, draw_actions: list[DrawAction], sock: socket.socket):
        """
        Saves incoming drawing actions for the current turn and forwards them to all other clients
        """
        self.round_manager.turn.draw_actions.extend(draw_actions)
        self._forward(draw_actions, sock)

    def _on_player_name_action(
        self, actions: list[PlayerNameAction], sock: socket.socket
    ):
        """
        Updates the player's name on the server and broadcasts the updated player list
        """
        self.state.players[sock].name = actions[-1].name
        self._broadcast_player_list()

    def _on_start_game(self, al: list[StartGameAction], sock: socket.socket):
        """
        Starts the game if the server state is valid, broadcasts the start, and begins the first round
        """
        if self._is_valid_state:
            self.state.is_playing = True
            self._forward(al, sock)
            next(self.round_manager.players)

    def _on_word_picked(self, al: list[WordPickedAction], sock: socket.socket):
        """
        Sets the chosen word for the current turn using the last received WordPickedAction
        """
        word = al[-1].picked_word
        self.round_manager.set_turn_word(word)

    def _on_chat_message(self, actions: list[ChatMessageAction], sock: socket.socket):
        """
        Handles a chat message, checks if it's a correct guess, updates the chat and sends updates (including possible turn end) to all players
        """
        message = actions[-1].message
        if self.round_manager.check_guess(sock, message.text):
            message = ChatMessage(
                SYSTEM_PLAYER_ID,
                f"{self.state.players[sock].get_player_name(None)} guessed the word!",
                GREEN,
            )
        self.state.chat_messages.append(message)
        actions_to_send = [ChatMessageAction(message)]

        if self.round_manager.is_turn_finished():
            actions_to_send.append(
                self.round_manager.build_turn_end(
                    TurnEndReason.EVERYONE_GUESSED_CORRECTLY
                )
            )
        for p_sock, player in self.state.players.items():
            ActionProtocol.send_batch(p_sock, actions_to_send)

    def _on_game_over(self):
        """
        Sends a GameOverAction to all clients, closes their connections after a short delay, and resets the game state
        """
        # dealing with multiple winners using groupby
        score, winners = next(
            groupby(self.state.players.values(), key=lambda p: p.score)
        )
        game_over_action = GameOverAction(score=score, winners=[p.id for p in winners])
        for s in self.state.players.keys():
            ActionProtocol.send_batch(s, game_over_action)
            sleep(2)
            s.close()
        self._init_room()

    def _is_valid_state(self):
        """
        Checks if the game has at least 2 players to be considered valid; returns False if not
        """
        if len(self.state.players) < 2:
            return False

    def _others(self, sock: socket.socket):
        """
        Returns an iterator over all players except the one associated with the given socket
        """
        return filter(lambda t: t[0] != sock, self.state.players.items())

    def _forward(self, actions_list: list[Action], sock: socket.socket):
        """
        Sends the provided actions_list to all players except the one associated with the given socket
        """
        for other_sock, other_player in self._others(sock):
            ActionProtocol.send_batch(other_sock, actions_list)

    def _broadcast_player_list(self):
        """
        Sends the updated list of players (plist) to all connected players
        """
        plist = self.state.get_player_list()
        for sock, player in self.state.players.items():
            ActionProtocol.send_batch(sock, PlayerListAction(players_list=plist))

    def _send_initial_game_state(self, sock: socket.socket):
        """
        Sends the initial game state (including player list, player ID, chat messages, and max rounds) to a specific player (sock)
        """
        plist = self.state.get_player_list()
        ActionProtocol.send_batch(
            sock,
            InitGameStateAction(
                players_list=plist,
                you=self.state.players[sock].id,
                chat_messages=self.state.chat_messages,
                max_rounds=self.round_manager.max_rounds,
            ),
        )

    def _client_thread_main(self, sock: socket.socket, addr):
        """
        Handles communication with a connected client. It sends the initial game state, processes incoming actions in batches, and manages exceptions or client disconnections, ensuring that the client is removed when the connection ends
        """
        logging.info("Got connection from %s", addr)
        self._send_initial_game_state(sock)
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
                        logging.warning("Unknown action type %s", action_type)
        except socket.error:
            logging.exception("Error handling client %s", addr)
        except (ConnectionResetError, BrokenPipeError):
            logging.exception("Client forcibly closed the connection")
        finally:
            logging.info("Connection closed from %s", addr)
            self.remove_client(sock)
