import asyncio

from github_api.client import GitHubAPI


async def main():

    async with GitHubAPI() as api:

        user = await api.get_user("torvalds")

        print("\n=== USER INFO ===")
        print("Name:", user["name"])
        print("Followers:", user["followers"])

        print("\n=== REPOSITORIES ===")

        async for repo in api.get_repos("torvalds"):

            print("-", repo["name"])


asyncio.run(main())