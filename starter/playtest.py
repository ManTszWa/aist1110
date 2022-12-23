# Prototype obviously
import gym
import gamecode
from gym.utils import play
import gym.utils
import pygame

# this version is just to play the game in human-controlled mode

env = gym.make('haha', render_mode="rgb_array")
# env = gym.make('haha')

mapping = {
    (pygame.K_RIGHT,): 0, 
    (pygame.K_DOWN,): 1,
    (pygame.K_LEFT,): 2,
    (pygame.K_UP,): 3
}


# print(gym.utils.env_checker.check_reset_seed(env)) # For testing


play.play(env, keys_to_action=mapping, noop=None)

