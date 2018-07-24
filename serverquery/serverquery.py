import os
from .utils.dataIO import dataIO

import discord
from discord.ext import commands

import valve.source.a2s

DATA_PATH = "data/serverquery/"
JSON_PATH = DATA_PATH + "config.json"
# LOG_PATH = DATA_PATH + "serverquery.log"


class ServerQuery:
    """Server information and query tool for life is feudal server."""

    def __init__(self, bot):
        self.bot = bot
        self.config = dataIO.load_json(JSON_PATH)

    def query_info(self, ctx):
        server_address = (self.config[ctx.message.server.id]['ip'], self.config[ctx.message.server.id]['port'])

        with valve.source.a2s.ServerQuerier(server_address) as server:
            return server.info()

    def query_players(self, ctx):
        server_address = (self.config[ctx.message.server.id]['ip'], self.config[ctx.message.server.id]['port'])

        with valve.source.a2s.ServerQuerier(server_address) as server:
            return server.players()

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


def check_folders():
    if os.path.exists("data/serverquery/"):
        os.rename("data/serverquery/", DATA_PATH)
    if not os.path.exists(DATA_PATH):
        print("Creating data/serverquery folder...")
        os.mkdir(DATA_PATH)


def check_files():
    if not dataIO.is_valid_json(JSON_PATH):
        print("Creating config.json...")
        dataIO.save_json(JSON_PATH, {})


def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(ServerQuery(bot))
