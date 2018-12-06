import numpy as np
from collections import namedtuple
import random
import torch
from torch import nn, optim
import torch.nn.functional as F

from tetris_env import Tetris

BATCH_SIZE = 32
CAPACITY = 10000

Transition = namedtuple("Transition", ("state", "action", "next_state", "reward"))

GAMMA = 0.99
MAX_STEPS = 14
NUM_EPISODES = 5000
TARGET_SCORE = 4

class ReplayMemory:

    def __init__(self, CAPACITY):
        self.capacity = CAPACITY
        self.memory = []
        self.index = 0
    
    def push(self, state, action, state_next, reward):
        if len(self.memory) < self.capacity:
            self.memory.append(None)
        
        self.memory[self.index] = Transition(state, action, state_next, reward)
        self.index = (self.index + 1) % self.capacity
    
    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)

class Brain:
    def __init__(self, num_states, num_actions):
        self.num_actions = num_actions # まぁ0..39の40個なんだけどね
        self.memory = ReplayMemory(CAPACITY)

        self.model = nn.Sequential()
        self.model.add_module('fc1', nn.Linear(num_states, 32)) # 状態が200個あるので特徴も200個以上ある...?とりあえず32で
        self.model.add_module('relu1', nn.ReLU())
        self.model.add_module('fc2', nn.Linear(32, 32))
        self.model.add_module('relu2', nn.ReLU())
        self.model.add_module('fc3', nn.Linear(32, num_actions))

        # print(self.model)

        self.optimizer = optim.Adam(self.model.parameters(), lr=0.0001)
    
    def replay(self):
        if len(self.memory) < BATCH_SIZE:
            return
        
        transitions = self.memory.sample(BATCH_SIZE)
        batch = Transition(*zip(*transitions))

        state_batch = torch.cat(batch.state)
        action_batch = torch.cat(batch.action)
        reward_batch = torch.cat(batch.reward)
        non_final_next_states = torch.cat([s for s in batch.next_state if s is not None])

        self.model.eval()

        state_action_values = self.model(state_batch).gather(1, action_batch)

        non_final_mask = torch.ByteTensor(tuple(map(lambda s: s is not None, batch.next_state)))
        next_state_values = torch.zeros(BATCH_SIZE)

        next_state_values[non_final_mask] = self.model(non_final_next_states).max(1)[0].detach()

        expected_state_action_values = reward_batch + GAMMA * next_state_values

        self.model.train()

        loss = F.smooth_l1_loss(state_action_values, expected_state_action_values.unsqueeze(1))

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def decide_action(self, state, episode):
        epsilon = 0.5 * (1 / (episode + 1))

        if epsilon <= np.random.uniform(0, 1):
            self.model.eval()
            with torch.no_grad():
                action = self.model(state).max(1)[1].view(1, 1)
        
        else:
            action = torch.LongTensor([[random.randrange(self.num_actions)]])
        
        return action
    
class Agent:
    def __init__(self, num_states, num_actions):
        self.brain = Brain(num_states, num_actions)

    def update_q_function(self):
        self.brain.replay()
    
    def get_action(self, state, episode):
        action = self.brain.decide_action(state, episode)
        return action
    
    def memorize(self, state, action, state_next, reward):
        self.brain.memory.push(state, action, state_next, reward)
    
## ここから要注意

def make_observation(am, field):
    observation = np.array(field)
    observation = np.append(observation, am)
    return observation

class Environment:
    def __init__(self):
        self.env = Tetris()
        # self.num_states = self.env.observation_space.shape[0]
        self.num_states = 211 # <= 20 * 11 + 1(降ってきているブロック)
        # self.num_actions = self.env.action_space.n
        self.num_actions = 40 # <= [north, east, south, west] * 10

        self.agent = Agent(self.num_states, self.num_actions)
    
    def run(self):
        episode_10_list = np.zeros(10)

        complete_episodes = 0 # scoreがTARGET_SCORE以上になった試行数
        episode_final = False
        # frames = []

        for episode in range(NUM_EPISODES):
            am, field = self.env.reset()
            observation = make_observation(am, field)
            state = torch.from_numpy(observation).type(torch.FloatTensor)
            state = torch.unsqueeze(state, 0)

            sum_reward = 0
            sum_density_reward = 0

            for step in range(MAX_STEPS):
                action = self.agent.get_action(state, episode)
                am, field, step_reward, done = self.env.step(action.item())
                observation_next = make_observation(am, field)

                real_score = step_reward // 1
                sum_reward += real_score
                sum_density_reward += step_reward - real_score

                if done:
                    state_next = None

                    episode_10_list = np.hstack((episode_10_list[1:], sum_reward))

                    if step < (MAX_STEPS-1): # 窒息死
                        reward = torch.FloatTensor([-10.0])
                    else:
                        reward = torch.FloatTensor([float(step_reward)]) # 報酬はいつも通り
                    
                    if sum_reward < TARGET_SCORE:
                        complete_episodes = 0
                    else:
                        complete_episodes += 1
                
                else:
                    reward = torch.FloatTensor([float(step_reward)])
                    state_next = torch.from_numpy(observation_next).type(torch.FloatTensor)
                    state_next = torch.unsqueeze(state_next, 0)
                
                self.agent.memorize(state, action, state_next, reward)
                self.agent.update_q_function()
                state = state_next
                    
                if done:
                    print(f"{episode} Episode: Finished with score {sum_reward} ; density_score {sum_density_reward / 14} : 10試行の平均SCORE = {episode_10_list.mean():.1f}")
                    break
                    
            if episode_final is True:
                print("episode final's score:", sum_reward)
                break

            if complete_episodes >= 10:
                print(f"10回連続{TARGET_SCORE}点越え")
                episode_final = True

tetris_envi = Environment()
tetris_envi.run()