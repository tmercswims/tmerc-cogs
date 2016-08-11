import discord
from discord.ext import commands

import aiohttp
import re

class Dog:
    """Shows a random dog."""

    def __init__(self, bot):
        self.bot = bot
        self.url = 'http://random.dog/'

    @commands.command(pass_context=True, no_pm=True)
    async def dog(self, ctx):
        """Shows a random dog."""
        async with aiohttp.get(self.url) as response:
            content = await response.text()
            print(content)
            try:
                img = self.url + re.search(r'.*<img src="(.*)">.*', content).group(1)
                await self.bot.say(img)
            except:
                await self.bot.say("Something went wrong.")

def setup(bot):
    bot.add_cog(Dog(bot))
