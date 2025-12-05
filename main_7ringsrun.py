"""
7 RINGS RUN — Flujo y lógica

Presentación (resumen rápido)
- Endless runner lateral en 2D con Ariana; objetivo: correr infinito, esquivar obstáculos, recolectar anillos (monedas) y corazones.
- Estados: MENÚ → TIENDA → JUEGO → GAME OVER → MENÚ.
- Economía: los anillos recogidos al morir se guardan como monedas persistentes en SQLite para comprar/seleccionar skins.

Algoritmo/flujo principal
- Bucle de juego (60 FPS): procesa eventos, dibuja según estado y, en modo JUEGO, actualiza mundo y colisiones.
- Spawns: obstáculos y anillos aparecen con intervalos y patrones; corazones más raros y más frecuentes durante el poder.
- Colisiones: obstáculos → muerte; anillos → +1 moneda; corazones → progresan hacia poder especial; poder activa invencibilidad y más velocidad.
- Game Over: muestra botón Quit; R reinicia; al morir se guardan puntaje y anillos→monedas.

Esquema de estados (simplificado)
MENÚ -> (Play) -> JUEGO -> (muerte) -> GAME OVER -> (Quit/R) -> MENÚ
    \-> (Shop) -> TIENDA -> (ESC) -> MENÚ

Jugabilidad: cómo ganar / cómo se pierde
- Ganar: es un endless runner; “ganar” es sobrevivir y maximizar distancia/anillos. No hay final fijo.
- Perder: chocar con un obstáculo cuando no hay poder activo. Al morir se registra score y se acreditan anillos como monedas.
"""

import pygame
from modules.player import Player
from modules.obstacle import Obstacle
from modules.ring import Ring
from modules.heart import Heart
from modules.game_manager import GameManager
from modules.ui import draw_ui
from modules import db
from modules.menu import Menu, MenuState
from modules.shop import Shop

# Inicializar pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("7 Rings Run ")
clock = pygame.time.Clock()

# Cargar y establecer logo como icono de ventana
try:
    logo = pygame.image.load("assets/images/LOGO_7RINGS_RUN.png")
    pygame.display.set_icon(logo)
except Exception:
    pass

# Colores y fondo
PINK = (255, 182, 193)
background = pygame.image.load("assets/images/background.png").convert()
# No escalar la imagen, mantener su tamaño original
background_width = background.get_width()

# Cargar imagen de poder especial
try:
    thank_u_next_image = pygame.image.load("assets/images/thank_u_next.png").convert_alpha()
    thank_u_next_image = pygame.transform.scale(thank_u_next_image, (300, 150))
except Exception:
    thank_u_next_image = None

# Modulos principales
player = Player()
game = GameManager()
# Inicializar base de datos (crear tablas si no existen)
try:
    db.init_db()
except Exception:
    # Si hay problemas con la BD, no detendremos el juego; pero no persistiremos datos
    pass
# Cargar fuente Bodoni
try:
    font = pygame.font.Font("assets/fonts/BodoniXT.ttf", 24)
except Exception:
    try:
        font = pygame.font.SysFont("Bodoni MT", 24)
    except Exception:
        font = pygame.font.SysFont("arial", 24)

# Player DB id
player_id = None

# Menú y tienda
menu = Menu(WIDTH, HEIGHT)
shop = Shop(WIDTH, HEIGHT)
current_state = MenuState.MAIN_MENU

# Aplicar skin seleccionado al jugador
try:
    player.set_skin(shop.get_selected_skin_key())
except Exception:
    pass

# Musica
pygame.mixer.music.load("assets/sounds/music.mp3")
pygame.mixer.music.play(-1)

# Listas de obstaculos y anillos
obstacles = []
rings = []
hearts = []

# Variables para parallax scrolling
background_offset = 0
parallax_speed = 2
base_parallax_speed = 2  # Velocidad base

# Variables para animación de imagen de poder
power_image_timer = 0
power_image_fade_duration = 120  # 2 segundos a 60 FPS

