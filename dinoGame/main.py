"""
griddo
Dino Game

Description: A near-exact clone of google chrome's no internet game, or the "google dinosaur game", except i added
a couple features.
Game Mechanics:
1. Random Obstacles
2. Parallax Effect with stars/clouds/the moon
3. Breakable Barriers
4. Powerups
5. Score Counter
6. High Score Saving System

How To Play:
W/Up Arrow/Space to jump
S/Down Arrow to duck
Click the brick obstacles to destroy them
Collect Bananas and Milk to get powerups
Bananas make the dino jump much higher for 8 seconds
Milk allows the dino to survive one obstacle hit in the next 16 seconds

Credit:
wayou - Recreated the dino spritesheet on GitHub
Google - Inspiration and original sprites
A bunch of people on StackOverflow - help with code
Some Guy Online - the font used for the text
(^ i tried to find this guys name/username but i couldn't)
"""

import pygame as pg
import random as rnd
import tkinter as tk

# prepare some variables for later
tk = tk.Tk()
clock = pg.time.Clock()

# initialize pygame
pg.init()

# make it so that keypresses repeat immediately
pg.key.set_repeat(1, 1)

# find the monitor's width and height so that the window is fullscreen
screenWidth = tk.winfo_screenwidth()
screenHeight = tk.winfo_screenheight()
# leave this at 60
framerate = 60

# set up the screen
# the base screen
baseScreen = pg.display.set_mode((screenWidth, screenHeight))
# the screen everything is drawn to, allows for screenshake (which we dont use in this game)
screen = pg.Surface((screenWidth, screenHeight), pg.HWACCEL)
# the offset of the drawing screen. changing it moves the entire screen.
screenOffset = (0, 0)

# load the game_data.txt file for high score purposes
gameData = open(r"game_data.txt", "r+")

# get the font for the score
scoreFont = pg.font.Font(r"mojangles.otf", 32)

# load all the images (theres a lot)
dinoJump = pg.image.load(r"sprites/dino_1.png")
dinoWalk1 = pg.image.load(r"sprites/dino_2.png")
# nice
dinoWalk2 = pg.image.load(r"sprites/dino_3.png")
dinoDead = pg.image.load(r"sprites/dino_4.png")
dinoCrouch1 = pg.image.load(r"sprites/dino_5.png")
dinoCrouch2 = pg.image.load(r"sprites/dino_6.png")
cactus1 = pg.image.load(r"sprites/cacti_group_1.png")
cactus2 = pg.image.load(r"sprites/cacti_large_1.png")
cactus3 = pg.image.load(r"sprites/cacti_large_2.png")
cactus4 = pg.image.load(r"sprites/cacti_large_3.png")
cactus5 = pg.image.load(r"sprites/cacti_large_4.png")
cactus6 = pg.image.load(r"sprites/cacti_small_1.png")
cactus7 = pg.image.load(r"sprites/cacti_small_2.png")
cactus8 = pg.image.load(r"sprites/cacti_small_3.png")
cactus9 = pg.image.load(r"sprites/cacti_small_4.png")
cactus10 = pg.image.load(r"sprites/cacti_small_5.png")
cactus11 = pg.image.load(r"sprites/cacti_small_6.png")
cactiList = [cactus1, cactus2, cactus3, cactus4, cactus5, cactus6, cactus7, cactus8, cactus9, cactus10, cactus11]
breakableBrick = pg.image.load(r"sprites/broken_brick.png")
pickupBanana = pg.image.load(r"sprites/pickup_banana.png")
powerupJump = pg.image.load(r"sprites/power_up_jump.png")
pickupMilk = pg.image.load(r"sprites/pickup_milk.png")
powerupShield = pg.image.load(r"sprites/power_up_shield.png")
ptera1 = pg.image.load(r"sprites/ptera_1.png")
ptera2 = pg.image.load(r"sprites/ptera_2.png")
cloud1 = pg.image.load(r"sprites/cloud_1.png").convert_alpha() # idk if this actually does anything but its supposed to
ground = pg.image.load(r"sprites/ground.png")
star1 = pg.image.load(r"sprites/star_1.png").convert_alpha() # allow for transparency and these need to be transparent
star2 = pg.image.load(r"sprites/star_2.png").convert_alpha() # so i stuck it on here just in case
star3 = pg.image.load(r"sprites/star_3.png").convert_alpha()
starList = [star1, star2, star3]
moon1 = pg.image.load(r"sprites/moon_1.png")
moon2 = pg.image.load(r"sprites/moon_2.png")
moon3 = pg.image.load(r"sprites/moon_3.png")
moon4 = pg.image.load(r"sprites/moon_4.png")
moon5 = pg.image.load(r"sprites/moon_5.png")
moon6 = pg.image.load(r"sprites/moon_6.png")
moon7 = pg.image.load(r"sprites/moon_7.png")
moonList = [moon1, moon2, moon3, moon4, moon5, moon6, moon7]
currentMoon = 0
gameover = pg.image.load(r"sprites/game_over.png")
startButton = pg.image.load(r"sprites/start_button.png")

