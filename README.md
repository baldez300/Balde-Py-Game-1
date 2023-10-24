# Balde-Py-Game-1
Development of a space invader game with python.
Join me in making it even better for gamers.

Download Python:
	•	Visit the official Python website at python.org.
	•	Click on the "Downloads" tab.

https://www.python.org/downloads/

You can install 'pygame' using pip, which is the Python package manager. Open your terminal and run the following command:
pip install pygame

To install Visual Studio Code (VSCode), follow these steps:
		Download VSCode: Visit the official VSCode website: https://code.visualstudio.com/.
		Choose Your Operating System:
	•	For Windows, click on the "Windows" button.
	•	For macOS, click on the "macOS" button.
	•	For Linux, click on the "Linux" button and select the appropriate package for your distribution.
		Install on Windows:
	•	After downloading the installer, run it.
	•	Follow the installation wizard instructions.
	•	You can choose to add "Open with Code" and "Add to PATH" during the installation, which can be helpful for command-line usage.
	•	Click "Install" to begin the installation.


```
Certainly..!!
Let's break down the key components and functionality of the code:

Initializing pygame and Constants:

You start by initializing the pygame library and defining some constants for the game, such as screen dimensions, player speed, bullet speed, enemy speed, and the number of enemies.
Creating the Game Screen:

You create the game screen with the defined dimensions (800x600 pixels).
Loading Images:

You load images for the background, player character, enemy characters, and bullets. These images will be used to display objects in the game.
Initializing Player and Enemies:

You set up the initial position and speed of the player character and multiple enemy characters. The enemy positions are randomized.
Initializing Bullets and Game State:

You set up initial bullet properties and game state variables, including the player's remaining lives, current score, and fonts for displaying text.
Defining Functions:

You define several functions that help with different aspects of the game:
show_score(x, y): Displays the player's score on the screen.
show_game_count(x, y, count): Displays the remaining player lives on the screen.
player(x, y): Draws the player character on the screen.
enemy(x, y, i): Draws enemy characters on the screen.
fire_bullet(x, y): Fires a bullet from the player's character.
is_collision(enemy_x, enemy_y, bullet_x, bullet_y): Checks for collisions between enemies and bullets.
show_game_over(): Displays "GAME OVER" and other messages on the screen when the game ends.
Game Loop:

You implement the game loop using a while loop. This loop is responsible for running the game continuously.
Handling User Input:

Inside the game loop, you handle user input. The player can control the player character's movement (left and right) and fire bullets using the keyboard.
Moving Player and Enemies:

You update the player's position based on user input and constrain it within the screen boundaries. You also update the positions of enemy characters, causing them to move back and forth horizontally.
Game Logic:

You handle game logic, such as detecting collisions between bullets and enemies, increasing the player's score, and respawning enemies when they are destroyed.
Displaying Game Elements:

You draw the player character, enemies, score, remaining lives, and bullets on the screen during the game.
Game Over State:

If certain conditions are met, such as when an enemy crosses the bottom of the screen or when the player runs out of lives, you enter the game over state. In this state, you display "GAME OVER" and provide options to restart the game or quit.
Restarting the Game:

When the game is over and the player chooses to restart, you reset the game by initializing the player's position, score, and remaining lives. You also randomize the enemy positions again.
Quitting the Game:

If the player chooses to quit during the game over state, you exit the game.
Updating the Screen:

After each iteration of the game loop, you update the screen to reflect changes in the game state.

Overall, the code provides a functional and interactive space shooter game with features for scoring, lives, and game restart. Players can control the player character, shoot at enemies, and aim for a high score. The game handles the transition between the main game and the game over state smoothly.

```

