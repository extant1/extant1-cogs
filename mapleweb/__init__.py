from redbot.core.bot import Red
from .mapleweb import MapleWeb


async def setup(bot: Red) -> None:
    await bot.add_cog(MapleWeb(bot))