from redbot.core.bot import Red

from .streamrole import StreamRole


def setup(bot: Red):
  bot.add_cog(StreamRole(bot))
