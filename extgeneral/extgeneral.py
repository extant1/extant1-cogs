import random

import discord
from discord.ext import commands


class ExtGeneral:
    """General commands."""

    def __init__(self, bot):
        self.bot = bot

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

    @commands.command(pass_context=True)
    async def predictcombatpatch(self, ctx):
        """When will the combat patch be released?"""
        days = random.randint(0, 365)
        hours = random.randint(0, 24)
        minutes = random.randint(0, 60)
        seconds = random.randint(0, 60)
        if days == 0 and hours == 0 and minutes == 0 and seconds == 0:
            await self.bot.say("The combat patch is coming out right meow!")
        else:
            await self.bot.say(
                "The combat patch will be released in {} days, {} hours, {} minutes, and {} seconds.".format(days,
                                                                                                             hours,
                                                                                                             minutes,
                                                                                                             seconds))

    @commands.command(pass_context=True)
    async def predicttoren(self, ctx):
        """When will Toren play lif again?"""
        days = random.randint(0, 365)
        hours = random.randint(0, 24)
        minutes = random.randint(0, 60)
        seconds = random.randint(0, 60)
        if days == 0 and hours == 0 and minutes == 0 and seconds == 0:
            await self.bot.say("Toren is connecting right meow!")
        else:
            await self.bot.say(
                "Toren will play life is feudal in {} days, {} hours, {} minutes, and {} seconds.".format(days,
                                                                                                             hours,
                                                                                                             minutes,
                                                                                                             seconds))


def setup(bot):
    bot.add_cog(ExtGeneral(bot))
