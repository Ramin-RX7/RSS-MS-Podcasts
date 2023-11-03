from bson import ObjectId

from db import db
from config import SETTINGS
from schemas import Podcast,Episode
from services import PodcastAPIService



podcast_service = PodcastAPIService(SETTINGS.PODCASTS_URL)


async def get_podcast_list():
    resp = await podcast_service.podcast_list()
    if not resp:
        return None
    return resp.data


async def get_podcast_details(identifier):
    podcast = await db["podcasts"].find_one({
        # "api_identifier" : int(identifier),
        "_id" : ObjectId(identifier),
    })
    if podcast is None: return
    podcast = Podcast(**podcast)
    resp = await podcast_service.podcast_details(podcast.api_identifier)
    resp_data = resp.data
    # NOTE: line below must be made to a function to be used for all schemas
    # Also the excludes from both (resp and podcast) must be previously defined
    data = {**resp_data["podcast"], **podcast.model_dump(exclude=["api_identifier"])}
    return data

