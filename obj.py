import pygame, random
from pygame.locals import *
from const import CONST, STATE

class Object(object):
    def __init__(self, name, sf, hi, sp, ad, fr, x, y):
        ## Name (string)
        self.name = name

        ## Sprite file (Pygame surface)
        self.sprite_file = self.create_images(sf, False, frames=fr)
        ## Hitbox file (Pygame surface)
        self.hitbox_file = self.create_images(hi, True, frames=fr)

        self.speed = sp          ## Speed of the object
        self.frame_data = fr     ## Number of frames per animation sequence
        self.attack_damage = ad  ## Damage that is dealt upon collision

        ## Other constants to initialize
        self.xpos = x            ## X-coordinate
        self.ypos = y            ## Y-coordinate
        self.frame = 0           ## Current frame of animation
        self.frame_counter = 0   ## Tracks frames per second
        self.back_image   = self.sprite_file[0][self.frame] ## Background image to display
        self.front_image  = self.sprite_file[1][self.frame] ## Foreground image to display
        self.hitbox_im    = self.hitbox_file[self.frame]    ## Current hitbox

        ## Hitbox and hurtbox data
        self.hitbox = pygame.mask.from_surface(self.hitbox_im)
        self.hitbox_rect = self.hitbox_im.get_rect()
        self.hitbox_rect.center = [self.xpos,self.ypos]

        ## Boolean values
        self.is_moving_left  = True
        self.is_moving_right = False

    def create_images(self, image, is_hitbox=False, frames=None):
        ## Set up a new array of images for animation of this object
        image_array = []
        if not is_hitbox:
            ## If we're looking at a sprite image, read in the foreground and background
            for n in range(2):
                image_array.append([])
            for n in range(2):
                for p in range(frames[n]):
                    sub = image.subsurface(p*16,n*16,16,16)
                    sub = pygame.transform.scale(sub, (64,64))
                    image_array[n].append(sub)
        else:
            ## If we're looking at the hitbox image, just put it in the array as-is
            for p in range(frames[0]):
                sub = image.subsurface(p*16,0,16,16)
                sub = pygame.transform.scale(sub, (64,64))
                image_array.append(sub)

        return image_array

    def update(self, fps, fighters):
        ## Handle what happens during each frame
        
        for fighter in fighters:
            ## Damage the fighter if they collided with this object
            if fighter.state in [STATE.FLYING_A, STATE.FLYING_B, STATE.FLYING_C]:
                fighter.damage_sound.play()
                fighter.health -= random.randint(self.attack_damage[0], self.attack_damage[1])
                if fighter.health <= 0:
                    fighter.health = 0
                    fighter.state = STATE.FLYING_C

        ## Move left until 25% of the screen width, then turn around
        if self.is_moving_left:
            self.xpos -= self.speed
            if self.xpos <= abs(CONST.RIGHT - CONST.LEFT) / 4:
                self.is_moving_left = False
                self.is_moving_right = True
        ## Move right until 75% of the screen width, then turn around
        elif self.is_moving_right:
            self.xpos += self.speed
            if self.xpos >= abs(CONST.RIGHT - CONST.LEFT) * 3 / 4:
                self.is_moving_left = True
                self.is_moving_right = False
        
        ## Image handling
        self.frame_counter += 1 ## Tick up the frame counter
        if self.frame_counter > fps:
            ## If we've exceeded the frame counter, loop back to the beginning of animation
            self.frame_counter = 0
            self.frame += 1
            if self.frame > self.frame_data[0] - 1:
                self.frame = 0
            self.back_image   = self.sprite_file[0][self.frame] ## New background sprite
            self.front_image  = self.sprite_file[1][self.frame] ## New foreground sprite
            self.hitbox_im    = self.hitbox_file[self.frame]    ## New hitbox
            
        ## Update the hitbox rect objects
        self.hitbox = pygame.mask.from_surface(self.hitbox_im)
        self.hitbox_rect = self.hitbox_im.get_rect()
        self.hitbox_rect.center = [self.xpos,self.ypos]
