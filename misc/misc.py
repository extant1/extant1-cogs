import random
from random import choice

import discord
from redbot.core import Config, commands, checks
from redbot.core import commands


class Misc(commands.Cog):
    """General commands."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=91928524318855168)

    @commands.command()
    async def flip(self, ctx, user: discord.Member = None):
        """Flip a coin... or a user.
        Defaults to a coin.
        """
        if user is not None:
            msg = ""
            if user.id == ctx.bot.user.id:
                user = ctx.author
                msg = "Nice try. You think this is funny?\n How about *this* instead:\n\n"
                if user.id == 272200608319275009:
                    msg = "Nice try. You think this is funny?\n How about *this* instead..wait.. what's happening.. auughh she's too powerful!:\n\n"
            char = "abcdefghijklmnopqrstuvwxyz"
            tran = "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz"
            table = str.maketrans(char, tran)
            name = user.display_name.translate(table)
            char = char.upper()
            tran = "∀qƆpƎℲפHIſʞ˥WNOԀQᴚS┴∩ΛMX⅄Z"
            table = str.maketrans(char, tran)
            name = name.translate(table)
            await ctx.send(msg + "(╯°□°）╯︵ " + name[::-1])
        else:
            await ctx.send("*flips a coin and... " + choice(["HEADS!*", "TAILS!*"]))

    @commands.command()
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
            await ctx.send(msg + name + " ノ( ゜-゜ノ)")
        else:
            name = ctx.message.author.display_name
            await ctx.send(name + " ノ( ゜-゜ノ)")

    @commands.command()
    async def predictcombatpatch(self, ctx):
        """When will the combat patch be released?"""
        days = random.randint(0, 365)
        hours = random.randint(0, 24)
        minutes = random.randint(0, 60)
        seconds = random.randint(0, 60)
        if days == 0 and hours == 0 and minutes == 0 and seconds == 0:
            await ctx.send("The combat patch is coming out right meow!")
        else:
            await ctx.send(
                "The combat patch will be released in {} days, {} hours, {} minutes, and {} seconds.".format(days,
                                                                                                             hours,
                                                                                                             minutes,
                                                                                                             seconds))

    @commands.command()
    async def predicttoren(self, ctx):
        """When will Toren play lif again?"""
        days = random.randint(0, 365)
        hours = random.randint(0, 24)
        minutes = random.randint(0, 60)
        seconds = random.randint(0, 60)
        if days == 0 and hours == 0 and minutes == 0 and seconds == 0:
            await ctx.send("Toren is connecting right meow!")
        else:
            await ctx.send(
                "Toren will play life is feudal in {} days, {} hours, {} minutes, and {} seconds.".format(days,
                                                                                                             hours,
                                                                                                             minutes,
                                                                                                             seconds))

    @commands.command()
    async def seentitus(self, ctx):
        """Who is Titus?"""
        await ctx.send("I've never seen Titus.")
