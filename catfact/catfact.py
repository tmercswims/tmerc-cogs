import discord
from discord.ext import commands

import aiohttp
import json

class Catfact:
    """Gets random cat facts."""

    def __init__(self, bot: commands.bot.Bot):
        self.bot = bot
        self.url = "https://catfacts-api.appspot.com/api/facts?number=1"

    @commands.command(pass_context=True, no_pm=True, name="catfact")
    async def _catfact(self, context: commands.context.Context):
        """Gets a random cat fact."""

        await self.bot.type()
        async with aiohttp.get(self.url) as response:
            fact = json.loads(await response.text())["facts"][0]
            await self.bot.say(fact)

def setup(bot: commands.bot.Bot):
    bot.add_cog(Catfact(bot))
