import pygame
from enum import Enum


class MenuState(Enum):
    MAIN_MENU = 1
    SHOP = 2
    GAME = 3
    NAME_ENTRY = 4


class Button:
    def __init__(self, x, y, image_path, width=150, height=60):
        """Crear un botón con imagen"""
        try:
            img = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(img, (width, height))
        except Exception:
            # Fallback: crear un rectángulo de color si no carga la imagen
            self.image = pygame.Surface((width, height))
            self.image.fill((100, 100, 100))
        
        self.rect = self.image.get_rect(x=x, y=y)
        self.hovered = False
    
    def update(self, mouse_pos):
        """Actualizar estado hover del botón"""
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def draw(self, screen):
        """Dibujar el botón con efecto hover"""
        img = self.image.copy()
        if self.hovered:
            # Efecto hover: aumentar brillo
            img.set_alpha(200)
        screen.blit(img, self.rect)
    
    def is_clicked(self, mouse_pos, mouse_pressed):
        """Verificar si el botón fue clickeado"""
        return self.rect.collidepoint(mouse_pos) and mouse_pressed


class Menu:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.state = MenuState.MAIN_MENU
        
        # Cargar fondo
        try:
            self.background = pygame.image.load("assets/images/Background.png").convert()
        except Exception:
            self.background = pygame.Surface((width, height))
            self.background.fill((20, 20, 40))
        
        # Cargar logo
        try:
            logo = pygame.image.load("assets/images/LOGO_7RINGS_RUN.png").convert_alpha()
            self.logo = pygame.transform.scale(logo, (150, 150))
        except Exception:
            self.logo = None
        
        # Botones del menú principal
        self.play_button = Button(
            self.width // 2 - 75,
            self.height // 2 - 50,
            "assets/images/ButtonPlayGame.png",
            width=150,
            height=60
        )
        self.shop_button = Button(
            self.width // 2 - 75,
            self.height // 2 + 30,
            "assets/images/ButtonShop.png",
            width=150,
            height=60
        )
        # Botón quit para pantalla de game over
        self.quit_button = Button(
            self.width // 2 - 75,
            self.height // 2 + 110,
            "assets/images/ButtonQuit.png",
            width=150,
            height=60
        )
    
    def handle_events(self, events, mouse_pos, mouse_pressed):
        """Manejar eventos del menú"""
        if self.state == MenuState.MAIN_MENU:
            self.play_button.update(mouse_pos)
            self.shop_button.update(mouse_pos)
            
            if self.play_button.is_clicked(mouse_pos, mouse_pressed):
                return MenuState.GAME
            if self.shop_button.is_clicked(mouse_pos, mouse_pressed):
                return MenuState.SHOP
        
        return self.state
    
    def draw(self, screen, font):
        """Dibujar menú principal"""
        # Dibujar fondo
        screen.blit(self.background, (0, 0))
        
        # Dibujar logo
        if self.logo:
            logo_x = self.width // 2 - self.logo.get_width() // 2
            logo_y = 30
            screen.blit(self.logo, (logo_x, logo_y))
        
        # Título
        title = font.render("7 RINGS RUN", True, (255, 105, 180))
        screen.blit(title, (self.width // 2 - title.get_width() // 2, 200))
        
        # Botones
        self.play_button.draw(screen)
        self.shop_button.draw(screen)
        
        # Instrucciones
        instructions = font.render("Presiona JUGAR para comenzar", True, (200, 200, 200))
        screen.blit(instructions, (self.width // 2 - instructions.get_width() // 2, self.height - 50))
    
    def draw_quit_button(self, screen):
        """Dibujar botón quit (para pantalla de game over)"""
        self.quit_button.draw(screen)
    
    def update_quit_button(self, mouse_pos):
        """Actualizar estado del botón quit"""
        self.quit_button.update(mouse_pos)
    
    def is_quit_clicked(self, mouse_pos, mouse_pressed):
        """Verificar si el botón quit fue clickeado"""
        return self.quit_button.is_clicked(mouse_pos, mouse_pressed)
