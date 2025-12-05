import pygame
import random
from modules.obstacle import Obstacle
from modules.ring import Ring
from modules.heart import Heart

class GameManager:
    def __init__(self):
        self.score = 0
        self.distance = 0
        self.spawn_timer = 0
        self.spawn_interval = 120  # frames (más espaciado entre obstáculos)
        self.game_over = False
        self.rings_collected = 0
        self.ring_spawn_timer = 0
        self.ring_spawn_interval = 80  # frames entre grupos de anillos
        
        # Cargar sonido de recoleccion de anillo
        self.collect_sound = pygame.mixer.Sound("assets/sounds/collect_ring.mp3")
        # Cargar sonido de recoleccion de corazon
        try:
            self.collect_heart_sound = pygame.mixer.Sound("assets/sounds/collect_heart.mp3")
        except Exception:
            self.collect_heart_sound = None
        # Sonido de electrocutado al morir (opcional)
        try:
            self.electrified_sound = pygame.mixer.Sound("assets/sounds/electrified.wav")
        except Exception:
            self.electrified_sound = None
        
        # Sistema de corazones
        self.hearts_collected = 0
        self.hearts_for_power = 5  # Corazones necesarios para desbloquear poder
        self.heart_spawn_timer = 0
        self.heart_spawn_interval = 200  # frames entre spawns de corazones
        
        # Power especial "thank u next"
        self.power_active = False
        self.power_duration = 900  # 15 segundos a 60 FPS
        self.power_timer = 0

    def spawn_rings(self, rings):
        """Generar grupos aleatorios de anillos en patrones variados"""
        self.ring_spawn_timer += 1
        
        # Reducir intervalo durante poder especial para más anillos
        current_spawn_interval = self.ring_spawn_interval
        if self.power_active:
            current_spawn_interval = max(20, self.ring_spawn_interval // 2)  # Mitad del intervalo
        
        if self.ring_spawn_timer >= current_spawn_interval:
            # Patrones: linea horizontal, linea vertical, diagonal, grupito
            pattern = random.choice(['horizontal', 'vertical', 'diagonal', 'cluster'])
            
            # Mantener anillos dentro de limites visibles y por encima del suelo
            ring_min_y = 60
            ring_max_y = 440  # teniendo en cuenta altura del ring (~40) y ground_y=480
            start_y = random.randint(ring_min_y, ring_max_y)
            start_x = 800
            
            if pattern == 'horizontal':
                # L�nea horizontal de 3-4 anillos
                num_rings = random.randint(3, 4)
                for i in range(num_rings):
                    ring_type = random.randint(1, 4)
                    y = max(ring_min_y, min(start_y, ring_max_y))
                    rings.append(Ring(start_x + i * 60, y, ring_type))
            
            elif pattern == 'vertical':
                # L�nea vertical de 2-3 anillos
                num_rings = random.randint(2, 3)
                for i in range(num_rings):
                    ring_type = random.randint(1, 4)
                    y = start_y + i * 50
                    y = max(ring_min_y, min(y, ring_max_y))
                    rings.append(Ring(start_x, y, ring_type))
            
            elif pattern == 'diagonal':
                # Diagonal de 3 anillos
                for i in range(3):
                    ring_type = random.randint(1, 4)
                    y = start_y - i * 50
                    y = max(ring_min_y, min(y, ring_max_y))
                    rings.append(Ring(start_x + i * 50, y, ring_type))
            
            elif pattern == 'cluster':
                # Grupito de 4-5 anillos
                num_rings = random.randint(4, 5)
                for _ in range(num_rings):
                    ring_type = random.randint(1, 4)
                    offset_x = random.randint(-40, 40)
                    offset_y = random.randint(-40, 40)
                    y = start_y + offset_y
                    y = max(ring_min_y, min(y, ring_max_y))
                    rings.append(Ring(start_x + offset_x, y, ring_type))
            
            self.ring_spawn_timer = 0
            # Reducir intervalo poco a poco para m�s frecuencia
            if self.ring_spawn_interval > 40:
                self.ring_spawn_interval -= 1

    def update_rings(self, rings):
        """Actualizar posicion de anillos y remover los que salen de pantalla"""
        for ring in rings[:]:
            ring.update()
            if ring.rect.right < 0:
                rings.remove(ring)

    def collect_ring(self):
        """Incrementar contador de anillos recolectados y reproducir sonido"""
        self.rings_collected += 1
        self.collect_sound.play()

    def spawn_hearts(self, hearts):
        """Generar corazones esporodicamente o en patrones durante el poder"""
        self.heart_spawn_timer += 1
        
        # Durante poder especial: generar patrones de corazones
        if self.power_active:
            if self.heart_spawn_timer >= 40:  # Spawn cada 40 frames durante poder
                # Patrón: línea diagonal de corazones
                pattern = random.choice(['diagonal', 'vertical', 'horizontal'])
                start_y = random.randint(100, 400)
                
                if pattern == 'diagonal':
                    for i in range(4):
                        hearts.append(Heart(800 + i * 80, start_y - i * 60))
                elif pattern == 'vertical':
                    for i in range(3):
                        hearts.append(Heart(800, start_y + i * 80))
                elif pattern == 'horizontal':
                    for i in range(4):
                        hearts.append(Heart(800 + i * 80, start_y))
                
                self.heart_spawn_timer = 0
            return
        
        # Modo normal: generar un único corazón esporádicamente
        if self.heart_spawn_timer >= self.heart_spawn_interval:
            # Generar un único corazón en posición aleatoria
            start_y = random.randint(100, 500)
            hearts.append(Heart(800, start_y))
            self.heart_spawn_timer = 0
            # Aumentar espaciado entre spawns (corazones raramente aparecen)
            if self.heart_spawn_interval < 300:
                self.heart_spawn_interval += 5

    def update_hearts(self, hearts):
        """Actualizar posicion de corazones y remover los que salen de pantalla"""
        for heart in hearts[:]:
            heart.update()
            if heart.rect.right < 0:
                hearts.remove(heart)

    def collect_heart(self):
        """Recolectar corazon e intentar activar poder especial"""
        self.hearts_collected += 1
        # Reproducir sonido de recoleccion
        if self.collect_heart_sound:
            try:
                self.collect_heart_sound.play()
            except Exception:
                pass
        # Si se alcanzaron 5 corazones, activar poder especial
        if self.hearts_collected >= self.hearts_for_power and not self.power_active:
            self.activate_power()

    def activate_power(self):
        """Activar poder especial 'thank u next'"""
        self.power_active = True
        self.power_timer = 0
        self.hearts_collected = 0  # Resetear contador de corazones

    def update_power(self, hearts=None):
        """Actualizar duración del poder especial"""
        if self.power_active:
            self.power_timer += 1
            # Limpiar corazones 150 frames antes de que se acabe el poder (2.5 segundos)
            if hearts is not None and self.power_timer >= (self.power_duration - 150):
                hearts.clear()
            if self.power_timer >= self.power_duration:
                self.power_active = False
                self.power_timer = 0

    def spawn_obstacles(self, obstacles):
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            # Elegir patrón de aparición para hacer más variedad: single, horizontal, vertical, diagonal, cluster
            pattern = random.choice(['single', 'horizontal', 'vertical', 'diagonal', 'cluster'])

            # Ocasionalmente elegir patrones más densos; mantener baja probabilidad
            if random.random() < 0.10:
                pattern = random.choice(['diagonal', 'cluster'])

            start_x = 800
            # Generar según patrón
            if pattern == 'single':
                obs = Obstacle()
                obstacles.append(obs)

            if pattern == 'horizontal':
                # Línea horizontal de 2-3 obstáculos con pequeñas diferencias en x
                count = random.randint(2, 3)
                base_y = random.randint(80, 360)
                for i in range(count):
                    obs = Obstacle()
                    obs.rect.x = start_x + i * 140
                    obs.rect.y = max(60, base_y + random.randint(-20, 20))
                    obstacles.append(obs)

            elif pattern == 'vertical':
                # Torre vertical de 2 obstáculos (reducido para menor densidad vertical)
                count = 2
                x_pos = start_x + random.randint(0, 100)
                base_y = random.randint(80, 220)
                for i in range(count):
                    obs = Obstacle()
                    obs.rect.x = x_pos
                    obs.rect.y = base_y + i * (obs.rect.height + 8)
                    obstacles.append(obs)

            elif pattern == 'diagonal':
                # Diagonal descendente o ascendente (2-4 obstáculos)
                count = random.randint(2, 4)
                base_y = random.randint(80, 300)
                direction = random.choice([-1, 1])
                for i in range(count):
                    obs = Obstacle()
                    obs.rect.x = start_x + i * 110
                    obs.rect.y = max(50, base_y + direction * i * 55)
                    obstacles.append(obs)

            elif pattern == 'cluster':
                # Grupo en área (2-4 obstáculos)
                num = random.randint(2, 4)
                base_y = random.randint(80, 360)
                for _ in range(num):
                    obs = Obstacle()
                    obs.rect.x = start_x + random.randint(-40, 120)
                    obs.rect.y = max(60, base_y + random.randint(-60, 60))
                    obstacles.append(obs)

            self.spawn_timer = 0
            # aumenta dificultad poco a poco
            if self.spawn_interval > 30:
                self.spawn_interval -= 1

    def update_obstacles(self, obstacles):
        for obs in obstacles[:]:
            obs.update()
            if obs.rect.right < 0:
                obstacles.remove(obs)

    def update_distance(self, speed):
        # Incrementar distancia basada en la velocidad del juego
        # Usamos un factor pequeño para que los "metros" avancen a ritmo realista
        self.distance += speed * 0.02
        self.score = int(self.distance)  # Mostrar metros como entero

    def reset(self):
        self.score = 0
        self.distance = 0
        self.spawn_timer = 0
        self.spawn_interval = 60
        self.game_over = False
        self.rings_collected = 0
        self.ring_spawn_timer = 0
        self.ring_spawn_interval = 80
        self.hearts_collected = 0
        self.heart_spawn_timer = 0
        self.heart_spawn_interval = 200
        self.power_active = False
        self.power_timer = 0
