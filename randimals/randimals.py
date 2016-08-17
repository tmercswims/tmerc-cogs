import discord
from discord.ext import commands

import aiohttp
import io
import json
import os.path

class Randimals:
    """Shows random animals."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True, name='cat')
    async def _cat(self, ctx):
        """Shows a random cat."""
        url = 'http://random.cat/meow'
        async with aiohttp.get(url) as response:
            img_url = json.loads(await response.text())['file']
            filename = os.path.basename(img_url)
            async with aiohttp.get(img_url) as image:
                await self.bot.send_file(ctx.message.channel, io.BytesIO(await image.read()), filename=filename)

    @commands.command(pass_context=True, no_pm=True, name='dog')
    async def _dog(self, ctx):
        """Shows a random dog."""
        url = 'http://random.dog/'
        async with aiohttp.get(url + 'woof') as response:
            filename = await response.text()
            async with aiohttp.get(url + filename) as image:
                await self.bot.send_file(ctx.message.channel, io.BytesIO(await image.read()), filename=filename)

def setup(bot):
    bot.add_cog(Randimals(bot))
