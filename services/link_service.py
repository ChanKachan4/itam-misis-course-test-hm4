from utils.utils_random import random_alfanum
from repositories.link_repository import LinkRepository
from fastapi import Request


class LinkService:
    def __init__(self) -> None:
        self._link_repository = LinkRepository()

    async def create_link(self, real_link: str) -> str:
        short_link = random_alfanum(5)

        await self._link_repository.create_link(short_link, real_link)

        return short_link

    async def get_real_link(self, short_link: str, user_agent: str, ip: str) -> str | None:
        link = await self._link_repository.get_link(short_link=short_link)
        if link is None:
            return None

        await self._link_repository.create_link_usage(
            link_id=link.id,
            user_agent=user_agent,
            ip=ip
        )

        return str(link.real_link)

    async def get_link_statistics(self, short_link: str, page: int = 1, page_size: int = 10):
        return await self._link_repository.get_link_usage(short_link, page, page_size)
