from redbot.core.bot import Red

from .welcome import Welcome


async def setup(bot: Red):
    await bot.add_cog(Welcome())
