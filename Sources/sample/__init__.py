from gym.envs.registration import register

register(
    id='CartPoleMultidict-v0',
    entry_point='Sources.sample.cartpole_multidict:CartPoleMultidictEnv'
)
