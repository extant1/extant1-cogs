from redbot.core.bot import Red
from .sentinel import Sentinel


async def setup(bot: Red) -> None:
    await bot.add_cog(Sentinel(bot))
