import events
import pygame


class Controller:
    def __init__(self, event_manager):
        self._event_manager = event_manager
        self._event_manager.register_listener(self)
        self._game_state = "run"

    def notify(self, event):
        ev = None
        if isinstance(event, events.GameOverEvent):
            self._game_state = "game_over"
        elif isinstance(event, events.ServerUpdateReceived):
            if self._game_state == "run":
                # Handle input events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        ev = events.QuitEvent()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            ev = events.MoveEvent("", "left")
                        elif event.key == pygame.K_RIGHT:
                            ev = events.MoveEvent("", "right")
                        elif event.key == pygame.K_UP:
                            ev = events.MoveEvent("", "up")
                        elif event.key == pygame.K_DOWN:
                            ev = events.MoveEvent("", "down")
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            ev = events.MouseEvent(event.pos)
            elif self._game_state == "game_over":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        ev = events.QuitEvent()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            ev = events.RestartEvent()
                            self._game_state = "run"
                        elif event.key == pygame.K_q:
                            ev = events.QuitEvent()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            ev = events.MouseEvent(event.pos)
        if ev:
            self._event_manager.post(ev)

