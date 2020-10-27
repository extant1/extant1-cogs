import json
import httpx

from redbot.core import Config, commands


class MapleWeb(commands.Cog):
    """Companion cog to the ardent maple website to link users to the website for purposes of synchronizing roles."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=91928524318855168)
        self.verify_url = "https://ardentmaples.com/api/discord/verify"

    @commands.command(aliases=["register", "witnessme"])
    async def verify(self, ctx):
        """Make get request to web api and return a code which is
        passed to the user with instructions on how to use it on the website."""
        # get user id snowflake
        snowflake = ctx.author.id
        # make get request
        async with httpx.AsyncClient() as client:
            data = json.dumps({'snowflake': snowflake})
            r = await client.post(self.verify_url, data=data, headers={'Content-Type': 'application/json'})
        # return
        if r.status_code == 200:
            if r.json()['status'] == 1:
                await ctx.send("Your code is:  {}".format(r.json()['code']))
                await ctx.send(
                    "Visit the https://ardentmaples.com/settings/ and input the discord code to synchronize with the website.")
            elif r.json()['status'] == 2:
                await ctx.send("A previous attempt was found!")
                await ctx.send("Your code is:  {}".format(r.json()['code']))
                await ctx.send(
                    "Visit the https://ardentmaples.com/settings/ and input the discord code to synchronize with the website.")
            else:
                await ctx.send("Something went wrong!")
