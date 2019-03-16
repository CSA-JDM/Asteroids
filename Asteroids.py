# Jacob Meadows
# Computer Programming II, 6th Period
# 05 March, 2019
"""
asteroids.py

Create a game in which users (space ship) on the left side of the screen are shooting asteroids (coming from right side
of the screen) for points. For each asteroid they get 100 points, they lose 100 for each that gets through. The user
starts with three lives, and loses one for each time they are hit. The user moves up and down and can shoot their laser
multiple times. It is up to you how many asteroids are on the screen at a time (must be more than one), how fast they
come, how fast they go, and where they come from (it can be random, following the user, etc). You need to show points
and lives on the screen as well. You need to keep track of high scores. Have some kind of leveling, either the asteroids
get bigger/faster/smarter/etc. I will post my helpful hints on a following announcement.
-------------------------
Use Steps
-background
-Object
-movement
-interaction
-points/punishment
-AI/Enemy movement

Kill the program whenever you can while coding! You want to find the errors early, not ignore them
Classes, create classes for EVERYTHING (enemy, user, weapons, inventory, etc)

Copyright (C) 2018 Jacob Meadows

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
import pygame
import sys
import math
import random


class App:
    def __init__(self):
        pygame.mixer.init(22100, -16, 2, 64)
        pygame.init()
        pygame.display.set_caption("Asteroids")
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()

        player_sprite = pygame.Surface((50, 50))
        pygame.draw.polygon(player_sprite, (255, 255, 255), ((49, 25), (10, 5), (10, 45)), 1)
        pygame.draw.lines(player_sprite, (255, 255, 255), False, ((49, 25), (1, 1), (49, 25), (1, 49)))
        player_sprite.set_colorkey((0, 0, 0))
        self.score_int = 0
        self.player = Player(
            app=self, image=player_sprite, tran_speed=300, rot_speed=2, shot_speed=4, lives=3, controls="mouse",
            rect=((self.screen.get_width() / 2) - (player_sprite.get_width() / 2),
                  (self.screen.get_height() / 2) - (player_sprite.get_height() / 2), player_sprite.get_size())
        )
        self.title_font = pygame.font.SysFont("Times New Roman", 60)
        self.text_font = pygame.font.SysFont("Times New Roman", 30)
        self.paragraph_font = pygame.font.SysFont("Times New Roman", 20)
        score_text = self.text_font.render(f"Score: {self.score_int}", True, (255, 255, 255), (0, 0, 0))
        lives_text = self.text_font.render(f"Lives: {self.player.lives}", True, (255, 255, 255), (0, 0, 0))
        self.score = ScreenObject(app=self, image=score_text, rect=(10, 10, 100, 40))
        self.lives = ScreenObject(app=self, image=lives_text, rect=(10, 50, 100, 40))
        self.game_sprites = pygame.sprite.LayeredUpdates()
        self.game_init()
        self.laser_surface = pygame.Surface((10, 3))
        self.laser_surface.fill((255, 0, 0), (1, 1, 49, 9))
        self.laser_surface.set_colorkey((0, 0, 0))
        asteroid_sprite = pygame.Surface((50, 50))
        pygame.draw.circle(asteroid_sprite, (255, 255, 255), (25, 25), 25)
        asteroid_sprite.set_colorkey((0, 0, 0))
        asteroid_counter = 0
        asteroid_health = 1
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000)
        blit_queue = []
        in_game = False

        while True:
            rects = [sprite.rect.copy() for sprite in self.game_sprites]
            asteroids = [sprite.rect.copy() for sprite in self.game_sprites if isinstance(sprite, Asteroid)]
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    with open("high_scores.txt", "w") as high_scores:
                        high_scores.write("\n".join([str(score) for score in current_scores]))
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.event.post(pygame.event.Event(pygame.QUIT, dict()))
                    elif event.key == pygame.K_SPACE:
                        if not in_game:
                            in_game = True
                            self.screen.fill((0, 0, 0))
                            self.game_animation = 0
                            pygame.display.flip()
                        if not self.player.lives > 0 and self.game_animation == 149:
                            self.screen.fill((0, 0, 0))
                            self.game_init()
                            self.game_animation = 0
                            asteroid_counter = 0
                            asteroid_health = 1
                            pygame.display.flip()
                            self.high_score_surfs = [pygame.Surface((200, 100)) for _ in range(20)]
                elif event.type == pygame.USEREVENT + 1:
                    for _ in range(4):
                        if len(asteroids) < 30 and in_game and self.player.lives > 0:
                            x = random.randint(0, self.screen.get_width())
                            rot = random.randint(0, 100)
                            temp_rect = pygame.Rect(x, -50, 50, 50)
                            while temp_rect.collidelist([sprite.rect.copy() for sprite in self.game_sprites]) != -1:
                                x = random.randint(0, self.screen.get_width())
                                temp_rect = pygame.Rect(x, -50, 50, 50)
                            asteroid = Asteroid(app=self, image=asteroid_sprite, rect=(x, -50, 50, 50), rot=rot,
                                                tran_speed=100, health=asteroid_health)
                            self.game_sprites.add(asteroid)
                            asteroid_counter += 1
                        if asteroid_counter >= 30 and asteroid_health < 5:
                            asteroid_counter -= 20
                            asteroid_health += 1
                elif event.type == pygame.USEREVENT + 2:
                    if len(blit_queue) > 0:
                        self.screen.blit(*blit_queue[0])
                        del blit_queue[0]
                    else:
                        pygame.time.set_timer(pygame.USEREVENT + 2, 0)
            if not in_game:
                if self.game_animation == 0:
                    self.game_sprites.draw(self.screen)
                    bg = pygame.Surface(self.screen.get_size())
                    bg.set_alpha(127)
                    bg.fill((0, 0, 0))
                    self.screen.blit(bg, (0, 0))
                    scores_text = self.title_font.render("Asteroids", True, (255, 255, 255), (0, 0, 0))
                    self.screen.blit(scores_text, ((self.screen.get_width() / 2) - (scores_text.get_width() / 2), 60))
                    intro_text = "How to Play:\n" \
                                 "* Controls:\n" \
                                 "  > Forward - W or Left Mouse Click\n" \
                                 "  > Backward - S or Left Mouse Click + Middle Mouse Click\n" \
                                 "  > Turn Left - A or Mouse Movement\n" \
                                 "  > Turn Right - D or Mouse Movement\n" \
                                 "  > Swap Player Controls - I\n" \
                                 "  > Quit the game - Esc\n" \
                                 "* Goal:\n" \
                                 "  > Your goal is to dodge and destroy as many asteroids as you possibly can.\n" \
                                 "* There are also attack speed drops that occasionally drop from the asteroids " \
                                 "after they've been destroyed."
                    for line in range(len(intro_text.split("\n"))):
                        start_text = self.paragraph_font.render(
                            intro_text.split("\n")[line], True, (255, 255, 255), (0, 0, 0)
                        )
                        self.screen.blit(start_text, ((self.screen.get_width() / 8), 180 + line * 35))
                    start_text = self.text_font.render(
                        "Press the space bar to start", True, (255, 255, 255), (0, 0, 0)
                    )
                    self.screen.blit(start_text, ((self.screen.get_width() / 2 - start_text.get_width() / 2), 600))
                    self.game_animation += 1
                pygame.display.flip()
            elif self.player.lives > 0:
                for rect in rects:
                    self.screen.fill((0, 0, 0), rect)
                self.game_sprites.update()
                self.game_sprites.draw(self.screen)
                for sprite in self.game_sprites:
                    rects.append(sprite.rect.copy())
                pygame.display.update(rects)
            else:
                if self.game_animation < 128:
                    bg = pygame.Surface(self.screen.get_size())
                    bg.set_alpha(1)
                    bg.fill((0, 0, 0))
                    self.screen.blit(bg, (0, 0))
                    self.game_animation += 1
                elif self.game_animation == 128:
                    scores_text = self.text_font.render("High Scores", True, (255, 255, 255), (0, 0, 0))
                    self.screen.blit(scores_text, ((self.screen.get_width() / 2) - (scores_text.get_width() / 2), 20))
                    pygame.time.set_timer(pygame.USEREVENT + 2, 100)
                    self.game_animation += 1
                elif 128 < self.game_animation < 148:
                    if self.score_int >= int(current_scores[self.game_animation - 129]):
                        current_scores[self.game_animation - 129], self.score_int = \
                            self.score_int, int(current_scores[self.game_animation - 129])
                    self.high_score_surfs[self.game_animation - 129].blit(
                        self.text_font.render(
                            str(current_scores[self.game_animation - 129]), True, (255, 255, 255)
                        ), (0, 0)
                    )
                    blit_queue.append((self.high_score_surfs[self.game_animation - 129],
                                      ((self.screen.get_width() / 2) - (scores_text.get_width() / 2),
                                      40 + 30 * (self.game_animation - 128))))
                    self.game_animation += 1
                elif self.game_animation == 148:
                    restart_text = self.text_font.render(
                        "Press the space bar to play again", True, (255, 255, 255), (0, 0, 0)
                    )
                    blit_queue.append((restart_text, ((self.screen.get_width() / 2) - (restart_text.get_width() / 2),
                                                      45 + 30 * (self.game_animation - 128))))
                    self.game_animation += 1
                pygame.display.flip()
            pygame.event.pump()
            self.clock.tick()
            # print(self.clock.get_fps())

    def game_init(self):
        self.game_sprites.empty()
        self.game_sprites.add(self.player, self.score, self.lives, layer=1)
        self.player.reset()
        self.score_int = 0
        self.score.image = self.text_font.render(f"Score: {self.score_int}", True, (255, 255, 255), (0, 0, 0))
        self.lives.image = self.text_font.render(f"Lives: {self.player.lives}", True, (255, 255, 255), (0, 0, 0))
        self.game_animation = 0
        self.high_score_surfs = [pygame.Surface((200, 40)) for _ in range(20)]


class ScreenObject(pygame.sprite.Sprite):
    def __init__(self, app=None, image=None, rect=None):
        super().__init__()
        if image:
            if isinstance(image, str):
                self.original_image = pygame.image.load(image).convert()
                self.image = pygame.image.load(image).convert()
            else:
                self.original_image = image
                self.image = image
            if rect:
                self.rect = pygame.Rect(*rect[:2], *self.image.get_size())
            else:
                self.rect = self.image.get_rect()
        else:
            if rect:
                self.rect = pygame.Rect(rect)
            else:
                self.rect = pygame.Rect(0, 0, 0, 0)
            self.original_image = pygame.Surface(self.rect.size)
            self.image = pygame.Surface(self.rect.size)
        self.original_rect = self.rect.copy()
        self.mask = pygame.mask.from_surface(self.image)
        self.app = app


class Entity(ScreenObject):
    def __init__(self, tran_speed=1, rot_speed=1, rot=0, **kwargs):
        super().__init__(**kwargs)
        self.tran_speed = tran_speed
        self.rot_speed = rot_speed
        self.dist = [0.0, 0.0]
        self.rot = rot

    def update(self, *args):
        if self.dist[0] < -1.0 or self.dist[0] > 1.0:
            self.rect.x += int(self.dist[0])
            self.dist[0] -= int(self.dist[0])
        if self.dist[1] < -1.0 or self.dist[1] > 1.0:
            self.rect.y += int(self.dist[1])
            self.dist[1] -= int(self.dist[1])
        self.image = pygame.transform.rotate(self.original_image, (-self.rot * (180 / math.pi)))
        rect_center = self.rect.center
        self.rect = pygame.Rect(*self.rect[:2], *self.image.get_size())
        self.rect.center = rect_center
        if self.rect.x < 0 - self.rect.width:
            self.rect.x = pygame.display.get_surface().get_width()
        if self.rect.x > pygame.display.get_surface().get_width():
            self.rect.x = 0 - self.rect.width
        if self.rect.y < 0 - self.rect.height:
            self.rect.y = pygame.display.get_surface().get_height()
        if self.rect.y > pygame.display.get_surface().get_height():
            self.rect.y = 0 - self.rect.height


class Player(Entity):
    def __init__(self, shot_speed=1, controls="keyboard", lives=3, **kwargs):
        super().__init__(**kwargs)
        self.controls = controls
        self.original_shot_speed = shot_speed
        self.shot_speed = shot_speed
        self.cool_down = 1.0
        self.original_lives = lives
        self.lives = lives
        self.ms_counter = 1000
        self.fire_sound = pygame.mixer.Sound("player_fire.wav")
        self.fire_sound.set_volume(.2)
        self.thrust_sound = pygame.mixer.Sound("player_thrust.wav")
        self.thrust_sound.set_volume(.2)
        self.channels = [pygame.mixer.Channel(0), pygame.mixer.Channel(1)]

    def reset(self):
        self.lives = self.original_lives
        self.shot_speed = self.original_shot_speed
        self.image = self.original_image.copy()
        self.rect = self.original_rect.copy()
        self.ms_counter = 1000
        self.cool_down = 1.0


    def update(self, *args):
        time_ms = self.app.clock.get_time()
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pos()
        net_tran_speed = self.tran_speed * (time_ms / 1000)
        net_rot_speed = self.rot_speed * (time_ms / 1000)
        orig_size = self.original_image.get_size()

        if keys[pygame.K_i] and self.ms_counter == 1000:
            if self.controls == "keyboard":
                self.controls = "mouse"
            elif self.controls == "mouse":
                self.controls = "keyboard"
            self.ms_counter -= time_ms
        elif self.ms_counter != 1000:
            if self.ms_counter <= 0:
                self.ms_counter = 1000
            elif self.ms_counter > 0:
                self.ms_counter -= time_ms
        if self.controls == "keyboard":
            if keys[pygame.K_a]:
                self.rot -= net_rot_speed
            if keys[pygame.K_d]:
                self.rot += net_rot_speed
            if keys[pygame.K_w]:
                self.dist[0] += net_tran_speed * math.cos(self.rot)
                self.dist[1] += net_tran_speed * math.sin(self.rot)
            if keys[pygame.K_s]:
                self.dist[0] -= net_tran_speed * math.cos(self.rot)
                self.dist[1] -= net_tran_speed * math.sin(self.rot)
            if keys[pygame.K_SPACE] and self.cool_down == 1.0:
                self.cool_down -= self.shot_speed * (time_ms / 1000)
                image = pygame.transform.rotate(self.original_image, (-self.rot * (180 / math.pi)))
                rect_center = self.rect.center
                rect = pygame.Rect(*self.rect[:2], *image.get_size())
                rect.center = rect_center
                laser_sprite = Laser(self, app=self.app, image=self.app.laser_surface,
                                     rect=pygame.Rect(rect.centerx + orig_size[0] / 2 * math.cos(self.rot),
                                                      rect.centery + orig_size[1] / 2 * math.sin(self.rot),
                                                      *self.app.laser_surface.get_size()))
                self.app.game_sprites.add(laser_sprite)
                self.fire_sound.play()
        elif self.controls == "mouse":
            mouse = math.atan2(mouse[1] - self.rect.centery, mouse[0] - self.rect.centerx)
            net_mouse = mouse - self.rot
            if net_mouse > math.pi:
                net_mouse -= math.pi * 2
            elif net_mouse < -math.pi:
                net_mouse += math.pi * 2
            self.rot += (net_mouse / abs(net_mouse)) * net_rot_speed
            if self.rot > math.pi:
                self.rot -= math.pi * 2
            elif self.rot < -math.pi:
                self.rot += math.pi * 2
            if pygame.mouse.get_pressed()[0] and self.app.player.lives > 0:
                if not pygame.mouse.get_pressed()[1]:
                    self.dist[0] += net_tran_speed * math.cos(self.rot)
                    self.dist[1] += net_tran_speed * math.sin(self.rot)
                else:
                    self.dist[0] -= net_tran_speed * math.cos(self.rot)
                    self.dist[1] -= net_tran_speed * math.sin(self.rot)
                self.channels[0].play(self.thrust_sound, -1)
            else:
                self.channels[0].stop()
            if pygame.mouse.get_pressed()[2] and self.cool_down == 1.0 and self.app.player.lives > 0:
                self.cool_down -= self.shot_speed * (time_ms / 1000)
                laser_surface = pygame.Surface((10, 3))
                laser_surface.fill((255, 0, 0), (1, 1, 49, 9))
                laser_surface.set_colorkey((0, 0, 0))
                orig_size = self.original_image.get_size()
                image = pygame.transform.rotate(self.original_image, (-self.rot * (180 / math.pi)))
                rect_center = self.rect.center
                rect = pygame.Rect(*self.rect[:2], *image.get_size())
                rect.center = rect_center
                laser_sprite = Laser(self, app=self.app, image=laser_surface,
                                     rect=pygame.Rect(rect.centerx + orig_size[0] / 2 * math.cos(self.rot),
                                                      rect.centery + orig_size[1] / 2 * math.sin(self.rot),
                                                      *laser_surface.get_size()))
                self.app.game_sprites.add(laser_sprite)
                self.channels[1].play(self.fire_sound)
        for sprite in self.app.game_sprites:
            if isinstance(sprite, Entity) and not isinstance(sprite, Player) and not isinstance(sprite, Laser) and \
                    not isinstance(sprite, Asteroid) and self.rect.colliderect(sprite.rect):
                    self.app.game_sprites.remove(sprite)
                    self.shot_speed += .1
        if self.cool_down <= 0:
            self.cool_down = 1.0
        if self.cool_down != 1.0:
            self.cool_down -= self.shot_speed * (time_ms / 1000)
        super().update()


class Laser(Entity):
    def __init__(self, player, **kwargs):
        super().__init__(**kwargs)
        self.player = player
        self.rot = self.player.rot
        self.tot_dist = 0

    def update(self, *args):
        time_ms = self.app.clock.get_time()
        net_tran_speed = self.player.tran_speed * 2 * (time_ms / 1000)
        self.dist[0] += net_tran_speed * math.cos(self.rot)
        self.dist[1] += net_tran_speed * math.sin(self.rot)
        self.tot_dist += math.sqrt(
            (net_tran_speed * math.cos(self.rot)) ** 2 + (net_tran_speed * math.sin(self.rot)) ** 2
        )
        super().update()
        if self.tot_dist > 1000:
            self.app.game_sprites.remove(self)


class Asteroid(Entity):
    def __init__(self, health=1, **kwargs):
        super().__init__(**kwargs)
        self.original_health = health
        self.health = health
        self.explosion_sound = pygame.mixer.Sound("asteroid_explosion.wav")
        self.explosion_sound.set_volume(.2)
        self.channel = pygame.mixer.Channel(3)
        self.speed_drop_image = pygame.Surface((20, 20))
        pygame.draw.rect(self.speed_drop_image, (255, 255, 255), (0, 0, 20, 20), 1)
        pygame.draw.lines(self.speed_drop_image, (255, 255, 255), False, ((15, 6), (15, 10), (15, 8), (13, 8), (17, 8)))
        self.speed_drop_image.blit(self.app.laser_surface, (2, 7))

    def update(self, *args):
        time_ms = self.app.clock.get_time()
        net_tran_speed = self.tran_speed * (time_ms / 1000)
        self.dist[0] += net_tran_speed * math.cos(self.rot)
        self.dist[1] += net_tran_speed * math.sin(self.rot)
        super().update()
        for sprite in self.app.game_sprites:
            if isinstance(sprite, Laser) and self.rect.colliderect(sprite.rect):
                if pygame.sprite.collide_mask(self, sprite):
                    self.health -= 1
                    if self.health == 0:
                        self.app.game_sprites.remove(self)
                        if random.randint(0, 100) > 75:
                            self.app.game_sprites.add(Entity(image=self.speed_drop_image, rect=self.rect.copy()))
                        self.app.score_int += 100
                        score_text = self.app.text_font.render(f"Score: {self.app.score_int}", True,
                                                               (255, 255, 255), (0, 0, 0))
                        self.app.score.image = score_text
                        self.app.score.rect = pygame.Rect(10, 10, *self.app.score.image.get_size())
                        self.channel.play(self.explosion_sound)
                    else:
                        self.original_image = pygame.Surface((50, 50))
                        shade_ratio = self.health / self.original_health
                        pygame.draw.circle(self.original_image,
                                           (255 * shade_ratio, 255 * shade_ratio, 255 * shade_ratio), (25, 25), 25)
                        self.original_image.set_colorkey((0, 0, 0))
                    self.app.game_sprites.remove(sprite)
                    break
            elif isinstance(sprite, Player) and self.rect.colliderect(sprite.rect):
                if pygame.sprite.collide_mask(self, sprite):
                    self.app.game_sprites.remove(self)
                    sprite.lives -= 1
                    lives_text = self.app.text_font.render(f"Lives: {sprite.lives}", True, (255, 255, 255), (0, 0, 0))
                    self.app.lives.image = lives_text
                    break


if __name__ == '__main__':
    try:
        with open("high_scores.txt", "r") as high_scores:
            current_scores = high_scores.read().split("\n")
    except FileNotFoundError:
        with open("high_scores.txt", "w") as high_scores:
            single_score = '0\n'
            high_scores.write(f"{single_score * 19}0")
        with open("high_scores.txt", "r") as high_scores:
            current_scores = high_scores.read().split("\n")
    App()
