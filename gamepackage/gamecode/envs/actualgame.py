import gym
import pygame
import numpy as np
from gym import spaces

class BallWorldEnv(gym.Env):
    metadata = {"render_modes": ["rgb_array", "human"], "render_fps": 30}
    window_size = 1024
    window = None
    ball_size = 15
    
    def __init__(self, render_mode=None):
        self.render_mode = render_mode
        self.action_space = spaces.Discrete(4) # Maybe need 8 if all 8 direction?
        self.observation_space = spaces.Box(0, 2 * 1024**2, shape=(4,), dtype=np.float64) # Maybe upper limit is np.inf
        self._action_to_direction = {
            0: np.array([1, 0]), # Right
            1: np.array([0, 1]), # Down
            2: np.array([-1, 0]), # Left
            3: np.array([0, -1]), # Up
        }

    def _get_obs(self):
        shortest = np.inf
        for enemy in self.enemy:
            distance = self.distancesq(enemy, self.player)
            if  distance < shortest:
                shortest = distance

        goaldistance = self.distancesq(self.goal, self.player)

        # return np.concatenate((self.player.pos, self.player.pos), axis=0) # Wrong! just for test
        return np.concatenate((self.player.pos, np.array([shortest, goaldistance], dtype=np.float64)))

    def _get_info(self):
        return {'empty':'dictionary'}
    
    @staticmethod
    def distancesq(a, b): # Receive two ball
        return (a.pos[0] - b.pos[0]) ** 2 + (a.pos[1] - b.pos[1]) ** 2

    class Player():
        def __init__(self):
            # self.x = BallWorldEnv.window_size/2 + 1 # This should be middle
            # self.y = BallWorldEnv.window_size/2 + 1
            middle = BallWorldEnv.window_size/2 + 1
            self.pos = np.array([middle, middle])
            self.speed = 10
            self.live = 1
            self.iframe = 0 # Immunity frame, not implemented yet
            self.score = 0

    class Enemy():
        speedmultiplier = 5
        speedincrease = 1
        def __init__(self, player):
            self.pos = np.array([np.random.randint(20, BallWorldEnv.window_size-20), np.random.randint(20, BallWorldEnv.window_size-20)]).astype(np.float64) # Need more change
            
            self._speed = -np.array([self.pos[0]-player.pos[0], self.pos[1]-player.pos[1]]) # This is only direction, speed can vary
            self._speed = self._speed / np.sqrt(self._speed[0]**2 + self._speed[1]**2) # |velo| = 1
            self._speed = np.array(self._speed)
            # self.speed *= BallWorldEnv.Enemy.speedmultiplier
            

        @property
        def speed(self):
            return self._speed * self.speedmultiplier

        @speed.setter
        def speed(self, value):
            self._speed = np.array(value)

        

    class Goal():
        def __init__(self):
            self.pos = np.array([np.random.randint(20, BallWorldEnv.window_size-20), np.random.randint(20, BallWorldEnv.window_size-20)]) # Need more change


    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.player = BallWorldEnv.Player()
        self.enemy = [BallWorldEnv.Enemy(self.player) for _ in range(4)] # self.enemy is a list of object
        self.goal = BallWorldEnv.Goal()

        observation = self._get_obs()
        info = self._get_info()

        return observation, info # Rmb info is wrong

    def step(self, action): # action = 0 or 1 or 2 or 3
        if action is not None:
            direction = self._action_to_direction[action]
            self.player.pos = np.clip(self.player.pos + direction * self.player.speed, 0, BallWorldEnv.window_size) # May change boundary

        # Enemy moves
        for enemy in self.enemy:
            # If out of bound, change direction
            # for k in range(2):
                # if not 0 < enemy.pos[k] < BallWorldEnv.window_size:
                #     print(enemy.speed)
                #     enemy.speed[k] =- enemy.speed[k]
            if not 0 < enemy.pos[0] < BallWorldEnv.window_size:
                enemy.speed = (-enemy._speed[0], enemy._speed[1])
            if not 0 < enemy.pos[1] < BallWorldEnv.window_size:
                enemy.speed = (enemy._speed[0], -enemy._speed[1])

            enemy.pos += enemy.speed
        
        # self._get_obs()[2] is closest enemy distancesq, may change later
        if np.sqrt(self._get_obs()[2]) < 2 * BallWorldEnv.ball_size:
            self.player.live -= 1

        # check if reaching goal
        if np.sqrt(self._get_obs()[3]) < 2 * BallWorldEnv.ball_size:
            self.player.score += 1
            self.goal = BallWorldEnv.Goal()
            self.enemy.append(self.Enemy(self.player))
            for enemy in self.enemy:
                enemy.speedmultiplier = BallWorldEnv.Enemy.speedmultiplier + self.player.score * BallWorldEnv.Enemy.speedincrease



        terminated = self.player.live == 0
        observation = self._get_obs()
        reward = observation[2] + -observation[3]
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        

        return observation, reward, terminated, False, info

    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_frame()

    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init() # Should be not needed but leave it here anyways
            self.window = pygame.display.set_mode((self.window_size, self.window_size))

        canvas = pygame.Surface((self.window_size, self.window_size))
        canvas.fill((0, 0, 0)) # Black background

        # Draw Player
        pygame.draw.circle(canvas, (0, 255, 0), (self.player.pos[0], self.player.pos[1]), BallWorldEnv.ball_size)
        # Draw Goal
        pygame.draw.circle(canvas, (255, 255, 0), (self.goal.pos[0], self.goal.pos[1]), BallWorldEnv.ball_size)
        # Draw Enemy
        for enemy in self.enemy:
            pygame.draw.circle(canvas, (255, 0, 0), (enemy.pos[0], enemy.pos[1]), BallWorldEnv.ball_size)


        if self.render_mode == 'human':
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump() # wts this
            pygame.display.update()
        else:  # rgb_array
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
            )

    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()

