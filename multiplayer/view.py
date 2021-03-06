import os
import events
import pygame
import json
os.environ['SDL_VIDEO_CENTERED'] = '1'

black = (0, 0, 0)
white = (255, 255, 255)

class PygameView:

    def __init__(self, event_manager):
        self._event_manager = event_manager
        self._event_manager.register_listener(self)
        pygame.init()
        self._font = pygame.font.Font(None, 32)
        self._screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Hi-Snake")
        self._background = pygame.Surface(self._screen.get_size())
        self._background.fill(black)
        self._screen.blit(self._background, (0, 0))
        pygame.display.flip()

    def notify(self, event):
        if isinstance(event, events.ServerUpdateReceived):
            #Draw
            self._screen.blit(self._background, (0, 0))
            game_data = json.loads(event.get_json_string())
            snakes = game_data["snakes"]
            apples = game_data["apples"]
            players = game_data["players"]
            game_timer = game_data["game_timer"]
            snake_surface = pygame.Surface((600, 600))
            surfaceRect = pygame.Rect(0, 0, 600, 600)
            pygame.draw.rect(snake_surface, white, surfaceRect, 5)

            timer_text = self._font.render(str(game_timer), 1, white)
            timer_text_pos = timer_text.get_rect()
            timer_text_pos.centerx = snake_surface.get_rect().centerx
            timer_text_pos.top = 0

            snake_surface.blit(timer_text, timer_text_pos)

            for apple in apples:
                pygame.draw.circle(snake_surface, white, (apple[0] * 20 + 10, apple[1] * 20 + 10), 5)
            
            for idx, snake in enumerate(snakes):
                for part in snake:
                    snake_part = pygame.Rect(part[0]*20, part[1]*20, 20, 20)
                    pygame.draw.rect(snake_surface, pygame.Color(players[idx][1]), snake_part)
            
            score_surface = pygame.Surface((200, 600))

            #PLAYER 1
            p1_score_text = self._font.render(players[0][0] + "'s Score: " + str(players[0][2]), 1, pygame.Color(players[0][1]))
            p1_score_text_pos = p1_score_text.get_rect()
            p1_score_text_pos.centerx = score_surface.get_rect().centerx
            p1_score_text_pos.top = 25

            #PLAYER 2
            p2_score_text = self._font.render(players[1][0] + "'s Score: " + str(players[1][2]), 1, pygame.Color(players[1][1]))
            p2_score_text_pos = p2_score_text.get_rect()
            p2_score_text_pos.centerx = score_surface.get_rect().centerx
            p2_score_text_pos.top = 175

            #PLAYER 3
            p3_score_text = self._font.render(players[2][0] + "'s Score: " + str(players[2][2]), 1, pygame.Color(players[2][1]))
            p3_score_text_pos = p3_score_text.get_rect()
            p3_score_text_pos.centerx = score_surface.get_rect().centerx
            p3_score_text_pos.top = 325

            #PLAYER 4
            p4_score_text = self._font.render(players[3][0] + "'s Score: " + str(players[3][2]), 1, pygame.Color(players[3][1]))
            p4_score_text_pos = p4_score_text.get_rect()
            p4_score_text_pos.centerx = score_surface.get_rect().centerx
            p4_score_text_pos.top = 475

            score_surface.blit(p1_score_text, p1_score_text_pos)
            score_surface.blit(p2_score_text, p2_score_text_pos)
            score_surface.blit(p3_score_text, p3_score_text_pos)
            score_surface.blit(p4_score_text, p4_score_text_pos)
            
            if game_timer == 0:
                #print(players)
                # Sort the players by their score. Announce winner with highest score
                players.sort(key = lambda s: s[2], reverse = True)
                game_over_text = self._font.render("Game Over. " + players[0][0] + " Wins the Game!", 1, white)
                game_over_text_pos = game_over_text.get_rect()
                game_over_text_pos.centerx = snake_surface.get_rect().centerx
                game_over_text_pos.centery = snake_surface.get_rect().centery
                snake_surface.blit(game_over_text, game_over_text_pos)
            self._screen.blit(snake_surface, (0, 0))
            self._screen.blit(score_surface, (600, 0))
            pygame.display.flip()
        elif isinstance(event, events.QuitEvent):
            pygame.display.quit()
        elif isinstance(event, events.GameOverEvent):
            pygame.time.delay(5000)
            pygame.display.quit()