from fastapi import APIRouter

from db.podcasts import get_podcast_details, get_podcast_episode_details, get_podcast_episode_list, get_podcast_list

router = APIRouter(prefix='/v1')




@router.get("/podcasts")
async def podcast_list():
    res = await get_podcast_list()
    return res


@router.get("/podcast/{id}")
async def podcast_details(id):
    res = await get_podcast_details(id)
    return res

