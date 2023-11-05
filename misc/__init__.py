from redbot.core.bot import Red
from .misc import Misc


async def setup(bot: Red) -> None:
    await bot.add_cog(Misc(bot))
