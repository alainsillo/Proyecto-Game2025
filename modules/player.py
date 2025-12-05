import pygame

class Player:
    def __init__(self):
        self.current_skin = "original"
        # Cargar sprites por skin (se inicializa con la original)
        self._load_skin(self.current_skin)
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 480  # Posición inicial más baja
        self.vel_y = 0
        self.is_jumping = False
        self.gravity = 0.4  # Gravedad más lenta
        self.thrust = -0.2  # Propulsión más suave cuando se mantiene espacio (reducida)
        self.ground_y = 480  # Posición del suelo
        self.space_pressed_last_frame = False
        self.dead = False

    def update(self, space_pressed):
        # Si el jugador está muerto, ignorar controles y aplicar gravedad hasta el suelo
        if self.dead:
            self.vel_y += self.gravity
            # Limitar velocidad de caída por seguridad
            if self.vel_y > 12:
                self.vel_y = 12
            self.rect.y += self.vel_y
            if self.rect.y >= self.ground_y:
                self.rect.y = self.ground_y
                self.vel_y = 0
                # Al aterrizar, mostrar el sprite caído
                self.image = self.image_down
            return

        # Detectar si se presionó espacio en este frame
        space_just_pressed = space_pressed and not self.space_pressed_last_frame

        # Si se presiona espacio mientras cae, propulsarse hacia arriba (menos fuerza)
        if space_just_pressed:
            self.vel_y = -6  # Velocidad normal de propulsión (menos sensible)

        # Aplicar propulsión si está saltando y se mantiene espacio
        if space_pressed and self.vel_y < 0:  # Solo propulsionar mientras sube
            self.vel_y += self.thrust  # Propulsión hacia arriba

        # Aplicar gravedad (solo cuando no hay propulsión activa)
        if not space_pressed or self.vel_y >= 0:
            self.vel_y += self.gravity

        # Limitar la velocidad máxima hacia arriba para reducir sensibilidad
        if self.vel_y < -6:
            self.vel_y = -6

        self.rect.y += self.vel_y

        # Límite suelo - volver a la posición inicial
        if self.rect.y >= self.ground_y:
            self.rect.y = self.ground_y
            self.vel_y = 0
            self.is_jumping = False
            # Mostrar sprite de reposo en el suelo
            self.image = self.image_up
        else:
            # Mostrar sprite de vuelo cuando está en el aire
            self.image = self.image_fly

        # Iniciar salto cuando se presiona espacio y está en el suelo
        if not self.is_jumping and space_pressed:
            self.is_jumping = True
            self.vel_y = -8  # Velocidad inicial del salto

        # Límite techo: no rebotar si se mantiene espacio; permitir propulsión
        if self.rect.y <= 0:
            self.rect.y = 0
            if not space_pressed:
                # Solo empujar hacia abajo cuando NO se está presionando espacio
                self.vel_y = 0.5  # Pequeña velocidad hacia abajo al golpear techo

        # Guardar estado de la tecla para el siguiente frame
        self.space_pressed_last_frame = space_pressed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def die(self):
        """Cambiar sprite al de caída/derrota (efecto) y comenzar a caer."""
        if not self.dead:
            # Preferir imagen de 'dead' si existe, sino usar 'down'
            if self.image_dead:
                self.image = self.image_dead
            else:
                self.image = self.image_down
            self.dead = True
            # Asegurar que comience a caer hacia abajo
            self.vel_y = 2

    def reset(self):
        self.rect.y = self.ground_y
        self.vel_y = 0
        self.is_jumping = False
        self.space_pressed_last_frame = False
        # Volver al sprite vivo
        self.image = self.image_up
        self.dead = False

    def _load_skin(self, skin_key: str):
        """Cargar sprites según el skin seleccionado."""
        prefix = "ariana_original"
        if skin_key == "dangerous_woman":
            prefix = "ariana_dw"

        def load_scaled(path):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (60, 60))

        self.image_up = load_scaled(f"assets/images/{prefix}_up.png")
        self.image_fly = load_scaled(f"assets/images/{prefix}_fly.png")
        self.image_down = load_scaled(f"assets/images/{prefix}_down.png")
        try:
            self.image_dead = load_scaled(f"assets/images/{prefix}_dead.png")
        except Exception:
            self.image_dead = None
        self.image = self.image_up

    def set_skin(self, skin_key: str):
        """Aplicar un skin (cambia sprites al vuelo)."""
        if skin_key != self.current_skin:
            try:
                self._load_skin(skin_key)
                self.current_skin = skin_key
            except Exception:
                # Si falla la carga, mantener el skin actual
                pass
