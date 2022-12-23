import gym
import gamecode
from gym.utils import play
import gym.utils
import pygame
from cmdargs import args

render_mode = args.mode
if render_mode == "human_rand":
    render_mode = "human"

# render_mode = 'human' # delete this later

episodes = args.episodes
max_steps = args.max_steps

env = gym.make('haha', render_mode=render_mode)
env = gym.wrappers.TimeLimit(env, max_episode_steps=max_steps)

if args.fps is not None:
    env.metadata["render_fps"] = args.fps

env.action_space.seed(args.seed)
observation, info = env.reset(seed=args.seed)

episode = 0
success_episodes = 0
running = True
step = 0

while running and episode < episodes:
    action = None
    if args.mode == "human":
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    action = 0
                if event.key == pygame.K_DOWN:
                    action = 1
                if event.key == pygame.K_LEFT:
                    action = 2
                if event.key == pygame.K_UP:
                    action = 3
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.QUIT:
                running = False
    else:
        action = env.action_space.sample()  # random
        
    if action is not None:
        observation, reward, done, truncated, info = env.step(action)
        #print(episode, action, observation, reward, info)
        step += 1
        if done or truncated:
            observation, info = env.reset(seed=args.seed)
            if done:
                print(f"Episode {episode} succeeded in {step} steps ...")
                success_episodes += 1
            else:
                print(f"Episode {episode} truncated ...")
            episode += 1
            step = 0

if episode > 0:
    print(f"Success rate: {success_episodes/episode:.2f}")

env.close()
