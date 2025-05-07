import logging
import random
import socket
import threading
from dataclasses import dataclass, field
from itertools import groupby
from typing import Callable, Mapping

from shared.actions import Action
from shared.actions.draw_action import DrawAction
from shared.actions.player_list_action import PlayerListAction
from shared.actions.player_name_action import PlayerNameAction
from shared.player import Player
from shared.protocol import ActionProtocol

type OnActionCallable = Callable[[list[Action], socket.socket], bool]
"""
This helper callable type is for the on action function, called on every action type the server should
listen and do something for

The set of operation goes as follows:
1. if an action type is in the map  
    1.1. call the function  
        1.2 returned True - forward the actions  
        1.3 False - drop it, it was meant for the server only  
2. otherwise just forward it to the other clients (broadcast)
"""


@dataclass
class Turn:
    draw_actions: list[DrawAction] = field(default_factory=list)


class Room:
    players: dict[socket.socket, Player]
    round: int
    word: str
    drawing_client: socket.socket
    turn = Turn()

    def __init__(self):
        self.actionsMap: Mapping[Action, OnActionCallable] = {
            DrawAction: self._on_draw_action,
            PlayerNameAction: self._on_player_name_action,
        }
        self.players = dict()
        self.round = 0

    def add_client(self, sock: socket.socket, addr):
        self.players[sock] = Player(name="", is_owner=not len(self.players))
        t = threading.Thread(target=self._client_thread_main, args=[sock, addr])
        t.start()

    def remove_client(self, sock: socket.socket):
        sock.close()
        del self.players[sock]

    def _on_draw_action(self, draw_actions: list[DrawAction], _: socket.socket):
        self.turn.draw_actions.extend(draw_actions)
        return True

    def _on_player_name_action(
        self, actions: list[PlayerNameAction], sock: socket.socket
    ):
        self.players[sock].name = actions[-1].name

        self._broadcast_player_list()
        return False

    def _broadcast_player_list(self):
        plist = list(self.players.values())
        for sock, player in self.players.items():
            ActionProtocol.send_batch(
                sock,
                [
                    PlayerListAction(
                        players_list=plist,
                        you=player.id,
                    )
                ],
            )

    def _start_game(self):
        self.drawing_client = random.choice(self.clients)

    def _generateWord(self):
        self.word = "tree"

    def _others(self, sock: socket.socket):
        return filter(lambda t: t[0] != sock, self.players.items())

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
                        if not self.actionsMap[action_type](action_list, sock):
                            continue
                    logging.debug(
                        "forward action of type %s and length %d",
                        action_type,
                        len(action_list),
                    )
                    for other_sock, player in self._others(sock):
                        ActionProtocol.send_batch(other_sock, action_list)
        except socket.error:
            logging.exception("Error handling client %s", addr)
        except (ConnectionResetError, BrokenPipeError):
            logging.exception("Client forcibly closed the connection")
        finally:
            logging.info("Connection closed from %s", addr)
            self.remove_client(sock)
            logging.info("Sending final broadcast")
            self._broadcast_player_list()
