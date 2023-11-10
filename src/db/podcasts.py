from bson import ObjectId

from db import db
from config import SETTINGS
from schemas import Podcast,Episode, UserLikeStruct
from services import PodcastAPIService



podcast_service = PodcastAPIService(SETTINGS.PODCASTS_URL)
podcasts_collection = db["podcasts"]
episodes_collection = db["episodes"]


async def get_by_id(collection_name:str, id:str|ObjectId):
    if type(id) is str:
        id = ObjectId(id)
    return await db[collection_name].find_one({"_id":id})


def get_episode_query(podcast_id,episode_id):
    query = {"_id": podcast_id, "episodes.id": str(episode_id)}
    return query


async def get_podcast_list():
    resp = await podcast_service.podcast_list()
    if not resp:
        return None
    return resp.data


async def get_podcast_details(identifier:str|ObjectId):
    podcast = await get_by_id("podcasts", identifier)
    if podcast is None: return
    podcast = Podcast(**podcast)
    resp = await podcast_service.podcast_details(podcast.api_identifier)
    resp_data = resp.data
    # NOTE: line below must be made to a function to be used for all schemas
    # Also the excludes from both (resp and podcast) must be previously defined
    data = {**resp_data["podcast"], **podcast.model_dump(exclude=["api_identifier"])}
    return data


# async def get_podcast_episode_list(podcast_identifier):
#     resp = await podcast_service.podcast_episode_list(podcast_identifier)
#     if not resp: return None
#     resp_episodes = resp.data["episodes"]
#     print(resp_episodes)
#     episode_db_ids = [episode["id"] for episode in resp_episodes]
#     db_episodes = db["episodes"].find({
#         "api_identifier" : {"$in":episode_db_ids},
#     })
#     db_episodes = list(map(lambda episode:Episode(**episode).model_dump(), await db_episodes.to_list(100)))
#     data = merge_episodes(db_episodes, resp_episodes)
#     return data

# def merge_episodes(db, resp):
#     data = []
#     for db_episode in db:
#         api_identifier = db_episode["api_identifier"]
#         for resp_episode in resp:
#             if resp_episode["id"] == api_identifier:
#                 data.append({**db_episode,**resp_episode})
#     return data



async def get_podcast_episode_details(podcast_id:str|ObjectId, episode_id:str|ObjectId):
    query = get_episode_query(podcast_id,episode_id)
    projection = {"episodes.$": 1,"api_identifier":1}
    podcast = await podcasts_collection.find_one(query,projection=projection)
    if not podcast: return
    podcast = Podcast.model_validate(podcast)
    episode = Episode.model_validate(podcast.episodes[0])

    resp = await podcast_service.podcast_episode_details(podcast.api_identifier,episode.api_identifier)
    if not resp: return

    return {**(resp.data["episode"]), "likes":episode.model_dump()["likes"]}



async def like_episode(podcast_id:str,episode_id:str, user_id:str) -> bool:
    #] Episode validation
    # episode = await get_podcast_episode_details(episode_id)
    # if not episode: return
    #] User validation.  NOTE: we suppose the user is already validated
    # user = await
    # if not user: return
    podcast_id = ObjectId(podcast_id)
    user_id = ObjectId(user_id)
    add_to_podcast = await podcasts_collection.update_one(
        get_episode_query(podcast_id,episode_id),
        {"$addToSet": {"episodes.$.likes": user_id}
    })
    add_to_user = await db["users"].update_one(
            {"api_identifier":user_id},
            {"$addToSet": {
                "liked_episodes": UserLikeStruct(
                    podcast_identifier=podcast_id,
                    episode_identifier=episode_id
                ).model_dump()
            }}
        )

    if add_to_user.matched_count == 0:
        print("here")
        res = await db["users"].insert_one({
            "api_identifier": user_id,
            "liked_episodes": [
                UserLikeStruct(podcast_identifier=podcast_id, episode_identifier=episode_id).model_dump()
            ]
        })
        return True
    assert add_to_podcast.modified_count  ==  add_to_user.modified_count, "invalid data found in db"
    if (add_to_podcast.modified_count != 1)  or  (add_to_user.modified_count != 1):
        return False
    return True


async def unlike_episode(podcast_id:str, episode_id:str, user_id:str):
    #] Episode validation
    # episode = await get_podcast_episode_details(episode_id)
    # if not episode: return
    #] User validation.  NOTE: we suppose the user is already validated
    # user = await
    # if not user: return
    podcast_id = ObjectId(podcast_id)
    user_id = ObjectId(user_id)
    rem_from_episode = await podcasts_collection.update_one(
        get_episode_query(podcast_id,episode_id),
        {"$pull": {"episodes.$.likes": user_id}
    })
    rem_from_user = await db["users"].update_one(
        {"api_identifier":user_id},
        {"$pull": {
            "liked_episodes": {"episode_identifier":episode_id}
        }}
    )
    assert rem_from_episode.modified_count  ==  rem_from_user.modified_count, "invalid data found in db"
    if (rem_from_episode.modified_count != 1)  or  (rem_from_user.modified_count != 1):
        return False
    return True



async def subscribe_podcast(podcast_id:str, user_id:str):
    await db["podcasts"].find_one_and_update(
        {"_id": podcast_id},
        {"$push": {"subscribers": {"user":ObjectId(user_id)}}}
                                          #? Make `PodcastSubsStruct` and then dump it?
    )
    await db["users"].find_one_and_update(
        {"_id": podcast_id},
        {"$push": {"subscriptions": {"podcast":ObjectId(podcast_id)}}}
                                              #? Make `UserSubsStruct` and then dump it?
    )

async def unsubscribe_podcast(podcast_id:str, user_id:str):
    await db["podcasts"].find_one_and_update(
        {"_id": podcast_id},
        {"$pull": {"subscribers": {"user":ObjectId(user_id)}}}  #? Make `PodcastSubsStruct` and then dump it?
    )
    await db["users"].find_one_and_update(
        {"_id": podcast_id},
        {"$pull": {"subscriptions": {"podcast":ObjectId(podcast_id)}}}  #? Make `UserSubsStruct` and then dump it?
    )

