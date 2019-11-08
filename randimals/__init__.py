from redbot.core.bot import Red

from .randimals import Randimals


def setup(bot: Red):
    bot.add_cog(Randimals())
