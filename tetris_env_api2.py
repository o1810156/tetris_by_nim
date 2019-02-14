from ctypes import cdll, c_char_p, c_int
# from ctypes import windll, c_char_p, c_int
import ctypes
import pandas as pd

import re

# init_flag = False
# dll = None

class Tetris(object):
    def __init__(self):
        # global dll
        dll = cdll.LoadLibrary('./tetris_api2.dll')
        self._reset = dll.reset
        self._reset.restype = c_char_p

        self._step = dll.step
        self._step.restype = c_char_p
        self._step.argtype = c_int

        self._step_preview = dll.step_preview
        self._step_preview.restype = c_char_p
        self._step_preview.argtype = c_int

        self._revert = dll.revert

    def _str_to_arr(self, st):
        # print(st)
        st = st.replace("true", "1.0").replace("false", "0.0")
        arr = st.split("/")
        for i, elm in enumerate(arr):
            arr[i] = eval(elm)
        # print(arr)
        return arr

    # def analyzer(self, tet_i):
    #     obs = str(teti)
    #     am, _field, done, reward = int(obs[0]), obs[1:211], (obs[212] == 1), int(obs[213:])
    #     field = [int(s) for s in _field]
    #     return (am, field, reward, done)

    def reset(self):
        # global init_flag
        # if init_flag:
        #     global dll
        #     del dll
        #     dll = cdll.LoadLibrary('./tetris_api.dll')
        #     self._reset = dll.reset
        #     self._reset.restype = c_char_p

        #     self._step = dll.step
        #     self._step.restype = c_char_p
        #     self._step.argtype = c_int

        #     self._revert = dll.revert
        
        # else:
        #     init_flag = True

        for _ in range(3):
            try:
                am, field, _, _ = self._str_to_arr(self._reset().decode())
                break
            except OSError:
                continue

        return am, field

    def step(self, i):
        for _ in range(3):
            try:
                am, field, reward, done = self._str_to_arr(self._step(i).decode())
                break
            except OSError:
                # print("retry")
                self._revert()
                continue

        # 密度をスコアに含める
        blocks_sum = 0
        line_num = 0
        for line in field:
            if all(map(lambda item: item == 0.0, line)):
                continue
            line_num += 1
            for block in line:
                if block == 1.0:
                    blocks_sum += 1
        
        density = blocks_sum / (line_num * 10)
        # if density >= 1: print("計算式見直せ")
        reward += density

        done = (done == 1.0)
        return am, field, reward, done

    def step_preview(self, i):
        for _ in range(3):
            try:
                _, field, _, _ = self._str_to_arr(self._step_preview(i).decode())
                break
            except OSError:
                continue

        return field
    
    def revert(self):
        self._revert()

class Tetris_role_model(object):
    def __init__(self, rm_file_path):
        with open(rm_file_path) as f:
            all_lines = f.readlines()
            self.episodes_num = len(all_lines)//15
            episode_iters = []
            for episode_n in range(self.episodes_num):
                episode = []
                for line in all_lines[episode_n*15:(episode_n+1)*15]:
                    line = line.split(",")
                    action = int(line[0])
                    am = int(line[1])
                    field = [[float(j) for j in line[i+2:i+12]] for i in range(0, 210, 10)]
                    reward = float(line[212])
                    done = True if "True" in line[213] else False
                    episode.append([action, am, field, reward, done])
                episode_iters.append(iter(episode))
            self.epi_ite_iters = iter(episode_iters)

    def reset(self):
        self.episode_iter = next(self.epi_ite_iters)
        _, am, field, _, _ = next(self.episode_iter)
        return am, field

    def step(self):
        return next(self.episode_iter)


# デバッグ用

# def showField(arr):
#     res = ""
#     for i in range(21):
#         res += "".join(arr[(i*10):((i+1)*10)]) + "\n"
#     return res

def showField(field):
    res = ""
    for line in field:
        res += "".join(map(lambda b: "1" if b == 1.0 else "0", line)) + "\n"
    return res

def play_and_save():
    recorder = []
    tetris = Tetris()
    am, field = tetris.reset()
#     print(f"""\
# ActiveMino: {["i", "o", "s", "z", "j", "l", "t"][am]}
# Field:
# {showField(field)}
# """)
    done = False
    recorder.append([0, am, field, 0, False])
    while not done:
        i = 0
        field = tetris.step_preview(i)
        while True:
            print(f"""\
action: {i}
Field:
{showField(field).replace("1", "■").replace("0", "□")}
""")
            b = input("A B R L D rev: ")
            if b in "Aa":
                i = (i+10) % 40
            elif b in "Bb":
                i = (i-10) % 40
            elif b in "Rr":
                i = i + 1 if i%10 + 1 < 10 else i
            elif b in "Ll":
                i = i - 1 if i%10 - 1 >= 0 else i
            elif b == "rev":
                i = 0
                tetris.revert()
                recorder = recorder[:-1]
                field = tetris.step_preview(i)
            elif b in "Dd":
                break
            field = tetris.step_preview(i)

        am, field, reward, done = tetris.step(i)
        recorder.append([i, am, field, reward, done])
        print(f"""\
droped
ActiveMino: {["i", "o", "s", "z", "j", "l", "t"][am]}
Reward: {reward}
Done: {done}
Field:
{showField(field).replace("1", "■").replace("0", "□")}
""")
    return recorder

if __name__=="__main__":
    arr = play_and_save()
    name = input("file name : ").replace(".csv", "")
    with open(name+".csv", "a") as f:
        # f.write("action, active_mino, "+", ".join([str(i) for i in range(21*10)])+", reward, done\n")
        for data in arr:
            f.write(re.sub(r"[\[\]]", "", str(data)))
            f.write("\n")
