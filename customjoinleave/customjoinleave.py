import discord
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks, chat_formatting as cf
from __main__ import send_cmd_help

import aiohttp
import asyncio
import os
import os.path

default_settings = {
    "join_on": False,
    "leave_on": False
}

class Customjoinleave:
    """Play a sound byte."""
    def __init__(self, bot: commands.bot.Bot):
        self.bot = bot
        self.audio_player = False
        self.sound_base = "data/customjoinleave"
        self.settings_path = "data/customjoinleave/settings.json"
        self.settings = dataIO.load_json(self.settings_path)

    def voice_channel_full(self, voice_channel: discord.Channel) -> bool:
        return len(voice_channel.voice_members) >= voice_channel.user_limit

    def voice_connected(self, server: discord.Server) -> bool:
        return self.bot.is_voice_connected(server)

    def voice_client(self, server: discord.Server) -> discord.VoiceClient:
        return self.bot.voice_client_in(server)

    async def _leave_voice_channel(self, server: discord.Server):
        if not self.voice_connected(server):
            return
        voice_client = self.voice_client(server)

        if self.audio_player:
            self.audio_player.stop()
        await voice_client.disconnect()

    async def wait_for_disconnect(self, server: discord.Server):
        while not self.audio_player.is_done():
            await asyncio.sleep(0.01)
        await self._leave_voice_channel(server)

    async def sound_init(self, server: discord.Server, path: str):
        options = "-filter \"volume=volume=0.15\""
        voice_client = self.voice_client(server)
        self.audio_player = voice_client.create_ffmpeg_player(path, options=options)

    async def sound_play(self, server: discord.Server, channel: discord.Channel, p: str):
        if self.voice_channel_full(channel):
            return

        if not channel.is_private:
            if self.voice_connected(server):
                if not self.audio_player:
                    await self.sound_init(server, p)
                    self.audio_player.start()
                    await self.wait_for_disconnect(server)
                else:
                    if self.audio_player.is_playing():
                        self.audio_player.stop()
                    await self.sound_init(server, p)
                    self.audio_player.start()
                    await self.wait_for_disconnect(server)
            else:
                await self.bot.join_voice_channel(channel)
                if not self.audio_player:
                    await self.sound_init(server, p)
                    self.audio_player.start()
                    await self.wait_for_disconnect(server)
                else:
                    if self.audio_player.is_playing():
                        self.audio_player.stop()
                    await self.sound_init(server, p)
                    self.audio_player.start()
                    await self.wait_for_disconnect(server)

    @commands.group(pass_context=True, no_pm=True, name="joinleaveset")
    async def _joinleaveset(self, context: commands.context.Context):
        """Sets custom join/leave settings."""

        server = context.message.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            dataIO.save_json(self.settings_path, self.settings)
        if context.invoked_subcommand is None:
            await send_cmd_help(context)

    @_joinleaveset.command(pass_context=True, no_pm=True, name="togglejoin")
    @checks.admin_or_permissions(manage_server=True)
    async def _togglejoin(self, context: commands.context.Context):
        """Toggles custom join sounds on/off."""

        await self.bot.type()

        server = context.message.server
        self.settings[server.id]["join_on"] = not self.settings[server.id]["join_on"]
        if self.settings[server.id]["join_on"]:
            await self.bot.reply(cf.info("Custom join sounds are now enabled."))
        else:
            await self.bot.reply(cf.info("Custom join sounds are now disabled."))
        dataIO.save_json(self.settings_path, self.settings)

    @_joinleaveset.command(pass_context=True, no_pm=True, name="toggleleave")
    @checks.admin_or_permissions(manage_server=True)
    async def _toggleleave(self, context: commands.context.Context):
        """Toggles custom join sounds on/off."""

        await self.bot.type()

        server = context.message.server
        self.settings[server.id]["leave_on"] = not self.settings[server.id]["leave_on"]
        if self.settings[server.id]["leave_on"]:
            await self.bot.reply(cf.info("Custom leave sounds are now enabled."))
        else:
            await self.bot.reply(cf.info("Custom leave sounds are now disabled."))
        dataIO.save_json(self.settings_path, self.settings)

    @commands.command(pass_context=True, no_pm=True, name="setjoinsound")
    async def _setjoinsound(self, context: commands.context.Context, link: str=None):
        """Sets the join sound for the calling user."""

        await self._set_sound(context, link, "join", context.message.author.id)

    @commands.command(pass_context=True, no_pm=True, name="setleavesound")
    async def _setleavesound(self, context: commands.context.Context, link: str=None):
        """Sets the leave sound for the calling user."""

        await self._set_sound(context, link, "leave", context.message.author.id)

    @commands.command(pass_context=True, no_pm=True, name="setjoinsoundfor")
    @checks.admin_or_permissions(Administrator=True)
    async def _setjoinsoundfor(self, context: commands.context.Context, user: discord.User, link: str=None):
        """Sets the join sound for the given user. Must be a mention!"""

        await self._set_sound(context, link, "join", user.id)

    @commands.command(pass_context=True, no_pm=True, name="setleavesoundfor")
    @checks.admin_or_permissions(Administrator=True)
    async def _setleavesoundfor(self, context: commands.context.Context, user: discord.User, link: str=None):
        """Sets the leave sound for the given user. Must be a mention!"""

        await self._set_sound(context, link, "leave", user.id)

    async def _set_sound(self, context: commands.context.Context, link: str, action: str, userid: str):
        await self.bot.type()

        server = context.message.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            dataIO.save_json(self.settings_path, self.settings)

        attach = context.message.attachments
        if len(attach) > 1 or (attach and link):
            await self.bot.reply(cf.error("Please only provide one file."))
            return

        url = ""
        if attach:
            url = attach[0]["url"]
        elif link:
            url = link
        else:
            await self.bot.reply(cf.error("You must provide either a Discord attachment or a direct link to a sound."))
            return

        path = "{}/{}".format(self.sound_base, server.id)
        if not os.path.exists(path):
            os.makedirs(path)

        path = "{}/{}/{}".format(self.sound_base, server.id, userid)
        if not os.path.exists(path):
            os.makedirs(path)

        path += "/" + action
        if os.path.exists(path):
            await self.bot.reply(cf.question("There is already a custom {} sound. Do you want to replace it? (yes/no)".format(action)))
            answer = await self.bot.wait_for_message(timeout=15, author=context.message.author)

            if answer.content.lower().strip() != "yes":
                await self.bot.reply("{} sound not replaced.".format(action.capitalize()))
                return

            os.remove(path)

        async with aiohttp.get(url) as nwsnd:
            f = open(path, "wb")
            f.write(await nwsnd.read())
            f.close
            await self.bot.reply("{} sound added.".format(action.capitalize()))

    @commands.command(pass_context=True, no_pm=True, name="deljoinsound")
    async def _deljoinsound(self, context: commands.context.Context):
        """Deletes the join sound for the calling user."""

        await self._del_sound(context, "join", context.message.author.id)

    @commands.command(pass_context=True, no_pm=True, name="delleavesound")
    async def _delleavesound(self, context: commands.context.Context):
        """Deletes the leave sound for the calling user."""

        await self._del_sound(context, "leave", context.message.author.id)

    @commands.command(pass_context=True, no_pm=True, name="deljoinsoundfor")
    @checks.admin_or_permissions(Administrator=True)
    async def _deljoinsoundfor(self, context: commands.context.Context, user: discord.User):
        """Deletes the join sound for the given user. Must be a mention!"""

        await self._del_sound(context, "join", user.id)

    @commands.command(pass_context=True, no_pm=True, name="delleavesoundfor")
    @checks.admin_or_permissions(Administrator=True)
    async def _delleavesoundfor(self, context: commands.context.Context, user: discord.User):
        """Deletes the leave sound for the given user. Must be a mention!"""

        await self._del_sound(context, "leave", user.id)

    async def _del_sound(self, context, action, userid):
        await self.bot.type()

        server = context.message.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            dataIO.save_json(self.settings_path, self.settings)

        path = "{}/{}".format(self.sound_base, server.id)
        if not os.path.exists(path):
            await self.bot.reply(cf.warning("There is not a custom {} sound.".format(action)))
            return

        path = "{}/{}/{}".format(self.sound_base, server.id, userid)
        if not os.path.exists(path):
            await self.bot.reply(cf.warning("There is not a custom {} sound.".format(action)))
            return

        path += "/" + action
        if not os.path.exists(path):
            await self.bot.reply(cf.warning("There is not a custom {} sound.".format(action)))
            return

        os.remove(path)
        await self.bot.reply(cf.info("{} sound deleted.".format(action.capitalize())))

    async def voice_state_update(self, before: discord.Member, after: discord.Member):
        bserver = before.server
        aserver = after.server

        if bserver.id not in self.settings:
            self.settings[bserver.id] = default_settings
            dataIO.save_json(self.settings_path, self.settings)

        if aserver.id not in self.settings:
            self.settings[aserver.id] = default_settings
            dataIO.save_json(self.settings_path, self.settings)

        if before.voice.voice_channel != after.voice.voice_channel:
            # went from no channel to a channel
            if before.voice.voice_channel is None and after.voice.voice_channel is not None and self.settings[aserver.id]["join_on"] and after.voice.voice_channel != aserver.afk_channel:
                path = "{}/{}/{}/join".format(self.sound_base, aserver.id, after.id)
                if os.path.exists(path):
                    await self.sound_play(aserver, after.voice.voice_channel, path)
            # went from one channel to another
            elif before.voice.voice_channel is not None and after.voice.voice_channel is not None:
                if self.settings[bserver.id]["leave_on"] and before.voice.voice_channel != bserver.afk_channel:
                    path = "{}/{}/{}/leave".format(self.sound_base, bserver.id, before.id)
                    if os.path.exists(path):
                        await self.sound_play(bserver, before.voice.voice_channel, path)
                if self.settings[aserver.id]["join_on"] and after.voice.voice_channel != aserver.afk_channel:
                    path = "{}/{}/{}/join".format(self.sound_base, aserver.id, after.id)
                    if os.path.exists(path):
                        await self.sound_play(aserver, after.voice.voice_channel, path)
            # went from a channel to no channel
            elif before.voice.voice_channel is not None and after.voice.voice_channel is None and self.settings[bserver.id]["leave_on"] and before.voice.voice_channel != bserver.afk_channel:
                path = "{}/{}/{}/leave".format(self.sound_base, bserver.id, before.id)
                if os.path.exists(path):
                    await self.sound_play(bserver, before.voice.voice_channel, path)

def check_folders():
    if not os.path.exists("data/customjoinleave"):
        print("Creating data/customjoinleave directory...")
        os.makedirs("data/customjoinleave")

def check_files():
    f = "data/customjoinleave/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating data/customjoinleave/settings.json...")
        dataIO.save_json(f, {})

def setup(bot: commands.bot.Bot):
    check_folders()
    check_files()
    n = Customjoinleave(bot)
    bot.add_listener(n.voice_state_update, "on_voice_state_update")

    bot.add_cog(n)
