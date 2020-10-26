import httpx

from redbot.core import Config, commands


class MapleWeb(commands.Cog):
    """Companion cog to the ardent maple website to link users to the website for purposes of synchronizing roles."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=91928524318855168)
        self.verify_url = "https://ardentmaples.com/api/verify"

    @commands.command(aliases=["register", "witnessme"])
    async def verify(self, ctx):
        """Make get request to web api and return a code which is
        passed to the user with instructions on how to use it on the website."""
        # get user id snowflake
        snowflake = ctx.author.id
        # make get request
        async with httpx.AsyncClient() as client:
            params = {'snowflake': snowflake}
            response = await client.post(self.verify_url, params=params)
        # return
        response.json()
