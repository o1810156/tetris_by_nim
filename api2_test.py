from tetris_env_api2 import Tetris_role_model

env = Tetris_role_model(input("path: "))
for _ in range(env.episodes_num):
    print(env.reset())

    for _ in range(14):
        print(env.step())
    
    print("\n####\n")