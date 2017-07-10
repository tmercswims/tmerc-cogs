import asyncio
from copy import deepcopy
import os
import re
from typing import List, Tuple

import discord
from discord.ext import commands
try:
    from valve.rcon import RCON
    valve_available = True
except:
    valve_available = False

from .utils.dataIO import dataIO
from .utils import checks, chat_formatting as cf

default_settings = {
    "ct_channel": None,
    "t_channel": None,
    "server_address": None,
    "rcon_password": None,
    "steam_ids": {}
}


class RetakeChannels:

    """Auto-move people to voice channels based on retakes teams."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.settings_path = "data/retakechannels/settings.json"
        self.settings = dataIO.load_json(self.settings_path)
        self.tasks = {}
        self.enabled = {}

    @commands.group(pass_context=True, no_pm=True, name="retchanset")
    @checks.admin_or_permissions(administrator=True)
    async def _retchanset(self, ctx: commands.Context):
        """Sets RetakeChannels settings."""

        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = deepcopy(default_settings)
            dataIO.save_json(self.settings_path, self.settings)
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @_retchanset.command(pass_context=True, no_pm=True, name="ctchan")
    async def _ctchan(self, ctx: commands.Context, *, channel: discord.Channel):
        """Sets the voice channel for the Counter-Terrorists."""

        if channel.type != discord.ChannelType.voice:
            await self.bot.reply(cf.error("Channel must be a voice channel."))
            return

        server = ctx.message.server
        self.settings[server.id]["ct_channel"] = channel.id
        dataIO.save_json(self.settings_path, self.settings)

        await self.bot.reply(cf.info(
            "Counter-Terrorists will now be put in the channel '{}'.".format(
                channel.name)))

    @_retchanset.command(pass_context=True, no_pm=True, name="tchan")
    async def _tchan(self, ctx: commands.Context, *, channel: discord.Channel):
        """Sets the voice channel for the Terrorists."""

        if channel.type != discord.ChannelType.voice:
            await self.bot.reply(cf.error("Channel must be a voice channel."))
            return

        server = ctx.message.server
        self.settings[server.id]["t_channel"] = channel.id
        dataIO.save_json(self.settings_path, self.settings)

        await self.bot.reply(cf.info(
            "Terrorists will now be put in the channel '{}'.".format(
                channel.name)))

    @_retchanset.command(pass_context=True, no_pm=True, name="server")
    async def _server(self, ctx: commands.Context, server: str):
        """Set the server address (don't include the port!)."""

        serv = ctx.message.server
        self.settings[serv.id]["server_address"] = server
        dataIO.save_json(self.settings_path, self.settings)
        await self.bot.reply(cf.info("Server set."))

    @_retchanset.command(pass_context=True, no_pm=True, name="rconpassword")
    async def _rconpassword(self, ctx: commands.Context, password: str):
        """Set the RCON password."""

        server = ctx.message.server

        await self.bot.delete_message(ctx.message)

        self.settings[server.id]["rcon_password"] = password
        dataIO.save_json(self.settings_path, self.settings)

        await self.bot.reply(cf.info("RCON password set."))

    @commands.command(pass_context=True, no_pm=True, name="setsteamid")
    async def _setsteamid(self, ctx: commands.Context, steamID: str):
        """Associates your Discord account to the Steam profile
        with the given ID.

        You MUST provide your text ID, which has the form 'STEAM_X:X:XXXXXX'.
        You can use http://steamidfinder.com/ to get it.
        """

        if re.compile(r"STEAM_\d:\d:\d+").match(steamID) is None:
            await self.bot.reply(cf.error(
                "Provided Steam ID does not seem to be in the correct format. "
                "You need to provide the ID of the form 'STEAM_X:X:XXXXXX'. "
                "You can use http://steamidfinder.com/ to get it."))
            return

        server = ctx.message.server
        self.settings[server.id]["steam_ids"][steamID.split(":")[-1]] = ctx.message.author.id
        dataIO.save_json(self.settings_path, self.settings)

        await self.bot.reply(cf.info("Steam ID set."))

    @commands.command(pass_context=True, no_pm=True, name="retchanstart")
    async def _retchanstart(self, ctx: commands.Context):
        """Starts retake channels."""

        server = ctx.message.server
        serv_settings = self.settings[server.id]
        if server.id in self.enabled and self.enabled[server.id]:
            await self.bot.reply(
                cf.info("Retake channels is already started."))
            return

        self.enabled[server.id] = True
        self.tasks[server.id] = self.bot.loop.create_task(
            self._task(server.id))

        await self.bot.reply(cf.info("Retake channels started."))

    @commands.command(pass_context=True, no_pm=True, name="retchanstop")
    async def _retchanstop(self, ctx: commands.Context):
        """Stops retake channels."""

        server = ctx.message.server
        serv_settings = self.settings[server.id]
        if server.id not in self.enabled or not self.enabled[server.id]:
            await self.bot.reply(
                cf.info("Retake channels is already stopped."))
            return

        self.enabled[server.id] = False
        if server.id in self.tasks:
            self.tasks[server.id].cancel()
            del self.tasks[server.id]

        await self.bot.reply(cf.info("Retake channels stopped."))

    def _get_players(self, server_id: str) -> List[Tuple[str, str]]:
        address = (self.settings[server_id]["server_address"], 27015)
        password = self.settings[server_id]["rcon_password"]

        with RCON(address, password) as rcon:
            return [tuple(x.split(";")) for x in rcon.execute("sm_player_teams").text.strip().split("\n")[:-1]]

    async def _task(self, server_id: str):
        empty_count = 0
        while True:
            server_settings = self.settings[server_id]
            ct_channel = self.bot.get_channel(server_settings["ct_channel"])
            t_channel = self.bot.get_channel(server_settings["t_channel"])
            players = self._get_players(server_id)

            if len(players) == 0:
                empty_count += 1
                if empty_count >= 30:
                    empty_count = 0
                    self.enabled[server_id] = False
                    del self.tasks[server_id]
                    return
            else:
                empty_count = 0

            for steamid_l,team in players:
                steamid = steamid_l.split(":")[-1]
                if steamid in server_settings["steam_ids"]:
                    member = self.bot.get_server(server_id).get_member(
                        server_settings["steam_ids"][steamid])
                    if team == "2":
                        if member not in t_channel.voice_members:
                            await self.bot.move_member(member, t_channel)
                    elif team == "3":
                        if member not in ct_channel.voice_members:
                            await self.bot.move_member(member, ct_channel)
            await asyncio.sleep(2)


def check_folders():
    if not os.path.exists("data/retakechannels"):
        print("Creating data/retakechannels directory...")
        os.makedirs("data/retakechannels")


def check_files():
    f = "data/retakechannels/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating data/retakechannels/settings.json...")
        dataIO.save_json(f, {})


def setup(bot: commands.Bot):
    check_folders()
    check_files()

    if valve_available:
        bot.add_cog(RetakeChannels(bot))
    else:
        raise RuntimeError(
            "You need to install `python-valve`: `pip install"
            " git+git://github.com/Holiverh/python-valve.git`.")
