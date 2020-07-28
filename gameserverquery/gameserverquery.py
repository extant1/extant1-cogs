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
            "enabled": False,
            "gm_role": None,
            "game": None,
            "ip": None,
            "game_port": None,
            "query_port": None
        }
        self.config.register_guild(**default_guild)

    async def query_info(self, ctx):
        ip = await self.config.guild(ctx.guild).ip()
        port = await self.config.guild(ctx.guild).port()
        if ip and port:
            try:
                return await a2s.info((ip, port), 2)
            except socket.timeout:
                await ctx.send("Connection timed out to server.")
                return None
            except socket.gaierror:
                await ctx.send("Invalid host address.")
                return None
        else:
            await ctx.send("IP and Port must be set.")
            return None

    async def query_players(self, ctx):
        ip = await self.config.guild(ctx.guild).ip()
        port = await self.config.guild(ctx.guild).port()
        if ip and port:
            try:
                return await a2s.players((ip, port), 2)
            except socket.timeout:
                await ctx.send("Connection timed out to server.")
                return None
            except socket.gaierror:
                await ctx.send("Invalid host address.")
                return None
        else:
            await ctx.send("IP and Port must be set.")
            return None

    @staticmethod
    def remove_microseconds(delta):
        return delta - datetime.timedelta(microseconds=delta.microseconds)

    @commands.guild_only()
    @commands.command(aliases=["p", "s"])
    async def players(self, ctx):
        """Query for player count."""
        info = await self.query_info(ctx)
        if info:
            if info.player_count == 0:
                await ctx.send("The server is empty.")
            else:
                await ctx.send("There are currently **{0}/{1}** players.".format(info.player_count, info.max_players))
        else:
            await ctx.send("Server could not be reached.")

    @commands.guild_only()
    @commands.command()
    async def ip(self, ctx):
        """Display the server IP and port."""
        ip = await self.config.guild(ctx.guild).ip()
        game_port = await self.config.guild(ctx.guild).game_port()
        if ip and game_port:
            await ctx.send("The server ip is " + bold(ip) + ":" + bold(game_port) + ".")
        else:
            await ctx.send("This information is not yet configured.")

    @commands.guild_only()
    @commands.command()
    async def mission(self, ctx):
        """Display the current mission."""
        info = self.query_info(ctx)
        if info:
            if info.folder is not None or "lifyo":
                await ctx.send("The server is running **" + info.game + "** on ** " + info.map_name + " **.")
            else:
                await ctx.send("There is no mission available for this game.")
        else:
            await ctx.send("Server could not be reached.")

    @commands.guild_only()
    @commands.command(name="who")
    async def who(self, ctx):
        """Display players in the server."""
        ip = await self.config.guild(ctx.guild).ip()
        port = await self.config.guild(ctx.guild).port()
        game = await self.config.guild(ctx.guild).game()
        if game is 'lifyo':
            await ctx.send("This game does not support player queries.")
        else:
            # necessary?
            info = self.query_info(ctx)
            if info.player_count == 0:
                await ctx.send("The server empty.")
            else:
                players = self.query_players(ctx)
                embed = discord.Embed(title="There are currently {0}/{1} players.".format(
                    info.player_count, info.max_players), description="Player list", color=0x1675a3)
                embed.set_author(name=info.server_name)
                for player in players:
                    embed.add_field(name=player.name, value=str(
                        self.remove_microseconds(datetime.timedelta(seconds=player.duration))), inline=True)
                await ctx.send(embed=embed)

    @checks.admin()
    @commands.guild_only()
    @commands.group(name="gameserverquery", alias="gsq", invoke_without_command=False)
    async def _gsq(self, ctx):
        """Change or view settings"""
        if ctx.invoked_subcommand is None:
            enabled = await self.config.guild(ctx.guild).enabled()
            ip = await self.config.guild(ctx.guild).ip()
            game_port = await self.config.guild(ctx.guild).game_port()
            query_port = await self.config.guild(ctx.guild).query_port()
            game = await self.config.guild(ctx.guild).game()
            gm_role = await self.config.guild(ctx.guild).gm_role()
            embed = discord.Embed(title="GameServerQuery settings",
                                  description="Current settings for the GameServerQuery.", color=0x1675a3)
            embed.add_field(name="Enabled", value=enabled, inline=True)
            embed.add_field(name="Game", value=game, inline=True)
            embed.add_field(name="IP", value=ip, inline=True)
            embed.add_field(name="Game Port", value=game_port, inline=True)
            embed.add_field(name="Query Port", value=query_port, inline=True)
            embed.add_field(name="GM Role", value=gm_role, inline=True)
            await ctx.send(embed=embed)

    @checks.admin()
    @commands.guild_only()
    @_gsq.command(name="ip")
    async def _ip(self, ctx, ip: str = None):
        """Set the ip."""
        if ip is not None:
            await self.config.guild(ctx.guild).ip.set(ip)
            await ctx.send("GameServerQuery ip is set to " + bold(ip) + ".")
        else:
            await ctx.send_help()

    @checks.admin()
    @commands.guild_only()
    @_gsq.command(name="gameport")
    async def _game_port(self, ctx, game_port: str = None):
        """Set the game port."""
        if game_port is not None:
            await self.config.guild(ctx.guild).game_port.set(game_port)
            await ctx.send("GameServerQuery game port is set to " + bold(game_port) + ".")
        else:
            await ctx.send_help()

    @checks.admin()
    @commands.guild_only()
    @_gsq.command(name="queryport")
    async def _query_port(self, ctx, query_port: str = None):
        """Set the query port."""
        if query_port is not None:
            await self.config.guild(ctx.guild).query_port.set(query_port)
            await ctx.send("GameServerQuery query port is set to " + bold(query_port) + ".")
        else:
            await ctx.send_help()

    @checks.admin()
    @commands.guild_only()
    @_gsq.command(name="role")
    async def _role(self, ctx, gm_role: str = None):
        """Set the discord GM role."""
        if gm_role is not None:
            await self.config.guild(ctx.guild).gm_role.set(gm_role)
            await ctx.send("GameServerQuery GM role is set to " + bold(gm_role) + ".")
        else:
            await ctx.send_help()

    @checks.admin()
    @commands.guild_only()
    @_gsq.command(name="game")
    async def _game(self, ctx, game: str = None):
        """Set the game."""
        if game is not None:
            await self.config.guild(ctx.guild).game.set(game)
            await ctx.send("GameServerQuery game is set to " + bold(game) + ".")
        else:
            info = self.query_info(ctx)
            await self.config.guild(ctx.guild).game.set(info.folder)
            await ctx.send("GameServerQuery used query info and set game to " + bold(game) + ".")

    @checks.admin()
    @commands.guild_only()
    @_gsq.command(name="toggleenable")
    async def _enable(self, ctx):
        """Enable or disable the GSQ."""
        enabled = await self.config.guild(ctx.guild).enabled()
        enabled = not enabled
        if enabled:
            await ctx.send("GameServerQuery is now enabled.")
        else:
            await ctx.send("GameServerQuery is now disabled.")
        await self.config.guild(ctx.guild).enabled.set(enabled)

    @checks.admin()
    @commands.guild_only()
    @commands.group(name="gsqdebug", invoke_without_command=False)
    async def _gsqdebug(self, ctx):
        """GameServerQuery debug"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @checks.admin()
    @commands.guild_only()
    @_gsqdebug.command(name="info")
    async def _info(self, ctx):
        """GameServerQuery debug info query."""
        info = (await self.query_info(ctx))
        debug_info = ""

        if info:
            for x, y in info:
                debug_info += '{} = {}\n'.format(x, y)
            await ctx.send("```py\n" + debug_info + "```")
        else:
            await ctx.send("Server could not be reached.")

    @checks.admin()
    @commands.guild_only()
    @_gsqdebug.command(name="player")
    async def _player(self, ctx):
        """GameServerQuery debug player query."""
        players = self.query_players(ctx)
        debug_info = ""

        if len(players) != 0:
            for x in players:
                debug_info += '{}\n'.format(x.name)
            await ctx.send("```json\n" + debug_info + "```")
        else:
            await ctx.send("Server could not be reached.")

    @checks.admin()
    @commands.guild_only()
    @_gsqdebug.command(name="what")
    async def _what(self, ctx):
        """GameServerQuery debug player query."""
        info = (await self.query_info(ctx))

        if info:
            await ctx.send(info)
