import re, sys
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
# NUM_EPISODES = 5000 # メモリの都合で5000もできなかった
NUM_EPISODES = 3000
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

class Net(nn.Module):
    def __init__(self, n_in, n_mid, n_out):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(n_in, n_mid)
        self.fc2 = nn.Linear(n_mid, n_mid)
        self.fc3_adv = nn.Linear(n_mid, n_out)
        self.fc3_v = nn.Linear(n_mid, 1)

    def forward(self, x):
        h1 = F.relu(self.fc1(x))
        h2 = F.relu(self.fc2(h1))

        adv = self.fc3_adv(h2)
        val = self.fc3_v(h2).expand(-1, adv.size(1))

        output = val + adv - adv.mean(1, keepdim=True).expand(-1, adv.size(1))

        return output

class Brain:
    def __init__(self, num_states, num_actions):
        self.num_actions = num_actions # まぁ0..39の40個なんだけどね
        self.memory = ReplayMemory(CAPACITY)

        n_mid = int(input("mid?: "))
        # n_in, n_mid, n_out = num_states, 32, num_actions
        n_in, n_out = num_states, num_actions
        self.main_q_network = Net(n_in, n_mid, n_out)
        self.target_q_network = Net(n_in, n_mid, n_out)

        # !! nexts で追加 !!

        net_name = sys.argv[1] if len(sys.argv) > 1 else input("filename?: ")
        self.main_q_network.load_state_dict(torch.load(f"./{net_name}"))
        self.target_q_network.load_state_dict(torch.load(f"./{net_name}"))

        self.cont_episode_num = int(re.findall(r"dueqn_(\d+).net", net_name)[0])

        # print(self.main_q_network)

        self.optimizer = optim.Adam(self.main_q_network.parameters(), lr=0.0001)
    
    def replay(self):
        if len(self.memory) < BATCH_SIZE:
            return

        self.batch, self.state_batch, self.action_batch, self.reward_batch, self.non_final_next_states = self.make_minibatch()
        self.expected_state_action_values = self.get_expected_state_action_values()
        self.update_main_q_network()

    def decide_action(self, state, episode):
        epsilon = 0.5 * (1 / (episode + 1))

        if epsilon <= np.random.uniform(0, 1):
            self.main_q_network.eval()
            with torch.no_grad():
                action = self.main_q_network(state).max(1)[1].view(1, 1)
        
        else:
            action = torch.LongTensor([[random.randrange(self.num_actions)]])
        
        return action
    
    def make_minibatch(self):
        transitions = self.memory.sample(BATCH_SIZE)
        batch = Transition(*zip(*transitions))
        state_batch = torch.cat(batch.state)
        action_batch = torch.cat(batch.action)
        reward_batch = torch.cat(batch.reward)
        non_final_next_states = torch.cat([s for s in batch.next_state if s is not None])

        return batch, state_batch, action_batch, reward_batch, non_final_next_states

    def get_expected_state_action_values(self):
        self.main_q_network.eval()
        self.target_q_network.eval()

        self.state_action_values = self.main_q_network(self.state_batch).gather(1, self.action_batch)
        non_final_mask = torch.ByteTensor(tuple(map(lambda s: s is not None, self.batch.next_state)))

        next_state_values = torch.zeros(BATCH_SIZE)

        a_m = torch.zeros(BATCH_SIZE).type(torch.LongTensor)

        a_m[non_final_mask] = self.main_q_network(self.non_final_next_states).detach().max(1)[1]

        a_m_non_final_next_states = a_m[non_final_mask].view(-1, 1)

        next_state_values[non_final_mask] = self.target_q_network(self.non_final_next_states).gather(1, a_m_non_final_next_states).detach().squeeze()

        expected_state_action_values = self.reward_batch + GAMMA * next_state_values

        return expected_state_action_values

    def update_main_q_network(self):
        self.main_q_network.train()
        loss = F.smooth_l1_loss(self.state_action_values, self.expected_state_action_values.unsqueeze(1))

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
    
    def update_target_q_network(self):
        self.target_q_network.load_state_dict(self.main_q_network.state_dict())
    
    def save_network(self, episode):
        if input("save[y/n]? ") in ["Y", "y"]:
            torch.save(self.main_q_network.state_dict(), f"./dueqn_{episode}.net")
            # torch.save(self.target_q_network.state_dict(), "./dueqn_target.net")
            print("network was saved")
        else:
            print("network was not saved")        

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
    
    def update_target_q_function(self):
        self.brain.update_target_q_network()
    
    def save_brain_network(self, episode):
        self.brain.save_network(episode)
    
    def get_cont_episode_num(self):
        return self.brain.cont_episode_num

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
        last_episode_num = 0
        # frames = []

        cont_episode_num = self.agent.get_cont_episode_num() + 1

        # for episode in range(cont_episode_num, (cont_episode_num + NUM_EPISODES)):
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
                    print(f"{episode} Episode: Finished with score {sum_reward} ; density_score {sum_density_reward / 14} : 10_ave_SCORE = {episode_10_list.mean():.1f}")
                    if(episode % 2 == 0):
                        self.agent.update_target_q_function()
                    break
                    
            if episode_final is True:
                print("episode final's score:", sum_reward)
                break

            if complete_episodes >= 10:
                print(f"10回連続{TARGET_SCORE}点越え")
                episode_final = True
            
            last_episode_num = episode

        # torch.save(self..state_dict(), "./")
        self.agent.save_brain_network(last_episode_num+cont_episode_num)

tetris_envi = Environment()
tetris_envi.run()