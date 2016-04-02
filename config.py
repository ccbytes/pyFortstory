#!/bin/python

import math


# CLIENT
TICKS_PER_SEC = 60


# WORLD
SECTOR_SIZE = 12
PLAYER_REACH = 3 # max distance player can interact with objects
WORLD_SIZE = 42 # Size of sectors used to ease block loading.
GRAVITY = 12.0
TERMINAL_VELOCITY = 50


# PLAYER
WALKING_SPEED = 7
FLYING_SPEED = 15
MAX_JUMP_HEIGHT = 2.0 # About the height of a block.
# To derive the formula for calculating jump speed, first solve
#    v_t = v_0 + a * t
# for the time at which you achieve maximum height, where a is the acceleration
# due to gravity and v_t = 0. This gives:
#    t = - v_0 / a
# Use t and the desired MAX_JUMP_HEIGHT to solve for v_0 (jump speed) in
#    s = s_0 + v_0 * t + (a * t^2) / 2
JUMP_SPEED = math.sqrt(2 * GRAVITY * MAX_JUMP_HEIGHT)
PLAYER_HEIGHT = 2
PLAYER_REACH = 3 # max distance player can interact with objects
