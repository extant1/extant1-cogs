from .serverquery import ServerQuery


def setup(bot):
    bot.add_cog(ServerQuery())
