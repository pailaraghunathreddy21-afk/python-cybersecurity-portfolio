import aiohttp
import asyncio
from typing import AsyncGenerator

from github_api.exceptions import (
    NotFoundError,
    RateLimitError,
    ServerError
)


class GitHubAPI:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str = None):
        self.token = token

        headers = {}

        if token:
            headers["Authorization"] = f"Bearer {token}"

        self.session = aiohttp.ClientSession(headers=headers)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def _request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.BASE_URL}/{endpoint}"

        for attempt in range(3):

            try:
                async with self.session.request(
                    method,
                    url,
                    **kwargs
                ) as response:

                    print(f"Status: {response.status}")

                    if response.status == 404:
                        raise NotFoundError("Resource not found")

                    if response.status == 429:
                        raise RateLimitError("Rate limit exceeded")

                    if response.status in [500, 502, 503]:
                        raise ServerError("GitHub server error")

                    response.raise_for_status()

                    return await response.json()

            except ServerError:
                print(f"Retrying... Attempt {attempt + 1}")
                await asyncio.sleep(2)

    async def get_user(self, username: str) -> dict:

        return await self._request(
            "GET",
            f"users/{username}"
        )

    async def get_repos(
        self,
        username: str
    ) -> AsyncGenerator[dict, None]:

        page = 1

        while True:

            data = await self._request(
                "GET",
                f"users/{username}/repos",
                params={
                    "page": page,
                    "per_page": 10
                }
            )

            if not data:
                break

            for repo in data:
                yield repo

            page += 1