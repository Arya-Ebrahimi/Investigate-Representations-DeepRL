import numpy as np
from typing import Optional
import gymnasium as gym
from gymnasium import spaces

DOWN = 0
RIGHT = 1
UP = 2
LEFT = 3

class MazEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}
    

    def __init__(self, render_mode=None, size=15):
        self.size = size  # The size of the square grid
        self.shape = (size, size)
        self.observation_space = spaces.Discrete(self.size**2)
        self.action_space = spaces.Discrete(4)
        
        self.start_state = np.ravel_multi_index((7, 1), self.shape)
        self.goal_state = np.ravel_multi_index((9, 10), self.shape)
        self.goal_state_index = np.unravel_index(self.goal_state, self.shape)

        self._action_to_direction = {
            0: np.array([1, 0]),
            1: np.array([0, 1]),
            2: np.array([-1, 0]),
            3: np.array([0, -1]),
        }
        
        self.walls = self._calculate_wall()
        
        self.P = {}
        for s in range(self.observation_space.n):
            pos = np.unravel_index(s, self.shape)
            self.P[s] = {a: [] for a in range(self.action_space.n)}
            self.P[s][RIGHT] = self._calculate_transition_prob(pos, self._action_to_direction[RIGHT])
            self.P[s][UP] = self._calculate_transition_prob(pos, self._action_to_direction[UP])
            self.P[s][LEFT] = self._calculate_transition_prob(pos, self._action_to_direction[LEFT])
            self.P[s][DOWN] = self._calculate_transition_prob(pos, self._action_to_direction[DOWN])
        

        self.render_mode = render_mode

        self.window = None
        self.clock = None
        
    def _calculate_wall(self):
            walls = np.zeros(self.shape)
            walls[2, 0:6] = 1
            walls[2, 8:] = 1
            walls[2:6, 5] = 1
            walls[5, 2:7] = 1
            walls[5, 9:] = 1
            walls[8:12, 2] = 1
            walls[11, 2:6] = 1
            walls[8:, 6] = 1
            walls[8, 9:] = 1
            walls[8:12, 9] = 1
            walls[11, 9:12] = 1
            
            return walls
        
    
    def _limit_coordinate(self, pos):
        x = pos[0]
        y = pos[1]
        
        if x < 0 or x >= self.size or y < 0 or y >= self.size or self.walls[x][y]==1:
            return False
        return True
    
    def _calculate_transition_prob(self, current_pos, action):
        """
        
        Args:
            current_pos (_type_): _description_
            action (_type_): _description_
        
        Retruns:
            (prob, new_state, reward, is_terminated)
        
        """
        new_pos = current_pos + action
        if not self._limit_coordinate(new_pos):
            new_pos = current_pos
            
        new_state = np.ravel_multi_index(new_pos, self.shape)
        
        if new_state == self.goal_state:
            return[1.0, new_state, +1, True]
        
        return [1.0, new_state, 0, False]
    

    def step(self, a): 
        
        prob, next_state, reward, terminate = self.P[self.s][a]     
        self.s = next_state
        self.current_state_index = np.unravel_index(self.s, self.shape)

        self.last_action = a
        
        return(int(next_state), reward, terminate, False, {})
        
    def reset(self, *, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)
        self.s = self.start_state
        self.last_action = None
        self.current_state_index = np.unravel_index(self.s, self.shape)

        if self.render_mode == "human":
            self.render()
            
        return int(self.s), {"prob": 1}
    
    def get_state_image(self):
        image = np.ones((self.size, self.size, 3)) * 255
        image[self.walls==1, 0] = 0
        image[self.current_state_index[0], self.current_state_index[1], 1] = 0
        image[self.goal_state_index[0], self.goal_state_index[1]] = np.array([0, 255, 0])
        
        return image.astype('uint8')