from environs import Env

env = Env()
env.read_env()

MY_ID = env.int("MY_ID")
GROUP_ID = env.int("GROUP_ID")
DESCRIPTION = env("DESCRIPTION")
BOT_TOKEN = env("BOT_TOKEN")