running = True
while running:
    clock.tick(60)
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()[0]
    
    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Manejar menú principal
        if current_state == MenuState.MAIN_MENU:
            new_state = menu.handle_events([event], mouse_pos, mouse_pressed)
            if new_state != current_state:
                current_state = new_state
                if current_state == MenuState.SHOP:
                    # Refrescar monedas al entrar a la tienda
                    try:
                        shop.coins = shop.load_coins()
                    except Exception:
                        pass
        
        # Manejar tienda
        elif current_state == MenuState.SHOP:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    current_state = MenuState.MAIN_MENU
                # Selección/compra de skins con teclas numéricas 1-9
                if pygame.K_1 <= event.key <= pygame.K_9:
                    idx = event.key - pygame.K_1
                    ok, msg = shop.select_or_buy(idx)
                    if msg:
                        shop.set_message(msg)
                    if ok:
                        try:
                            player.set_skin(shop.get_selected_skin_key())
                        except Exception:
                            pass

    # Entradas
    keys = pygame.key.get_pressed()
    space_pressed = keys[pygame.K_SPACE]

    # MENÚ PRINCIPAL
    if current_state == MenuState.MAIN_MENU:
        menu.draw(screen, font)
        pygame.display.flip()
        continue
    
    # TIENDA
    elif current_state == MenuState.SHOP:
        shop.draw(screen, font)
        pygame.display.flip()
        continue
    
    # JUEGO EN EJECUCIÓN
    elif current_state != MenuState.GAME:
        pygame.display.flip()
        continue
    
    # Crear jugador automáticamente si no existe
    if current_state == MenuState.GAME and player_id is None:
        try:
            player_id = db.add_player("Player")
        except Exception:
            player_id = None

    # Si el juego NO está terminado, actualizar animaciones y lógica
    if not game.game_over:
        # Aumentar velocidad durante poder especial
        if game.power_active:
            parallax_speed = base_parallax_speed * 2.0  # 100% más rápido (el doble)
        else:
            parallax_speed = base_parallax_speed
        # Desplazar fondo
        background_offset -= parallax_speed
        if background_offset <= -background_width:
            background_offset = 0

        # Dibujar fondo con desplazamiento
        screen.blit(background, (background_offset, 0))
        screen.blit(background, (background_offset + background_width, 0))

        # Actualizar
        player.update(space_pressed)
        game.update_distance(parallax_speed)
        game.spawn_obstacles(obstacles)
        game.update_obstacles(obstacles)
        game.spawn_rings(rings)
        game.update_rings(rings)
        game.spawn_hearts(hearts)
        game.update_hearts(hearts)
        game.update_power(hearts)

        # Colisiones con obstáculos
        for obs in obstacles:
            if player.rect.colliderect(obs.rect):
                # Solo causar game over si el poder especial NO está activo (invencible)
                if not game.game_over and not game.power_active:
                    game.game_over = True
                    # Cambiar sprite a estado 'dead' y comenzar la caida
                    player.die()
                    # Guardar puntuación en la base de datos (si está disponible)
                    try:
                        db.add_score(player_id, game.score)
                        # Agregar anillos como monedas y actualizar tienda
                        new_coins = db.add_rings_as_coins(game.rings_collected)
                        shop.coins = new_coins
                    except Exception:
                        pass
                    # Reproducir sonido electrificado si está disponible
                    if getattr(game, 'electrified_sound', None):
                        try:
                            game.electrified_sound.play()
                        except Exception:
                            pass
        
        # Colisiones con anillos (recolectar)
        for ring in rings[:]:
            if player.rect.colliderect(ring.rect):
                game.collect_ring()
                rings.remove(ring)
        
        # Colisiones con corazones (recolectar)
        for heart in hearts[:]:
            if player.rect.colliderect(heart.rect):
                # Solo recolectar si el poder no está activo
                if not game.power_active:
                    game.collect_heart()
                hearts.remove(heart)
        
        # Dibujar entidades en juego activo
        player.draw(screen)
        for obs in obstacles:
            obs.draw(screen)
        for ring in rings:
            ring.draw(screen)
        for heart in hearts:
            heart.draw(screen)
        
        # Mostrar imagen de poder especial si está activo
        if game.power_active and thank_u_next_image:
            power_image_timer += 1
            # Calcular alpha para fade in (primeros 30 frames) y fade out (últimos 30 frames)
            if power_image_timer <= 30:
                # Fade in
                alpha = int((power_image_timer / 30) * 255)
            elif power_image_timer >= power_image_fade_duration - 30:
                # Fade out
                alpha = int(((power_image_fade_duration - power_image_timer) / 30) * 255)
            else:
                # Visible completamente
                alpha = 255
            
            # Crear copia con alpha
            thank_u_next_faded = thank_u_next_image.copy()
            thank_u_next_faded.set_alpha(alpha)
            # Centrar la imagen en la pantalla
            thank_u_next_rect = thank_u_next_faded.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(thank_u_next_faded, thank_u_next_rect)
        else:
            # Resetear timer cuando poder no está activo
            power_image_timer = 0
        
        # Aplicar tinte rosado si el poder está activo
        if game.power_active:
            pink_overlay = pygame.Surface((WIDTH, HEIGHT))
            pink_overlay.set_alpha(40)  # Transparencia del 40%
            pink_overlay.fill((255, 182, 193))  # Color rosa pastel
            screen.blit(pink_overlay, (0, 0))
    else:
        # Juego terminado: dibujar estado congelado (no actualizamos posiciones)
        screen.blit(background, (background_offset, 0))
        screen.blit(background, (background_offset + background_width, 0))
        # Actualizar la caída del sprite de derrota para que caiga al suelo
        player.update(False)
        player.draw(screen)
        for obs in obstacles:
            obs.draw(screen)
        for ring in rings:
            ring.draw(screen)
        for heart in hearts:
            heart.draw(screen)

    # Dibujar UI (mostrando metros, anillos, corazones y poder)
    draw_ui(screen, font, game.score, game.rings_collected, game.hearts_collected, game.power_active, game.power_timer, game.power_duration)

    # Game Over
    if game.game_over:
        text = font.render(" Game Over - Presiona R para reiniciar", True, (255, 255, 255))
        screen.blit(text, (WIDTH/2 - 200, HEIGHT/2))
        
        # Actualizar y dibujar botón Quit
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        menu.update_quit_button(mouse_pos)
        menu.draw_quit_button(screen)
        
        # Manejar input
        if keys[pygame.K_r]:
            game.reset()
            player.reset()
            obstacles.clear()
            rings.clear()
            hearts.clear()
            background_offset = 0
            current_state = MenuState.MAIN_MENU
        
        if menu.is_quit_clicked(mouse_pos, mouse_pressed):
            game.reset()
            player.reset()
            obstacles.clear()
            rings.clear()
            hearts.clear()
            background_offset = 0
            current_state = MenuState.MAIN_MENU

    pygame.display.flip()

pygame.quit()
