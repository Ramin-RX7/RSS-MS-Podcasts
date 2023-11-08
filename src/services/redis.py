from redis import asyncio as aioredis

from config.settings import SETTINGS



class RedisService:
    def __init__(self, url:str=None, **kwargs) -> None:
        """Creates connection to Redis client (async)

        Args:
            url (str): url of redis instance (requires complete url containing auth and db (if needed))
        """
        self.client = aioredis.from_url(url or SETTINGS.REDIS_URL, **kwargs)


    async def set(self, key:str, value:str, ttl:int|None=None):
        await self.client.set(
            name = key,
            value = value,
            ex = ttl or SETTINGS.REDIS_KEY_TTL
        )

    async def get(self, key:str):
        result = await self.client.get(key)
        return result.decode() if result else None

    async def keys(self, pattern:str):
        return await self.client.keys(pattern)

    async def new_client(self, url):
        self.clinet = aioredis.from_url(url or SETTINGS.REDIS_URL)

    async def delete(self, *keys):
        return await self.client.delete(*keys)
