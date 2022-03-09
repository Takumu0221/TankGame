import datetime
import glob

from keras.utils.vis_utils import plot_model
# from rl.processors import MultiInputProcessor
from rl.processors import MultiInputProcessor

from Sources.tank.tank_game.env import TankEnv
from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Flatten, Input, concatenate
from keras import optimizers
import gym
from gym.spaces import utils
from rl.agents.dqn import DQNAgent
from rl.policy import EpsGreedyQPolicy
from rl.memory import SequentialMemory


tank_env = gym.make('tank_game-v0')
nb_actions = tank_env.action_space.n

model = Sequential()
model.add(Flatten(input_shape=(1, utils.flatdim_dict(tank_env.observation_space))))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(nb_actions))
model.add(Activation('linear'))

memory = SequentialMemory(limit=50000, window_length=1)

policy = EpsGreedyQPolicy(eps=0.001)
dqn = DQNAgent(model=model, nb_actions=nb_actions, gamma=0.99, memory=memory, nb_steps_warmup=10,
               target_model_update=1e-2, policy=policy)
dqn.compile(optimizers.adam_v2.Adam(lr=1e-3), metrics=['mae'])  # コンパイル

tf = True
load_filename = None
if tf:
    # モデルの読み込み
    for filename in glob.glob(f'models/tank_num_{tank_env.env.Enemy_num_learn}/*.h5'):
        print(f'load model {filename}')
        dqn.load_weights(f'{filename}')
        load_filename = filename
        break

history = dqn.fit(tank_env, nb_steps=10000000, visualize=True, verbose=2)  # 学習

tank_env.env.set_fps(30)  # fpsの更新
dqn.test(tank_env, nb_episodes=1, visualize=True)  # テスト

# モデルの保存
now = datetime.datetime.now()
if load_filename:
    # モデルを読み込んだ時は，同じ名前で保存
    dqn.save_weights(load_filename, overwrite=True)
else:
    dqn.save_weights(f'models/tank_num_{tank_env.env.Enemy_num_learn}/{now.strftime("%Y-%m-%d-%H:%M:%S")}.h5', overwrite=True)
