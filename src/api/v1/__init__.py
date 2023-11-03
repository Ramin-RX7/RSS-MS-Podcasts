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


@router.get("/podcast/{id}/episodes")
async def podcast_episodes(id):
    res = await get_podcast_episode_list(id)
    return res


@router.get("/podcast/{podcast_id}/episode/{episode_id}")
async def podcast_episode_detail(podcast_id, episode_id):
    res = await get_podcast_episode_details(episode_id)
    return res
