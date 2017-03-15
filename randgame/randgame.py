import asyncio
from copy import deepcopy
import os
import os.path
import random

import discord
from discord.ext import commands

from .utils.dataIO import dataIO
from .utils import checks, chat_formatting as cf


default_settings = {
    "delay": 60,
    "games": [
        "Half-Life 2",
        "Halo: Combat Evolved",
        "Rock-Paper-Scissors",
        "Overwatch",
        "Baseball",
        "Jak & Daxter",
        "Counter-Strike: Global Offensive",
        "Chrono Trigger"
    ],
    "del": []
}


class RandGame:

    """Sets the bot's game to a random one from a list you specify,
    every certain number of seconds.

    Supports additions to, removals from, and complete replacements
    of the list. Interval between changes is also configurable.
    """

    def __init__(self, bot: commands.bot.Bot):
        self.bot = bot
        self.settings_path = "data/randgame/settings.json"
        self.settings = dataIO.load_json(self.settings_path)

        self.switch_task = self.bot.loop.create_task(self._switch_game())

    async def _switch_game(self):
        await self.bot.wait_until_ready()
        while True:
            delay = self.settings["delay"]

            await self._cycle_game()

            await asyncio.sleep(delay)

    async def _cycle_game(self):
        servers = list(self.bot.servers)

        if len(servers) > 0:
            current_game = servers[0].get_member(self.bot.user.id).game
            current_game_name = ""
            if current_game is not None:
                current_game_name = current_game.name

            new_game_name = self._random_game_name(current_game_name)
            if new_game_name is not None:
                if (current_game_name in self.settings["games"] or
                        current_game_name == "" or
                        current_game_name in self.settings["del"]):
                    await self.bot.change_presence(
                        game=discord.Game(name=new_game_name))
                    self.settings["del"] = []
                    dataIO.save_json(self.settings_path, self.settings)
            else:
                await self.bot.change_presence(game=None)

    def _random_game_name(self, current_name):
        new_name = current_name
        if len(self.settings["games"]) > 1:
            while current_name == new_name:
                new_name = random.choice(self.settings["games"])
        elif len(self.settings["games"]) == 1:
            new_name = self.settings["games"][0]
        else:
            new_name = None
        return new_name

    @commands.group(pass_context=True, no_pm=True, name="randgame")
    @checks.mod_or_permissions(administrator=True)
    async def _randgame(self, ctx: commands.Context):
        """Adjust settings and game list."""

        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @_randgame.command(pass_context=True, no_pm=True, name="delay")
    async def _delay(self, ctx: commands.Context, seconds: int):
        """Sets the delay between game changes.

        Must be at least 15 seconds.
        """

        if seconds < 15:
            await self.bot.reply(
                cf.error("Delay must be at least 15 seconds."))
            return

        self.settings["delay"] = seconds
        dataIO.save_json(self.settings_path, self.settings)

        await self.bot.reply(
            cf.info("Delay set to {} seconds.".format(seconds)))

    @_randgame.command(pass_context=True, no_pm=True, name="add")
    async def _add(self, ctx: commands.Context, *, game: str):
        """Adds a game to the list."""

        self.settings["games"].append(game)
        dataIO.save_json(self.settings_path, self.settings)

        await self.bot.reply(
            cf.info("{} added to the game list.".format(game)))

    @_randgame.command(pass_context=True, no_pm=True, name="del")
    async def _del(self, ctx: commands.Context, *, game: str):
        """Removes a game from the list."""

        try:
            self.settings["games"].remove(game)
        except ValueError:
            await self.bot.reply(
                cf.warning("{} is not in the game list.".format(game)))
            return

        self.settings["del"].append(game)

        dataIO.save_json(self.settings_path, self.settings)

        await self.bot.reply(
            cf.info("{} removed from the game list.".format(game)))

    @_randgame.command(pass_context=True, no_pm=True, name="set")
    async def _set(self, ctx: commands.Context, *games: str):
        """Replaces the game list with the given list."""

        games_str = ", ".join(sorted(list(games)))

        await self.bot.reply(cf.question(
            "You are about to replace the current game list with this:{}"
            "Are you sure you want to proceed? (yes/no)".format(
                cf.box(games_str))))

        answer = await self.bot.wait_for_message(timeout=15,
                                                 author=ctx.message.author)

        if answer is None or answer.content.lower().strip() != "yes":
            await self.bot.reply("Game list not replaced.")
            return

        self.settings["del"] += self.settings["games"]

        self.settings["games"] = list(games)
        dataIO.save_json(self.settings_path, self.settings)

        await self.bot.reply(cf.info("Game list replaced."))

    @_randgame.command(pass_context=True, no_pm=True, name="get")
    async def _get(self, ctx: commands.Context):
        """Gets the current list of games."""

        games = ", ".join(sorted(self.settings["games"]))

        await self.bot.reply(cf.box(games))

    @_randgame.command(pass_context=True, no_pm=True, name="cycle")
    async def _cycle(self, ctx: commands.Context):
        """Cycles the current game."""

        await self._cycle_game()


def check_folders():
    if not os.path.exists("data/randgame"):
        print("Creating data/randgame directory...")
        os.makedirs("data/randgame")


def check_files():
    f = "data/randgame/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating data/randgame/settings.json...")
        dataIO.save_json(f, deepcopy(default_settings))


def setup(bot: commands.bot.Bot):
    check_folders()
    check_files()

    bot.add_cog(RandGame(bot))
