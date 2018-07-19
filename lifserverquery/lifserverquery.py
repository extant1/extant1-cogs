import discord
from discord.ext import commands

import valve.source.a2s

def query_server():
    SERVER_ADDRESS = ('64.94.95.122', 28082)

    with valve.source.a2s.ServerQuerier(SERVER_ADDRESS) as server:
        info = server.info()
    return "There are currently {player_count}/{max_players} players.".format(**info)


class LifServerQuery:
    """Server information and query tool for life is feudal server."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def players(self):
        """Query the server for player count."""
        await self.bot.say(query_server())
	
    @commands.command()
    async def ip(self):
        """Display the server IP."""

        await self.bot.say("The server ip is:  64.94.95.122:28082")
		
    @commands.command()
    async def password(self):
        """Display the server password."""

        await self.bot.say("There is currently no server password.")
		
	

def setup(bot):
    bot.add_cog(LifServerQuery(bot))
