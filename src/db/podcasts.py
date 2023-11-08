from bson import ObjectId

from db import db
from config import SETTINGS
from schemas import Podcast,Episode
from services import PodcastAPIService



podcast_service = PodcastAPIService(SETTINGS.PODCASTS_URL)



async def get_by_id(collection_name:str, id:str|ObjectId):
    if type(id) is str:
        id = ObjectId(id)
    return await db[collection_name].find_one({"_id":id})


async def get_podcast_list():
    resp = await podcast_service.podcast_list()
    if not resp:
        return None
    return resp.data


async def get_podcast_details(identifier):
    podcast = await get_by_id("podcasts", identifier)
    if podcast is None: return
    podcast = Podcast(**podcast)
    resp = await podcast_service.podcast_details(podcast.api_identifier)
    resp_data = resp.data
    # NOTE: line below must be made to a function to be used for all schemas
    # Also the excludes from both (resp and podcast) must be previously defined
    data = {**resp_data["podcast"], **podcast.model_dump(exclude=["api_identifier"])}
    return data


async def get_podcast_episode_list(podcast_identifier):
    resp = await podcast_service.podcast_episode_list(podcast_identifier)
    if not resp: return None
    resp_episodes = resp.data["episodes"]
    print(resp_episodes)
    episode_db_ids = [episode["id"] for episode in resp_episodes]
    db_episodes = db["episodes"].find({
        "api_identifier" : {"$in":episode_db_ids},
    })
    db_episodes = list(map(lambda episode:Episode(**episode).model_dump(), await db_episodes.to_list(100)))
    data = merge_episodes(db_episodes, resp_episodes)
    return data

def merge_episodes(db, resp):
    data = []
    for db_episode in db:
        api_identifier = db_episode["api_identifier"]
        for resp_episode in resp:
            if resp_episode["id"] == api_identifier:
                data.append({**db_episode,**resp_episode})
    return data



async def get_podcast_episode_details(episode_identifier):
    episode = await get_by_id("episodes", episode_identifier)
    if not episode: return
    episode = Episode(**episode)
    resp = await podcast_service.podcast_episode_details(episode_identifier)
    if not resp: return None
    # episode.likes =
    return {**(resp.data), "likes":episode.model_dump()["likes"]}


async def like_episode(episode_id:str, user_id:str):
    #] Episode validation
    # episode = await get_podcast_episode_details(episode_id)
    # if not episode: return
    #] User validation.  NOTE: we suppose the user is already validated
    # user = await
    # if not user: return
    await db["episodes"].find_one_and_update(
        {"_id":episode_id},
        {"$push": {"likes": ObjectId(user_id)}}
    )
    await db["users"].find_one_and_update(
            {"_id":episode_id},
            {"$push": {"liked_episodes": ObjectId(episode_id)}}
        )

async def unlike_episode(episode_id:str, user_id:str):
    #] Episode validation
    # episode = await get_podcast_episode_details(episode_id)
    # if not episode: return
    #] User validation.  NOTE: we suppose the user is already validated
    # user = await
    # if not user: return
    await db["episodes"].find_one_and_update(
        {"_id":episode_id},
        {"$pull": {"likes": ObjectId(user_id)}}
    )
    await db["users"].find_one_and_update(
        {"_id":episode_id},
        {"$pull": {"liked_episodes": ObjectId(episode_id)}}
    )
