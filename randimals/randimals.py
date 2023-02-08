import aiohttp
import asyncio
import discord
import io
import logging
import os
from typing import Awaitable, Callable

from redbot.core import commands

from .errors import RetryLimitExceeded

__author__ = "tmerc"

log = logging.getLogger("red.tmerc.randimals")


class Randimals(commands.Cog):
    """Get some random animal images."""

    # 8MB; not using 1024 because not sure how exactly Discord does it, erring on small side
    SIZE_LIMIT = 1000 * 1000 * 8
    # number of times we can fail to get an acceptable image before giving up
    RETRY_LIMIT = 10

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.__session = aiohttp.ClientSession()

    def cog_unload(self) -> None:
        if self.__session:
            asyncio.get_event_loop().create_task(self.__session.close())

    @commands.command()
    async def dog(self, ctx: commands.Context) -> None:
        """Get a random dog."""

        await ctx.trigger_typing()

        async def fetcher() -> str:
            url = "https://random.dog/woof.json"
            async with self.__session.get(url) as response:
                return (await response.json())["url"]

        try:
            file = await self.__get_image_carefully(fetcher)
            await ctx.send(file=file)
        except (aiohttp.ClientError, RetryLimitExceeded):
            log.warning("API call failed; unable to get dog picture")
            await ctx.send("I was unable to get a dog picture.")

    @commands.command()
    async def cat(self, ctx: commands.Context) -> None:
        """Get a random cat."""

        await ctx.trigger_typing()

        async def fetcher() -> str:
            url = "http://shibe.online/api/cats?count=1"
            async with self.__session.get(url) as response:
                return (await response.json())[0]

        try:
            file = await self.__get_image_carefully(fetcher)
            await ctx.send(file=file)
        except (aiohttp.ClientError, RetryLimitExceeded):
            log.warning("API call failed; unable to get cat picture")
            await ctx.send("I was unable to get a cat picture.")

    @commands.command()
    async def bigcat(self, ctx: commands.Context) -> None:
        """Get a random bigcat."""

        await ctx.trigger_typing()

        async def fetcher() -> str:
            url = "https://randombig.cat/roar.json"
            async with self.__session.get(url) as response:
                return (await response.json())["url"]

        try:
            file = await self.__get_image_carefully(fetcher)
            await ctx.send(file=file)
        except (aiohttp.ClientError, RetryLimitExceeded):
            log.warning("API call failed; unable to get bigcat picture")
            await ctx.send("I was unable to get a bigcat picture.")

    @commands.command()
    async def bunny(self, ctx: commands.Context) -> None:
        """Get a random bunny."""

        await ctx.trigger_typing()

        async def fetcher() -> str:
            url = "https://api.bunnies.io/v2/loop/random/?media=gif"
            async with self.__session.get(url) as response:
                return (await response.json())["media"]["gif"]

        try:
            file = await self.__get_image_carefully(fetcher)
            await ctx.send(file=file)
        except (aiohttp.ClientError, RetryLimitExceeded):
            log.warning("API call failed; unable to get bunny picture")
            await ctx.send("I was unable to get a bunny picture.")

    @commands.command()
    async def capybara(self, ctx: commands.Context) -> None:
        """Get a random capybara."""

        await ctx.trigger_typing()

        async def fetcher() -> str:
            url = "https://api.capy.lol/v1/capybara?json=true"
            async with self.__session.get(url) as response:
                return (await response.json())["data"]["url"]

        try:
            file = await self.__get_image_carefully(fetcher)
            file.filename += '.jpg'
            await ctx.send(file=file)
        except (aiohttp.ClientError, RetryLimitExceeded):
            log.warning("API call failed; unable to get capybara picture")
            await ctx.send("I was unable to get a capybara picture.")

    @commands.command()
    async def duck(self, ctx: commands.Context) -> None:
        """Get a random duck."""

        await ctx.trigger_typing()

        async def fetcher() -> str:
            url = "https://random-d.uk/api/random"
            async with self.__session.get(url) as response:
                return (await response.json())["url"]

        try:
            file = await self.__get_image_carefully(fetcher)
            await ctx.send(file=file)
        except (aiohttp.ClientError, RetryLimitExceeded):
            log.warning("API call failed; unable to get duck picture")
            await ctx.send("I was unable to get a duck picture.")

    @commands.command()
    async def koala(self, ctx: commands.Context) -> None:
        """Get a random koala."""

        await ctx.trigger_typing()

        async def fetcher() -> str:
            url = "https://some-random-api.ml/img/koala"
            async with self.__session.get(url) as response:
                return (await response.json())["link"]

        try:
            file = await self.__get_image_carefully(fetcher)
            await ctx.send(file=file)
        except (aiohttp.ClientError, RetryLimitExceeded):
            log.warning("API call failed; unable to get koala picture")
            await ctx.send("I was unable to get a koala picture.")

    @commands.command()
    async def panda(self, ctx: commands.Context) -> None:
        """Get a random panda."""

        await ctx.trigger_typing()

        async def fetcher() -> str:
            url = "https://some-random-api.ml/img/panda"
            async with self.__session.get(url) as response:
                return (await response.json())["link"]

        try:
            file = await self.__get_image_carefully(fetcher)
            await ctx.send(file=file)
        except (aiohttp.ClientError, RetryLimitExceeded):
            log.warning("API call failed; unable to get panda picture")
            await ctx.send("I was unable to get a panda picture.")

    @commands.command()
    async def lizard(self, ctx: commands.Context) -> None:
        """Get a random lizard."""

        await ctx.trigger_typing()

        async def fetcher() -> str:
            url = "https://nekos.life/api/v2/img/lizard"
            async with self.__session.get(url) as response:
                return (await response.json())["url"]

        try:
            file = await self.__get_image_carefully(fetcher)
            await ctx.send(file=file)
        except (aiohttp.ClientError, RetryLimitExceeded):
            log.warning("API call failed; unable to get lizard picture")
            await ctx.send("I was unable to get a lizard picture.")

    @commands.command()
    async def fox(self, ctx: commands.Context) -> None:
        """Get a random fox."""

        await ctx.trigger_typing()

        async def fetcher() -> str:
            url = "https://wohlsoft.ru/images/foxybot/randomfox.php"
            async with self.__session.get(url) as response:
                return (await response.json())["file"]

        try:
            file = await self.__get_image_carefully(fetcher)
            await ctx.send(file=file)
        except (aiohttp.ClientError, RetryLimitExceeded):
            log.warning("API call failed; unable to get fox picture")
            await ctx.send("I was unable to get a fox picture.")

    @commands.command()
    async def bird(self, ctx: commands.Context) -> None:
        """Get a random bird."""

        await ctx.trigger_typing()

        async def fetcher() -> str:
            url = "http://shibe.online/api/birds?count=1"
            async with self.__session.get(url) as response:
                return (await response.json())[0]

        try:
            file = await self.__get_image_carefully(fetcher)
            await ctx.send(file=file)
        except (aiohttp.ClientError, RetryLimitExceeded):
            log.warning("API call failed; unable to get bird picture")
            await ctx.send("I was unable to get a bird picture.")

    async def __get_image_carefully(self, fetcher: Callable[[], Awaitable[str]]) -> discord.File:
        for x in range(Randimals.RETRY_LIMIT):
            try:
                img_url = await fetcher()
                filename = os.path.basename(img_url)
                async with self.__session.head(img_url) as size_check:
                    if size_check.content_length is None or size_check.content_length > Randimals.SIZE_LIMIT:
                        continue
                    async with self.__session.get(img_url) as image:
                        return discord.File(io.BytesIO(await image.read()), filename=filename)
            except aiohttp.ClientError:
                continue
        raise RetryLimitExceeded()
