import pygame
import random

class Obstacle:
    def __init__(self):
        # Cargar imagen original y escalar manteniendo proporción
        img = pygame.image.load("assets/images/obstacle.png").convert_alpha()
        orig_w, orig_h = img.get_size()
        # Altura objetivo moderada para buena visibilidad sin ser demasiado grande
        target_h = 90
        # Calcular ancho proporcional
        target_w = max(30, int(orig_w * (target_h / orig_h)))
        scaled = pygame.transform.scale(img, (target_w, target_h))

        # Decide aleatoriamente si rotar este obstáculo (30% probabilidad)
        if random.random() < 0.3:
            # Rotación aleatoria entre -40 y 40 grados
            self.angle = random.randint(-40, 40)
            self.image = pygame.transform.rotate(scaled, self.angle)
        else:
            self.angle = 0
            self.image = scaled

        # Obtener rect después de la posible rotación
        self.rect = self.image.get_rect()
        self.rect.x = 800
        # Asegurar que el obstáculo quede dentro de la pantalla y por encima del suelo (ground_y = 480)
        ground_y = 480
        max_y = max(0, ground_y - self.rect.height)
        # Posición aleatoria en altura entre 60 y el máximo permitido
        self.rect.y = random.randint(60, max_y) if max_y > 60 else 60
        self.speed = random.randint(6, 10)

    def update(self):
        self.rect.x -= self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)
