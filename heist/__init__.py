from redbot.core.bot import Red
from .heist import Heist


async def setup(bot: Red) -> None:
    await bot.add_cog(Heist(bot))