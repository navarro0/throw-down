#!usr/bin/env python
#
# Joey Navarro
#
# This is a fighting game that uses only two buttons for
# input (due to keyboard limitations). Players must throw
# their opponent into the floating ring to deal damage.
#
# Licensed under the MIT License

import pygame, random, sys, os, itertools
from pygame.locals import *
from const import *
from text import Text
from obj import Object
from fighter import Fighter

## Center the video
os.environ["SDL_VIDEO_CENTERED"] = "1"       
        
## Main wrapper class; sets up the entire game
class Main():
    def __init__(self):
        ## Initialize the Pygame module
        pygame.mixer.pre_init(44100, -16, 2, 4096)
        pygame.init()

        ## Create the display screen
        self.display = pygame.display.set_mode((800,480), SWSURFACE)
        self.display.fill((0,0,0))

        ## We draw to this screen and then scale it for a pixelly effect
        self.screen = pygame.Surface((400,240))
        self.screen.fill((0,0,0))

        ## Create the game clock
        self.clock = pygame.time.Clock()

        ## Set the window caption
        pygame.display.set_caption("Throw Down")

        ## Initialize stuff
        self.init_constants() ## Initialize constants
        self.load_images()    ## Load global GUI images
        self.load_sounds()    ## Load sound effects

        ## Run the game
        while True:
            p1, p2  = self.character_select()  ## Character selection menu
            results = [RESULTS.DRAW, RESULTS.DRAW, RESULTS.DRAW] ## Current sum = 3
            winner  = None
            loser   = None
            stages = [1,2,3]
            random.shuffle(stages)
            ## Start a best-of-three match set
            for i in range(3):
                results[i] = self.run(p1, p2, stages[i]) ## Start a match
                ## When the second match is done, check to see if someone has
                ## won twice in a row. If so, break the loop.
                if i == 1:
                    ## Sum = 5 results from the array [2,2,1]
                    if sum(results) == 5:
                        winner = p1
                        loser  = p2
                        break
                    ## Sum = 9 results from the array [4,4,1]
                    elif sum(results) == 9:
                        winner = p2
                        loser  = p1
                        break
                elif i == 2:
                    ## If we haven't gotten a winner by the time the third
                    ## match has started, we must do an exhaustive analysis.
                    if sum(results) in [5,8]:
                        ## Sum = 5 results from the array [2,1,2] and Sum = 8
                        ## results from the array [2,4,2]
                        winner = p1
                        loser  = p2
                    elif sum(results) in [9,10]:
                        ## Sum = 9 results from the array [4,1,4] and Sum = 10
                        ## results from the array [4,2,4]
                        winner = p2
                        loser  = p1
                    elif sum(results) == 3:
                        ## Sum = 3 means everything was a draw
                        winner = 0
                        loser  = 0

            ready_p1 = False
            ready_p2 = False
            text_top = Text("", (4,4), size=8)
            text_bot = Text("", (4,228), size=8)
            text_winner = Text("Winner!", (84,48), size=8)
            text_loser = Text("Loser...", (84,96), size=8)
            text_remind = Text("an alpha", (286,148), size=8)
            pygame.mixer.music.stop()
            
            while not ready_p1 or not ready_p2:
                self.clock.tick(self.game_fps)
                pygame.display.set_caption("Throw Down: %d FPS" %self.clock.get_fps())

                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                        elif e.key == pygame.K_SPACE:
                            ready_p1 = True if not ready_p1 else False
                            self.menu_2.play()
                        elif e.key == pygame.K_RETURN:
                            ready_p2 = True if not ready_p2 else False
                            self.menu_2.play()

                self.screen.blit(self.menuback1, (0,0))
                self.screen.blit(self.logo, (196,48))
                text_remind.draw(self.screen)

                ## Update the reminder text for player 1
                if not ready_p1:
                    pygame.draw.rect(self.screen, (50,50,50), (0,0,400,16))
                    text_top.update("VIEWING RESULTS...")
                else:
                    pygame.draw.rect(self.screen, (255,82,82), (0,0,400,16))
                    text_top.update("READY FOR THE NEXT BATTLE!")

                ## Update the reminder text for player 2
                if not ready_p2:
                    pygame.draw.rect(self.screen, (50,50,50), (0,224,400,16))
                    text_bot.update("VIEWING RESULTS...")
                else:
                    pygame.draw.rect(self.screen, (82,82,255), (0,224,400,16))
                    text_bot.update("READY FOR THE NEXT BATTLE!")

                ## Draw both texts
                text_top.draw(self.screen)
                text_bot.draw(self.screen)

                ## Draw the portrait for player 1
                if winner != 0:
                    pygame.draw.rect(self.screen, (50,50,50), (28, 52, 46, 32))
                    self.screen.blit(self.portraits[winner-1], (24,48))
                if loser != 0:
                    pygame.draw.rect(self.screen, (50,50,50), (28, 100, 46, 32))
                    self.screen.blit(self.portraits[loser-1], (24,96))

                text_winner.draw(self.screen)
                text_loser.draw(self.screen)

                ## Render everything to the real screen
                pygame.transform.scale(self.screen, (800,480), self.display)
                pygame.display.flip()

    def init_constants(self):
        ## Initialize frames-per-second data
        self.game_fps = CONST.FPS
        self.obj_fps = CONST.OBJ_FRAMERATE
        self.fighter_fps = CONST.FRAMERATE
        
    def check_collision(self, mask_a, mask_b, rect_a, rect_b):
        ## Checks collision between two masks
        offset_x, offset_y = (rect_b.left - rect_a.left, rect_b.top - rect_a.top)
        if mask_a.overlap(mask_b, (offset_x, offset_y)):
            return True
        return False

    def load_sounds(self):
        self.menu_1 = pygame.mixer.Sound("RES/SOUND/MENU1.ogg")
        self.menu_2 = pygame.mixer.Sound("RES/SOUND/MENU2.ogg")        

    def load_images(self):
        ## Load portraits 1 through 9 for the character select menu
        self.portraits = []
        for i in range(9):
            temp_portrait = pygame.image.load("RES/CHAR/%02d/EXTRA.png" %(i+1)).convert()
            temp_portrait.set_colorkey((0,0,0))
            temp_portrait = pygame.transform.scale(temp_portrait, (52,40))
            self.portraits.append(temp_portrait)

        ## Load the character select background
        self.menuback1 = pygame.image.load("RES/GUI/MENUBACK1.png").convert()
        self.menuback1 = pygame.transform.scale(self.menuback1, (400,240))

        ## Load the game logo
        self.logo = pygame.image.load("RES/GUI/LOGO.png").convert()
        self.logo.set_colorkey((0,0,0))
        self.logo = pygame.transform.scale(self.logo, (176,112))
        
        ## Load the timer frame to display during the match
        self.timer_frame = pygame.image.load("RES/GUI/TIMER.png").convert()
        self.timer_frame = pygame.transform.scale(self.timer_frame, (48,32))

        ## Load the frame for the health bars during the match
        self.health_frame = pygame.image.load("RES/GUI/HEALTH_FRAME.png").convert()
        self.health_frame = pygame.transform.scale(self.health_frame, (124,20))
        self.health_frame.set_colorkey((0,0,0))

        ## Load the animated decreasing health bar
        self.health_red = pygame.image.load("RES/GUI/HEALTH_RED.png").convert()
        self.health_red = pygame.transform.scale(self.health_red, (116,12))

        ## Load the static health bar
        self.health_yellow = pygame.image.load("RES/GUI/HEALTH_YELLOW.png").convert()
        self.health_yellow = pygame.transform.scale(self.health_yellow, (116,12))

        ## Load the super meter
        self.super_meter = pygame.image.load("RES/GUI/COMBO.png").convert()
        self.super_meter = pygame.transform.scale(self.super_meter, (132,4))

        ## Load the GUI drop shadow
        self.shadow = pygame.image.load("RES/GUI/SHADOW.png").convert()
        self.shadow = pygame.transform.scale(self.shadow, (400,240))
        self.shadow.set_colorkey((0,0,0))

    def draw_obj_back(self, obj):
        ## Method for drawing the background portion of an object
        self.screen.blit(obj.back_image, obj.back_image.get_rect(center=(obj.xpos,obj.ypos)))

    def draw_obj_front(self, obj):
        ## Method for drawing the foreground portion of an object
        self.screen.blit(obj.front_image, obj.front_image.get_rect(center=(obj.xpos,obj.ypos)))
        #self.screen.blit(obj.hitbox_im, obj.hitbox_rect)

    def draw_fighter(self, fighter, other):
        ## Facing correction for a fighter's left and right relative positions
        if fighter.health > 0 and fighter.state != STATE.THROW:
            if fighter.xpos < other.xpos:
                fighter.face_right = True
            else:
                fighter.face_right = False

        ## Shaking animation when grabbed by opponent
        if fighter.is_grabbed:
            xmod = random.randint(-1,1)
            ymod = random.randint(-1,1)
        else:
            xmod = 0
            ymod = 0

        ## Render the afterimage of the fighter
        if fighter.state in [STATE.FLYING_A, STATE.FLYING_B, STATE.FLYING_C] or fighter.dashing:
            for pos in fighter.old_pos:
                self.screen.blit(fighter.afterimage, fighter.afterimage.get_rect(midbottom=(pos[0]+xmod,pos[1]+ymod)))
        ## Render the actual fighter
        self.screen.blit(fighter.image, fighter.image.get_rect(midbottom=(fighter.xpos+xmod,fighter.ypos+ymod)))
        #self.screen.blit(fighter.hitbox_im, fighter.hitbox_rect)
        #self.screen.blit(fighter.hurtbox_im, fighter.hurtbox_rect)
        

    def draw_hud(self, surface, fighter_1, fighter_2):
        ## Renders the heads-up-display in-game
        surface.blit(self.shadow, (0,0))
        surface.blit(fighter_1.other_file[0], (0,0))
        surface.blit(fighter_2.other_file[0], (348,0))
        surface.blit(self.health_frame, (52,0))
        surface.blit(self.health_frame, (224,0))
        surface.blit(self.timer_frame, (176,0))

        ## Draw all text to screen
        self.timer_text.draw(surface)
        self.name_1.draw(surface)
        self.name_2.draw(surface)

        if self.countdown > 1:
            pygame.draw.rect(surface, (50,50,50), (0,110,400,20))
            self.text_1.draw(surface)
            self.text_1.x += 6
        elif self.countdown > 0:
            pygame.draw.rect(surface, (50,50,50), (0,110,400,20))
            self.text_2.draw(surface)
            self.text_2.x += 6
        elif self.paused:
            pygame.draw.rect(surface, (50,50,50), (0,110,400,20))
            self.text_4.draw(surface)
            self.text_4.x += 6
            if self.text_4.x >= CONST.RIGHT:
                self.text_4.x = -self.text_4.width
                
        ## Render player 1's red health bar
        percentage = float(fighter_1.display_health) / fighter_1.max_health
        width = int(116 * percentage)
        temp_bar = self.health_red.subsurface(0,0,width,12)
        surface.blit(temp_bar, (56,4))
        ## Render player 1's yellow health bar
        percentage = float(fighter_1.health) / fighter_1.max_health
        width = int(116 * percentage)
        temp_bar = self.health_yellow.subsurface(0,0,width,12)
        surface.blit(temp_bar, (56,4))

        ## Render player 1's super bar
        percentage = float(fighter_1.display_super) / fighter_1.max_super
        width = min(132, int(132 * percentage))
        temp_bar = self.super_meter.subsurface(0,0,width,4)
        surface.blit(temp_bar, (4,228))

        ## Render player 2's red health bar
        percentage = float(fighter_2.display_health) / fighter_2.max_health
        width = int(116 * percentage)
        temp_bar = self.health_red.subsurface(0,0,width,12)
        surface.blit(temp_bar, (228,4))
        ## Render player 2's yellow health bar
        percentage = float(fighter_2.health) / fighter_2.max_health
        width = int(116 * percentage)
        temp_bar = self.health_yellow.subsurface(0,0,width,12)
        surface.blit(temp_bar, (228,4))

        ## Render player 2's super bar
        percentage = float(fighter_2.display_super) / fighter_2.max_super
        width = min(132, int(132 * percentage))
        temp_bar = self.super_meter.subsurface(0,0,width,4)
        temp_bar = pygame.transform.flip(temp_bar, True, False)
        surface.blit(temp_bar, temp_bar.get_rect(topright=(396,228)))

        if self.finished:
            pygame.draw.rect(surface, (50,50,50), (0,110,400,20))
            self.text_3.draw(surface)
            self.text_3.x += 10
            if self.text_3.x >= CONST.RIGHT:
                self.text_3.x = -self.text_3.width

    def draw_screen(self, fighter_1, fighter_2, obj_list):
        ## Handles drawing the screen as a whole
        if not self.finished and not self.paused:
            if (fighter_1.hit_ceiling and fighter_1.state != STATE.DEAD) or\
               (fighter_2.hit_ceiling and fighter_2.state != STATE.DEAD):
                ## Shake the screen if either player has hit the ceiling
                xoff = 0
                yoff = random.choice((-12,-11,-10,10,11,12))
            elif (fighter_1.ypos < CONST.FLOOR and not fighter_1.is_grabbed and ((fighter_1.xpos == CONST.RIGHT) or (fighter_1.xpos == CONST.LEFT))) or\
                 (fighter_2.ypos < CONST.FLOOR and not fighter_2.is_grabbed and ((fighter_2.xpos == CONST.RIGHT) or (fighter_2.xpos == CONST.LEFT))):
                ## Shake the screen if either player has hit the floor
                xoff = random.choice((-12,-11,-10,10,11,12))
                yoff = 0
            elif (fighter_1.ypos >= CONST.FLOOR and fighter_1.state in [STATE.FLYING_B, STATE.FLYING_C, STATE.DOWN]) or\
                 (fighter_2.ypos >= CONST.FLOOR and fighter_2.state in [STATE.FLYING_B, STATE.FLYING_C, STATE.DOWN]):
                ## I don't think this ever happens anymore
                xoff = random.randint(-2,2)
                yoff = random.randint(-4,4)
            else:
                ## Default offsets
                xoff = 0
                yoff = 0
        else:
            ## Default offsets
            xoff = 0
            yoff = 0
        ## Draw the background with the given offsets
        self.screen.blit(self.background, (xoff,yoff))

        ## Draw the background portion of each in-game object
        for obj in obj_list:
            self.draw_obj_back(obj)

        ## Draw the actual fighters
        self.draw_fighter(fighter_1, fighter_2)
        self.draw_fighter(fighter_2, fighter_1)

        ## Draw the foreground portion of each in-game object
        for obj in obj_list:
            self.draw_obj_front(obj)

        ## Draw the heads-up-display
        self.draw_hud(self.screen, fighter_1, fighter_2)
        ## Scale the screen to the desired size
        pygame.transform.scale(self.screen, (800,480), self.display)

    def character_select(self):
        ## Character select menu
        cursor_p1 = [0,0]    ## Default the cursors to the first two characters
        cursor_p2 = [0,1]
        selected_p1 = False  ## Neither player has decided on a character yet
        selected_p2 = False
        ## Matrix of possible characters
        characters = [[1,2,3],[4,5,6],[7,8,9]]

        ## Mutable text to denote whether a player is ready or not
        text_top = Text("", (4,4), size=8)
        text_bot = Text("", (4,228), size=8)
        text_remind = Text("an alpha", (286,148), size=8)

        pygame.mixer.music.load("RES/SOUND/BGM.ogg")
        pygame.mixer.music.set_volume(0.8)
        pygame.mixer.music.play(-1)

        while not selected_p1 or not selected_p2:
            ## While at least one player is still selecting...
            
            self.clock.tick(self.game_fps) ## Tick the clock
            pygame.display.set_caption("Throw Down: %d FPS" %self.clock.get_fps())
            ## Pump the events
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    ## Allow players to exit out
                    pygame.quit()
                    sys.exit()
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        ## Allow players to press ESC to exit
                        pygame.quit()
                        sys.exit()
                    else:
                        if not selected_p1:
                            ## Allow player 1 to select if he hasn't done so already
                            if e.key == pygame.K_w:
                                cursor_p1[0] -= 1
                                if cursor_p1[0] < 0:
                                    cursor_p1[0] = 2
                                if cursor_p1[0] == cursor_p2[0] and cursor_p1[1] == cursor_p2[1]:
                                    cursor_p1[0] += 1
                                    if cursor_p1[0] > 2:
                                        cursor_p1[0] = 0
                                self.menu_1.play()
                            elif e.key == pygame.K_s:
                                cursor_p1[0] += 1
                                if cursor_p1[0] > 2:
                                    cursor_p1[0] = 0
                                if cursor_p1[0] == cursor_p2[0] and cursor_p1[1] == cursor_p2[1]:
                                    cursor_p1[0] -= 1
                                    if cursor_p1[0] < 0:
                                        cursor_p1[0] = 2
                                self.menu_1.play()
                            elif e.key == pygame.K_a:
                                cursor_p1[1] -= 1
                                if cursor_p1[1] < 0:
                                    cursor_p1[1] = len(characters[cursor_p1[0]]) - 1
                                if cursor_p1[1] == cursor_p2[1] and cursor_p1[0] == cursor_p2[0]:
                                    cursor_p1[1] += 1
                                    if cursor_p1[1] > len(characters[cursor_p1[0]]) - 1:
                                        cursor_p1[1] = 0
                                self.menu_1.play()
                            elif e.key == pygame.K_d:
                                cursor_p1[1] += 1
                                if cursor_p1[1] > len(characters[cursor_p1[0]]) - 1:
                                    cursor_p1[1] = 0
                                if cursor_p1[1] == cursor_p2[1] and cursor_p1[0] == cursor_p2[0]:
                                    cursor_p1[1] -= 1
                                    if cursor_p1[1] < 0:
                                        cursor_p1[1] = len(characters[cursor_p1[0]]) - 1
                                self.menu_1.play()
                            elif e.key == pygame.K_SPACE:
                                selected_p1 = True
                                self.menu_2.play()
                        else:
                            ## Undo the selection
                            if e.key == pygame.K_SPACE:
                                selected_p1 = False
                                self.menu_1.play()
                                
                        if not selected_p2:
                            ## Allow player 2 to select if he hasn't done so already
                            if e.key == pygame.K_UP:
                                cursor_p2[0] -= 1
                                if cursor_p2[0] < 0:
                                    cursor_p2[0] = 2
                                if cursor_p2[0] == cursor_p1[0] and cursor_p2[1] == cursor_p1[1]:
                                    cursor_p2[0] += 1
                                    if cursor_p2[0] > 2:
                                        cursor_p2[0] = 0
                                self.menu_1.play()
                            elif e.key == pygame.K_DOWN:
                                cursor_p2[0] += 1
                                if cursor_p2[0] > 2:
                                    cursor_p2[0] = 0
                                if cursor_p2[0] == cursor_p1[0] and cursor_p2[1] == cursor_p1[1]:
                                    cursor_p2[0] -= 1
                                    if cursor_p2[0] < 0:
                                        cursor_p2[0] = 2
                                self.menu_1.play()
                            elif e.key == pygame.K_LEFT:
                                cursor_p2[1] -= 1
                                if cursor_p2[1] < 0:
                                    cursor_p2[1] = len(characters[cursor_p2[0]]) - 1
                                if cursor_p2[1] == cursor_p1[1] and cursor_p2[0] == cursor_p1[0]:
                                    cursor_p2[1] += 1
                                    if cursor_p2[1] > len(characters[cursor_p2[0]]) - 1:
                                        cursor_p2[1] = 0
                                self.menu_1.play()
                            elif e.key == pygame.K_RIGHT:
                                cursor_p2[1] += 1
                                if cursor_p2[1] > len(characters[cursor_p2[0]]) - 1:
                                    cursor_p2[1] = 0
                                if cursor_p2[1] == cursor_p1[1] and cursor_p2[0] == cursor_p1[0]:
                                    cursor_p2[1] -= 1
                                    if cursor_p2[1] < 0:
                                        cursor_p2[1] = len(characters[cursor_p2[0]]) - 1
                                self.menu_1.play()
                            elif e.key == pygame.K_RETURN:
                                selected_p2 = True
                                self.menu_2.play()
                        else:
                            ## Undo the selection
                            if e.key == pygame.K_RETURN:
                                selected_p2 = False
                                self.menu_1.play()

                ## Draw everything
                self.screen.blit(self.menuback1, (0,0))
                self.screen.blit(self.logo, (196,48))
                text_remind.draw(self.screen)

                for i in range(3):
                    for j in range(3):
                        pygame.draw.rect(self.screen, (50,50,50), (56*i+24, 46*j+54, 46, 32))
                if not selected_p1:
                    pygame.draw.rect(self.screen, (255,82,82), (56*cursor_p1[1]+24, 46*cursor_p1[0]+54, 46, 32))
                if not selected_p2:
                    pygame.draw.rect(self.screen, (82,82,255), (56*cursor_p2[1]+24, 46*cursor_p2[0]+54, 46, 32))
                    
                for i in range(3):
                    self.screen.blit(self.portraits[i], (56*i+20,50))
                for i in range(3):
                    self.screen.blit(self.portraits[i+3], (56*i+20,96))
                for i in range(3):
                    self.screen.blit(self.portraits[i+6], (56*i+20,142))

                ## Update the reminder text for player 1
                if not selected_p1:
                    pygame.draw.rect(self.screen, (50,50,50), (0,0,400,16))
                    text_top.update("PLAYER 1 SELECTING...")
                else:
                    pygame.draw.rect(self.screen, (255,82,82), (0,0,400,16))
                    text_top.update("PLAYER 1 READY!")

                ## Update the reminder text for player 2
                if not selected_p2:
                    pygame.draw.rect(self.screen, (50,50,50), (0,224,400,16))
                    text_bot.update("PLAYER 2 SELECTING...")
                else:
                    pygame.draw.rect(self.screen, (82,82,255), (0,224,400,16))
                    text_bot.update("PLAYER 2 READY!")

                ## Draw both texts
                text_top.draw(self.screen)
                text_bot.draw(self.screen)

                ## Render everything to the real screen
                pygame.transform.scale(self.screen, (800,480), self.display)
                pygame.display.flip()

        ## Return the character selections for both player 1 and player 2
        return characters[cursor_p1[0]][cursor_p1[1]], characters[cursor_p2[0]][cursor_p2[1]]
        
    def run(self, p1, p2, num):
        ## Pick a random background and scale it to size
        background = pygame.image.load("RES/STAGE/%02d/STAGE.png" %num).convert()
        self.background = pygame.transform.scale(background, (400,300))
        pygame.mixer.music.stop()
        pygame.mixer.music.load("RES/STAGE/%02d/BGM.ogg" %num)
        pygame.mixer.music.set_volume(0.8)
        pygame.mixer.music.play(-1)

        ## Create the fighter objects and the ring
        fighter_1 = self.load_fighter(p1, True, 132, CONST.FLOOR)
        fighter_2 = self.load_fighter(p2, False, 268, CONST.FLOOR)
        ring_1    = self.load_object("RING", 200, 112)

        time = 99
        self.timer_text = Text(str(time), (185,9))
        self.name_1 = Text(fighter_1.name, (56,24), size=8)
        self.name_2 = Text(fighter_2.name, (344,24), size=8, right=True)

        self.text_1 = Text("Ready?", (0,112))
        self.text_2 = Text("Throw!", (0,112))
        self.text_3 = Text("Game set!", (0,112))
        self.text_4 = Text("Paused!", (0,112))
        
        self.countdown = 2

        self.finished = False
        self.paused = False

        while not self.finished:
            tick = self.clock.tick(self.game_fps) / 1500.0
            pygame.display.set_caption("Throw Down: %d FPS" %self.clock.get_fps())
            
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        self.paused = True if not self.paused else False
                    elif not self.paused:
                        if e.key in [pygame.K_a, pygame.K_d]:
                            fighter_1.button_count += 1
                            fighter_1.button_cooldown = CONST.COOLDOWN
                        elif e.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                            fighter_2.button_count += 1
                            fighter_2.button_cooldown = CONST.COOLDOWN

            if self.countdown > 0:
                ## Don't accept input if the countdown is still going
                self.countdown -= tick                
            elif not self.paused:
                ## Update time
                self.timer_text.update("%02d" %(int(time)))
                
                time -= tick
                if time <= 0:
                    time = 0
                    self.finished = True

                fighter_1.buttons = []
                fighter_2.buttons = []

                ## Player 1 keys
                if pygame.key.get_pressed()[K_a]:
                    fighter_1.buttons.append(BUTTON.LEFT)
                if pygame.key.get_pressed()[K_d]:
                    fighter_1.buttons.append(BUTTON.RIGHT)

                if len(fighter_1.buttons) <= 1 and fighter_2.is_grabbed:
                    fighter_2.is_grabbed = False
                if fighter_1.button_cooldown > 0:
                    fighter_1.button_cooldown -= 1
                else:
                    fighter_1.button_count = 0

                ## Player 2 keys
                if pygame.key.get_pressed()[K_LEFT]:
                    fighter_2.buttons.append(BUTTON.LEFT)
                if pygame.key.get_pressed()[K_RIGHT]:
                    fighter_2.buttons.append(BUTTON.RIGHT)

                if len(fighter_2.buttons) <= 1 and fighter_1.is_grabbed:
                    fighter_1.is_grabbed = False
                if fighter_2.button_cooldown > 0:
                    fighter_2.button_cooldown -= 1
                else:
                    fighter_2.button_count = 0

            if not self.paused:
                ## Get collisions
                collision_1 = None
                collision_2 = None
                collision_3 = None
                collision_4 = None

                if self.check_collision(fighter_1.hitbox, fighter_2.hurtbox, fighter_1.hitbox_rect, fighter_2.hurtbox_rect):
                    if fighter_1.state == STATE.GRAB:
                        collision_1 = 1
                if self.check_collision(fighter_2.hitbox, fighter_1.hurtbox, fighter_2.hitbox_rect, fighter_1.hurtbox_rect):
                    if fighter_2.state == STATE.GRAB:
                        collision_2 = 1
                if self.check_collision(ring_1.hitbox, fighter_1.hurtbox, ring_1.hitbox_rect, fighter_1.hurtbox_rect):
                    collision_3 = 1
                if self.check_collision(ring_1.hitbox, fighter_2.hurtbox, ring_1.hitbox_rect, fighter_2.hurtbox_rect):
                    collision_4 = 1

                ## Modify throw vectors
                if fighter_1.face_right:
                    fighter_1.throw_vector = fighter_1.right_vector[:]
                    fighter_2.throw_vector = fighter_2.left_vector[:]
                else:
                    fighter_2.throw_vector = fighter_2.right_vector[:]
                    fighter_1.throw_vector = fighter_1.left_vector[:]

                if fighter_1.display_super >= fighter_1.max_super:
                    fighter_1.throw_vector[0] = int(fighter_1.throw_vector[0] * 2.25)
                    fighter_1.throw_vector[1] = int(fighter_1.throw_vector[1] * 1.525)
                if fighter_2.display_super >= fighter_2.max_super:
                    fighter_2.throw_vector[0] = int(fighter_2.throw_vector[0] * 2.25)
                    fighter_2.throw_vector[1] = int(fighter_2.throw_vector[1] * 1.425)

                ## Update the fighters
                if fighter_1.state != STATE.FLYING_A:
                    fighter_1.update(self.fighter_fps, fighter_2, collision_2)
                    fighter_2.update(self.fighter_fps, fighter_1, collision_1)
                elif fighter_2.state != STATE.FLYING_A:
                    fighter_2.update(self.fighter_fps, fighter_1, collision_1)
                    fighter_1.update(self.fighter_fps, fighter_2, collision_2)
                else:
                    fighter_1.update(self.fighter_fps, fighter_2, collision_2)
                    fighter_2.update(self.fighter_fps, fighter_1, collision_1)

                if fighter_1.display_health <= 0 or fighter_2.display_health <= 0:
                    self.finished = True
                    
                fighter_list_1 = []
                obj_list = [ring_1]
                
                if collision_3:
                    fighter_list_1.append(fighter_1)
                if collision_4:
                    fighter_list_1.append(fighter_2)
                    
                ring_1.update(self.obj_fps, fighter_list_1)

            self.draw_screen(fighter_1, fighter_2, obj_list)
            pygame.display.flip()

        self.countdown = 3
        while self.finished:
            tick = self.clock.tick(self.game_fps) / 1500.0
            self.countdown -= tick
            if self.countdown < 0:
                self.countdown = 0
                
            pygame.display.set_caption("Throw Down: %d FPS" %self.clock.get_fps())

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif self.countdown == 0:
                        self.finished = False

            self.draw_screen(fighter_1, fighter_2, obj_list)                
            pygame.display.flip()

        if fighter_1.health < fighter_2.health:
            return RESULTS.P2_WIN
        elif fighter_2.health < fighter_1.health:
            return RESULTS.P1_WIN
        else:
            return RESULTS.DRAW

    def load_object(self, name, x, y):
        fi = open("RES/OBJECT/%s/DATA" %name, "r").readlines()

        ## Default values to fall back on, in case the DATA file is corrupt
        name = "NULL"
        sf_str = "SPRITE.png" ## Sprite file
        hi_str = "HIT.png"    ## Hitbox image

        sp = 1
        ad = [0,1]
        fr = [1,1]

        ## Parse through the DATA file to get the proper values
        for line in fi:
            ## Name string
            if line.startswith("name:"):
                name = line.lstrip("name:").rstrip()
            ## Sprite images
            elif line.startswith("sprite_file:"):
                sf_str = line.lstrip("sprite_file:").rstrip()
            ## Hitbox image
            elif line.startswith("hit_file:"):
                hi_str = line.lstrip("hit_file:").rstrip()
            ## Frame count for idling
            elif line.startswith("speed:"):
                sp = int(line.lstrip("speed:").rstrip())
            ## Frame count for idling
            elif line.startswith("back_frame:"):
                fr[0] = int(line.lstrip("back_frame:").rstrip())
            ## Frame count for idling
            elif line.startswith("front_frame:"):
                fr[1] = int(line.lstrip("front_frame:").rstrip())
            ## Attack damage range
            elif line.startswith("attack_damage:"):
                damage = line.lstrip("attack_damage:").rstrip().split(",")
                ad[0] = int(damage[0])
                ad[1] = int(damage[1])

        ## Get the image described by sf_str and make it transparent
        sf = pygame.image.load("RES/OBJECT/%s/" %(name) + sf_str).convert()
        sf.set_colorkey((0,0,0))

        ## Get the image described by sf_str and make it transparent
        hi = pygame.image.load("RES/OBJECT/%s/" %(name) + hi_str).convert()
        hi.set_colorkey((0,0,0))

        obj = Object(name, sf, hi, sp, ad, fr, x, y)

        return obj
            
    def load_fighter(self, num, face, x, y):
        ## Load the DATA file into memory
        fi = open("RES/CHAR/%02d/DATA" %num, "r").readlines()

        ## Default values to fall back on, in case the DATA file is corrupt
        name = "NULL"
        sf_str = "SPRITE.png" ## Sprite file
        of_str = "EXTRA.png"  ## Other images
        hi_str = "HIT.png"    ## Hitbox image
        hu_str = "HURT.png"   ## Hurtbox image
        he = 1            ## Health
        sp = 1            ## Speed
        jp = 1            ## Jump
        mc = 400          ## Max super
        tv = [0,0]        ## Throw vector
        ad = 1            ## Attack damage
        at = 0            ## Attack type
        fr = [1,1,1,1,1,1,1,1,1,1,1,1,1] ## Frame count

        ## Parse through the DATA file to get the proper values
        for line in fi:
            ## Name string
            if line.startswith("name:"):
                name = line.lstrip("name:").rstrip()
            ## Sprite images
            elif line.startswith("sprite_file:"):
                sf_str = line.lstrip("sprite_file:").rstrip()
            ## Other images
            elif line.startswith("other_file:"):
                of_str = line.lstrip("other_file:").rstrip()
            ## Hitbox image
            elif line.startswith("hit_file:"):
                hi_str = line.lstrip("hit_file:").rstrip()
            ## Hurtbox image
            elif line.startswith("hurt_file:"):
                hu_str = line.lstrip("hurt_file:").rstrip()
            ## Frame count for idling
            elif line.startswith("idle_frame:"):
                fr[0] = int(line.lstrip("idle_frame:").rstrip())
            ## Frame count for walking
            elif line.startswith("walk_frame:"):
                fr[1] = int(line.lstrip("walk_frame:").rstrip())
            ## Frame count for backdashing
            elif line.startswith("back_frame:"):
                fr[2] = int(line.lstrip("back_frame:").rstrip())
            ## Frame count for crouching
            elif line.startswith("crouch_frame:"):
                fr[3] = int(line.lstrip("crouch_frame:").rstrip())
            ## Frame count for jumping
            elif line.startswith("jump_frame:"):
                fr[4] = int(line.lstrip("jump_frame:").rstrip())
            ## Frame count for blocking
            elif line.startswith("block_frame:"):
                fr[5] = int(line.lstrip("block_frame:").rstrip())
            ## Frame count for being thrown
            elif line.startswith("fall_a_frame:"):
                fr[6] = int(line.lstrip("fall_a_frame:").rstrip())
            ## Frame count for flying through the air
            elif line.startswith("fall_b_frame:"):
                fr[7] = int(line.lstrip("fall_b_frame:").rstrip())
            ## Frame count for hitting the ground
            elif line.startswith("fall_c_frame:"):
                fr[8] = int(line.lstrip("fall_c_frame:").rstrip())
            ## Frame count for being downed
            elif line.startswith("down_frame:"):
                fr[9] = int(line.lstrip("down_frame:").rstrip())
            ## Frame count for grabbing
            elif line.startswith("grab_frame:"):
                fr[10] = int(line.lstrip("grab_frame:").rstrip())
            ## Frame count for throwing
            elif line.startswith("throw_frame:"):
                fr[11] = int(line.lstrip("throw_frame:").rstrip())
            ## Frame count for being dead
            elif line.startswith("dead_frame:"):
                fr[12] = int(line.lstrip("dead_frame:").rstrip())
            ## Health value
            elif line.startswith("health:"):
                he = int(line.lstrip("health:").rstrip())
            ## Speed value
            elif line.startswith("speed:"):
                sp = int(line.lstrip("speed:").rstrip())
            ## Jump value
            elif line.startswith("jump:"):
                jp = int(line.lstrip("jump:").rstrip())
            ## Max super
            elif line.startswith("max_combo:"):
                mc = int(line.lstrip("max_combo:").rstrip())
            ## Throwing direction
            elif line.startswith("throw_vector:"):
                vector = line.lstrip("throw_vector:").rstrip().split(",")
                tv[0] = int(vector[0])
                tv[1] = int(vector[1])
            ## Attack damage range
            elif line.startswith("attack_damage:"):
                ad = int(line.lstrip("attack_damage:").rstrip())

        ## Get the image described by sf_str and make it transparent
        sf = pygame.image.load("RES/CHAR/%02d/" %(num) + sf_str).convert()
        sf.set_colorkey((0,0,0))
        
        ## Get the image described by sf_str and make it transparent
        af = pygame.image.load("RES/CHAR/%02d/" %(num) + sf_str).convert()
        af.set_alpha(128)
        af.set_colorkey((0,0,0))

        ## Get the image described by of_str and make it transparent
        of = pygame.image.load("RES/CHAR/%02d/" %(num) + of_str).convert()
        of.set_colorkey((0,0,0))

        ## Get the image described by hi_str
        hi = pygame.image.load("RES/CHAR/%02d/" %(num) + hi_str).convert()
        hi.set_colorkey((0,0,0))

        ## Get the image described by hu_str
        hu = pygame.image.load("RES/CHAR/%02d/" %(num) + hu_str).convert()
        hu.set_colorkey((0,0,0))

        fighter = Fighter(name, sf, af, of, hi, hu, he, sp, jp, tv, mc, ad, fr, face, x, y)

        return fighter

if __name__ == "__main__":
    main = Main()
