import pygame
import math
import random

# Initialize the pygame
pygame.init()

# Create the screen
screen = pygame.display.set_mode((800, 600))

# Background
background = pygame.image.load('background.jpg')

# Title and Icon
pygame.display.set_caption("Space Invader from Balde")
icon = pygame.image.load('ufo.png')
pygame.display.set_icon(icon)

# Player
playerImg = pygame.image.load('player.png')
playerX = 370
playerY = 480
playerX_change = 0
# Added FOR MORE FUN By BALDE 1 line
playerY_change = 0

# Enemy
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []

num_of_enemies = 6

for i in range(num_of_enemies):
    enemyImg.append(pygame.image.load('enemy.png'))
    enemyX.append(random.randint(0, 735))
    enemyY.append(random.randint(50, 150))
    enemyX_change.append(5)
    enemyY_change.append(40)

# Bullet
bulletImg = pygame.image.load('bullet.png')
bulletX = 0
bulletY = 480
bulletX_change = 0
bulletY_change = 20
# Ready means you can't see the bullet on the screen
# Fire means the bullet is currentlty moving
bullet_state = "ready"

# Score
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 22)
textX = 10
textY = 10


def show_score(x, y):
    score = font.render("Score: " + str(score_value), True, (0, 255, 0))
    screen.blit(score, (x, y))

# Added FOR MORE FUN By BALDE 1 line
# enemyY_change = 0


def player(x, y):
    screen.blit(playerImg, (x, y))


def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))


def fire_bullet(x,y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bulletImg, (x + 16, y + 10))  


def isCollision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt((math.pow(enemyX - bulletX, 2)) + (math.pow(enemyY - bulletY, 2)))
    if distance < 27:
        return True
    else:
        return False   


