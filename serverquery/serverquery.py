import os
from .utils.dataIO import dataIO
from .utils import checks

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

    def _set_setting(self, ctx, setting, value):
        settings = self._get_settings(ctx)
        if not settings:
            settings = {"ip": "", "port": 0, "discord_gm_role": None}
        settings[setting] = value
        return self._set_settings(ctx, settings)

    def _set_settings(self, ctx, settings):
        serverid = ctx.message.server.id
        if serverid not in self.config:
            self.config[serverid] = {}
        self.config[serverid] = settings
        dataIO.save_json(JSON_PATH, self.config)

    def _get_settings(self, ctx):
        serverid = ctx.message.server.id
        if serverid not in self.config:
            return None
        else:
            return self.config[serverid]

    def query_info(self, ctx):
        settings = self._get_settings(ctx)
        if settings is not None:
            server_address = (settings['ip'], settings['port'])
            with valve.source.a2s.ServerQuerier(server_address) as server:
                return server.info()
        else:
            return None

    def query_players(self, ctx):
        settings = self._get_settings(ctx)
        if settings is not None:
            server_address = (settings['ip'], settings['port'])
            with valve.source.a2s.ServerQuerier(server_address) as server:
                return server.players()
        else:
            return None

    @commands.command(pass_context=True)
    async def players(self, ctx):
        """Query the server for player count."""
        if self.query_info(ctx) is not None:
            await self.bot.say("There are currently {player_count}/{max_players} players.".format(**self.query_info(ctx)))
        else:
            await self.bot.say("No server config available.")

    @commands.command(pass_context=True)
    async def ip(self, ctx):
        """Display the server IP."""
        if self.query_info(ctx) is not None:
            await self.bot.say("The server ip is: " + self.config[ctx.message.server.id]['ip'] + self.config[ctx.message.server.id]['port'])
        else:
            await self.bot.say("No server config available.")

    @commands.command(pass_context=True)
    async def mission(self, ctx):
        if self.query_info(ctx) is not None:
            await self.bot.say("We are playing {game} on {map}.".format(**self.query_info(ctx)))
        else:
            await self.bot.say("No server config available.")

    @checks.admin()
    @commands.group(name="gameserver", invoke_without_command=False, no_pm=True, pass_context=True)
    async def _server(self, ctx):
        """Change the server settings"""
        if ctx.invoked_subcommand is None:
            await self.bot.say("Missing required subcommand.")

    @_server.command(name="ip", pass_context=True)
    async def _ip(self, ctx, ip: str = None):
        """Add a game server ip to this discord."""
        self._set_setting(ctx, "ip", ip)

    @_server.command(name="port", pass_context=True)
    async def _port(self, ctx, port: int = None):
        """Add a game server port to this discord."""
        self._set_setting(ctx, "port", port)

    @_server.command(name="gm", pass_context=True)
    async def _gm(self, ctx, role: str = None):
        """Add the discord role that is an admin for this discord."""
        self._set_setting(ctx, "discord_gm_role", role)


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
