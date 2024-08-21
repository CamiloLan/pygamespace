import pygame
import sys
import os
import random

# Inicializar Pygame y configurar la pantalla
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Warships")
clock = pygame.time.Clock()

# Definir colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Ruta base de los assets
ASSETS_PATH = os.path.join(os.path.dirname(__file__), '../assets')

# Función para cargar y escalar imágenes
def load_image(name, width=None, height=None):
    path = os.path.join(ASSETS_PATH, name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Archivo no encontrado: {path}")
    image = pygame.image.load(path).convert_alpha()
    if width and height:
        image = pygame.transform.scale(image, (width, height))
    return image

# Cargar imágenes
player_image = load_image('player.png', width=50, height=38)
bullet_image = load_image('bullet.png', width=10, height=20)
enemy_image = load_image('enemy.png', width=40, height=30)
boss_image = load_image('boss.png', width=100, height=80)
boss_bullet_image = load_image('bullet.png', width=15, height=25)  # Puedes usar una imagen diferente para las balas del jefe
powerup_weapon_image = load_image('powerup_weapon.png', width=30, height=30)
powerup_shield_image = load_image('shield.png', width=30, height=30)

# Cargar sonidos
shoot_sound = pygame.mixer.Sound(os.path.join(ASSETS_PATH, 'shoot.wav'))
explosion_sound = pygame.mixer.Sound(os.path.join(ASSETS_PATH, 'explosion.wav'))
powerup_sound = pygame.mixer.Sound(os.path.join(ASSETS_PATH, 'powerup.wav'))
boss_shoot_sound = pygame.mixer.Sound(os.path.join(ASSETS_PATH, 'shoot.wav'))  # Puedes usar un sonido diferente para el jefe
pygame.mixer.music.load(os.path.join(ASSETS_PATH, 'background_music.wav'))
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)  # Repetir indefinidamente

# Fuente para texto
font = pygame.font.Font(None, 36)

# Clases del juego
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH / 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed_x = 0
        self.speed_y = 0
        self.health = 100
        self.powered_up = False
        self.shielded = False
        self.power_time = 0
        self.shield_time = 0

    def update(self):
        self.speed_x = 0
        self.speed_y = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speed_x = -5
        if keys[pygame.K_RIGHT]:
            self.speed_x = 5
        if keys[pygame.K_UP]:
            self.speed_y = -5
        if keys[pygame.K_DOWN]:
            self.speed_y = 5

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Mantener al jugador dentro de la pantalla
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

        # Verificar si el poder o escudo ha expirado
        if self.powered_up and pygame.time.get_ticks() > self.power_time:
            self.powered_up = False

        if self.shielded and pygame.time.get_ticks() > self.shield_time:
            self.shielded = False

    def shoot(self):
        shoot_sound.play()
        if self.powered_up:
            bullet_left = Bullet(self.rect.centerx - 15, self.rect.top)
            bullet_center = Bullet(self.rect.centerx, self.rect.top)
            bullet_right = Bullet(self.rect.centerx + 15, self.rect.top)
            all_sprites.add(bullet_left, bullet_center, bullet_right)
            bullets.add(bullet_left, bullet_center, bullet_right)
        else:
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)

    def powerup(self, type):
        if type == 'weapon':
            self.powered_up = True
            self.power_time = pygame.time.get_ticks() + 5000  # 5 segundos
        elif type == 'shield':
            self.shielded = True
            self.shield_time = pygame.time.get_ticks() + 5000  # 5 segundos

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_image
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x, y)
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        # Eliminar la bala si sale de la pantalla
        if self.rect.bottom < 0:
            self.kill()

class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = boss_bullet_image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x, y)
        self.speed_y = 7  # Velocidad de la bala del jefe

    def update(self):
        self.rect.y += self.speed_y
        # Eliminar la bala si sale de la pantalla
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed_y, speed_x):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = speed_y
        self.speed_x = speed_x

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        # Rebotar en los bordes horizontales
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speed_x *= -1
        # Eliminar si sale de la pantalla por abajo
        if self.rect.top > SCREEN_HEIGHT + 10:
            self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self, health, speed_y, speed_x):
        super().__init__()
        self.image = boss_image
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH / 2
        self.rect.y = -self.rect.height
        self.speed_y = speed_y
        self.health = health  # Salud del jefe ajustada por nivel
        self.max_health = self.health  # Para la barra de salud
        self.moving = False
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        if not self.moving:
            self.rect.y += self.speed_y
            if self.rect.top >= 50:
                self.moving = True
                self.speed_x = 3
        else:
            self.rect.x += self.speed_x
            if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
                self.speed_x *= -1

        # Disparar balas
        now = pygame.time.get_ticks()
        if now - self.last_shot > 1500:  # Dispara cada 1.5 segundos
            self.shoot()
            self.last_shot = now

        if self.health <= 0:
            explosion_sound.play()
            self.kill()

    def shoot(self):
        boss_shoot_sound.play()
        boss_bullet = BossBullet(self.rect.centerx, self.rect.bottom)
        all_sprites.add(boss_bullet)
        boss_bullets.add(boss_bullet)

    def draw_health_bar(self, surface):
        BAR_LENGTH = 200
        BAR_HEIGHT = 20
        fill = (self.health / self.max_health) * BAR_LENGTH
        outline_rect = pygame.Rect(300, 20, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pygame.Rect(300, 20, fill, BAR_HEIGHT)
        pygame.draw.rect(surface, RED, fill_rect)
        pygame.draw.rect(surface, WHITE, outline_rect, 2)

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, center, type):
        super().__init__()
        self.type = type
        if self.type == 'weapon':
            self.image = powerup_weapon_image
        elif self.type == 'shield':
            self.image = powerup_shield_image
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speed_y = 3

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Crear grupos de sprites
all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
bullets = pygame.sprite.Group()
boss_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
powerups = pygame.sprite.Group()
bosses = pygame.sprite.Group()

