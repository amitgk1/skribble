import queue


class GameState:
    def __init__(self):
        self.running = True
        self.pending_draw_lines = queue.Queue()
