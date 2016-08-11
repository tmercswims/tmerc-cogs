import os
import random

import discord
from discord.ext import commands

import aiohttp
import json

class Cat:
    """Shows a random cat."""

    def __init__(self, bot):
        self.bot = bot
        self.url = 'http://random.cat/meow'

    @commands.command(pass_context=True, no_pm=True)
    async def cat(self, ctx):
        """Shows a random cat."""
        async with aiohttp.get(self.url) as response:
            j = json.loads(await response.text())
            await self.bot.say(j['file'])

def setup(bot):
    bot.add_cog(Cat(bot))
