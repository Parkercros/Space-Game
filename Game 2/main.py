import sys
import random
import pygame.font
import pygame.mixer

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# display
WIDTH, HEIGHT = 1600, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("asteroids")

# Load assets
spaceship_img = pygame.image.load('assets/spaceship.png')
asteroid_img = pygame.image.load('assets/asteroid.png').convert_alpha()
game_over_img = pygame.image.load('assets/game_over.png')
game_over_img = pygame.transform.scale(game_over_img, (WIDTH, HEIGHT))
shoot_sound = pygame.mixer.Sound('assets/laser.mp3')
background_img = pygame.image.load('assets/gamebackground.jpg')
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

game_over_font = pygame.font.Font(None, 50)
background_music = 'assets/music.mp3'
pygame.mixer.music.load(background_music)
pygame.mixer.music.play(-1)
projectile_img = pygame.image.load('assets/projectile.png')
game_over_sound = pygame.mixer.Sound('assets/gameover.mp3')


# Score and level system
score = 0
level = 1
score_font = pygame.font.Font(None, 36)
score_text = score_font.render(f"Score: {score}", True, (255, 255, 255))
level_text = score_font.render(f"Level: {level}", True, (255, 255, 255))

def update_level(score):
    return 1 + score // 10

def update_asteroid_speed(level):
    return random.randint(2, 6) * level

# Spaceship
class Spaceship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = spaceship_img
       
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 60)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = projectile_img
        self.image = pygame.transform.scale(projectile_img, (20, 40))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.y -= 10
        if self.rect.y < 0:
            self.kill()

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        self.image = pygame.transform.scale(asteroid_img, (90, 65))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = update_asteroid_speed(level)

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(-100, -40)
            self.speed = update_asteroid_speed(level)

# game objects
all_sprites = pygame.sprite.Group()
spaceship = Spaceship()
all_sprites.add(spaceship)
projectiles = pygame.sprite.Group()
asteroids = pygame.sprite.Group()

for _ in range(8):
    asteroid = Asteroid(level)
    all_sprites.add(asteroid)
    asteroids.add(asteroid)

def opening_screen():
    background_img = pygame.image.load('assets/frontscreen.png')
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    font_title = pygame.font.Font(None, 80)
    font_prompt = pygame.font.Font(None, 40)
    title_text = font_title.render("", True, (255, 255, 255))
    prompt_text = font_prompt.render("Press any key to start", True, (255, 255, 255))

    screen.blit(background_img, (0, 0))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
    screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYUP:
                waiting = False


opening_screen()

# Game loop
running = True
game_over = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                projectile = Projectile(spaceship.rect.centerx, spaceship.rect.top)
                all_sprites.add(projectile)
                projectiles.add(projectile)
                shoot_sound.play()

    all_sprites.update()

    # Check for collisions
    collisions = pygame.sprite.groupcollide(projectiles, asteroids, True, True)
    for collision in collisions:
        score += 1
        level = update_level(score)
        score_text = score_font.render(f"Score: {score}", True, (255, 255, 255))
        level_text = score_font.render(f"Level: {level}", True, (255, 255, 255))
        asteroid = Asteroid(level)
        all_sprites.add(asteroid)
        asteroids.add(asteroid)

        # Draw background image
    screen.blit(background_img, (0, 0))

    # Check for collisions between spaceship and asteroids
    if not game_over:
        hits = pygame.sprite.spritecollide(spaceship, asteroids, False)
        if hits:
            game_over = True
            spaceship.kill()
            pygame.mixer.music.stop()
            game_over_sound.play()


    if game_over:
        screen.blit(game_over_img, (WIDTH // 2 - game_over_img.get_width() // 2, HEIGHT // 2 - game_over_img.get_height() // 2))
        final_score_text = game_over_font.render(f"Your Score: {score}", True, (255, 255, 255))
        screen.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 2 + 100))

    else:
        all_sprites.draw(screen)
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 50))

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()
