import asyncio

import aiohttp

from config import API_URL, API_TOKEN, MAIN_URL
from exceptions import BackendError


class APIClient:
    def __init__(self):
        self.base_url = API_URL
        self.token = API_TOKEN
        self.main_url = MAIN_URL

    async def fetch(self, url):
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Token {self.token}"}
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise BackendError("Backend response status not provided 200")

    async def post_request(self, category: str, data: dict):
        async with aiohttp.ClientSession() as session: # noqa
            headers = {"Authorization": f"Token {self.token}"}
            async with session.post(self.base_url + category + "/",
                                    headers=headers,
                                    json=data) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    raise BackendError("Backend response status not provided 201")

    async def create_user_request(self, data: dict):
        async with aiohttp.ClientSession() as session: # noqa
            headers = {"Authorization": f"Token {self.token}"}
            async with session.post(self.main_url + "create-user/",
                                    headers=headers,
                                    json=data) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    raise BackendError("Backend response status not provided 201")

    async def get_types(self,
                        tg_id: str,
                        category: str = "profit",
                        parent_id: int = None,
                        is_final: bool = True,
                        ):
        fetch_url = self.base_url + category + 'types/' + "?tg_id=" + str(tg_id)
        if is_final is False:
            resp = await self.fetch(fetch_url + "&parent_id=" + str(parent_id))
        else:
            resp = await self.fetch(fetch_url)

        return resp

    async def get_history(self, pk: str, tg_id: int, category: str = "profit"):
        fetch_url = self.base_url + category + 'types/'
        resp = await self.fetch(fetch_url + pk + "/?tg_id=" + str(tg_id))
        return resp

    async def get_report(self, user_id: int):
        await self.fetch(self.main_url + "send-report/?category=outlay&tg_id=" + str(user_id))
        await asyncio.sleep(5)
        await self.fetch(self.main_url + "send-report/?category=profit&tg_id=" + str(user_id))


api = APIClient()
