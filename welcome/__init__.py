from redbot.core.bot import Red

from .welcome import Welcome


def setup(bot: Red):
  bot.add_cog(Welcome(bot))
