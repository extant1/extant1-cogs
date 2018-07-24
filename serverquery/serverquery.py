import json

import discord
from discord.ext import commands

import valve.source.a2s

with open('config.json', 'r') as f:
    config = json.load(f)


def query_info(ctx):
    server_address = (config[ctx.message.server.id]['ip'], config[ctx.message.server.id]['port'])

    with valve.source.a2s.ServerQuerier(server_address) as server:
        return server.info()


def query_players(ctx):
    server_address = (config[ctx.message.server.id]['ip'], config[ctx.message.server.id]['port'])

    with valve.source.a2s.ServerQuerier(server_address) as server:
        return server.players()


class ServerQuery:
    """Server information and query tool for life is feudal server."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="players", pass_context=True)
    async def players(self, ctx):
        """Query the server for player count."""
        await self.bot.say("There are currently {player_count}/{max_players} players.".format(**query_info(ctx)))

    @commands.command(name="ip", pass_context=True)
    async def ip(self, ctx):
        """Display the server IP."""

        await self.bot.say("The server ip is: " + config[ctx.message.server.id]['ip'] + config[ctx.message.server.id]['port'])

    # @commands.command()
    # async def password(self):
    #     """Display the server password."""
    #
    #     await self.bot.say("There is currently no server password.")

    @commands.command(name="mission", pass_context=True)
    async def mission(self, ctx):
        await self.bot.say("We are playing {game} on {map}.".format(**query_info(ctx)))

    @commands.command(pass_context=True)
    async def unflip(self, ctx, user: discord.Member = None):
        """Unflip yourself or another user."""
        if user != None:
            msg = ""
            if user.id == self.bot.user.id:
                pass
            char = "abcdefghijklmnopqrstuvwxyz"
            tran = "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz"
            table = str.maketrans(char, tran)
            name = user.display_name
            await self.bot.say(msg + name + " ノ( ゜-゜ノ)")
        else:
            name = ctx.message.author.display_name
            await self.bot.say(name + " ノ( ゜-゜ノ)")


def setup(bot):
    bot.add_cog(ServerQuery(bot))
