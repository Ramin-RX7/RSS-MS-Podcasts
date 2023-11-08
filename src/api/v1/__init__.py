from fastapi import APIRouter, Depends

from auth import JWTHandler
from db.podcasts import (
    get_podcast_details,
    get_podcast_episode_details,
    get_podcast_episode_list,
    get_podcast_list,
    like_episode,
    subscribe_podcast,
    unlike_episode,
    unsubscribe_podcast,
)
from schemas.jwt import JWTPayload


router = APIRouter(prefix='/v1')

jwt_object = JWTHandler()



@router.get("/podcasts")
async def podcast_list():
    res = await get_podcast_list()
    return res or {"msg":"not podcast found"}


@router.get("/podcast/{id}")
async def podcast_details(id):
    res = await get_podcast_details(id)
    return res or {"msg":"no podcast with this id found"}


@router.get("/podcast/{id}/episodes")
async def podcast_episodes(id):
    res = await get_podcast_episode_list(id)
    return res or {"msg":"no episodes found"}


@router.get("/podcast/{podcast_id}/episode/{episode_id}")
async def podcast_episode_detail(podcast_id, episode_id):
    res = await get_podcast_episode_details(episode_id)
    return res
