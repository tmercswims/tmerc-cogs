from redbot.core.bot import Red

from .massdm import MassDM


async def setup(bot: Red) -> None:
    await bot.add_cog(MassDM())