# Game loop
running = True
while running:

    # RGB - red, green, blue
    screen.fill((0, 0, 0))
    # Background Image
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # If keystroke is pressed check whether its right or left
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                playerX_change = -5 
            if event.key == pygame.K_RIGHT:
                playerX_change = 5

            # If key-space is pressed it triggers the bullet out
            if event.key == pygame.K_SPACE:
                if bullet_state == "ready":
                    # Get the X cordinate of the spaceship
                    bulletX = playerX
                    fire_bullet(bulletX, bulletY)        
                   
            # Added FOR MORE FUN By BALDE 4 lines
            if event.key == pygame.K_UP:
                playerY_change = -5 
            if event.key == pygame.K_DOWN:
                playerY_change = 5     

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                playerX_change = 0

            # Added FOR MORE FUN By BALDE 2 lines
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                playerY_change = 0                   

    # Checking for boundries of spaceship 'so' it doesn't go out of bounds
    playerX += playerX_change

    if playerX <= 0:
        playerX = 0
    elif playerX >= 736:
        playerX = 736   

    # Added FOR MORE FUN By BALDE 5 lines
    playerY += playerY_change

    if playerY <= 0:
        playerY = 0
    elif playerY >= 536:
        playerY = 536 

    # Enemy Mouvement
    for i in range(num_of_enemies):
        enemyX[i] += enemyX_change[i]

        if enemyX[i] <= 0:
            enemyX_change[i] = 4
            enemyY[i] += enemyY_change[i]
        elif enemyX[i] >= 736:
            enemyX_change[i] = -4
            enemyY[i] += enemyY_change[i]

        # Collision
        collision = isCollision(enemyX[i], enemyY[i], bulletX, bulletY)
        if collision:
            bulletY = 480
            bullet_state = "ready"
            score_value += 1
            enemyX[i] = random.randint(0, 735)
            enemyY[i] = random.randint(50, 150)

        enemy(enemyX[i], enemyY[i], i)        

    # Bullet Mouvement
    if bulletY <= 0:
        bulletY = 480
        bullet_state = "ready"
        # These three lines ABOVE is to kill the bullet up & reload it
    if bullet_state == "fire":
        fire_bullet(bulletX, bulletY)
        bulletY -= bulletY_change    

    # Added FOR MORE FUN By BALDE 4 lines + 1rst one commented
    # enemyY += enemyY_change

    # if enemyY <= 0:
        # enemyY = 0
    # elif enemyY >= 536:
        # enemyY = 536

    player(playerX, playerY)
    show_score(textX, textY)
    pygame.display.update()

    
    """
import pygame
import math
import random

# Initialize the pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
BULLET_SPEED = 10
ENEMY_SPEED = 4
NUM_ENEMIES = 6

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Load images
background = pygame.image.load('background.jpg')
player_img = pygame.image.load('player.png')
enemy_img = [pygame.image.load('enemy.png') for _ in range(NUM_ENEMIES)]
bullet_img = pygame.image.load('bullet.png')

# Load sounds
pygame.mixer.init()
#bullet_sound = pygame.mixer.Sound('bullet.wav')
#explosion_sound = pygame.mixer.Sound('explosion.wav')
#background_music = pygame.mixer.Sound('background_music.wav')

# Initialize player
player_x = SCREEN_WIDTH // 2
player_y = SCREEN_HEIGHT - 64
player_x_change = 0

# Initialize enemies
enemy_x = [random.randint(0, SCREEN_WIDTH - 64) for _ in range(NUM_ENEMIES)]
enemy_y = [random.randint(50, 150) for _ in range(NUM_ENEMIES)]
enemy_x_change = [ENEMY_SPEED for _ in range(NUM_ENEMIES)]
enemy_y_change = [40 for _ in range(NUM_ENEMIES)]

# Initialize bullets
bullet_x = 0
bullet_y = player_y
bullet_x_change = 0
bullet_y_change = BULLET_SPEED
bullet_state = "ready"

# Initialize score
score = 0
font = pygame.font.Font('freesansbold.ttf', 32)
text_x = 10
text_y = 10

# Initialize game over state
game_over_font = pygame.font.Font('freesansbold.ttf', 64)

def show_score(x, y):
    score_display = font.render("Score: " + str(score), True, (0, 255, 0))
    screen.blit(score_display, (x, y))

def player(x, y):
    screen.blit(player_img, (x, y))

def enemy(x, y, i):
    screen.blit(enemy_img[i], (x, y))

def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bullet_img, (x + 16, y + 10))
    #bullet_sound.play()

def is_collision(enemy_x, enemy_y, bullet_x, bullet_y):
    distance = math.sqrt((enemy_x - bullet_x) ** 2 + (enemy_y - bullet_y) ** 2)
    return distance < 27

def game_over_text():
    game_over_surface = game_over_font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(game_over_surface, (200, 250))

# Game loop
running = True
while running:

    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player_x_change = -PLAYER_SPEED
            if event.key == pygame.K_RIGHT:
                player_x_change = PLAYER_SPEED
            if event.key == pygame.K_SPACE:
                if bullet_state == "ready":
                    bullet_x = player_x
                    fire_bullet(bullet_x, bullet_y)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                player_x_change = 0

    player_x += player_x_change

    if player_x <= 0:
        player_x = 0
    elif player_x >= SCREEN_WIDTH - 64:
        player_x = SCREEN_WIDTH - 64

    for i in range(NUM_ENEMIES):
        enemy_x[i] += enemy_x_change[i]

        if enemy_x[i] <= 0:
            enemy_x_change[i] = ENEMY_SPEED
            enemy_y[i] += enemy_y_change[i]
        elif enemy_x[i] >= SCREEN_WIDTH - 64:
            enemy_x_change[i] = -ENEMY_SPEED
            enemy_y[i] += enemy_y_change[i]

        if is_collision(enemy_x[i], enemy_y[i], bullet_x, bullet_y):
            #explosion_sound.play()
            bullet_y = player_y
            bullet_state = "ready"
            score += 1
            enemy_x[i] = random.randint(0, SCREEN_WIDTH - 64)
            enemy_y[i] = random.randint(50, 150)

        enemy(enemy_x[i], enemy_y[i], i)

    if bullet_y <= 0:
        bullet_y = player_y
        bullet_state = "ready"

    if bullet_state == "fire":
        fire_bullet(bullet_x, bullet_y)
        bullet_y -= bullet_y_change

    player(player_x, player_y)
    show_score(text_x, text_y)

    pygame.display.update()

    ===================WIIN!!===================
    win_score = 10  # Set your desired winning score

    while running:
    # ... (previous code)

    if score >= win_score:
        # Player wins
        win_message = font.render("WIN!!", True, (0, 255, 0))
        screen.blit(win_message, (350, 250))
        game_over = True  # Game over when the player wins

    if game_over:
        show_game_over()
        # ... (previous code)

    # ... (previous code)
    ===================WIIN!!===================
    """