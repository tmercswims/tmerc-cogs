import discord
from discord.ext import commands
from .utils import chat_formatting as cf

import aiohttp
import json


class Catfact:

    """Gets random cat facts."""

    def __init__(self, bot: commands.bot.Bot):
        self.bot = bot
        self.url = "https://catfacts-api.appspot.com/api/facts?number={}"

    @commands.command(pass_context=True, no_pm=True, name="catfact")
    async def _catfact(self, ctx: commands.context.Context, number: str="1"):
        """Gets random cat facts."""

        await self.bot.type()

        n = 0
        try:
            n = int(number)
        except ValueError:
            await self.bot.reply(cf.error("That is not a number!"))
            return

        if n > 10:
            await self.bot.reply(cf.warning("Be reasonable, please."))
            return

        async with aiohttp.get(self.url.format(number)) as response:
            for fact in json.loads(await response.text())["facts"]:
                await self.bot.say(fact)


def setup(bot: commands.bot.Bot):
    bot.add_cog(Catfact(bot))
