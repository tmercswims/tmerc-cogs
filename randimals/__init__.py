from redbot.core.bot import Red

from .randimals import Randimals


async def setup(bot: Red):
    await bot.add_cog(Randimals())
