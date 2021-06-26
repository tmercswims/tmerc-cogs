from redbot.core.bot import Red

from .randimage import RandImage


def setup(bot: Red):
    bot.add_cog(RandImage())
