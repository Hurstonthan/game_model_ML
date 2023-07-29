from stable_baselines3.common.env_checker import check_env
from training_envi import ZeldaEnvi
env = ZeldaEnvi()
check_env(env)