# set the current frame to the first walking frame
dinoCurrentFrame = dinoWalk1

# variables
# i would've used proper PEP-8 underscore variable formatting but i forgot until i had 80% of the program written
floorPos = screenHeight - round(screenHeight / 5)
dinoPosX = screenWidth / 8
dinoPosY = floorPos
dinoWidth = dinoCurrentFrame.get_width()
dinoHeight = dinoCurrentFrame.get_height()
crouching = False
jumpForce = 19
relativeChange = 0
jumping = False
obstacles = []
speed = 10
obstacleDelay = [speed * 100, speed * 200]
obstacleCurrentDelay = 1000
score = 0
scoreDelay = 100
scoreTimer = scoreDelay
scoreShadowDistance = 4
animationDelay = 100
animation = 0
animationTimer = animationDelay
clouds = []
groundOffset = 17
groundTiles = [
    [screenWidth - ground.get_width(), floorPos - groundOffset],
    [screenWidth, floorPos - groundOffset]
]
tileAdded = True
stars = []
moonPosX = screenWidth
moonPosY = screenHeight / 2
cloudSpeed = 15
starSpeed = 20
moonSpeed = 17
jumpPowerUp = False
shieldPowerUp = False
jumpPowerUpDuration = 8000
shieldPowerUpDuration = 16000
jumpPowerUpStart = 0
shieldPowerUpStart = 0

# add an obstacle
# i probably could've used classes/objects for this but i wrote wayyy too much of the code before thinking about that
# obstacle list format: [xPos, yPos, sprite, obstacleType, (optional) animationDelay, (optional) collider]
# obstacleType: 0 - standard | 1 - pterodactyl | 2 - breakable | 3 - banana | 4 - milk
def createObstacle():
    obstacleType = rnd.randint(1, 10)
    if obstacleType == 10 and score > 150:
        if rnd.randint(0, 1) == 0:
            obstacles.append([screenWidth, floorPos, pickupBanana, 3])
        else:
            obstacles.append([screenWidth, floorPos, pickupMilk, 4])
    elif obstacleType >= 8 and obstacleType <= 9 and score >= 100:
        obstacles.append([screenWidth, floorPos - 69, ptera1, 1, 300, None])
    elif obstacleType >= 6 and obstacleType <= 7 and score >= 200:
        obstacles.append([screenWidth, floorPos, breakableBrick, 2, 0, pg.Rect((screenWidth, floorPos), (breakableBrick.get_width(), breakableBrick.get_height()))])
    else:
        obstacles.append([screenWidth, floorPos, cactiList[rnd.randint(0, 5)], 0])

# add background effects
def createCloud():
    clouds.append([screenWidth, rnd.randint(50, floorPos - 150)])

def createStar():
    stars.append([screenWidth, rnd.randint(50, floorPos - 150), starList[rnd.randint(0, 2)]])

# create the start function because im too used to unity
def start():
    startingStars = rnd.randint(2, 8)
    for i in range(startingStars):
        stars.append([rnd.randint(150, screenWidth - 150), rnd.randint(50, floorPos - 150), starList[rnd.randint(0, 2)]])
    startingClouds = rnd.randint(0, 4)
    for i in range(startingClouds):
        clouds.append([rnd.randint(200, screenWidth - 200), rnd.randint(50, floorPos - 150)])

start(); # hehe i used a semicolon >:)

# create the main menu loop

running = True
death = True
menu = True

while menu:
    for event in pg.event.get():
        key = pg.key.get_pressed()
        # if escape key pressed, kill the program immediately, and skip all the other loops
        if key[pg.K_ESCAPE]:
            menu = False
            running = False
            death = False
    # handle clicking on the start button
    x, y = pg.mouse.get_pos()
    startButtonCollider = pg.Rect(((screenWidth / 2) - (startButton.get_width() / 2), (screenHeight / 2) - (startButton.get_height() / 2)), (startButton.get_width(), startButton.get_height()))
    if pg.mouse.get_pressed() == (1, 0, 0) and startButtonCollider.collidepoint(x, y):
        menu = False
    screen.fill((0, 0, 0))
    screen.blit(startButton, ((screenWidth / 2) - (startButton.get_width() / 2), (screenHeight / 2) - (startButton.get_height() / 2)))
    # send the screen to the display
    baseScreen.blit(screen, screenOffset)
    pg.display.update()
    clock.tick(framerate)

