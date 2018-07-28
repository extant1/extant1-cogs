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


def setup(bot):
    bot.add_cog(ExtGeneral(bot))
