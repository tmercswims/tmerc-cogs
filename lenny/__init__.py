from redbot.core.bot import Red

from .lenny import Lenny


def setup(bot: Red):
    bot.add_cog(Lenny())