# set up the running loop
while running:
    for event in pg.event.get():
        key = pg.key.get_pressed()
        # if escape key pressed, kill the program
        if key[pg.K_ESCAPE]:
            running = False
            death = False
        # if the space key, the w key, or the up arrow is pressed, jump
        if key[pg.K_SPACE] or key[pg.K_w] or key[pg.K_UP]:
            jumping = True
        # if the s key or the down arrow is pressed, duck
        if (key[pg.K_s] or key[pg.K_DOWN]) and not jumping:
            crouching = True
        else:
            crouching = False
    # if the dino is jumping and is on the floor, set the relative change to the total jump force
    if jumping and dinoPosY == floorPos:
        relativeChange = jumpForce
    # if we're jumping, but not on the floor (in the air)...
    if jumping:
        # subtract the relative change from dinoPosY (lower Y is higher on the screen)
        dinoPosY -= relativeChange
        # subtract relative change by one to simulate gravity
        relativeChange -= 1
        # if the dino is on the floor, set jumping to false and set the dinoPosY to the floor, just in case it passed the floor.
        if dinoPosY >= floorPos:
            jumping = False
            dinoPosY = floorPos
    
    # create an obstacle once the delay is up, and set the delay to a random value in the acceptable range
    if pg.time.get_ticks() > obstacleCurrentDelay:
        createObstacle()
        obstacleCurrentDelay = pg.time.get_ticks() + rnd.randint(obstacleDelay[0], obstacleDelay[1])

    speed += 0.003

    # increase the score and create background effects
    if pg.time.get_ticks() >= scoreTimer:
        score += 1
        scoreTimer = pg.time.get_ticks() + scoreDelay
        if rnd.randint(1, 42) == 42:
            createCloud()
        if rnd.randint(1, 30) == 30:
            createStar()

    # animate the dino
    if pg.time.get_ticks() >= animationTimer:
        animation = 1 if animation == 0 else 0
        animationTimer = pg.time.get_ticks() + animationDelay

    # use condition specific animation frames
    if not jumping and not crouching:
        dinoCurrentFrame = dinoWalk1 if animation == 0 else dinoWalk2
    elif not jumping and crouching:
        dinoCurrentFrame = dinoCrouch1 if animation == 0 else dinoCrouch2
    elif jumping:
        dinoCurrentFrame = dinoJump

    # dino size variables so that its easier to get these values for collision (i coulda used a rect but its too late)
    dinoWidth = dinoCurrentFrame.get_width()
    dinoHeight = dinoCurrentFrame.get_height()

    # start drawing everything, starting with the background
    screen.fill((0, 0, 0))

    # draw all the stars, and remove them if they're offscreen
    for star in stars:
        screen.blit(star[2], (star[0], star[1]))
        if star[0] < 0:
            stars.remove(star)
        star[0] -= speed / starSpeed

    # draw the ground
    for tile in groundTiles:
        screen.blit(ground, (tile[0], tile[1]))
        tile[0] -= speed
        if tile[0] < screenWidth - ground.get_width() and not tileAdded:
            groundTiles.append([screenWidth, floorPos - groundOffset])
            tileAdded = True
        if tile[0] < 0 - ground.get_width():
            groundTiles.remove(tile)
            tileAdded = False

    # draw the moon
    screen.blit(moonList[currentMoon], (moonPosX, moonPosY))
    # move the moon in a rough arc
    moonPosX -= speed / moonSpeed
    moonPosY = (abs(moonPosX - screenWidth / 2) / 10) + 250
    # update the moon phase
    if moonPosX <= -500:
        moonPosX = screenWidth
        currentMoon += 1
        if currentMoon > 6:
            currentMoon = 0

    # draw the clouds, and remove them if they're offscreen
    for cloud in clouds:
        screen.blit(cloud1, (cloud[0], cloud[1]))
        if cloud[0] < 0 - cloud1.get_width():
            clouds.remove(cloud)
        cloud[0] -= speed / cloudSpeed

    # draw the obstacles
    for obstacle in obstacles:
        screen.blit(obstacle[2], (obstacle[0], obstacle[1] - obstacle[2].get_height()))
        if obstacle[0] <= 0 - obstacle[2].get_width():
            obstacles.remove(obstacle)
        obstacle[0] -= speed
        # check for collision with the dino
        if (dinoPosX <= obstacle[0] <= dinoPosX + dinoWidth or dinoPosX <= obstacle[0] + obstacle[2].get_width() <= dinoPosX + dinoWidth) and (dinoPosY - dinoHeight <= obstacle[1] <= dinoPosY or dinoPosY - dinoHeight <= obstacle[1] - obstacle[2].get_height() <= dinoPosY):
            # if the obstacle is actually a banana, activate the jump high powerup
            if obstacle[3] == 3:
                jumpPowerUp = True
                jumpPowerUpStart = pg.time.get_ticks()
                obstacles.remove(obstacle)
                continue
            # if the obstacle is actually milk, activate the shield powerup
            elif obstacle[3] == 4:
                shieldPowerUp = True
                shieldPowerUpStart = pg.time.get_ticks()
                obstacles.remove(obstacle)
                continue
            # if the player doesn't have a shield and this is a normal obstacle, kill them
            elif not shieldPowerUp:
                running = False
            # if the player does have a shield and this is a normal obstacle, remove the powerup and the obstacle
            else:
                shieldPowerUp = False
                obstacles.remove(obstacle)
                continue
        # animate the pterodactlys, and move them slightly faster than the other obstacles
        if obstacle[3] == 1:
            obstacle[0] -= speed / 5
            if pg.time.get_ticks() > obstacle[4]:
                if obstacle[2] == ptera1:
                    obstacle[2] = ptera2
                else:
                    obstacle[2] = ptera1
                obstacle[4] = pg.time.get_ticks() + 200
        # handle mouse collision with breakable barriers
        if obstacle[3] == 2:
            obstacle[5].x = obstacle[0]
            obstacle[5].y = obstacle[1] - obstacle[2].get_height()

            x, y = pg.mouse.get_pos()
            if pg.mouse.get_pressed() == (1, 0, 0) and obstacle[5].collidepoint(x, y):
                obstacles.remove(obstacle)
    
    # if the player has the jump powerup make them jump really high
    if jumpPowerUp:
        jumpForce = 25
        # make sure the powerup isn't over yet
        if pg.time.get_ticks() > jumpPowerUpStart + jumpPowerUpDuration:
            jumpPowerUp = False
        # actually draw the powerup
        screen.blit(powerupJump, (dinoPosX, dinoPosY - 100))
    else:
        jumpForce = 19

    if shieldPowerUp:
        # make sure the powerup isn't over yet
        if pg.time.get_ticks() > shieldPowerUpStart + shieldPowerUpDuration:
            shieldPowerUp = False
        # if the player already has another powerup, draw this one above it so they dont overlap
        if jumpPowerUp:
            screen.blit(powerupShield, (dinoPosX, dinoPosY - 135))
        # otherwise draw it in the normal place
        else:
            screen.blit(powerupShield, (dinoPosX, dinoPosY - 100))

    # draw the dino, AFTER the game could've ended (this is important), and only if the game hasn't ended
    if running:
        screen.blit(dinoCurrentFrame, (dinoPosX, dinoPosY - dinoHeight))

    # prepare the score text
    scoreText = scoreFont.render(str(score), False, (255, 255, 255))
    # draw the score text
    screen.blit(scoreText, ((screenWidth / 2) - scoreFont.size(str(score))[0] / 2, round(screenHeight) / 20))
    # prepare the highscore text
    gameData.seek(0)
    highscoreText = scoreFont.render("high: {}".format(gameData.read()), False, (255, 255, 255))
    # draw the highscore text
    screen.blit(highscoreText, (30, 15))

    # send the screen to the display
    baseScreen.blit(screen, screenOffset)
    pg.display.update()
    clock.tick(framerate)

# prepare the game_data.txt file for writing
gameData.seek(0)

# if we got a highscore, write the highscore to game_data.txt
if score > int(gameData.read()):
    gameData.truncate(0)
    gameData.seek(0)
    gameData.write(str(score))

# the loop that keeps the window open so the player can see their score
while death:
    for event in pg.event.get():
        key = pg.key.get_pressed()                                  # extra nice
        if key[pg.K_ESCAPE]:
            death = False
    # this is why not drawing the dino if we died is important, because now we draw a dead dino sprite instead, and we
    # dont want the two dino sprites to overlap.
    dinoCurrentFrame = dinoDead
    screen.blit(dinoCurrentFrame, (dinoPosX, dinoPosY - dinoHeight))
    screen.blit(gameover, (screenWidth / 2 - gameover.get_width() / 2, screenHeight / 2 - 100))
    baseScreen.blit(screen, screenOffset)
    pg.display.update()

# make sure to close game_data.txt so there arent any memory leaks
gameData.close()

pg.quit()
