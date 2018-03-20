from redbot.core.bot import Red

from .nestedcommands import NestedCommands


def setup(bot: Red):
  bot.add_cog(NestedCommands(bot))
