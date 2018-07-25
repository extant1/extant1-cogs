import os
from .utils.dataIO import dataIO
from .utils import checks
from .utils import chat_formatting

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
        info = self.query_info(ctx)
        if info is not None:
            await self.bot.say("There are currently ***{player_count}/{max_players}*** players.".format(**info))
        else:
            await self.bot.say("No server config available.")

    @commands.command(pass_context=True)
    async def ip(self, ctx):
        """Display the server IP."""
        settings = self._get_settings(ctx)
        if settings['game'] is "Arma3":
            port = int(settings['port']) - 1
        elif settings['game'] is 'lifyo':
            port = int(settings['port'] -2)
        else:
            port = settings['game']
        if self.query_info(ctx) is not None:
            await self.bot.say("The server ip is: " + settings['ip'] + chat_formatting.bold(str(port)))
        else:
            await self.bot.say("No server config available.")

    @commands.command(pass_context=True)
    async def mission(self, ctx):
        """Display the current mission."""
        info = self.query_info(ctx)
        if info is not None:
            if info['game'] is not None or "Life is Feudal: Your Own":
                await self.bot.say("We are playing ***{game}*** on ***{map}***.".format(**info))
            else:
                return
        else:
            await self.bot.say("No server config available.")

    @checks.admin()
    @commands.group(name="gameserver", invoke_without_command=False, no_pm=True, pass_context=True)
    async def _server(self, ctx):
        """Change the server settings"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @_server.command(name="ip", pass_context=True)
    async def _ip(self, ctx, ip: str = None):
        """Set the server query ip."""
        if ip is not None:
            self._set_setting(ctx, "ip", ip)
            await self.bot.say("Setting server query ip to: " + chat_formatting.bold(ip))
        else:
            await self.bot.send_cmd_help(ctx)

    @_server.command(name="port", pass_context=True)
    async def _port(self, ctx, port: int = None):
        """Set the server query port."""
        if port is not None:
            self._set_setting(ctx, "port", port)
            await self.bot.say("Setting server query port to: " + chat_formatting.bold(str(port)))
        else:
            await self.bot.send_cmd_help(ctx)

    @_server.command(name="role", pass_context=True)
    async def _role(self, ctx, role: str = None):
        """Set the server query discord GM role."""
        if role is not None:
            self._set_setting(ctx, "discord_gm_role", role)
            await self.bot.say("Setting server query GM role to: " + chat_formatting.bold(role))
        else:
            await self.bot.send_cmd_help(ctx)

    @_server.command(name="game", pass_context=True)
    async def _game(self, ctx, game: str = None):
        """Set the server query game."""
        if game is not None:
            self._set_setting(ctx, "game", game)
            await self.bot.say("Setting server query game to: " + chat_formatting.bold(game))
        else:
            info = self.query_info(ctx)
            self._set_setting(ctx, "game", info['folder'])
            await self.bot.say("Setting server query game to: " + chat_formatting.bold(info['folder']))

    @checks.admin()
    @commands.command(name="querydebug", pass_context=True)
    async def _querydebug(self, ctx):
        info = self.query_info(ctx)
        debug_info = ""

        if info is not None:
            for x, y in info.items():
                debug_info += '{} = {}\n'.format(x, y)
            await self.bot.say("```py\n" + debug_info + "```")
        else:
            await self.bot.say("No server config available.")


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
