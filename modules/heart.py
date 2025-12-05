import pygame
import math
import random

class Heart:
    def __init__(self, x, y):
        """Corazón animado con movimiento en ondas"""
        self.sprites = []
        for i in range(1, 5):
            sprite = pygame.image.load(f"assets/images/heart_{i}.png").convert_alpha()
            sprite = pygame.transform.scale(sprite, (30, 30))
            self.sprites.append(sprite)
        
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 8  # Frames entre cambio de sprite
        self.image = self.sprites[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = random.randint(2, 4)
        
        # Movimiento en ondas
        self.wave_offset = random.uniform(0, 2 * math.pi)  # Fase inicial aleatoria
        self.wave_amplitude = 80  # Amplitud de la onda vertical
        self.wave_frequency = 0.02  # Frecuencia de la onda
        self.start_y = y
        self.distance_traveled = 0

    def update(self):
        # Actualizar animación
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.current_frame = (self.current_frame + 1) % 4
            self.image = self.sprites[self.current_frame]
            self.animation_timer = 0
        
        # Movimiento horizontal
        self.rect.x -= self.speed
        self.distance_traveled += self.speed
        
        # Movimiento en ondas (vertical)
        wave_y = math.sin(self.wave_offset + self.distance_traveled * self.wave_frequency) * self.wave_amplitude
        self.rect.y = int(self.start_y + wave_y)
        
        # Limitar altura de pantalla
        if self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.y > 450:  # Mantener por encima del suelo (480)
            self.rect.y = 450

    def draw(self, screen):
        screen.blit(self.image, self.rect)
