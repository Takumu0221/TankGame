from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras import optimizers
import gym
from rl.agents.dqn import DQNAgent
from rl.policy import EpsGreedyQPolicy
from rl.memory import SequentialMemory

env = gym.make('MountainCar-v0')
nb_actions = env.action_space.n

model = Sequential()
model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
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
dqn = DQNAgent(model=model, nb_actions=nb_actions,gamma=0.99, memory=memory, nb_steps_warmup=10,
               target_model_update=1e-2, policy=policy)
dqn.compile(optimizers.adam_v2.Adam(lr=1e-3), metrics=['mae'])

history = dqn.fit(env, nb_steps=50000, visualize=False, verbose=2)

dqn.test(env, nb_episodes=1, visualize=True)

