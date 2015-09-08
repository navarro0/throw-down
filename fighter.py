import pygame, random
from pygame.locals import *
from const import CONST, STATE, BUTTON

## Fighter class; describes one of two players in a match
class Fighter(object):
    def __init__(self, name, sf, af, of, hi, hu, he, sp, jp, tv, mc, ad, fr, face, x, y):
        ## Name (string)
        self.name = name

        ## Sound effects
        self.collide      = pygame.mixer.Sound("RES/SOUND/COLLIDE.ogg")  ## Plays whenever a collision is made
        self.critical     = pygame.mixer.Sound("RES/SOUND/CRITICAL.ogg") ## Plays whenever a critical throw is made
        self.damage_sound = pygame.mixer.Sound("RES/SOUND/DAMAGE.ogg")   ## Plays whenever damage is taken
        self.grab         = pygame.mixer.Sound("RES/SOUND/GRAB.ogg")     ## Plays whenever a grab is attempted
        self.throw        = pygame.mixer.Sound("RES/SOUND/THROW.ogg")    ## Plays whenever a normal throw is made

        ## Sprite file (Pygame surface)
        self.sprite_file = self.create_images(sf, face, False, frames=fr)
        ## Afterimage file (Pygame surface)
        self.after_file = self.create_images(af, face, False, frames=fr)
        ## Portrait file (Pygame surface)
        self.other_file = self.create_images(of, face, True)
        ## Hitbox file (Pygame surface)
        self.hitbox_file = self.create_images(hi, face, False, frames=fr)
        ## Hurtbox file (Pygame surface)
        self.hurtbox_file = self.create_images(hu, face, False, frames=fr)
        
        self.health        = he      ## Health (int)
        self.speed         = sp      ## Speed (int)
        self.jump          = jp      ## Jump (int)
        self.max_super     = mc      ## Max super (int)
        self.right_vector  = tv[:]   ## Throw vector if facing right
        self.left_vector   = tv[:]   ## Throw vector if facing left
        self.left_vector[0] *= -1
        ## Current throwing vector
        self.throw_vector  = self.right_vector[:] if face else self.left_vector[:]
        self.attack_damage = ad      ## Attack damage (int)
        self.frame_data    = fr      ## Frame count (int 13-array)
        self.buttons = []
        self.button_cooldown = CONST.COOLDOWN
        self.button_count = 0

        ## Other constants to initialize
        self.xpos = x            ## X position 
        self.ypos = y            ## Y position
        self.old_pos = []        ## Array of old positions for afterimage effects
        self.state = STATE.IDLE  ## State handler
        self.face_right = face   ## Facing right or not (Boolean)

        self.super = 0           ## Counter for consecutive, uninterrupted throws
        self.display_super = 0   ## Displayable super meter
        self.frame_counter = 0   ## Animation counter
        self.gravity = 0         ## Air-time counter
        self.anti_grab = 0       ## Counter to escape grabs
        self.other_throw_vector = [0,0] ## Other throwing vector
        self.frame = 0           ## Current frame of animation
        self.image   = self.sprite_file[self.state][self.frame]   ## Image to display
        self.afterimage = self.after_file[self.state][self.frame] ## Afterimage to display
        
        self.max_health     = he ## Maximum health value
        self.display_health = he ## Displayed health meter

        ## Hitbox and hurtbox data
        self.hitbox_im  = self.hitbox_file[self.state][self.frame]
        self.hurtbox_im = self.hurtbox_file[self.state][self.frame]
        self.hitbox  = pygame.mask.from_surface(self.hitbox_im)   ## Current hitbox
        self.hurtbox = pygame.mask.from_surface(self.hurtbox_im)  ## Current hurtbox
        self.hitbox_rect = self.hitbox_im.get_rect()
        self.hitbox_rect.midbottom = [self.xpos,self.ypos]
        self.hurtbox_rect = self.hurtbox_im.get_rect()
        self.hurtbox_rect.midbottom = [self.xpos,self.ypos]
        
        ## Boolean variables
        self.is_grabbed = False ## Differentiates between being grabbed and being thrown
        self.is_moving_left = False ## Controls whether we move left
        self.is_moving_right = False ## Controls whether we move right
        self.reverse_dir = False
        self.dashing = False
        
    def create_images(self, image, face, other_file, frames=None):
        ## Load images into arrays
        if other_file:
            ## If we're dealing with portraits, just scale them
            portrait = pygame.transform.scale(image, (52,40))
            if not face:
                portrait = pygame.transform.flip(portrait, True, False)
            
            ## Set up a new array of images for formality's sake
            image_array = [portrait]
        else:
            ## If we're dealing with basic animation frames, set up a new array
            image_array = []
            for n in range(13):
                image_array.append([])
            for n in range(13):
                for p in range(frames[n]):
                    sub = image.subsurface(p*16,n*16,16,16)
                    sub = pygame.transform.scale(sub, (64,64))
                    image_array[n].append(sub)

        return image_array

    def get_grabbed(self):
        ## Handles what happens when you get grabbed by the opponent
        self.state = STATE.FLYING_A ## Grab animation
        self.is_grabbed = True      ## Grabbed sub-state
        self.ypos -= 5              ## Get lifted off the ground
        self.grab.play()            ## Play the sound effect

    def update(self, fps, enemy, enemy_collision):
        ## State handling
        state = self.state ## Default case is that we haven't changed our state

        ## Old position queue is updated for afterimage purposes
        self.old_pos.append((self.xpos, self.ypos))
        if len(self.old_pos) > 2:
            self.old_pos = self.old_pos[1:]

        ## Animate health meter
        if self.display_health > self.health:
            self.display_health -= 5
        elif self.display_health < self.health:
            self.display_health = self.health

        ## Animate super meter
        if self.display_super < self.super:
            self.display_super += 5
            if self.display_super > self.max_super:
                self.display_super = self.max_super
        elif self.display_super > self.super:
            self.display_super -= 10
            if self.display_super < 0:
                self.display_super = 0
        
        ## Idle state
        if state == STATE.IDLE:
            ## Control variables are reset
            self.hit_ceiling = False
            self.is_grabbed = False
            self.reverse_dir = False
            self.is_moving_left = False
            self.is_moving_right = False

            ## It is possible to be grabbed out of this state
            if enemy_collision == 1:
                self.get_grabbed()
                
            ## Horizontal movement
            elif BUTTON.LEFT in self.buttons and BUTTON.RIGHT not in self.buttons:
                ## If facing right, a left button press is a backstep
                if self.face_right:
                    self.state = STATE.BACK
                ## Otherwise, it's a forward walking motion
                else:
                    self.state = STATE.WALK
                self.moving_left = True
                self.dashing = True if (self.button_count >= 2 and self.button_cooldown > 0) else False
                
            elif BUTTON.RIGHT in self.buttons and BUTTON.LEFT not in self.buttons:
                ## If facing right, a right button press is a forward walking motion
                if self.face_right:
                    self.state = STATE.WALK
                ## Otherwise, it's a backstep
                else:
                    self.state = STATE.BACK
                self.moving_right = True
                self.dashing = True if (self.button_count >= 2 and self.button_cooldown > 0) else False
                
            ## Grabbing motion
            elif BUTTON.LEFT in self.buttons and BUTTON.RIGHT in self.buttons:
                self.state = STATE.GRAB

        ## Walking or backing-up state
        elif state == STATE.WALK or state == STATE.BACK:
            ## Prevents random sliding
            self.is_moving_left = False
            self.is_moving_right = False
            
            ## It is possible to be grabbed out of this state
            if enemy_collision == 1:
                self.get_grabbed()

            ## Button inputs
            elif len(self.buttons) == 0:
                ## If no buttons are being pressed, we assume the idle state
                self.state = STATE.IDLE
                
            ## Horizontal movement
            elif BUTTON.LEFT in self.buttons and BUTTON.RIGHT not in self.buttons:
                if self.face_right:
                    self.state = STATE.BACK
                else:
                    self.state = STATE.WALK
                self.is_moving_left = True
                self.dashing = True if (self.button_count >= 2 and self.button_cooldown > 0) else False
                
            ## Horizontal movement
            elif BUTTON.RIGHT in self.buttons and BUTTON.LEFT not in self.buttons:
                if self.face_right:
                    self.state = STATE.WALK
                else:
                    self.state = STATE.BACK
                self.is_moving_right = True
                self.dashing = True if (self.button_count >= 2 and self.button_cooldown > 0) else False
                
            ## Grabbing motion
            elif BUTTON.LEFT in self.buttons and BUTTON.RIGHT in self.buttons:
                self.state = STATE.GRAB

        ## Flying state A
        elif state == STATE.FLYING_A:
            if not self.is_grabbed:
                ## Reset the grapple escape counter
                self.anti_grab = 0

                ## If the enemy is throwing and we are not grabbed but are still in this state,
                ## we assume that we have been thrown
                if enemy.state == STATE.THROW:
                    
                    ## If the enemy's super meter is maxed out, drain it, and play the critical sound
                    if enemy.display_super >= enemy.max_super:
                        enemy.super = 0
                        enemy.critical.play()

                    ## Modify the dx motion according to the opponent's throw vector
                    dx = self.other_throw_vector[0]
                    if self.reverse_dir:
                        dx *= -1
                    self.xpos += dx

                    ## Handle ceiling collisions
                    if self.ypos - CONST.IMAGE_WIDTH*2 > 0 and not self.hit_ceiling:
                        dy = self.other_throw_vector[1] - self.gravity * CONST.GRAVITY
                        self.ypos -= dy
                    else:
                        self.hit_ceiling = True
                        dy = self.other_throw_vector[1] + self.gravity * CONST.GRAVITY
                        self.ypos += dy

                    ## Tick up gravity accelerator
                    self.gravity += 1

                    ## Immediately switch to the second flying state
                    self.state = STATE.FLYING_B
                    self.hit_ceiling = False
                    self.throw.play()
                        
                else:
                    ## If the enemy is not throwing but we are in the sstate, we assume
                    ## that we have simply been let go of
                    self.state = STATE.IDLE
                    self.ypos = CONST.FLOOR
            else:
                if enemy.state == STATE.FLYING_A:
                    ## If we are grabbed but the opponent is also in this state, we must
                    ## prevent both fighters from being in the air at the same time
                    self.state = STATE.IDLE
                    self.ypos = CONST.FLOOR
                else:
                    ## Store the opponent's throwing vector into a member variable
                    temp_throw_vector = enemy.throw_vector[:]
                    temp_throw_vector[0] += random.randint(-1,1)
                    temp_throw_vector[1] += random.randint(-1,1)
                    self.other_throw_vector = temp_throw_vector
                    
                    ## Handle attempts to break free of the grab
                    if len(self.buttons) != 0:
                        self.anti_grab += 1
                        ## If we've pressed enough buttons, break free
                        if self.anti_grab >= 20:
                            self.anti_grab = 0
                            self.ypos += 5
                            self.state = STATE.IDLE
                    else:
                        ## If you stop struggling to get away, the counter resets
                        self.anti_grab = 0
        
        ## Flying state B
        elif state == STATE.FLYING_B:
            ## Allow for directional influence in the air
            if BUTTON.LEFT in self.buttons:
                self.is_moving_left = True
            elif BUTTON.RIGHT in self.buttons:
                self.is_moving_right = True

            ## Modify the dx motion according to the opponent's throw vector
            dx = self.other_throw_vector[0]
            if self.reverse_dir:
                dx *= -1
            self.xpos += dx

            ## Handle ceiling collision
            if self.ypos - CONST.IMAGE_WIDTH*2 > 0 and not self.hit_ceiling:
                dy = self.other_throw_vector[1] - self.gravity * CONST.GRAVITY
                self.ypos -= dy
            else:
                if not self.hit_ceiling:
                    ## Once per collision, we gain some super meter as compensation
                    self.collide.play()
                    percentage = float(enemy.display_super) / enemy.max_super
                    self.health -= int(self.max_health * 0.025 * percentage)
                    self.super += 20
                    if self.super > self.max_super:
                        self.super = self.max_super
                self.hit_ceiling = True
                dy = self.other_throw_vector[1] + self.gravity * CONST.GRAVITY
                self.ypos += dy

            ## Tick up gravity accelerator
            self.gravity += 1

            ## If we've reached the peak of our flight, switch to the falling state
            if dy <= 0:
                self.hit_ceiling = False
                self.state = STATE.FLYING_C

            ## If we've hit the floor, ricochet off it
            if self.ypos >= CONST.FLOOR:
                self.hit_ceiling = False
                self.ypos = CONST.FLOOR
                self.collide.play()
                ## Gain some super meter as compensation
                percentage = float(enemy.display_super) / enemy.max_super
                self.health -= int(self.max_health * 0.025 * percentage)
                self.super += 20
                if self.super > self.max_super:
                    self.super = self.max_super

        ## Flying state C
        elif state == STATE.FLYING_C:
            ## Allow for directional influence in the air
            if BUTTON.LEFT in self.buttons:
                self.is_moving_left = True
            elif BUTTON.RIGHT in self.buttons:
                self.is_moving_right = True

            ## Modify the dx motion according to the opponent's throw vector
            dx = self.other_throw_vector[0]
            if self.reverse_dir:
                dx *= -1
            self.xpos += dx

            ## Handle ceiling collision
            if self.ypos - CONST.IMAGE_WIDTH*2 > 0 and not self.hit_ceiling:
                dy = self.other_throw_vector[1] - self.gravity * CONST.GRAVITY
                self.ypos -= dy
            else:
                if not self.hit_ceiling:
                    ## Once per collision, we gain some super meter as compensation
                    self.collide.play()
                    percentage = float(enemy.display_super) / enemy.max_super
                    self.health -= int(self.max_health * 0.025 * percentage)
                    self.super += 20
                    if self.super > self.max_super:
                        self.super = self.max_super
                self.hit_ceiling = True
                dy = self.other_throw_vector[1] + self.gravity * CONST.GRAVITY
                self.ypos += dy

            ## Tick up the gravity accelerator
            self.gravity += 1

            if self.ypos >= CONST.FLOOR:
                ## If we've hit the floor, switch to the downed state
                self.gravity = 0
                self.ypos = CONST.FLOOR
                self.state = STATE.DOWN
                ## We gain some super meter as compensation
                self.collide.play()
                percentage = float(enemy.display_super) / enemy.max_super
                self.health -= int(self.max_health * 0.025 * percentage)
                self.super += 20
                if self.super > self.max_super:
                    self.super = self.max_super

        ## Downed state
        elif state == STATE.DOWN:
            if self.health > 0:
                ## If we're still alive, stand back up
                self.state = STATE.IDLE
            else:
                ## If we're dead... Well, we're dead
                self.is_moving_left = False
                self.is_moving_right = False
                self.state = STATE.DEAD
                
        ## Grabbing state
        elif state == STATE.GRAB:
            ## Allow ourselves to get grabbed out of this state
            if enemy_collision == 1:
                self.get_grabbed()

            if enemy.is_grabbed:
                ## Disallow movement once the enemy is grabbed
                self.is_moving_left = False
                self.is_moving_right = False

            ## Button inputs
            elif BUTTON.LEFT not in self.buttons or BUTTON.RIGHT not in self.buttons:
                ## If either button is released, throw the enemy if we're at the appropriate frame
                if self.frame == self.frame_data[self.state] - 1:
                    self.state = STATE.THROW
                else:
                    self.state = STATE.IDLE

        ## Throwing state
        elif state == STATE.THROW:
            ## Disallow movement during a throw
            self.is_moving_left = False
            self.is_moving_right = False
            ## Play through the entire throw animation before returning to idle state
            if self.frame == self.frame_data[self.state] - 1:
                self.state = STATE.IDLE

        ## Handle dx motion due to walking or attempted directional influence
        dx = self.speed * (2 if self.dashing else 1)
        if self.state == STATE.BACK:
            ## Backing up is 80% as fast as walking forward
            dx = int(dx * 0.8)
        elif self.state in [STATE.FLYING_B, STATE.FLYING_C]:
            ## Directional influence is 40% effective
            dx = int(dx * 0.4)

        ## Apply motion for left or right
        if self.is_moving_left:
            self.xpos -= dx
        elif self.is_moving_right:
            self.xpos += dx
                
        if self.ypos < CONST.FLOOR and self.state not in [STATE.FLYING_A, STATE.FLYING_B, STATE.FLYING_C]:
            ## If we're in the air for whatever reason...
            if self.reverse_dir:
                self.xpos -= self.other_throw_vector[0]
            else:
                self.xpos += self.other_throw_vector[0]

            ## Do something with the jump stat
            dy = self.jump - self.gravity * CONST.GRAVITY

            ## Modify Y-coordinate and tick up gravity
            self.ypos -= dy
            self.gravity += 1

            if self.ypos >= CONST.FLOOR:
                ## If we've hit the floor, reset all relevant variables and stop moving
                self.ypos = CONST.FLOOR
                self.gravity = 0
                self.other_throw_vector = [0,0]
                self.is_moving_right = False
                self.is_moving_left = False

        ## Correction for collision with screen edges
        if self.xpos > CONST.RIGHT or self.xpos < CONST.LEFT:
            if self.state != STATE.DEAD and self.ypos < CONST.FLOOR:
                ## Gain super meter as compensation for collision
                self.collide.play()
                percentage = float(enemy.display_super) / enemy.max_super
                self.health -= int(self.max_health * 0.025 * percentage)
                self.super += 20
                if self.super > self.max_super:
                    self.super = self.max_super
                self.reverse_dir = True if not self.reverse_dir else False
                
            ## Don't go beyond boundaries
            if self.xpos > CONST.RIGHT:
                self.xpos = CONST.RIGHT
            elif self.xpos < CONST.LEFT:
                self.xpos = CONST.LEFT
        
        ## Image handling
        self.frame_counter += 1 ## Tick up the frame counter to animate

        ## If our new state is different from the old one
        if self.state != state:
            self.frame_counter = 0                                    ## Play animation from beginning
            self.frame = 0                                            ## Play animation from beginning
            self.image = self.sprite_file[self.state][self.frame]     ## Load the new state's image
            self.afterimage = self.after_file[self.state][self.frame] ## Load the new state's afterimage
            self.hitbox_im  = self.hitbox_file[self.state][self.frame]   ## New hitbox
            self.hurtbox_im = self.hurtbox_file[self.state][self.frame]  ## New hurtbox
            ## Flip everything horizontally if facing left
            if not self.face_right:
                self.image = pygame.transform.flip(self.image, True, False)
                self.afterimage = pygame.transform.flip(self.afterimage, True, False)
                self.hitbox_im = pygame.transform.flip(self.hitbox_im, True, False)
                self.hurtbox_im = pygame.transform.flip(self.hurtbox_im, True, False)
            self.hitbox = pygame.mask.from_surface(self.hitbox_im)
            self.hurtbox = pygame.mask.from_surface(self.hurtbox_im)
                
        ## If we've exceeded the frame counter, move to the next frame
        elif self.frame_counter > fps:
            self.frame_counter = 0                                    ## Play animation from beginning
            self.frame += 1                                           ## Move to next frame
            if self.frame > self.frame_data[self.state] - 1:          ## Loop back to start of animation unless we're grabbing
                if self.state != STATE.GRAB:
                    self.frame = 0
                else:
                    self.frame = self.frame_data[self.state] - 1
            self.image = self.sprite_file[self.state][self.frame]     ## Load the new image
            self.afterimage = self.after_file[self.state][self.frame] ## Load the new afterimage
            self.hitbox_im  = self.hitbox_file[self.state][self.frame]   ## New hitbox
            self.hurtbox_im = self.hurtbox_file[self.state][self.frame]  ## New hurtbox
            ## Flip everything horizontally if facing left
            if not self.face_right:
                self.image = pygame.transform.flip(self.image, True, False)
                self.afterimage = pygame.transform.flip(self.afterimage, True, False)
                self.hitbox_im = pygame.transform.flip(self.hitbox_im, True, False)
                self.hurtbox_im = pygame.transform.flip(self.hurtbox_im, True, False)
            self.hitbox = pygame.mask.from_surface(self.hitbox_im)
            self.hurtbox = pygame.mask.from_surface(self.hurtbox_im)

        ## Get new hitbox and new hurtbox
        self.hitbox_rect = self.hitbox_im.get_rect()
        self.hitbox_rect.midbottom = [self.xpos,self.ypos]
        self.hurtbox_rect = self.hurtbox_im.get_rect()
        self.hurtbox_rect.midbottom = [self.xpos,self.ypos]
