import asyncio
import io
import logging
import os

import aiohttp
import discord
from redbot.core import commands

__author__ = "tmerc"

log = logging.getLogger("red.tmerc.randimals")


class Randimals(commands.Cog):
    """Get some random animal images."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__session = aiohttp.ClientSession()

    def cog_unload(self):
        if self.__session:
            asyncio.get_event_loop().create_task(self.__session.close())

    @commands.command()
    async def dog(self, ctx: commands.Context):
        """Get a random dog."""

        await ctx.trigger_typing()

        url = "https://random.dog/woof.json"

        try:
            async with self.__session.get(url) as response:
                img_url = (await response.json())["url"]
                filename = os.path.basename(img_url)
                async with self.__session.get(img_url) as image:
                    await ctx.send(file=discord.File(io.BytesIO(await image.read()), filename=filename))
        except aiohttp.ClientError:
            log.warning("API call failed; unable to get dog picture")
            await ctx.send("I was unable to get a dog picture.")

    @commands.command()
    async def cat(self, ctx: commands.Context):
        """Get a random cat."""

        await ctx.trigger_typing()

        url = "http://shibe.online/api/cats?count=1"

        try:
            async with self.__session.get(url) as response:
                img_url = (await response.json())[0]
                filename = os.path.basename(img_url)
                async with self.__session.get(img_url) as image:
                    await ctx.send(file=discord.File(io.BytesIO(await image.read()), filename=filename))
        except aiohttp.ClientError:
            log.warning("API call failed; unable to get cat picture")
            await ctx.send("I was unable to get a cat picture.")

    @commands.command()
    async def fox(self, ctx: commands.Context):
        """Get a random fox."""

        await ctx.trigger_typing()

        url = "https://wohlsoft.ru/images/foxybot/randomfox.php"

        try:
            async with self.__session.get(url) as response:
                img_url = (await response.json())["file"]
                filename = os.path.basename(img_url)
                async with self.__session.get(img_url) as image:
                    await ctx.send(file=discord.File(io.BytesIO(await image.read()), filename=filename))
        except aiohttp.ClientError:
            log.warning("API call failed; unable to get fox picture")
            await ctx.send("I was unable to get a fox picture.")

    @commands.command()
    async def bird(self, ctx: commands.Context):
        """Get a random bird."""

        await ctx.trigger_typing()

        url = "http://shibe.online/api/birds?count=1"

        try:
            async with self.__session.get(url) as response:
                img_url = (await response.json())[0]
                filename = os.path.basename(img_url)
                async with self.__session.get(img_url) as image:
                    await ctx.send(file=discord.File(io.BytesIO(await image.read()), filename=filename))
        except aiohttp.ClientError:
            log.warning("API call failed; unable to get bird picture")
            await ctx.send("I was unable to get a bird picture.")
