import asyncio
import logging

import aiohttp
from redbot.core import commands

__author__ = "tmerc"

log = logging.getLogger('red.tmerc.catfact')


class CatFact(commands.Cog):
    """Gets a random cat fact."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__url = 'https://catfact.ninja/fact'
        self.__session = aiohttp.ClientSession()

    def cog_unload(self):
        if self.__session:
            asyncio.get_event_loop().create_task(self.__session.close())

    @commands.command()
    async def catfact(self, ctx: commands.Context):
        """Gets a random cat fact."""

        await ctx.trigger_typing()

        try:
            async with self.__session.get(self.__url) as response:
                fact = (await response.json())['fact']
                await ctx.send(fact)
        except aiohttp.ClientError:
            log.warning("API call failed; unable to get cat fact")
            await ctx.send("I was unable to get a cat fact.")
