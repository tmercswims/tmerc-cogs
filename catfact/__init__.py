from redbot.core.bot import Red

from .catfact import CatFact


def setup(bot: Red):
    bot.add_cog(CatFact())
