from infrastructure.db.connection import create_all_tables, sqlite_connection
from persistent.db.link import Link
from persistent.db.link_usage import LinkUsage
from sqlalchemy import insert, select


class LinkRepository:
    def __init__(self) -> None:
        self._sessionmaker = sqlite_connection()
        create_all_tables()

    async def create_link(self, short_link: str, real_link: str) -> None:
        stmp = insert(Link).values({"short_link": short_link, "real_link": real_link})

        async with self._sessionmaker() as session:
            await session.execute(stmp)
            await session.commit()

    async def get_link(self, short_link: str) -> Link | None:
        stmp = select(Link).where(Link.short_link == short_link).limit(1)

        async with self._sessionmaker() as session:
            resp = await session.execute(stmp)

        row = resp.fetchone()
        if row is None:
            return None

        return row[0]

    async def create_link_usage(self, user_agent: str, ip: str, link_id: str) -> None:
        stmp = insert(LinkUsage).values({"link_id": link_id, "user_agent": user_agent, "ip": ip})

        async with self._sessionmaker() as session:
            await session.execute(stmp)
            await session.commit()

    async def get_link_usage(self, short_link: str, page: int = 1, page_size: int = 10) -> list[LinkUsage]:
        link = await self.get_link(short_link)
        if link is None:
            return []

        offset = (page - 1) * page_size
        stmp = (select(LinkUsage)
                .where(LinkUsage.link_id == link.id)
                .order_by(LinkUsage.created_at.desc())
                .offset(offset)
                .limit(page_size))

        async with self._sessionmaker() as session:
            result = await session.execute(stmp)

        return result.scalars().all()
