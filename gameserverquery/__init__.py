from redbot.core.bot import Red
from .gameserverquery import GameServerQuery


async def setup(bot: Red) -> None:
    await bot.add_cog(GameServerQuery(bot))
