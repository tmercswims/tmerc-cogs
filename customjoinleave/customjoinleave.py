from discord.ext import commands
from __main__ import send_cmd_help
from .utils import checks
from .utils.dataIO import fileIO

import aiohttp
import magic
import os
import os.path
import threading

default_settings = {
    "join_on": False,
    "leave_on": False
}

class Customjoinleave:
    """Play a sound byte."""
    def __init__(self, bot):
        self.bot = bot
        self.audio_player = False
        self.sound_base = "data/customjoinleave"
        self.settings_path = "data/customjoinleave/settings.json"
        self.settings = fileIO(self.settings_path, "load")

    def voice_connected(self, server):
        return self.bot.is_voice_connected(server)

    def voice_client(self, server):
        return self.bot.voice_client_in(server)

    async def _leave_voice_channel(self, server):
        if not self.voice_connected(server):
            return
        voice_client = self.voice_client(server)

        if self.audio_player:
            self.audio_player.stop()
        await voice_client.disconnect()

    async def sound_init(self, server, path):
        options = "-filter \"volume=volume=0.15\""
        voice_client = self.voice_client(server)
        self.audio_player = voice_client.create_ffmpeg_player(path, options=options)

    async def sound_play(self, server, channel, p):
        if not channel.is_private:
            if self.voice_connected(server):
                if not self.audio_player:
                    await self.sound_init(server, p)
                    threading.Thread(target=self.sound_thread, args=(self.audio_player, server,)).start()
                else:
                    # if not self.audio_player.is_playing():
                    await self.sound_init(server, p)
                    threading.Thread(target=self.sound_thread, args=(self.audio_player, server,)).start()
            else:
                await self.bot.join_voice_channel(channel)
                if not self.audio_player:
                    await self.sound_init(server, p)
                    threading.Thread(target=self.sound_thread, args=(self.audio_player, server,)).start()
                else:
                    # if not self.audio_player.is_playing():
                    await self.sound_init(server, p)
                    threading.Thread(target=self.sound_thread, args=(self.audio_player, server,)).start()

    def sound_thread(self, t, server):
        t.run()
        self.voice_client(server).loop.create_task(self._leave_voice_channel(server))

    @commands.group(pass_context=True, no_pm=True, name="joinleaveset")
    async def _joinleaveset(self, context):
        """Sets custom join/leave settings."""

        server = context.message.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            fileIO(self.settings_path, "save", self.settings)
        if context.invoked_subcommand is None:
            await send_cmd_help(context)

    @_joinleaveset.command(pass_context=True, no_pm=True, name="togglejoin")
    @checks.admin_or_permissions(manage_server=True)
    async def _togglejoin(self, context):
        """Toggles custom join sounds on/off."""

        self.bot.type()

        server = context.message.server
        self.settings[server.id]["join_on"] = not self.settings[server.id]["join_on"]
        if self.settings[server.id]["join_on"]:
            await self.bot.reply("Custom join sounds are now enabled.")
        else:
            await self.bot.reply("Custom join sounds are now disabled.")
        fileIO(self.settings_path, "save", self.settings)

    @_joinleaveset.command(pass_context=True, no_pm=True, name="toggleleave")
    @checks.admin_or_permissions(manage_server=True)
    async def _toggleleave(self, context):
        """Toggles custom join sounds on/off."""

        self.bot.type()

        server = context.message.server
        self.settings[server.id]["leave_on"] = not self.settings[server.id]["leave_on"]
        if self.settings[server.id]["leave_on"]:
            await self.bot.reply("Custom leave sounds are now enabled.")
        else:
            await self.bot.reply("Custom leave sounds are now disabled.")
        fileIO(self.settings_path, "save", self.settings)

    @commands.command(pass_context=True, no_pm=True, name="setjoinsound")
    async def _setjoinsound(self, context, *link):
        """Sets the join sound for the calling user."""

        self.bot.type()

        server = context.message.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            fileIO(self.settings_path, "save", self.settings)

        attach = context.message.attachments
        if len(attach) > 1 or (attach and link):
            await self.bot.reply("Please only provide one file.")
            return

        url = ""
        if attach:
            url = attach[0]["url"]
        elif link:
            url = "".join(link)
        else:
            await self.bot.reply("You must provide either a Discord attachment or a direct link to a sound.")
            return
        await self._set_sound(context, url, "join")

    @commands.command(pass_context=True, no_pm=True, name="setleavesound")
    async def _setleavesound(self, context, *link):
        """Sets the leave sound for the calling user."""

        self.bot.type()
        server = context.message.server

        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            fileIO(self.settings_path, "save", self.settings)

        attach = context.message.attachments
        if len(attach) > 1 or (attach and link):
            await self.bot.reply("Please only provide one file.")
            return

        url = ""
        if attach:
            url = attach[0]["url"]
        elif link:
            url = "".join(link)
        else:
            await self.bot.reply("You must provide either a Discord attachment or a direct link to a sound.")
            return
        await self._set_sound(context, url, "leave")

    async def _set_sound(self, context, url, action):
        server = context.message.server

        path = "{}/{}".format(self.sound_base, server.id)
        if not os.path.exists(path):
            os.makedirs(path)

        path = "{}/{}/{}".format(self.sound_base, server.id, context.message.author.id)
        if not os.path.exists(path):
            os.makedirs(path)

        path += "/" + action
        if os.path.exists(path):
            await self.bot.reply("You already have a custom {} sound. Do you want to replace it? (yes/no)".format(action))
            answer = await self.bot.wait_for_message(timeout=15, author=context.message.author)

            if answer.content.lower().strip() != "yes":
                await self.bot.reply("Sound not replaced.")
                return

            os.remove(path)

        async with aiohttp.get(url) as nwsnd:
            f = open(path, "wb")
            f.write(await nwsnd.read())
            f.close
            if "audio" not in magic.from_file(path).lower():
                await self.bot.reply("The file you provided does not appear to be audio, please try again.")
                os.remove(path)
                return
            await self.bot.reply("Your {} sound has been added.".format(action))

    async def voice_state_update(self, before, after):
        bserver = before.server
        aserver = after.server

        if bserver.id not in self.settings:
            self.settings[bserver.id] = default_settings
            fileIO(self.settings_path, "save", self.settings)

        if aserver.id not in self.settings:
            self.settings[aserver.id] = default_settings
            fileIO(self.settings_path, "save", self.settings)

        if before.voice.voice_channel != after.voice.voice_channel:
            if before.voice.voice_channel != None and after.voice.voice_channel == None and self.settings[bserver.id]["leave_on"]:
                path = "{}/{}/{}/leave".format(self.sound_base, bserver.id, before.id)
                if os.path.exists(path):
                    await self.sound_play(bserver, before.voice.voice_channel, path)
            elif after.voice.voice_channel != None:
                path = "{}/{}/{}/join".format(self.sound_base, aserver.id, after.id)
                if os.path.exists(path):
                    await self.sound_play(aserver, after.voice.voice_channel, path)

def check_folders():
    if not os.path.exists("data/customjoinleave"):
        print("Creating data/customjoinleave directory...")
        os.makedirs("data/customjoinleave")

def check_files():
    f = "data/customjoinleave/settings.json"
    if not fileIO(f, "check"):
        print("Creating data/customjoinleave/settings.json...")
        fileIO(f, "save", {})

def setup(bot):
    check_folders()
    check_files()
    n = Customjoinleave(bot)
    bot.add_listener(n.voice_state_update, "on_voice_state_update")

    bot.add_cog(n)
