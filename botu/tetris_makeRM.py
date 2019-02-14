# 録画用htmlを起動する...?
# いらないかも

# coding: utf-8

import re
import numpy as np

import torch
from torch import nn, optim
import torch.nn.functional as F

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

# model = Net(211, 32, 40)
model = Net(211, 211, 40)

# model.load_state_dict(torch.load("./n_mid32/dueqn_2999.net"))
# model.load_state_dict(torch.load("./n_mid32/dueqn_5999.net"))
# model.load_state_dict(torch.load("./n_mid32/dueqn_8999.net"))
# model.load_state_dict(torch.load("./n_mid32/dueqn_11999.net"))
# model.load_state_dict(torch.load("./n_mid32/dueqn_14999.net"))
# model.load_state_dict(torch.load("./n_mid32/dueqn_17999.net"))

# model.load_state_dict(torch.load("./n_mid211/dueqn_2999.net"))
# model.load_state_dict(torch.load("./n_mid211/dueqn_5999.net"))
# model.load_state_dict(torch.load("./n_mid211/dueqn_8999.net"))
# model.load_state_dict(torch.load("./n_mid211/dueqn_11999.net"))

model.load_state_dict(torch.load("./dueqn_2999.net"))
# model.load_state_dict(torch.load("./n_mid211_alp/dueqn_2999.net"))
# model.load_state_dict(torch.load("./n_mid211_alp/dueqn_5999.net"))
# model.load_state_dict(torch.load("./n_mid211_alp/dueqn_8999.net"))
# model.load_state_dict(torch.load("./n_mid211_alp/dueqn_11999.net"))
# model.load_state_dict(torch.load("./dueqn_11999.net"))
model.eval()

def make_state(am, field):
    state = np.array(field)
    state = np.append(state, am)
    state = torch.from_numpy(state).type(torch.FloatTensor)
    state = torch.unsqueeze(state, 0)
    return state

def decide_action(state):
    with torch.no_grad():
        action = model(state).max(1)[1].view(1, 1)
    return action.item()

MINO_TABLE = {
    "i": 0,
    "o": 1,
    "s": 2,
    "z": 3,
    "j": 4,
    "l": 5,
    "t": 6
}

import selenium
from selenium import webdriver
from selenium.webdriver import Chrome
from time import sleep

driver = Chrome()
driver.get("file:///C:/Users/namni/Desktop/tetris_by_nim/index.html")
# driver.get("./index.html")

game_over_flag = False

while not game_over_flag:
    am = driver.execute_script("javascript: return getActiveMino();")
    field = driver.execute_script("javascript: return getRawBoard();")
    field = [[(1.0 if b else 0.0) for b in line[1:-1]] for line in field[:-1]]
    state = make_state(am, field)
    action = decide_action(state)
    dir = action // 10
    target_y = action % 10
    driver.execute_script(f"javascript: apiSpin({dir});apiMove({target_y});")
    sleep(0.5)
    driver.execute_script("javascript: apiHardDrop();")
    game_over_flag = driver.execute_script("javascript: return getGameOverFlag();")

driver.close()
driver.quit()