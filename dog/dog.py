import discord
from discord.ext import commands

import aiohttp

class Dog:
    """Shows a random dog."""

    def __init__(self, bot):
        self.bot = bot
        self.url = 'http://random.dog/woof'

    @commands.command(pass_context=True, no_pm=True)
    async def cat(self, ctx):
        """Shows a random dog."""
        async with aiohttp.get(self.url) as response:
            await self.bot.say(self.url + await response.text())

def setup(bot):
    bot.add_cog(Dog(bot))
