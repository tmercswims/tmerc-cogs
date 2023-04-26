from redbot.core.bot import Red

from .catfact import CatFact


async def setup(bot: Red) -> None:
    await bot.add_cog(CatFact())
