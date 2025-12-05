import pygame
import random

class Ring:
    def __init__(self, x, y, ring_type):
        """
        ring_type: 1, 2, 3, o 4 (corresponde a Ring_1.png, Ring_2.png, etc.)
        """
        self.ring_type = ring_type
        # Cargar todos los sprites para animacion
        self.sprites = []
        for i in range(1, 5):
            sprite = pygame.image.load(f"assets/images/Ring_{i}.png").convert_alpha()
            sprite = pygame.transform.scale(sprite, (40, 40))
            self.sprites.append(sprite)
        
        self.current_frame = 0  # Empezar con Ring_1
        self.animation_timer = 0
        self.animation_speed = 10  # Frames entre cambio de sprite
        self.image = self.sprites[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = random.randint(6, 10)

    def update(self):
        # Actualizar animacion
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.current_frame = (self.current_frame + 1) % 4  # Ciclar entre 0-3
            self.image = self.sprites[self.current_frame]
            self.animation_timer = 0
        
        # Mover hacia la izquierda
        self.rect.x -= self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)
