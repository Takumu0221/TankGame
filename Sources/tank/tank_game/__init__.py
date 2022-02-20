from gym.envs.registration import register

register(
    id='tank_game-v0',
    entry_point='Sources.tank.tank_game.env:TankEnv'
)
