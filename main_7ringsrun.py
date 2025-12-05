import pygame
from modules.player import Player
from modules.obstacle import Obstacle
from modules.ring import Ring
from modules.heart import Heart
from modules.game_manager import GameManager
from modules.ui import draw_ui
from modules import db

# Inicializar pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("7 Rings Run ")
clock = pygame.time.Clock()

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

# Player name / DB id
player_name = ""
player_id = None
enter_name_mode = True

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
    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Name entry handling
        if enter_name_mode and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                player_name = player_name[:-1]
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                # Finalizar entrada de nombre
                name = player_name.strip() or "Player"
                try:
                    player_id = db.add_player(name)
                except Exception:
                    player_id = None
                enter_name_mode = False
            else:
                # Añadir carácter si es imprimible
                ch = event.unicode
                if ch.isprintable() and len(player_name) < 12:
                    player_name += ch

    # Entradas
    keys = pygame.key.get_pressed()
    space_pressed = keys[pygame.K_SPACE]

    # Si estamos en modo de entrada de nombre, mostrar UI y saltar lógica de juego
    if enter_name_mode:
        # Dibujar fondo estático
        screen.blit(background, (0, 0))
        title = font.render("Ingresa tu nombre (Enter para comenzar):", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
        # Caja de texto
        box_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 20, 400, 40)
        pygame.draw.rect(screen, (30, 30, 30), box_rect)
        pygame.draw.rect(screen, (255, 255, 255), box_rect, 2)
        name_surf = font.render(player_name or "", True, (255, 255, 255))
        screen.blit(name_surf, (box_rect.x + 8, box_rect.y + 6))
        pygame.display.flip()
        continue

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
        # Mostrar top scores
        try:
            top = db.get_top_scores(5)
            y = HEIGHT//2 + 40
            header = font.render("Top 5:", True, (255, 215, 0))
            screen.blit(header, (WIDTH//2 - 200, y))
            y += 30
            for score, name, created in top:
                line = font.render(f"{name or 'Player'} - {score}", True, (255, 255, 255))
                screen.blit(line, (WIDTH//2 - 200, y))
                y += 26
        except Exception:
            pass
        if keys[pygame.K_r]:
            game.reset()
            player.reset()
            obstacles.clear()
            rings.clear()
            hearts.clear()
            background_offset = 0

    pygame.display.flip()

pygame.quit()
