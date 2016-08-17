import discord
from discord.ext import commands

import aiohttp
import json

class Randimals:
    """Shows random animals."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True, name=cat)
    async def _cat(self, ctx):
        """Shows a random cat."""
        url = 'http://random.cat/meow'
        async with aiohttp.get(url) as response:
            async with aiohttp.get(json.loads(await response.text())['file']) as image:
                await self.bot.send_file(ctx.message.channel, image.read())

    @commands.command(pass_context=True, no_pm=True, name=dog)
    async def _dog(self, ctx):
        """Shows a random dog."""
        url = 'http://random.dog/'
        async with aiohttp.get(url + 'woof') as response:
            async with aiohttp.get(url + await response.text()) as image:
                await self.bot.send_file(ctx.message.channel, image.read())

def setup(bot):
    bot.add_cog(Randimals(bot))
