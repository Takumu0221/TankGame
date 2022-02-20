from rl.processors import MultiInputProcessor

from Sources.tank.tank_game.env import TankEnv
from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras import optimizers
import gym
from gym.spaces import utils
from rl.agents.dqn import DQNAgent
from rl.policy import EpsGreedyQPolicy
from rl.memory import SequentialMemory

tank_env = gym.make('tank_game-v0')
nb_actions = tank_env.action_space.n

model = Sequential()
model.add(Flatten(input_shape=(1,) + tank_env.observation_space.shape))
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
dqn.compile(optimizers.adam_v2.Adam(lr=1e-3), metrics=['mae'])

history = dqn.fit(tank_env, nb_steps=10000, visualize=False, verbose=2)

dqn.test(tank_env, nb_episodes=1, visualize=True)
