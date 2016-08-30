import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils import checks, chat_formatting as cf
from __main__ import send_cmd_help

import os
import random

default_settings = {
    "next_index": 1,
    "quotes": {}
}

class Quotes:
    """Stores and shows quotes."""

    def __init__(self, bot):
        self.bot = bot
        self.settings_path = "data/quotes/settings.json"
        self.settings = fileIO(self.settings_path, "load")

    def list_quotes(self, server):
        tups = [(int(k), v) for (k,v) in self.settings[server.id]["quotes"].items()]
        tups.sort(key=lambda x: x[0])
        return ["{}. {}".format(n, q) for (n, q) in tups]

    @commands.command(pass_context=True, no_pm=True, name="addquote")
    async def _addquote(self, context, *, new_quote):
        """Adds a new quote."""

        self.bot.type()
        server = context.message.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            fileIO(self.settings_path, "save", self.settings)

        idx = self.settings[server.id]["next_index"]
        self.settings[server.id]["quotes"][str(idx)] = new_quote
        self.settings[server.id]["next_index"] += 1
        fileIO(self.settings_path, "save", self.settings)

        await self.bot.reply(cf.info("Quote added as number {}.".format(idx)))

    @commands.command(pass_context=True, no_pm=True, name="delquote")
    async def _delquote(self, context, number):
        """Deletes an existing quote."""

        self.bot.type()
        server = context.message.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings

        try:
            int(number)
        except (ValueError, TypeError):
            await self.bot.reply(cf.error("Please provide a quote number to delete. Try \"{}allquotes\" for a list.".format(context.prefix)))

        try:
            del self.settings[server.id]["quotes"][number]
        except KeyError:
            await self.bot.reply(cf.error("A quote with that number cannot be found. Try \"{}allquotes for a list.\"".format(context.prefix)))
            return

        fileIO(self.settings_path, "save", self.settings)

        await self.bot.reply(cf.info("Quote number {} deleted.".format(number)))

    @commands.command(pass_context=True, no_pm=False, name="allquotes")
    async def _allquotes(self, context):
        """Sends all quotes in a PM."""

        self.bot.type()
        server = context.message.server

        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            fileIO(self.settings_path, "save", self.settings)

        if len(self.settings[server.id]["quotes"]) == 0:
            await self.bot.reply(cf.warning("There are no saved quotes. Use \"{}addquote\" to add one.".format(context.prefix)))
            return

        strbuffer = self.list_quotes(server)
        mess = "```"
        for line in strbuffer:
            if len(mess) + len(line) + 4 < 2000:
                mess += "\n" + line
            else:
                mess += "```"
                await self.bot.whisper(mess)
                mess = "```"
        if mess != "":
            mess += "```"
            await self.bot.whisper(mess)

        await self.bot.reply("Check your PMs!")

    @commands.command(pass_context=True, no_pm=True, name="quote")
    async def _quote(self, context, *number):
        """Sends a random quote."""

        self.bot.type()
        server = context.message.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            fileIO(self.settings_path, "save", self.settings)

        if len(self.settings[server.id]["quotes"]) == 0:
            await self.bot.reply(cf.warning("There are no saved quotes. Use \"{}addquote\" to add one.".format(context.prefix)))
            return

        # if len(number) > 1:
        #     await self.bot.reply("Please provide a number to get that specific quote. If you are trying to add a quote, use \"!addquote\".")
        #     return
        number = "".join(number)
        if number:
            try:
                int(number)
            except (ValueError, TypeError):
                await self.bot.reply(cf.warning("Please provide a number to get that specific quote. If you are trying to add a quote, use \"{}addquote\".".format(context.prefix)))
                return

            try:
                await self.bot.say(self.settings[server.id]["quotes"][number])
                return
            except KeyError:
                await self.bot.reply(cf.warning("A quote with that number cannot be found. Try \"{}allquotes\" for a list.".format(context.prefix)))
                return

        await self.bot.say(random.choice(list(self.settings[server.id]["quotes"].values())))

def check_folders():
    if not os.path.exists("data/quotes"):
        print("Creating data/quotes directory...")
        os.makedirs("data/quotes")

def check_files():
    f = "data/quotes/settings.json"
    if not fileIO(f, "check"):
        print("Creating data/quotes/settings.json...")
        fileIO(f, "save", {})

def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Quotes(bot))
