from pygame.math import Vector2
from pygame.transform import rotozoom
import pygame.time

from utils import get_random_velocity, load_sound, load_sprite, wrap_position

UP = Vector2(0, -1)


class GameObject:
    def __init__(self, position, sprite, velocity):
        self.position = Vector2(position)
        self.sprite = sprite
        self.radius = sprite.get_width() / 2
        self.velocity = Vector2(velocity)

    def draw(self, surface):
        blit_position = self.position - Vector2(self.radius)
        surface.blit(self.sprite, blit_position)

    def move(self, surface):
        self.position = wrap_position(self.position + self.velocity, surface)

    def collides_with(self, other_obj):
        distance = self.position.distance_to(other_obj.position)
        return distance < self.radius + other_obj.radius

class Spaceship(GameObject):


    def __init__(self, position, create_bullet_callback):
        self.thrust_sound = None
        self.create_bullet_callback = create_bullet_callback
        self.laser_sound = load_sound("laser")
        self.laser_sound.set_volume(0.1)
        self.invincible = False
        self.invincible_time = 0
        self.invincible_start_time = 0
        self.lifes = 3
        self.direction = Vector2(UP)
        self.MANEUVERABILITY = 3
        self.ACCELERATION = 0.15
        self.BULLET_SPEED = 15
        self.sprite_default = load_sprite("spaceship")
        self.sprite_accelerating = load_sprite("spaceship_ac")
        self.sprite = self.sprite_default
        self.accelerating = False

        super().__init__(position, self.sprite, Vector2(0))

    def rotate(self, clockwise=True):
        sign = 1 if clockwise else -1
        angle = self.MANEUVERABILITY * sign
        self.direction.rotate_ip(angle)

    def accelerate(self):
        self.sprite = self.sprite_accelerating
        self.thrust_sound = load_sound("thrust")
        self.thrust_sound.set_volume(0.1)
        self.thrust_sound.play()
        self.velocity += self.direction * self.ACCELERATION
        self.accelerating = True
        self.sprite = self.sprite_accelerating

    def shoot(self):
        bullet_velocity = self.direction * self.BULLET_SPEED + self.velocity
        bullet_position = self.position + self.direction * (self.sprite.get_height() / 2)
        bullet = Bullet(bullet_position, bullet_velocity)
        self.create_bullet_callback(bullet)
        self.laser_sound.play()

    def draw(self, surface):
        if self.invincible > 0:
            current_time = pygame.time.get_ticks()
            time_since_collision = current_time - self.invincible_start_time
            if time_since_collision % 500 > 250:
                return

        angle = self.direction.angle_to(UP)
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

class Asteroid(GameObject):
    def __init__(self, position):
        self.direction = Vector2(UP)
        super().__init__(
            position, load_sprite("asteroid"), get_random_velocity(1, 3)
        )

    def __init__(self, position, create_asteroid_callback, size=3):
        self.create_asteroid_callback = create_asteroid_callback
        self.size = size

        size_to_scale = {
            3: 1,
            2: 0.5,
            1: 0.25,
        }
        scale = size_to_scale[size]
        sprite = rotozoom(load_sprite("asteroid"), 0, scale)

        super().__init__(
            position, sprite, get_random_velocity(1, 3))

    def split(self):
        self.bang_sound = load_sound("bang")
        self.bang_sound.set_volume(0.1)
        self.bang_sound.play()
        if self.size > 1:
            for _ in range(2):
                asteroid = Asteroid(
                    self.position, self.create_asteroid_callback, self.size - 1
                )
                self.create_asteroid_callback(asteroid)


class Bullet(GameObject):
    def __init__(self, position, velocity):
        super().__init__(position, load_sprite("bullet"), velocity)

    def move(self, surface):
        self.position = self.position + self.velocity
