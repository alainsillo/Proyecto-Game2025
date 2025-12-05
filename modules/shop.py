import pygame
from modules import db


class Skin:
    def __init__(self, name, cost, unlocked=False):
        self.name = name
        self.cost = cost
        self.unlocked = unlocked


class Shop:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        
        # Cargar fondo
        try:
            self.background = pygame.image.load("assets/images/Background.png").convert()
        except Exception:
            self.background = pygame.Surface((width, height))
            self.background.fill((20, 20, 40))
        
        # Skins disponibles (nombre, costo)
        self.skins = [
            Skin("Ariana Original", 0, True),  # Gratis y desbloqueado por defecto
            Skin("Ariana Gold", 500),
            Skin("Ariana Pink", 750),
            Skin("Ariana Diamond", 1000),
        ]
        
        # Cargar dinero del jugador desde la BD
        self.coins = self.load_coins()
    
    def load_coins(self):
        """Cargar monedas del jugador desde la BD"""
        try:
            coins_str = db.get_setting("player_coins", "0")
            return int(coins_str)
        except Exception:
            return 0
    
    def save_coins(self):
        """Guardar monedas en la BD"""
        try:
            db.set_setting("player_coins", str(self.coins))
        except Exception:
            pass
    
    def buy_skin(self, skin_index):
        """Intentar comprar un skin"""
        if skin_index < 0 or skin_index >= len(self.skins):
            return False, "Skin inválido"
        
        skin = self.skins[skin_index]
        
        if skin.unlocked:
            return False, "Ya lo tienes desbloqueado"
        
        if self.coins >= skin.cost:
            self.coins -= skin.cost
            skin.unlocked = True
            self.save_coins()
            return True, f"¡Compraste {skin.name}!"
        else:
            return False, f"Necesitas {skin.cost - self.coins} monedas más"
    
    def add_coins(self, amount):
        """Agregar monedas (por victorias en el juego)"""
        self.coins += amount
        self.save_coins()
    
    def draw(self, screen, font):
        """Dibujar la tienda"""
        # Fondo
        screen.blit(self.background, (0, 0))
        
        # Título
        title = font.render("TIENDA DE SKINS", True, (255, 105, 180))
        screen.blit(title, (self.width // 2 - title.get_width() // 2, 20))
        
        # Mostrar dinero del jugador
        coins_text = font.render(f"Monedas: {self.coins}", True, (255, 215, 0))
        screen.blit(coins_text, (20, 20))
        
        # Mostrar skins disponibles
        y = 80
        for i, skin in enumerate(self.skins):
            color = (100, 255, 100) if skin.unlocked else (255, 100, 100)
            status = "DESBLOQUEADO" if skin.unlocked else f"${skin.cost}"
            
            skin_text = font.render(f"{i+1}. {skin.name} - {status}", True, color)
            screen.blit(skin_text, (50, y))
            y += 40
        
        # Instrucciones
        instructions = font.render("Presiona ESC para volver al menú", True, (200, 200, 200))
        screen.blit(instructions, (self.width // 2 - instructions.get_width() // 2, self.height - 50))
