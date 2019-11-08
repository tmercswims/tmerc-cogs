from redbot.core.bot import Red

from .massdm import MassDM


def setup(bot: Red):
    bot.add_cog(MassDM())
