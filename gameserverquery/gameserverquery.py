import datetime
import socket

import a2s
import discord

from redbot.core import Config, commands, checks
from redbot.core.utils.chat_formatting import bold


class GameServerQuery(commands.Cog):
    """Server information and query tool for life is feudal server."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=91928524318855168)
        default_guild = {
            "gm_role": None,
            "game": None,
            "ip": None,
            "game_port": None,
            "query_port": None
        }
        self.config.register_guild(**default_guild)

    @staticmethod
    async def query_info(self, ctx):
        ip = await self.config.guild(ctx.guild).ip()
        port = await self.config.guild(ctx.guild).port()
        if ip and port:
            try:
                return await a2s.info((ip, port), 2)
            except socket.timeout:
                await ctx.send("Connection timed out to server.")
            except socket.gaierror:
                await ctx.send("Invalid host address.")
        else:
            await ctx.send("IP and Port must be set.")
            return None

    @staticmethod
    async def query_players(self, ctx):
        ip = await self.config.guild(ctx.guild).ip()
        port = await self.config.guild(ctx.guild).port()
        if ip and port:
            try:
                return await a2s.players((ip, port), 2)
            except socket.timeout:
                await ctx.send("Connection timed out to server.")
            except socket.gaierror:
                await ctx.send("Invalid host address.")
        else:
            await ctx.send("IP and Port must be set.")
            return None

    @staticmethod
    def remove_microseconds(delta):
        return delta - datetime.timedelta(microseconds=delta.microseconds)

    @commands.command(pass_context=True, no_pm=True, aliases=["p"])
    async def players(self, ctx):
        """Query the server for player count."""
        info = self.query_info(ctx)
        if info is not None:
            if info['player_count'] is 0:
                await self.bot.say("The server is empty.")
            else:
                await self.bot.say("There are currently **{player_count}/{max_players}** players.".format(**info))
        else:
            await self.bot.say("There is either no server config or it is invalid and the server could not be reached.")

    @commands.command(pass_context=True, no_pm=True, aliases=["s"])
    async def server(self, ctx):
        """Reeeeeeeeeeeee."""
        info = self.query_info(ctx)
        if info is not None:
            if info['player_count'] is 0:
                await self.bot.say("There are no players inside me.")
            else:
                await self.bot.say("There are currently **{player_count}/{max_players}** players inside me.".format(**info))
        else:
            await self.bot.say("There is either no server config or it is invalid and the server could not be reached.")

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
                    "The server ip is: " + bold(settings['ip']) + ":" + bold(str(port)))
            else:
                await self.bot.say("There is either no server config or it is invalid and the server could not be reached.")

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
            await self.bot.say("There is either no server config or it is invalid and the server could not be reached.")

    @commands.command(name="who", pass_context=True, no_pm=True)
    async def who(self, ctx):
        """Display players in the server if available."""
        settings = self._get_settings(ctx)
        if settings['game'] is 'lifyo':
            await self.bot.say("This game does not support player queries.")
        elif settings['game'] is None:
            await self.bot.say("No one is currently in the server.")
        else:
            info = self.query_info(ctx)
            if info['player_count'] is 0:
                await self.bot.say("The server empty.")
            else:
                players = self.query_players(ctx)
                embed = discord.Embed(title="There are currently {player_count}/{max_players} players.".format(
                    **info), description="Player list", color=0x1675a3)
                embed.set_author(name=info['server_name'])
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
            await self.bot.say("Setting server query ip to: " + bold(ip))
        else:
            await self.bot.send_cmd_help(ctx)

    @checks.admin()
    @_server.command(name="port", pass_context=True, no_pm=True)
    async def _port(self, ctx, game_port: int = None):
        """Set the server query port."""
        if game_port is not None:
            await self.config.guild(ctx.guild).game_port.set(game_port)
            await ctx.send("GameServerQuery game port is set to " + bold(game_port) + ".")
        else:
            await self.bot.send_cmd_help(ctx)

    @checks.admin()
    @_server.command(name="role", pass_context=True, no_pm=True)
    async def _role(self, ctx, gm_role: str = None):
        """Set the server query discord GM role."""
        if gm_role is not None:
            await self.config.guild(ctx.guild).gm_role.set(gm_role)
            await ctx.send("GameServerQuery GM role is set to " + bold(gm_role) + ".")
        else:
            await self.bot.send_cmd_help(ctx)

    @checks.admin()
    @_server.command(name="game", pass_context=True, no_pm=True)
    async def _game(self, ctx, game: str = None):
        """Set the server query game."""
        if game is not None:
            await self.config.guild(ctx.guild).game.set(game)
            await ctx.send("GameServerQuery game is set to " + bold(game) + ".")
        else:
            info = self.query_info(ctx)
            await self.config.guild(ctx.guild).game.set(info.folder)
            await ctx.send("GameServerQuery used query info and set game to " + bold(game) + ".")

    # @checks.admin()
    # @commands.group(name="querydebug", invoke_without_command=False, no_pm=True, pass_context=True)
    # async def _querydebug(self, ctx):
    #     """Server Query debug info."""
    #     if ctx.invoked_subcommand is None:
    #         await self.bot.send_cmd_help(ctx)
    #
    # @checks.admin()
    # @_querydebug.command(name="info", pass_context=True, no_pm=True)
    # async def _info(self, ctx):
    #     """Server Query debug info query."""
    #     info = self.query_info(ctx)
    #     debug_info = ""
    #
    #     if info is not None:
    #         for x, y in info.items():
    #             debug_info += '{} = {}\n'.format(x, y)
    #         await self.bot.say("```py\n" + debug_info + "```")
    #     else:
    #         await self.bot.say("There is either no server config or it is invalid and the server could not be reached.")
    #
    # @checks.admin()
    # @_querydebug.command(name="player", pass_context=True, no_pm=True)
    # async def _player(self, ctx):
    #     """Server Query debug player query."""
    #     players = self.query_players(ctx)
    #     debug_info = ""
    #
    #     if len(players['players']) is not 0:
    #         for x in players['players']:
    #             debug_info += '{}\n'.format(x.values)
    #         await self.bot.say("```json\n" + debug_info + "```")
    #     else:
    #         await self.bot.say("There is either no server config or it is invalid and the server could not be reached.")
