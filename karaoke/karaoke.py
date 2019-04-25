from collections import deque

import discord
from discord.ext import commands

from .utils import checks


class Karaoke:
    """Karaoke queue commands."""

    def __init__(self, bot):
        self.bot = bot
        self.queue = deque()

    @commands.group(name="karaoke", invoke_without_command=False, pass_context=True, no_pm=True, aliases=["k"])
    async def _karaoke(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @_karaoke.command(pass_context=True, no_pm=True, aliases=["s"])
    async def list(self):
        await self.bot.say(", ".join(list(self.queue)))

    # needs karaoke role permission
    @_karaoke.command(pass_context=True, no_pm=True, aliases=["a"])
    async def add(self, ctx, user: discord.Member = None):
        if user:
            self.queue.append(user.display_name)
        else:
            user = ctx.message.author
            self.queue.append(user.display_name)
        await self.bot.say(user.display_name + " added to the queue.")

    @_karaoke.command(pass_context=True, no_pm=True, aliases=["j"])
    async def join(self, ctx):
        user = ctx.message.author
        self.queue.append(user.display_name)
        await self.bot.say(user.display_name + " added to the queue.")

    # needs karaoke role permission
    @_karaoke.command(pass_context=True, no_pm=True, aliases=["r"])
    async def remove(self, ctx, user: discord.Member = None):
        if user:
            self.queue.remove(user.display_name)
        else:
            user = ctx.message.author
            self.queue.remove(user.display_name)
        await self.bot.say(user.display_name + " removed from the queue.")

    @_karaoke.command(pass_context=True, no_pm=True, aliases=["l"])
    async def leave(self, ctx):
        user = ctx.message.author
        self.queue.remove(user.display_name)
        await self.bot.say(user.display_name + " removed from the queue.")

    # needs karaoke role permission
    @_karaoke.command(pass_context=True, no_pm=True, aliases=["skip", "n"])
    async def next(self, ctx, user: discord.Member = None):
        pass

    # needs karaoke role permission
    @_karaoke.command(pass_context=True, no_pm=True, aliases=["b"])
    async def back(self, ctx, user: discord.Member = None):
        pass

    @_karaoke.command(pass_context=True, no_pm=True, aliases=["d", "finished"])
    async def done(self, ctx, user: discord.Member = None):
        pass

    # needs karaoke role permission
    @_karaoke.command(pass_context=True, no_pm=True)
    async def reset(self, ctx):
        pass

    # needs karaoke role permission
    @_karaoke.command(pass_context=True, no_pm=True)
    async def shuffle(self, ctx):
        pass

    # @commands.command(pass_context=True)
    # async def inactive(self, ctx, user: discord.Member = None):
    #     pass

    # @commands.command(pass_context=True)
    # async def active(self, ctx, user: discord.Member = None):
    #     pass


def setup(bot):
    bot.add_cog(Karaoke(bot))
