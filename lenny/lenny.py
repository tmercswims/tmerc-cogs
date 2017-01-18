from random import choice

import aiohttp
from discord.ext import commands


class Lenny:

    """( ͡° ͜ʖ ͡°)"""

    def __init__(self, bot: commands.bot):
        self.bot = bot

    @commands.command(pass_context=True, name="lenny")
    async def _lenny(self, ctx: commands.Context):
        """Displays a random ASCII face."""

        url = "http://lenny.today/api/v1/random?limit=1"
        async with aiohttp.get(url) as response:
            lenny = (await response.json())[0]["face"]
            lenny = lenny.replace("*", "\*").replace(
                "`", "\`").replace("_", "\_").replace("~", "\~")

            await self.bot.say(lenny)


def setup(bot: commands.bot):
    bot.add_cog(Lenny(bot))
