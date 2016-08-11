import os
import random

import discord
from discord.ext import commands

class Randimage:
    """Picks a random image from the given directory."""

    def __init__(self, bot):
        self.bot = bot
        self.base = 'data/randimage/'

    def _list_image_dirs(self):
        ret = []
        for thing in os.listdir(self.base):
            if os.path.isdir(os.path.join(self.base, thing)):
                ret.append(thing)
        return ret

    @commands.command(pass_context=True, no_pm=True)
    async def randimage(self, ctx, name):
        lists = self._list_image_dirs()

        if not any(map(lambda l: os.path.split(l)[1] == name, lists)):
            await self.bot.say("Image directory not found.")
            return

        direc = os.path.join(self.base, name)

        await self.bot.send_file(ctx.message.channel, os.path.join(direc, random.choice(os.listdir(direc))))

def setup(bot):
    bot.add_cog(Randimage(bot))
