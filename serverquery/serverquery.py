import os
import datetime
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
            settings = {"ip": None, "port": None, "discord_gm_role": None, "port_modifier": None}
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

    @staticmethod
    def remove_microseconds(delta):
        return delta - datetime.timedelta(microseconds=delta.microseconds)

    @commands.command(pass_context=True, no_pm=True)
    async def players(self, ctx):
        """Query the server for player count."""
        info = self.query_info(ctx)
        if info is not None:
            if info['player_count'] is 0:
                await self.bot.say("The server is empty, why not ask if anyone would like to play?")
            else:
                await self.bot.say("There are currently **{player_count}/{max_players}** players.".format(**info))
        else:
            await self.bot.say("No server config available.")

    @commands.command(pass_context=True, no_pm=True)
    async def ip(self, ctx):
        """Display the server IP."""
        settings = self._get_settings(ctx)
        if settings['port_modifier'] is None:
            await self.bot.say(
                "Can't determine game join port without port modifier, please use !gameserver modifier to set.")
        else:
            port = (int(settings['port']) - int(settings['port_modifier']))
            if self.query_info(ctx) is not None:
                await self.bot.say(
                    "The server ip is: " + chat_formatting.bold(settings['ip']) + ":" + chat_formatting.bold(str(port)))
            else:
                await self.bot.say("No server config available.")

    @commands.command(pass_context=True, no_pm=True)
    async def mission(self, ctx):
        """Display the current mission."""
        info = self.query_info(ctx)
        if info is not None:
            if info['game'] is not None or "lifyo":
                await self.bot.say("The server is running **{game}** on **{map}**.".format(**info))
            else:
                return
        else:
            await self.bot.say("No server config available.")

    @commands.command(name="who", pass_context=True)
    async def who(self, ctx):
        """Display players in the server if available."""
        settings = self._get_settings(ctx)
        if settings['game'] is 'lifyo':
            await self.bot.say("This game does not support player queries.")
        elif settings['game'] is None:
            await self.bot.say("No one is currently in the server.")
        else:
            players = self.query_players(ctx)
            info = self.query_info(ctx)
            embed = discord.Embed(title="Player list")
            embed.set_author(name=info['server_name'], color=0x1675a3)
            for player in players['players']:
                embed.add_field(name=player.values['name'], value=str(
                    self.remove_microseconds(datetime.timedelta(seconds=player.values['duration']))), inline=True)
            await self.bot.say(embed=embed)

    @checks.admin()
    @commands.group(name="gameserver", invoke_without_command=False, pass_context=True, no_pm=True)
    async def _server(self, ctx):
        """Change the server settings"""
        if ctx.invoked_subcommand is None:
            settings = self._get_settings(ctx)
            embed = discord.Embed(title="Gameserver Settings",
                                  description="Current settings for the game server query.", color=0x1675a3)
            embed.add_field(name="IP", value=settings['ip'], inline=True)
            embed.add_field(name="Port", value=settings['port'], inline=True)
            embed.add_field(name="Game", value=settings['game'], inline=True)
            embed.add_field(name="GM Role", value=settings['discord_gm_role'], inline=True)
            embed.add_field(name="Port modifier", value="-" + str(settings['port_modifier']) + " (" + str(
                (settings['port'] - settings['port_modifier'])) + ")", inline=True)
            await self.bot.say(embed=embed)
            await self.bot.send_cmd_help(ctx)

    @checks.admin()
    @_server.command(name="ip", pass_context=True, no_pm=True)
    async def _ip(self, ctx, ip: str = None):
        """Set the server query ip."""
        if ip is not None:
            self._set_setting(ctx, "ip", ip)
            await self.bot.say("Setting server query ip to: " + chat_formatting.bold(ip))
        else:
            await self.bot.send_cmd_help(ctx)

    @checks.admin()
    @_server.command(name="port", pass_context=True, no_pm=True)
    async def _port(self, ctx, port: int = None):
        """Set the server query port."""
        if port is not None:
            self._set_setting(ctx, "port", port)
            await self.bot.say("Setting server query port to: " + chat_formatting.bold(str(port)))
        else:
            await self.bot.send_cmd_help(ctx)

    @checks.admin()
    @_server.command(name="modifier", pass_context=True, no_pm=True)
    async def _port_modifier(self, ctx, modifier: int = None):
        """Set the server query port modifier to the value needed to subtract to get the game server join port."""
        if modifier is not None:
            self._set_setting(ctx, "port_modifier", modifier)
            await self.bot.say("Setting server query port modifier to: " + chat_formatting.bold(str(modifier)))
        else:
            await self.bot.send_cmd_help(ctx)

    @checks.admin()
    @_server.command(name="role", pass_context=True, no_pm=True)
    async def _role(self, ctx, role: str = None):
        """Set the server query discord GM role."""
        if role is not None:
            self._set_setting(ctx, "discord_gm_role", role)
            await self.bot.say("Setting server query GM role to: " + chat_formatting.bold(role))
        else:
            await self.bot.send_cmd_help(ctx)

    @checks.admin()
    @_server.command(name="game", pass_context=True, no_pm=True)
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
    @commands.group(name="querydebug", invoke_without_command=False, no_pm=True, pass_context=True)
    async def _querydebug(self, ctx):
        """Server Query debug info."""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @checks.admin()
    @_querydebug.command(name="info", pass_context=True)
    async def _info(self, ctx):
        """Server Query debug info query."""
        info = self.query_info(ctx)
        debug_info = ""

        if info is not None:
            for x, y in info.items():
                debug_info += '{} = {}\n'.format(x, y)
            await self.bot.say("```py\n" + debug_info + "```")
        else:
            await self.bot.say("No server config available.")

    @checks.admin()
    @_querydebug.command(name="player", pass_context=True)
    async def _player(self, ctx):
        """Server Query debug player query."""
        players = self.query_players(ctx)
        debug_info = ""

        if len(players['players']) is not 0:
            for x in players['players']:
                debug_info += '{}\n'.format(x.values)
            await self.bot.say("```json\n" + debug_info + "```")
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
