import os
import random

import discord
from discord.ext import commands

soup_available = False
try:
    from bs4 import BeautifulSoup
    soup_available = True
except:
    soup_available = False

import aiohttp
import json

class Dog:
    """Shows a random dog."""

    def __init__(self, bot):
        self.bot = bot
        self.url = 'http://random.dog/'

    @commands.command(pass_context=True, no_pm=True)
    async def dog(self, ctx):
        """Shows a random dog."""
        async with aiohttp.get(self.url) as response:
            soup = BeautifulSoup(await response.text(), "html.parser")
        try:
            img = self.url + soup.find('img').get_text()
            await self.bot.say(img)
        except:
            await self.bot.say("Something went wrong.")

def setup(bot):
    if soup_available:
        bot.add_cog(Dog(bot))
    else:
        raise RuntimeError('Missing BeautifulSoup, run `pip3 install beautifulsoup4`.')
