## Static structure to contain some constants
class CONST:
    GRAVITY = 1
    FLOOR = 208
    LEFT = 0
    RIGHT = 400
    IMAGE_WIDTH = 32
    FPS = 60
    OBJ_FRAMERATE = 2
    FRAMERATE = 8
    COOLDOWN = 15

## Static structure to contain results of a match
class RESULTS:
    DRAW   = 1
    P1_WIN = 2
    P2_WIN = 4

## Static structure to contain the various states of a fighter
class STATE:
    IDLE      = 0
    WALK      = 1
    BACK      = 2
    CROUCH    = 3
    JUMP      = 4
    GUARD     = 5
    FLYING_A  = 6
    FLYING_B  = 7
    FLYING_C  = 8
    DOWN      = 9
    GRAB      = 10
    THROW     = 11
    DEAD      = 12
    
## Static structure to contain the various buttons to be pressed
class BUTTON:
    LEFT    = 1
    RIGHT   = 2
