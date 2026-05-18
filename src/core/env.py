from pathlib import Path
from decouple import config as decouple_config, Config, RepositoryEnv


BASE_DIR = Path(__file__).resolve().parent.parent


def find_env_file():
    for directory in Path(__file__).resolve().parents:
        env_file = directory / ".env"
        if env_file.exists():
            return env_file
    return None


def get_config():
    env_file_path = find_env_file()
    if env_file_path:
        return Config(RepositoryEnv(str(env_file_path)))
    return decouple_config


config = get_config()
