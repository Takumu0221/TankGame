import numpy as np
import gym

from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Flatten, Input
from keras.optimizers import Adam
from keras.utils import plot_model

from rl.agents.dqn import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory
from rl.processors import MultiInputProcessor


from rl.callbacks import (
    TrainEpisodeLogger,
    TrainIntervalLogger,
    FileLogger
)

ENV_NAME = 'CartPoleDict-v0'


# Get the environment and extract the number of actions.
env = gym.make(ENV_NAME)
# np.random.seed(123)
# env.seed(123)
nb_actions = env.action_space.n

# Next, we build a very simple model.
model = Sequential()

model.add(Flatten(input_shape=(1,) + (4,))) # env.observation_space.shape))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(16))
model.add(Activation('relu'))
# model.add(Dense(nb_actions))
# model.add(Activation('linear'))
model_input = Input(shape=(1,) + (4,), name='pole')
encoded_model = model(model_input)
output = Dense(nb_actions, activation='linear')(encoded_model)
model_final = Model(inputs=[model_input], outputs=output)
print(model.summary())
plot_model(model_final, to_file='model.png')

# Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
# even the metrics!
memory = SequentialMemory(limit=50000, window_length=1)
policy = BoltzmannQPolicy()
dqn = DQNAgent(model=model_final, nb_actions=nb_actions, memory=memory, nb_steps_warmup=200,
               target_model_update=1e-2, policy=policy)
dqn.processor = MultiInputProcessor(1)
dqn.compile(Adam(lr=1e-3), metrics=['mae'])
# dqn.load_weights('dqn_{}_weights.h5f'.format(ENV_NAME))

# Okay, now it's time to learn something! We visualize the training here for show, but this
# slows down training quite a lot. You can always safely abort the training prematurely using
# Ctrl + C.
dqn.fit(env, nb_steps=int(1e5), visualize=False, verbose=1, callbacks=[ TrainEpisodeLogger()])

# After training is done, we save the final weights.
dqn.save_weights('dqn_{}_weights.h5f'.format(ENV_NAME), overwrite=True)

# Finally, evaluate our algorithm for 5 episodes.
dqn.test(env, nb_episodes=10, visualize=True)
