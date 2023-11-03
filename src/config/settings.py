from pydantic_settings import BaseSettings




class _Config(BaseSettings):
    MONGODB_URL : str

    REDIS_URL : str
    REDIS_KEY_TTL : int

    PODCASTS_URL : str = ""

    # REDIX : _RedisConfig

    class Config:
        env_file = ".env"
        extra = "ignore"
        env_nested_delimiter = "_"


SETTINGS = _Config()
