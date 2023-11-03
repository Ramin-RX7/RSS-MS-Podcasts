import httpx

from schemas import Result



class PodcastAPIService:
    def __init__(self, accounts_url, http_client=None):
        self.base_url = accounts_url
        self.http_client = http_client or httpx.AsyncClient()

    async def __del__(self):  #!? Does this (async destructor) work?
        self.http_client.aclose()


    async def podcast_list(self):
        """
        NOTE: with considering response will be:
            resp = [
                {
                    ...
                }
            ]
        we do not need to change the response, so we return it directly
        """
        # status_code,resp = await self._request("podcasts")
        status_code = 200
        resp = [
            {
                "id" : 1,
                "title": "my podcast title",
                "category": "crime",
            }
        ]
        if status_code == 200:
            return Result(True, data={"podcasts":resp})

    async def podcast_details(self, identifier):
        """
        NOTE: with considering response will be:
            resp = {
                ...
            }
        we do not need to change the response, so we return it directly
        """
        # status_code,resp = await self._request("podcasts")
        status_code = 200
        resp = {
            "id" : 1,
            "title": "my podcast title",
            "category": "crime",
        }
        if status_code == 200:
            return Result(True, data={"podcast":resp})

    async def podcast_episode_list(self, podcast_identifier):
        """
        NOTE: with considering response will be:
            resp =[
                {
                    "id": 1,
                    "title": "ep1"
                },
                ...
            ]
        we do not need to change the response, so we return it directly
        """
        # status_code,resp = await self._request("podcasts")
        status_code = 200
        resp = [
            {
                "id": 2,
                "title": "ep1",
                "duration": 120,
            },
            {
                "id": 3,
                "title": "ep2",
                "duration": 53,
            }
        ]
        if status_code == 200:
            return Result(True, data={"episodes":resp})

    async def podcast_episode_details(self,podcast_identifier):
        """
        NOTE: with considering response will be:
            resp = {
                "id": 1,
                "title": "ep1"
            }
        we do not need to change the response, so we return it directly
        """
        # status_code,resp = await self._request("podcasts")
        status_code = 200
        resp = {
            "id": 2,
            "title": "ep2",
            "duration": 53,
        }
        if status_code == 200:
            return Result(True, data={"episode":resp})






    async def _request(self, url, data:dict=None) -> tuple[int, dict]:
        requested_url = f"{self.base_url}/{url}/"
        try:
            async with self.http_client as client:
                if data:
                    response = await client.post(requested_url, json=data)
                else:
                    response = await client.get(requested_url)
            return response.status_code,response.json()
        except Exception as e:
            res = Result.resolve_exception(e)
            res.status = None
            return 500,res
