import pygame


from pygame.math import Vector2
from models import Asteroid, Spaceship
from utils import get_random_position, load_sprite, print_text


class Asteroids:
    def __init__(self):
        self._init_pygame()
        self.running = True
        self.screen_Width = 1920
        self.screen_Height = 1080
        self.screen = pygame.display.set_mode((self.screen_Width, self.screen_Height))
        self.background = load_sprite("background", False)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('VectorBattle-e9XO.ttf', 128)
        self.score_font = pygame.font.Font('VectorBattle-e9XO.ttf', 48)
        self.tutorial_font = pygame.font.Font('VectorBattle-e9XO.ttf', 24)
        self.message = ""
        self.MIN_ASTEROID_DISTANCE = 250
        self.asteroids = []
        self.bullets = []
        self.spaceship = Spaceship((self.screen_Width / 2, self.screen_Height / 2), self.bullets.append)
        self.state = "menu"
        self.menu_items = ["Play", "Quit"]
        self.selected_item = 0
        self.high_score = 0
        self.score = 0
        self.high_score_file = "high_score.txt"
        self.high_score_text = self.font.render(f"High Score: {self.high_score}", True, (255, 255, 255))
        self.lives_text = self.score_font.render(str(self.spaceship.lifes), True, (255, 255, 255))
        self.text = "While you are playing on the left top of the screen you can see your score. " \
                    "For every asteroid that you destroy or split you get 10 points. " \
                    "Below your score you can see amount of your lifes. " \
                    "After you collide with an asteroid you have 3 second protection. "
        self.lines = self.text.split(". ")
        self.hud_text = self.score_font.render("INFO", True, (255, 255, 255))

    def main_loop(self):
        self.running = True

        while self.running:
            self.clock.tick(60)
            self._handle_input()
            self._update()
            self._process_game_logic()
            self._draw()

        pygame.quit()

    def _init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Asteroids")

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_item = (self.selected_item - 1) % len(self.menu_items)
                elif event.key == pygame.K_DOWN:
                    self.selected_item = (self.selected_item + 1) % len(self.menu_items)
                elif event.key == pygame.K_RETURN:

                    if self.menu_items[self.selected_item] == "Play":
                        self.state = "playing"
                    elif self.menu_items[self.selected_item] == "Quit":
                        self.running = False

            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            elif (
                    self.spaceship
                    and self.state == "playing"
                    and event.type == pygame.KEYDOWN
                    and event.key == pygame.K_SPACE

            ):
                self.spaceship.shoot()

        is_key_pressed = pygame.key.get_pressed()

        if self.spaceship and self.state == "playing":
            if is_key_pressed[pygame.K_RIGHT]:
                self.spaceship.rotate(clockwise=True)
            elif is_key_pressed[pygame.K_LEFT]:
                self.spaceship.rotate(clockwise=False)
            if is_key_pressed[pygame.K_UP]:
                self.spaceship.accelerate()
            else:
                self.spaceship.accelerating = False

    def _update(self):
        if self.spaceship:
            if not self.spaceship.accelerating:
                self.spaceship.sprite = self.spaceship.sprite_default

    def update_high_score(self):
        with open("high_score.txt", "r") as f:
            contents = f.read()
            if contents:
                self.high_score = int(contents)
            else:
                self.high_score = 0

            if self.score > self.high_score:
                self.high_score = self.score
            with open("high_score.txt", "w") as f:
                f.write(str(self.high_score))

            self.high_score_text = self.score_font.render(f"High Score: {self.high_score}", True, (255, 255, 255))

    def _process_game_logic(self):

        for game_object in self._get_game_objects():
            game_object.move(self.screen)

        if self.spaceship:
            for asteroid in self.asteroids:
                if asteroid.collides_with(self.spaceship):
                    if not self.spaceship.invincible:
                        self.spaceship.lifes -= 1
                        self.spaceship.velocity = [0, 0]
                        self.lives_text = self.score_font.render(str(self.spaceship.lifes), True, (255, 255, 255))
                        self.spaceship.position = Vector2(self.screen_Width / 2, self.screen_Height / 2)
                        self.spaceship.invincible_start_time = pygame.time.get_ticks()
                        if self.spaceship.lifes == 0:
                            self.spaceship = None
                            self.message = "GAME OVER"
                            break
                        else:
                            self.spaceship.invincible = True
                            self.invincible_time = 3000
                            self.spaceship.invincible_start_time = pygame.time.get_ticks()
                    break

        if self.spaceship and self.spaceship.invincible:
            if pygame.time.get_ticks() - self.spaceship.invincible_start_time > self.invincible_time:
                self.spaceship.invincible = False

        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                if asteroid.collides_with(bullet):
                    self.score += 10
                    self.update_high_score()
                    self.asteroids.remove(asteroid)
                    self.bullets.remove(bullet)
                    asteroid.split()
                    break

        for bullet in self.bullets[:]:
            if not self.screen.get_rect().collidepoint(bullet.position):
                self.bullets.remove(bullet)

        # Asteroids load and then spawn in waves

        if not self.asteroids and self.spaceship:
            if self.state == "playing":
                for _ in range(6):
                    while True:
                        position = get_random_position(self.screen)
                        if (
                                position.distance_to(self.spaceship.position)
                                > self.MIN_ASTEROID_DISTANCE
                        ):
                            break

                    self.asteroids.append(Asteroid(position, self.asteroids.append))

    def _draw(self):
        self.screen.fill((0, 0, 0))

        if self.state == "menu":
            for i, item in enumerate(self.menu_items):
                color = (255, 255, 255) if i == self.selected_item else (128, 128, 128)
                text = self.font.render(item, True, color)
                self.update_high_score()
                self.screen.blit(self.high_score_text, (15, 10))
                self.screen.blit(text, ((self.screen_Width - text.get_width()) / 2, (self.screen_Height / 2) + 128 * (i - len(self.menu_items) / 2)))

                self.screen.blit(self.hud_text, (15, 824))
                y = 896
                for line in self.lines:
                    rendered_line = self.tutorial_font.render(line + ".", True, (255, 255, 255))
                    self.screen.blit(rendered_line, (15, y))
                    y += 48

        elif self.state == "playing":
            self.score_text = self.score_font.render(str(self.score), True, (255, 255, 255))
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.score_text, (15, 10))
            self.screen.blit(self.lives_text, (15, 60))

            for game_object in self._get_game_objects():
                game_object.draw(self.screen)

            if self.message:
                print_text(self.screen, self.message, self.font)

            pass

        pygame.display.flip()

    def _get_game_objects(self):
        game_objects = [*self.asteroids, *self.bullets]

        if self.spaceship:
            game_objects.append(self.spaceship)

        return game_objects
