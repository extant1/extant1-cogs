import discord
from discord.ext import commands



class LifServerQuery:
    """Server information and query tool for life is feudal server."""

    def __init__(self, bot):
        self.bot = bot
	
	def query_server():
		SERVER_ADDRESS = ('64.94.95.122', 28082)

		with valve.source.a2s.ServerQuerier(SERVER_ADDRESS) as server:
			info = server.info()
		return "There are currently {player_count}/{max_players} players.".format(**info)

	
    @commands.command()
    async def ip(self):
        """Query the server for player count."""

        
        await self.bot.say("The server ip is:  64.94.95.122:28082")
		
	@commands.command()
    async def password(self):
        """Query the server for player count."""

        
        await self.bot.say("The is currently no server password.")
		
	

def setup(bot):
    bot.add_cog(LifServerQuery(bot))
