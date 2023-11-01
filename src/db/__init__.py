import motor.motor_asyncio

from config import SETTINGS


client = motor.motor_asyncio.AsyncIOMotorClient(SETTINGS.MONGODB_URL)
db = client["fastapi"]
