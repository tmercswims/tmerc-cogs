from redbot.core.bot import Red

from .streamrole import StreamRole


async def setup(bot: Red):
    await bot.add_cog(StreamRole())
