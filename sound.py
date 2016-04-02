#!/bin/python

from pyglet.resource import media
from pyglet.media import Player

player_fx_interact = Player()
player_fx_walk = Player()
player_music = Player()
player_ambience = Player()
player_fx_interact.volume = 0.8
player_fx_walk.volume = 0.3
player_music.volume = 0.1
player_ambience.volume = 0.8
player_ambience.pitch = 0.6
    
effects = {'player_respawn': media('assets/music/opengameart-org/magic-missile.wav', streaming=False),
           'player_interact_block_dirt': media('assets/music/freesound-org/crunch1.wav', streaming=False),
           'player_jump': media('assets/music/freesound-org/jump2.wav', streaming=False),
           'player_walk': media('assets/music/opengameart-org/stepdirt_1.wav', streaming=False)
           }

songs = {'nice1': media('assets/music/soundimage-org/monkey-island-band_looping.wav', streaming=False)
         }


ambience = {'wind': [media('assets/music/opengameart-org/wind0.wav', streaming=False),            
                     media('assets/music/opengameart-org/wind1.wav', streaming=False),
                     media('assets/music/opengameart-org/wind2.wav', streaming=False)]
            }


def play_effect_interact(fx, action):

    if 'LOOP' in action:
        player_fx_interact.eos_action = player_fx_interact.EOS_LOOP
    
    if 'STOP' or 'NONE' in action:
        player_fx_interact.eos_action = player_fx_interact.EOS_STOP

    player_fx_interact.next_source()
    player_fx_interact.queue(fx)
    player_fx_interact.play()

def play_effect_walk(fx, action):

    if 'LOOP' in action:
        player_fx_walk.eos_action = player_fx_walk.EOS_LOOP
        player_fx_walk.queue(fx)
        player_fx_walk.play()  
    
    if 'STOP' in action:
        player_fx_walk.pause() 
  


    
def play_game_music():
    player_music.queue(music['nice1'])
    player_music.eos_action = player_music.EOS_LOOP

    player_music.play()

def play_game_music(music):
    player_music.next_source()
    player_music.queue(music)
    player_music.eos_action = player_music.EOS_LOOP
    player_music.play()
    
def play_game_ambience(noise):
    player_ambience.next_source()
    
    for i in noise:
        player_ambience.queue(i)
    player_ambience.eos_action = player_music.EOS_LOOP
    player_ambience.play()
