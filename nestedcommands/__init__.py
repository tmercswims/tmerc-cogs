from redbot.core.bot import Red

from .nestedcommands import NestedCommands


async def setup(bot: Red):
    await bot.add_cog(NestedCommands(bot))
