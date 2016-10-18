import os
import random

import discord
from discord.ext import commands

from .utils import chat_formatting as cf


class RandImage:

    """Picks a random image from the given directory."""

    def __init__(self, bot: commands.bot.Bot):
        self.bot = bot
        self.base = "data/randimage/"

    def _list_image_dirs(self):
        ret = []
        for thing in os.listdir(self.base):
            if os.path.isdir(os.path.join(self.base, thing)):
                ret.append(thing)
        return ret

    @commands.command(pass_context=True, no_pm=True, name="randimage")
    async def _randimage(self, ctx: commands.context.Context, dirname: str):
        """Chooses a random image from the given directory
        (inside "data/randimage") and sends it.
        """

        await self.bot.type()
        lists = self._list_image_dirs()

        if not any(map(lambda l: os.path.split(l)[1] == dirname, lists)):
            await self.bot.reply(
                cf.error("Image directory {} not found.".format(dirname)))
            return

        direc = os.path.join(self.base, dirname)

        ls = os.listdir(direc)

        if not ls:
            await self.bot.reply(
                cf.error("There are no images in that directory."))
            return

        await self.bot.upload(os.path.join(direc, random.choice(ls)))


def setup(bot: commands.bot.Bot):
    bot.add_cog(RandImage(bot))
