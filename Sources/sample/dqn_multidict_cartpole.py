import numpy as np
import gym

from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Flatten, Input, concatenate
from keras import optimizers
from keras.utils.vis_utils import plot_model

from rl.agents.dqn import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory
from rl.processors import MultiInputProcessor

from rl.callbacks import (
    TrainEpisodeLogger,
    TrainIntervalLogger,
    FileLogger
)

from Sources.sample.cartpole_multidict import CartPoleMultidictEnv

ENV_NAME = 'CartPoleMultidict-v0'

# Get the environment and extract the number of actions.
env = gym.make(ENV_NAME)
# np.random.seed(123)
# env.seed(123)
nb_actions = env.action_space.n

# Next, we build a very simple model.

model_x = Sequential()
model_x.add(Flatten(input_shape=(1, 1), name='x'))
model_x_input = Input(shape=(1, 1), name='x')
model_x_encoded = model_x(model_x_input)

model_fx = Sequential()
model_fx.add(Flatten(input_shape=(1, 1), name='fx'))
model_fx_input = Input(shape=(1, 1), name='fx')
model_fx_encoded = model_fx(model_fx_input)

model_theta = Sequential()
model_theta.add(Flatten(input_shape=(1, 1), name='theta'))
model_theta_input = Input(shape=(1, 1), name='theta')
model_theta_encoded = model_theta(model_theta_input)

model_ftheta = Sequential()
model_ftheta.add(Flatten(input_shape=(1, 1), name='ftheta'))
model_ftheta_input = Input(shape=(1, 1), name='ftheta')
model_ftheta_encoded = model_ftheta(model_ftheta_input)

con = concatenate([model_x_encoded, model_fx_encoded, model_ftheta_encoded, model_theta_encoded])

hidden = Dense(16, activation='relu')(con)
for _ in range(2):
    hidden = Dense(16, activation='relu')(hidden)
output = Dense(nb_actions, activation='linear')(hidden)
model_final = Model(inputs=[model_x_input, model_fx_input, model_theta_input, model_ftheta_input], outputs=output)
# print(model.summary())
plot_model(model_final, to_file='model.png')

# Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
# even the metrics!
memory = SequentialMemory(limit=50000, window_length=1)
policy = BoltzmannQPolicy()
dqn = DQNAgent(model=model_final, nb_actions=nb_actions, memory=memory, nb_steps_warmup=2000,
               target_model_update=1e-2, policy=policy)
dqn.processor = MultiInputProcessor(4)
dqn.compile(optimizer=optimizers.adam_v2.Adam(lr=1e-3), metrics=['mae'])
# dqn.load_weights('dqn_{}_weights.h5f'.format(ENV_NAME))

# Okay, now it's time to learn something! We visualize the training here for show, but this
# slows down training quite a lot. You can always safely abort the training prematurely using
# Ctrl + C.
dqn.fit(env, nb_steps=int(1e5), visualize=False, verbose=1, callbacks=[TrainEpisodeLogger()])

# After training is done, we save the final weights.
dqn.save_weights('dqn_{}_weights.h5f'.format(ENV_NAME), overwrite=True)

# Finally, evaluate our algorithm for 5 episodes.
dqn.test(env, nb_episodes=10, visualize=True)
