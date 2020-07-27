from .gameserverquery import GameServerQuery


def setup(bot):
    bot.add_cog(GameServerQuery(bot))
