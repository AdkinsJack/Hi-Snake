import pygame
import events
from random import randint
import json
import sqlite3 as lite
import hashlib
import base64
import os



db = lite.connect('login.db', check_same_thread=False)
query = db.cursor()

class Apple:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def get_pos(self):
        return (self._x, self._y)

class Snake:
    def __init__(self, x, y, direction):
        self._direction = direction
        self._body = [(x,y)]

        if direction == "left":
            self._body.append((x + 1, y))
        if direction == "right":
            self._body.append((x - 1, y))
        if direction == "up":
            self._body.append((x, y + 1))
        if direction == "down":
            self._body.append((x, y - 1))

    def get_head(self):
        return self._body[0]

    def get_body(self):
        return self._body

    def add_part(self, pos):
        self._body.insert(0, pos)

    def del_body(self):
        del_count = len(self._body) - 1
        self._body = self._body[:1]
        return del_count

    def del_parts(self, pos):
        del_count = len(self._body[self._body.index(pos, 1):])
        self._body = self._body[:self._body.index(pos, 1)]
        return del_count

    def reverse_dir(self):
        if self._direction == "left":
            self._direction = "right"
        elif self._direction == "right":
            self._direction = "left"
        elif self._direction == "up":
            self._direction = "down"
        elif self._direction == "down":
            self._direction = "up"

    def change_dir(self, direction):
        if not (self._direction == "left" and direction == "right" or self._direction == "right" and direction == "left" or self._direction == "up" and direction == "down" or self._direction == "down" and direction == "up"):
            self._direction = direction

    def update(self):
        if self._direction == "right":
            self._body.insert(0, (self._body[0][0] + 1, self._body[0][1]))
        elif self._direction == "left":
            self._body.insert(0, (self._body[0][0] - 1, self._body[0][1]))
        elif self._direction == "up":
            self._body.insert(0, (self._body[0][0], self._body[0][1] - 1))
        elif self._direction == "down":
            self._body.insert(0, (self._body[0][0], self._body[0][1] + 1))

        self._body.pop()


class Player:
    def __init__(self, name, color):
        self._name = name
        self._color = color
        self._score = 0
        self._alive = True

    def get_name(self):
        return self._name

    def get_score(self):
        return self._score

    def get_color(self):
        return self._color

    def increment_score(self):
        self._score += 1

    def update_score(self, score):
        self._score = score

    def get_alive(self):
        return self._alive

    def set_alive(self, state):
        self._alive = state
	

    def set_dead(self):
        self._name = "DEAD"
        self._color = "white"
        self._score = 0
        self._alive = False


