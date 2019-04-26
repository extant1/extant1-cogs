from collections import deque
import os

import discord
from discord.ext import commands

from .utils import checks
from .utils.dataIO import dataIO
from .utils.chat_formatting import question, italics, bold, box


DATA_PATH = 'data/karaoke/'
JSON_PATH = DATA_PATH + 'config.json'


class Karaoke:
    """Karaoke queue commands."""

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json(JSON_PATH)
        self.queue = deque()

    def save(self):
        dataIO.save_json(JSON_PATH, self.settings)

    def get_settings(self, server):
        sid = server.id
        return self.settings.get(sid, {})

    def update_settings(self, server, settings):
        self.settings[server.id] = settings
        self.save()

    @commands.group(name="karaoke", invoke_without_command=False, pass_context=True, no_pm=True, aliases=["k"])
    async def _karaoke(self, ctx):
        if ctx.invoked_subcommand is None:
            if len(list(self.queue)) is not 0:
                embed = discord.Embed(title="Up Next:  " + self.queue[1], color=0x31df2d)
                embed.set_author(name="Current:  " + self.queue[0])
                if len(list(self.queue)) > 2:
                    embed.set_footer(text="Queue: " + ", ".join(list(self.queue)[2:]))
                await self.bot.say(embed=embed)
            else:
                await self.bot.say("The queue is empty.")

    @_karaoke.command(name="help", pass_context=True, no_pm=True)
    async def _help(self, ctx):
        user = ctx.message.author
        settings = self.get_settings(ctx.message.server)
        print(user.roles)
        print(settings['role'])
        embed = discord.Embed(title="Karaoke Commands")
        embed.add_field(name="join | j", value="Join the Queue.", inline=False)
        embed.add_field(name="leave | l", value="Leave the queue.", inline=False)
        embed.add_field(name="done | finished | d", value="End your turn to advance the queue.", inline=False)
        if settings['role'] in user.roles:
            embed.add_field(name="add | a", value="Add an @user to the queue.", inline=False)
        await self.bot.say(embed=embed)

    @_karaoke.command(name="list", pass_context=True, no_pm=True)
    async def _list(self):
        if len(list(self.queue)) is not 0:
            await self.bot.say(", ".join(list(self.queue)))
        else:
            await self.bot.say("The queue is empty.")

    # todo:  needs karaoke role permission, check if a user is online
    @_karaoke.command(name="add", pass_context=True, no_pm=True, aliases=["a"])
    async def _add(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.message.author
        if user.display_name not in self.queue:
            self.queue.append(user.display_name)
            await self.bot.say(bold(user.display_name) + " added to the queue.")
        else:
            await self.bot.say(bold(user.display_name) + " already in queue.")

    @_karaoke.command(name="join", pass_context=True, no_pm=True, aliases=["j"])
    async def _join(self, ctx):
        user = ctx.message.author
        if user.display_name not in self.queue:
            self.queue.append(user.display_name)
            await self.bot.say(bold(user.display_name) + " added to the queue.")
        else:
            await self.bot.say(bold(user.display_name) + " already in queue.")

    # needs karaoke role permission
    @_karaoke.command(name="remove", pass_context=True, no_pm=True, aliases=["r"])
    async def _remove(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.message.author
        if user.display_name in self.queue:
            self.queue.remove(user.display_name)
            await self.bot.say(bold(user.display_name) + " removed from the queue.")
        else:
            await self.bot.say(bold(user.display_name) + " not in queue.")

    @_karaoke.command(name="leave", pass_context=True, no_pm=True, aliases=["l"])
    async def _leave(self, ctx):
        user = ctx.message.author
        if user.display_name in self.queue:
            self.queue.remove(user.display_name)
            await self.bot.say(bold(user.display_name) + " removed from the queue.")
        else:
            await self.bot.say("You are not in queue.")

    # needs karaoke role permission
    @_karaoke.command(name="next", pass_context=True, no_pm=True, aliases=["skip", "n"])
    async def _next(self, ctx):
        self.queue.rotate(-1)
        # await self.bot.say(
        #     "It's now " + bold(self.queue[0]) + "'s turn!\nGet ready " + bold(self.queue[1]) + ", you're up next!")
        embed = discord.Embed(title="Get ready " + self.queue[1] + ", you're up next!", color=0x31df2d)
        embed.set_author(name="It's now " + self.queue[0] + "'s turn!")
        await self.bot.say(embed=embed)

    # needs karaoke role permission
    @_karaoke.command(name="back", pass_context=True, no_pm=True, aliases=["b", "rewind"])
    async def _back(self, ctx):
        self.queue.rotate(1)
        # await self.bot.say(
        #     "The queue has been rewound.\nIt's now " + bold(self.queue[0]) + "'s turn!\nGet ready " + bold(
        #         self.queue[1]) + ", you're up next!")
        embed = discord.Embed(title="Get ready " + self.queue[1] + ", you're up next!", color=0x31df2d)
        embed.set_author(name="It's now " + self.queue[0] + "'s turn!")
        await self.bot.say(embed=embed)

    @_karaoke.command(name="done", pass_context=True, no_pm=True, aliases=["d", "finished"])
    async def _done(self, ctx):
        """Allows the current singer to complete their turn."""
        user = ctx.message.author
        if user.display_name == self.queue[0]:
            self.queue.rotate(-1)
            # await self.bot.say(
            #     "Nice job " + bold(user.display_name) + "!\nIt's now " + bold(
            #         self.queue[0]) + "'s turn!\nGet ready " + bold(self.queue[1]) + ", you're up next!")
            embed = discord.Embed(title="Get ready " + self.queue[1] + ", you're up next!", color=0x31df2d)
            embed.set_author(name="It's now " + self.queue[0] + "'s turn!")
            await self.bot.say(embed=embed)
        else:
            await self.bot.say("It's " + bold(self.queue[0]) + "'s turn so you can't advance the queue!")

    # needs karaoke role permission
    @_karaoke.command(name="reset", pass_context=True, no_pm=True)
    async def _reset(self, ctx):
        """Empty the karaoke queue."""
        if len(list(self.queue)) is not 0:
            self.queue.clear()
            await self.bot.say("The queue is now clear.")

    # needs karaoke role permission
    # @_karaoke.command(name="shuffle", pass_context=True, no_pm=True)
    # async def _shuffle(self, ctx):
    #     pass

    # @commands.command(pass_context=True)
    # async def inactive(self, ctx, user: discord.Member = None):
    #     pass

    # @commands.command(pass_context=True)
    # async def active(self, ctx, user: discord.Member = None):
    #     pass

    @checks.admin()
    @_karaoke.command(pass_context=True, no_pm=True)
    async def role(self, ctx, role: str = None):
        """Set the karaoke manager role for the server."""
        if role is not None:
            server = ctx.message.server
            settings = self.get_settings(server)
            settings['role'] = role
            self.update_settings(server, settings)
            await self.bot.say("The karaoke manager role is set as: " + role)


def check_folders():
    if os.path.exists("data/karaoke/"):
        os.rename("data/karaoke/", DATA_PATH)
    if not os.path.exists(DATA_PATH):
        print("Creating data/karaoke folder...")
        os.mkdir(DATA_PATH)


def check_files():
    if not dataIO.is_valid_json(JSON_PATH):
        print("Creating duelist.json...")
        dataIO.save_json(JSON_PATH, {})


def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Karaoke(bot))
