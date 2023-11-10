from bson import ObjectId
import bson.errors

from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.responses import JSONResponse

from auth import JWTHandler
from db import db
from db.podcasts import (
    get_podcast_details,
    get_podcast_episode_details,
    # get_podcast_episode_list,
    get_podcast_list,
    like_episode,
    subscribe_podcast,
    unlike_episode,
    unsubscribe_podcast,
    update_db,
)
from schemas import JWTPayload, Podcast,Result



router = APIRouter(prefix='/v1')

jwt_object = JWTHandler()




def validate_id(id:str):
    try:
        return ObjectId(id)
    except bson.errors.InvalidId:
        raise HTTPException(404, "Not found")


@router.get("/podcasts")
async def podcast_list():
    res = await db["podcasts"].find(projection={"episodes":0,"subscribers":0}).to_list(100)
    if res:
        return list(map(
            lambda item: item.model_dump(exclude_defaults=True), map(Podcast.model_validate, res)
        ))
    return {"msg":"not podcast found"}


@router.get("/podcast/{id}")
async def podcast_details(id:str=Depends(validate_id)):
    res = await get_podcast_details(id)
    return res or {"msg":"no podcast with this id found"}


# @router.get("/podcast/{id}/episodes")
# async def podcast_episodes(id):
#     res = await get_podcast_episode_list(id)
#     return res or {"msg":"no episodes found"}

@router.get("/podcast/{podcast_id}/episode/{episode_id}")
async def podcast_episode_detail(podcast_id:str, episode_id:str):
    res = await get_podcast_episode_details(ObjectId(podcast_id), ObjectId(episode_id))
    return res or {"msg": "no episode with this id has been found"}



@router.post("/podcast/{podcast_id}/episode/{episode_id}/like")
async def like_episode_api(podcast_id, episode_id, jwt:JWTPayload=Depends(jwt_object)):
    res = await like_episode(episode_id, jwt.id)
    return {"msg":"ok"}

@router.post("/podcast/{podcast_id}/episode/{episode_id}/unlike")
async def unlike_episode_api(podcast_id, episode_id, jwt:JWTPayload=Depends(jwt_object)):
    res = await unlike_episode(episode_id, jwt.id)
    return {"msg":"ok"}


@router.post("/podcast/{podcast_id}/subscribe/")
async def subscribe_podcast_api(podcast_id, jwt:JWTPayload=Depends(jwt_object)):
    res = await subscribe_podcast(podcast_id, jwt.id)
    return {"msg":"ok"}

@router.post("/podcast/{podcast_id}/unsubscribe/")
async def unsubscribe_podcast_api(podcast_id, jwt:JWTPayload=Depends(jwt_object)):
    res = await unsubscribe_podcast(podcast_id, jwt.id)
    return {"msg":"ok"}


