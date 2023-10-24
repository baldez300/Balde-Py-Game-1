import pygame
import math
import random

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
BULLET_SPEED = 10
ENEMY_SPEED = 4
NUM_ENEMIES = 6
WIN_SCORE = 15  # Set the score required to win the game

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Load images
background = pygame.image.load('background.jpg')
player_img = pygame.image.load('player.png')
enemy_img = [pygame.image.load('enemy.png') for _ in range(NUM_ENEMIES)]
bullet_img = pygame.image.load('bullet.png')

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

# Initialize game counter
game_counter = 3

# Initialize score
score = 0
font = pygame.font.Font('freesansbold.ttf', 32)
text_x = 10
text_y = 10

# Initialize game over font
game_over_font = pygame.font.Font('freesansbold.ttf', 64)

# Initialize game over state
game_over = False  # Set to True when the game ends

def show_score(x, y):
    # Display the player's score on the screen
    score_display = font.render("Score: " + str(score), True, (0, 255, 0))
    screen.blit(score_display, (x, y))

def show_game_count(x, y, count):
    # Display the remaining player count on the screen
    player_count_display = font.render(f"Lives: {count}", True, (255, 255, 255))
    screen.blit(player_count_display, (x, y))

def show_win():
    # Display "WIN!!" text on the screen
    win_surface = game_over_font.render("WIN!!", True, (0, 255, 0))
    screen.blit(win_surface, (250, 250))

def player(x, y):
    # Draw the player's character on the screen
    screen.blit(player_img, (x, y))

def enemy(x, y, i):
    # Draw an enemy character on the screen
    screen.blit(enemy_img[i], (x, y))

def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bullet_img, (x + 16, y + 10))

def is_collision(enemy_x, enemy_y, bullet_x, bullet_y):
    # Check if a collision has occurred between an enemy and a bullet
    distance = math.sqrt((enemy_x - bullet_x) ** 2 + (enemy_y - bullet_y) ** 2)
    return distance < 27

def show_game_over():
    # Display "GAME OVER" text on the screen
    game_over_surface = game_over_font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(game_over_surface, (200, 250))
    restart_message = font.render("Press R to Restart", True, (255, 255, 255))
    quit_message = font.render("Press Q to Quit", True, (255, 255, 255))
    screen.blit(restart_message, (250, 350))
    screen.blit(quit_message, (300, 400))

# Game loop
running = True
while running:
    # Fill the screen with a black background
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    if not game_over:
        # Event handling when the game is not over
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle player input here
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

            if enemy_y[i] >= SCREEN_HEIGHT - 64:
                game_over = True  # Game over when enemy crosses the bottom line
                break

            if is_collision(enemy_x[i], enemy_y[i], bullet_x, bullet_y):
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

        if score >= WIN_SCORE:
            show_win()
            # game_over = True

    if game_over:
        show_game_over()

        # Event handling for game over state
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    if game_counter > 0:
                        # Restart the game
                        game_over = False
                        player_x = SCREEN_WIDTH // 2
                        player_y = SCREEN_HEIGHT - 64
                        score = 0
                        game_counter -= 1
                        # Reset enemy positions
                        enemy_x = [random.randint(0, SCREEN_WIDTH - 64) for _ in range(NUM_ENEMIES)]
                        enemy_y = [random.randint(50, 150) for _ in range(NUM_ENEMIES)]
                if event.key == pygame.K_q:
                    running = False  # Quit the game

    # Update player count next to the score
    show_game_count(text_x, text_y + 40, game_counter)

    pygame.display.update()