class Game:
    def __init__(self, event_manager):
        self._event_manager = event_manager
        self._event_manager.register_listener(self)
        self._clock = pygame.time.Clock()
        self._players = []
        self._snakes = []
        self._avail_snakes = [Snake(25, 25, "up"), Snake(5, 25, "right"), Snake(25, 5, "left"), Snake(5, 5, "down")]
        self._apples = []
        self._apples = [Apple(randint(1, 29), randint(1, 29))]
        self._borders = [pygame.Rect(0, 0, 2, 600), pygame.Rect(0, 0, 800, 2), pygame.Rect(798, 0, 2, 600), pygame.Rect(0, 598, 800, 2)]
        self._is_running = True
        self._game_state = "run"
        self._game_timer = 800
        # print_db()

    def run(self):
        self._spawn_snakes()
        apple_timer = 0
        while self._game_timer:
            self._game_timer -= 1
            self._clock.tick(10)
            if self._game_state == "run":
                apple_timer += 1
                for idx, snake in enumerate(self._snakes):
                    if self._players[idx].get_alive():
                        snake.update()
                        if self._collideBorder(snake):
                            for p in range(int(snake.del_body()/2)):
                                self._spawn_apple(Apple(randint(1, 29), randint(1, 29)))
                            self._players[idx].update_score(0)
                        if self._collideBody(snake):
                            pass
                        if self._collideApple(snake):
                            self._players[idx].increment_score()
                if apple_timer == 25:
                    self._spawn_apple(Apple(randint(1, 29), randint(1, 29)))
                    apple_timer = 0

            self._event_manager.post(events.TickEvent())
        winner = None
        for player in self._players:
            if winner == None:
                winner = player
            else:
                if player.get_score() > winner.get_score():
                    winner = player
        sql = ("UPDATE Users SET h_score = h_score + 1 WHERE username = ?")
        query.execute(sql, [winner.get_name()])
        db.commit()
        #print(winner.get_name())
        self._event_manager.post(events.GameOverEvent())

    def _add_player(self, name, color):
        self._players.append(Player(name, color))

    def _remove_player(self, name):
        for idx, player in enumerate(self._players):
            if player.get_name() == name:
                player.set_dead()

    def _spawn_apple(self, apple):
        self._apples.append(apple)

    def _destroy_apples(self, apple):
        self._apples.remove(apple)

    def _spawn_snakes(self):
        for player in self._players:
            self._snakes.append(self._avail_snakes.pop())

    def _collideApple(self, snake):
        for apple in self._apples:
            if snake.get_head() == apple.get_pos():
                snake.add_part(apple.get_pos())
                self._destroy_apples(apple)
                return True
        return False

    def _collideBorder(self, snake):
        x = snake.get_head()[0]
        y = snake.get_head()[1]
        if x < 0:
            snake._direction = "right"
            return True
        if x > 29:
            snake._direction = "left"
            return True
        if y < 0:
            snake._direction = "down"
            return True
        if y > 29:
            snake._direction = "up"
            return True
        return False

    def _collideSelf(self, snake):  
        for part in snake.get_body()[1:]:
            if part == snake.get_head():
                return True
        return False

    def _collideBody(self, attacker):
        for idx, snake in enumerate(self._snakes):
            if self._players[idx].get_alive():
                for part in snake.get_body()[1:]:
                    if part == attacker.get_head():
                        for p in range(int(snake.del_parts(part)/2)):
                            self._spawn_apple(Apple(randint(1, 29), randint(1, 29)))
                        self._players[idx].update_score(len(snake.get_body()) - 1)
            else:
                snake.add_part((30, 30))
                for part in snake.get_body():
                    if part == attacker.get_head():
                        for p in range(int(snake.del_parts(part)/2)):
                            self._spawn_apple(Apple(randint(1, 29), randint(1, 29)))



    def notify(self, event):
        if isinstance(event, events.QuitEvent):
            self._remove_player(event.get_username())
        elif isinstance(event, events.GameOverEvent):
            self._game_state = "game_over"
        elif isinstance(event, events.MoveEvent):
            for idx, player in enumerate(self._players):
                name = player.get_name()
                if player.get_name() == event.get_username():
                    self._snakes[idx].change_dir(event.get_direction())
        elif isinstance(event, events.RestartEvent):
            self._snakes.clear()
            self._snakes.append(Snake(20, 15, "down"))
            self._game_state = "run"
            
        elif isinstance(event, events.JoinEvent):
            self._add_player(event.get_username(), event.get_color())

        elif isinstance(event, events.LeaveGame):
            self._remove_player(event.get_username())

    def get_snakes(self):
        return self._snakes

    def get_apples(self):
        return self._apples

    def get_apples_pos(self):
        pos_list = []
        for apple in self._apples:
            pos_list.append(apple.get_pos())
        return pos_list

    def get_game_state(self):
        return self._game_state

    def receive_message(self, message):
        loaded_json = json.loads(message)
        print(json.dumps(loaded_json, sort_keys=True, indent=4))

    def send_update(self):
        snake_list = []
        for snake in self._snakes:
            snake_list.append(snake.get_body())
        player_list = []
        for player in self._players:
            player_list.append([player.get_name(), player.get_color(), player.get_score()])
        while len(player_list) < 4:
            player_list.append(["N/A", "white", 0])

        json_string = json.dumps(dict([("snakes", snake_list),
                                       ("apples", self.get_apples_pos()),
                                       ("players", player_list),
                                       ("game_timer", self._game_timer)]))
        return json_string
