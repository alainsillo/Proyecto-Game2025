import pygame
from modules import db


class Skin:
    def __init__(self, name, cost, key, unlocked=False):
        self.name = name
        self.cost = cost
        self.key = key  # clave interna para cargar sprites
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
        
        # Skins disponibles (nombre, costo, clave interna)
        self.skins = [
            Skin("Ariana Original", 0, "original", True),  # Gratis y desbloqueado por defecto
            Skin("Dangerous Woman", 500, "dangerous_woman"),
            Skin("Próximamente", 750, "pink"),
            Skin("Próximamente", 1000, "diamond"),
        ]
        
        # Cargar dinero del jugador desde la BD
        self.coins = self.load_coins()
        # Skin seleccionado
        self.selected_skin_key = self.load_selected_skin()
        self.selected_index = self._find_skin_index(self.selected_skin_key)
        # Mensaje de feedback en tienda
        self.message = ""
        self.message_timer = 0  # frames restantes
    
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

    def load_selected_skin(self):
        """Cargar skin seleccionado desde la BD"""
        try:
            return db.get_setting("selected_skin", "original")
        except Exception:
            return "original"

    def save_selected_skin(self):
        try:
            db.set_setting("selected_skin", self.selected_skin_key)
        except Exception:
            pass

    def _find_skin_index(self, skin_key):
        for i, s in enumerate(self.skins):
            if s.key == skin_key:
                return i
        return 0
    
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

    def select_or_buy(self, skin_index):
        """Si está desbloqueado, seleccionar; si no, intentar comprar y luego seleccionar."""
        ok, msg = True, ""
        if skin_index < 0 or skin_index >= len(self.skins):
            return False, "Skin inválido"
        skin = self.skins[skin_index]
        if not skin.unlocked:
            ok, msg = self.buy_skin(skin_index)
            if not ok:
                return ok, msg
        # Seleccionar
        self.selected_skin_key = skin.key
        self.selected_index = skin_index
        self.save_selected_skin()
        return True, f"Skin seleccionado: {skin.name}"
    
    def add_coins(self, amount):
        """Agregar monedas (por victorias en el juego)"""
        self.coins += amount
        self.save_coins()
    
    def draw(self, screen, font):
        """Dibujar la tienda"""
        # Fondo
        screen.blit(self.background, (0, 0))

        # Refrescar monedas desde BD cada vez que se dibuja (por si cambiaron)
        try:
            self.coins = self.load_coins()
        except Exception:
            pass
        
        # Título
        title = font.render("TIENDA DE SKINS", True, (255, 105, 180))
        screen.blit(title, (self.width // 2 - title.get_width() // 2, 20))
        
        # Mostrar dinero del jugador
        coins_text = font.render(f"Monedas: {self.coins}", True, (255, 215, 0))
        screen.blit(coins_text, (20, 20))
        
        # Mostrar skins disponibles
        y = 80
        for i, skin in enumerate(self.skins):
            selected = (i == self.selected_index)
            color = (100, 255, 100) if skin.unlocked else (255, 100, 100)
            status = "DESBLOQUEADO" if skin.unlocked else f"${skin.cost}"
            if selected:
                status = "SELECCIONADA" if skin.unlocked else status
            skin_text = font.render(f"{i+1}. {skin.name} - {status}", True, color)
            screen.blit(skin_text, (50, y))
            y += 40
        
        # Instrucciones
        instructions = font.render("Presiona 1-4 para comprar/seleccionar, ESC para volver", True, (200, 200, 200))
        screen.blit(instructions, (self.width // 2 - instructions.get_width() // 2, self.height - 50))

        # Mensaje de feedback
        if self.message_timer > 0 and self.message:
            msg_surf = font.render(self.message, True, (255, 255, 0))
            screen.blit(msg_surf, (self.width // 2 - msg_surf.get_width() // 2, self.height - 90))
            self.message_timer -= 1

    def get_selected_skin_key(self):
        return self.selected_skin_key

    def set_message(self, text, duration_frames=180):
        """Mostrar mensaje temporal en la tienda."""
        self.message = text
        self.message_timer = duration_frames
