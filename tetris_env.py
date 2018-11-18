from ctypes import cdll, c_char_p, c_int
# from ctypes import windll, c_char_p, c_int
import ctypes

# init_flag = False
# dll = None

class Tetris(object):
    def __init__(self):
        # global dll
        dll = cdll.LoadLibrary('./tetris_api.dll')
        self._reset = dll.reset
        self._reset.restype = c_char_p

        self._step = dll.step
        self._step.restype = c_char_p
        self._step.argtype = c_int

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

if __name__=="__main__":
    tetris = Tetris()
    am, field = tetris.reset()
    print(f"""\
ActiveMino: {["i", "o", "s", "z", "j", "l", "t"][am]}
Field:
{showField(field)}
""")
    done = False
    while not done:
        i = int(input())
        am, field, reward, done = tetris.step(i)
        print(f"""\
ActiveMino: {["i", "o", "s", "z", "j", "l", "t"][am]}
Reward: {reward}
Done: {done}
Field:
{showField(field)}
""")