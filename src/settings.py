from environs import Env

env = Env()
env.read_env()

DESCRIPTION = env.str("DESCRIPTION")
BOT_TOKEN = env.str("BOT_TOKEN")
DATABASE_URL = env.str("DATABASE_URL")
