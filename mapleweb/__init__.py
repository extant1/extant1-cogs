from .mapleweb import MapleWeb


def setup(bot):
    bot.add_cog(MapleWeb(bot))
