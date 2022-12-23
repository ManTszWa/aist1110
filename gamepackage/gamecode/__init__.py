from gym.envs.registration import register


register(
    id='haha',
    entry_point='gamecode.envs.actualgame:BallWorldEnv',
    # max_episode_steps=300,
)