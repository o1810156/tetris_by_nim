from tetris_env_api2 import Tetris

tetris = Tetris()
am, field = tetris.reset()
print(f"""\
ActiveMino: {["i", "o", "s", "z", "j", "l", "t"][am]}
Field:
{showField(field)}
""")
done = False

y = 0

while not done:
    

'''
    i = int(input())
    am, field, reward, done = tetris.step(i)
    print(f"""\
ActiveMino: {["i", "o", "s", "z", "j", "l", "t"][am]}
Reward: {reward}
Done: {done}
Field:
{showField(field)}
""")
'''