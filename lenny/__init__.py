from redbot.core.bot import Red

from .lenny import Lenny


async def setup(bot: Red) -> None:
    await bot.add_cog(Lenny())