wave_count = 0  # Contador de oleadas
boss_spawned = False  # Indicador para controlar si un jefe ya ha sido generado
current_wave_enemies = 0  # Enemigos generados en la oleada actual
level = 1  # Nivel inicial
max_level = 5  # Nivel máximo
enemies_per_wave = 10 * level  # Ajustar según el nivel
enemy_speed_y = 2 * level  # Velocidad de enemigos ajustada por nivel
boss_health = 50 + (level * 50)  # Salud del jefe ajustada por nivel
boss_speed_y = 2 * level  # Velocidad del jefe ajustada por nivel

def spawn_enemy():
    global current_wave_enemies, boss_spawned
    if current_wave_enemies < enemies_per_wave and not boss_spawned:
        speed_x = random.randrange(-3, 3)
        enemy = Enemy(speed_y=enemy_speed_y, speed_x=speed_x)
        all_sprites.add(enemy)
        enemies.add(enemy)
        current_wave_enemies += 1

def spawn_boss():
    boss = Boss(health=boss_health, speed_y=boss_speed_y, speed_x=3)
    all_sprites.add(boss)
    bosses.add(boss)

def spawn_powerup(center):
    type = random.choice(['weapon', 'shield'])
    powerup = PowerUp(center, type)
    all_sprites.add(powerup)
    powerups.add(powerup)

def draw_health_bar(surface, x, y, percent):
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (percent / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surface, GREEN, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)

def draw_text(surface, text, size, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

def next_level():
    global level, enemies_per_wave, enemy_speed_y, boss_health, boss_speed_y, current_wave_enemies, boss_spawned
    if level < max_level:
        level += 1
    else:
        level = 1  # Reiniciar a nivel 1 después del último nivel
    
    enemies_per_wave = 10 * level
    enemy_speed_y = 2 * level
    boss_health = 50 + (level * 50)
    boss_speed_y = 2 * level
    current_wave_enemies = 0
    boss_spawned = False

score = 0

# Bucle principal del juego
running = True
while running:
    clock.tick(60)  # FPS
    # Eventos de entrada
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # Generar enemigos o jefe si la oleada terminó
    if len(enemies) == 0 and not boss_spawned:
        if current_wave_enemies >= enemies_per_wave:
            spawn_boss()
            boss_spawned = True
        else:
            spawn_enemy()

    # Actualizar sprites
    all_sprites.update()

    # Colisiones entre balas y enemigos
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        score += 10
        explosion_sound.play()
        if random.random() < 0.35:  # 35% de probabilidad de aparecer un power-up
            spawn_powerup(hit.rect.center)

    # Colisiones entre balas y jefe
    boss_hits = pygame.sprite.groupcollide(bosses, bullets, False, True)
    for boss in boss_hits:
        boss.health -= 1
        if random.random() < 0.125:  # 12.5% de probabilidad de aparecer un power-up durante el jefe
            spawn_powerup(boss.rect.center)
        if boss.health <= 0:
            score += 100
            boss.kill()
            next_level()  # Pasar al siguiente nivel

    # Colisiones entre balas del jefe y el jugador
    hits = pygame.sprite.spritecollide(player, boss_bullets, True)
    for hit in hits:
        if player.shielded:
            player.shielded = False
        else:
            player.health -= 20
            if player.health <= 0:
                running = False

    # Colisiones entre jugador y enemigos
    hits = pygame.sprite.spritecollide(player, enemies, True, pygame.sprite.collide_circle)
    for hit in hits:
        if player.shielded:
            player.shielded = False
        else:
            player.health -= 20
            if player.health <= 0:
                running = False

    # Colisiones entre jugador y powerups
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        powerup_sound.play()
        player.powerup(hit.type)

    # Dibujar / Renderizar
    screen.fill(BLACK)
    all_sprites.draw(screen)
    draw_text(screen, f"Score: {score}", 30, 10, 10)
    draw_text(screen, f"Level: {level}", 30, SCREEN_WIDTH - 150, 10)  # Mostrar el nivel actual
    draw_health_bar(screen, 10, 50, player.health)
    for boss in bosses:
        boss.draw_health_bar(screen)  # Dibujar la barra de vida del jefe
    if player.shielded:
        pygame.draw.circle(screen, BLUE, player.rect.center, player.rect.width // 2 + 5, 2)

    # Actualizar pantalla
    pygame.display.flip()

pygame.quit()
sys.exit()
