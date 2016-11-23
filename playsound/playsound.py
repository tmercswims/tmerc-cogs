import asyncio
import glob
import os
import os.path
from typing import List

import aiohttp
import discord
from discord.ext import commands

from .utils.dataIO import dataIO
from .utils import checks, chat_formatting as cf


default_volume = 25


class PlaySound:

    """Play a sound byte."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.audio_players = {}
        self.sound_base = "data/playsound"

        self.settings_path = "data/playsound/settings.json"
        self.settings = dataIO.load_json(self.settings_path)

    def voice_channel_full(self, voice_channel: discord.Channel) -> bool:
        return (voice_channel.user_limit != 0 and
                len(voice_channel.voice_members) >= voice_channel.user_limit)

    def list_sounds(self, server_id: str) -> List[str]:
        return sorted(
            [os.path.splitext(s)[0] for s in os.listdir(os.path.join(
                self.sound_base, server_id))],
            key=lambda s: s.lower())

    def voice_connected(self, server: discord.Server) -> bool:
        return self.bot.is_voice_connected(server)

    def voice_client(self, server: discord.Server) -> discord.VoiceClient:
        return self.bot.voice_client_in(server)

    async def _join_voice_channel(self, ctx: commands.Context):
        channel = ctx.message.author.voice_channel
        if channel:
            await self.bot.join_voice_channel(channel)

    async def _leave_voice_channel(self, server: discord.Server):
        if not self.voice_connected(server):
            return
        voice_client = self.voice_client(server)

        if server.id in self.audio_players:
            self.audio_players[server.id].stop()
        await voice_client.disconnect()

    async def wait_for_disconnect(self, server: discord.Server):
        while not self.audio_players[server.id].is_done():
            await asyncio.sleep(0.01)
        await self._leave_voice_channel(server)

    async def sound_init(self, ctx: commands.Context, path: str, vol: int):
        server = ctx.message.server
        options = "-filter \"volume=volume={}\"".format(str(vol/100))
        voice_client = self.voice_client(server)
        self.audio_players[server.id] = voice_client.create_ffmpeg_player(
            path, options=options)

    async def sound_play(self, ctx: commands.Context, p: str, vol: int):
        server = ctx.message.server
        if not ctx.message.author.voice_channel:
            await self.bot.reply(
                cf.warning("You need to join a voice channel first."))
            return

        if self.voice_channel_full(ctx.message.author.voice_channel):
            return

        if not ctx.message.channel.is_private:
            if self.voice_connected(server):
                if server.id not in self.audio_players:
                    await self.sound_init(ctx, p, vol)
                    self.audio_players[server.id].start()
                    await self.wait_for_disconnect(server)
                else:
                    if self.audio_players[server.id].is_playing():
                        self.audio_players[server.id].stop()
                    await self.sound_init(ctx, p, vol)
                    self.audio_players[server.id].start()
                    await self.wait_for_disconnect(server)
            else:
                await self._join_voice_channel(ctx)
                if server.id not in self.audio_players:
                    await self.sound_init(ctx, p, vol)
                    self.audio_players[server.id].start()
                    await self.wait_for_disconnect(server)
                else:
                    if self.audio_players[server.id].is_playing():
                        self.audio_players[server.id].stop()
                    await self.sound_init(ctx, p, vol)
                    self.audio_players[server.id].start()
                    await self.wait_for_disconnect(server)

    @commands.command(no_pm=True, pass_context=True, name="playsound")
    async def _playsound(self, ctx: commands.Context, soundname: str):
        """Plays the specified sound."""

        server = ctx.message.server

        if server.id not in os.listdir(self.sound_base):
            os.makedirs(os.path.join(self.sound_base, server.id))

        if server.id not in self.settings:
            self.settings[server.id] = {}
            dataIO.save_json(self.settings_path, self.settings)

        f = glob.glob(os.path.join(
            self.sound_base, server.id, soundname + ".*"))
        if len(f) < 1:
            await self.bot.reply(cf.error(
                "Sound file not found. Try `{}allsounds` for a list.".format(
                    ctx.prefix)))
            return
        elif len(f) > 1:
            await self.bot.reply(cf.error(
                "There are {} sound files with the same name, but different"
                " extensions, and I can't deal with it. Please make filenames"
                " (excluding extensions) unique.".format(len(f))))
            return

        soundname = os.path.splitext(os.path.basename(f[0]))[0]
        if soundname in self.settings[server.id]:
            if "volume" in self.settings[server.id][soundname]:
                vol = self.settings[server.id][soundname]["volume"]
            else:
                vol = default_volume
                self.settings[server.id][soundname]["volume"] = vol
                dataIO.save_json(self.settings_path, self.settings)
        else:
            vol = default_volume
            self.settings[server.id][soundname] = {"volume": vol}
            dataIO.save_json(self.settings_path, self.settings)

        await self.sound_play(ctx, f[0], vol)

    @commands.command(pass_context=True, name="allsounds")
    async def _allsounds(self, ctx: commands.Context):
        """Sends a list of every sound in a PM."""

        await self.bot.type()

        server = ctx.message.server

        if server.id not in os.listdir(self.sound_base):
            os.makedirs(os.path.join(self.sound_base, server.id))

        if server.id not in self.settings:
            self.settings[server.id] = {}
            dataIO.save_json(self.settings_path, self.settings)

        strbuffer = self.list_sounds(server.id)

        if len(strbuffer) == 0:
            await self.bot.reply(cf.warning(
                "No sounds found. Use `{}addsound` to add one.".format(
                    ctx.prefix)))
            return

        mess = "```"
        for line in strbuffer:
            if len(mess) + len(line) + 4 < 2000:
                mess += "\n" + line
            else:
                mess += "```"
                await self.bot.whisper(mess)
                mess = "```" + line
        if mess != "":
            mess += "```"
            await self.bot.whisper(mess)

        await self.bot.reply("Check your PMs!")

    @commands.command(no_pm=True, pass_context=True, name="addsound")
    @checks.mod_or_permissions(administrator=True)
    async def _addsound(self, ctx: commands.Context, link: str=None):
        """Adds a new sound.

        Either upload the file as a Discord attachment and make your comment
        "[p]addsound", or use "[p]addsound direct-URL-to-file".
        """

        await self.bot.type()

        server = ctx.message.server

        if server.id not in os.listdir(self.sound_base):
            os.makedirs(os.path.join(self.sound_base, server.id))

        if server.id not in self.settings:
            self.settings[server.id] = {}
            dataIO.save_json(self.settings_path, self.settings)

        attach = ctx.message.attachments
        if len(attach) > 1 or (attach and link):
            await self.bot.reply(
                cf.error("Please only add one sound at a time."))
            return

        url = ""
        filename = ""
        if attach:
            a = attach[0]
            url = a["url"]
            filename = a["filename"]
        elif link:
            url = "".join(link)
            filename = os.path.basename(
                "_".join(url.split()).replace("%20", "_"))
        else:
            await self.bot.reply(
                cf.error("You must provide either a Discord attachment or a"
                         " direct link to a sound."))
            return

        filepath = os.path.join(self.sound_base, server.id, filename)

        if os.path.splitext(filename)[0] in self.list_sounds(server.id):
            await self.bot.reply(
                cf.error("A sound with that filename already exists."
                         " Please change the filename and try again."))
            return

        async with aiohttp.get(url) as new_sound:
            f = open(filepath, "wb")
            f.write(await new_sound.read())
            f.close()

        self.settings[server.id][
            os.path.splitext(filename)[0]] = {"volume": default_volume}
        dataIO.save_json(self.settings_path, self.settings)

        await self.bot.reply(
            cf.info("Sound {} added.".format(os.path.splitext(filename)[0])))

    @commands.command(no_pm=True, pass_context=True, name="soundvol")
    @checks.mod_or_permissions(administrator=True)
    async def _soundvol(self, ctx: commands.Context, soundname: str,
                        percent: int=None):
        """Sets the volume for the specified sound.

        If no value is given, the current volume for the sound is printed.
        """

        await self.bot.type()

        server = ctx.message.server

        if server.id not in os.listdir(self.sound_base):
            os.makedirs(os.path.join(self.sound_base, server.id))

        if server.id not in self.settings:
            self.settings[server.id] = {}
            dataIO.save_json(self.settings_path, self.settings)

        f = glob.glob(os.path.join(self.sound_base, server.id,
                                   soundname + ".*"))
        if len(f) < 1:
            await self.bot.say(cf.error(
                "Sound file not found. Try `{}allsounds` for a list.".format(
                    ctx.prefix)))
            return
        elif len(f) > 1:
            await self.bot.say(cf.error(
                "There are {} sound files with the same name, but different"
                " extensions, and I can't deal with it. Please make filenames"
                " (excluding extensions) unique.".format(len(f))))
            return

        if soundname not in self.settings[server.id]:
            self.settings[server.id][soundname] = {"volume": default_volume}
            dataIO.save_json(self.settings_path, self.settings)

        if percent is None:
            await self.bot.reply("Volume for {} is {}.".format(
                soundname, self.settings[server.id][soundname]["volume"]))
            return

        self.settings[server.id][soundname]["volume"] = percent
        dataIO.save_json(self.settings_path, self.settings)

        await self.bot.reply("Volume for {} set to {}.".format(soundname,
                                                               percent))

    @commands.command(no_pm=True, pass_context=True, name="delsound")
    @checks.mod_or_permissions(administrator=True)
    async def _delsound(self, ctx: commands.Context, soundname: str):
        """Deletes an existing sound."""

        await self.bot.type()

        server = ctx.message.server

        if server.id not in os.listdir(self.sound_base):
            os.makedirs(os.path.join(self.sound_base, server.id))

        f = glob.glob(os.path.join(self.sound_base, server.id,
                                   soundname + ".*"))
        if len(f) < 1:
            await self.bot.say(cf.error(
                "Sound file not found. Try `{}allsounds` for a list.".format(
                    ctx.prefix)))
            return
        elif len(f) > 1:
            await self.bot.say(cf.error(
                "There are {} sound files with the same name, but different"
                " extensions, and I can't deal with it. Please make filenames"
                " (excluding extensions) unique.".format(len(f))))
            return

        os.remove(f[0])

        if soundname in self.settings[server.id]:
            del self.settings[server.id][soundname]
            dataIO.save_json(self.settings_path, self.settings)

        await self.bot.reply(cf.info("Sound {} deleted.".format(soundname)))

    @commands.command(no_pm=True, pass_context=True, name="getsound")
    async def _getsound(self, ctx: commands.Context, soundname: str):
        """Gets the given sound."""

        await self.bot.type()

        server = ctx.message.server

        if server.id not in os.listdir(self.sound_base):
            os.makedirs(os.path.join(self.sound_base, server.id))

        f = glob.glob(os.path.join(self.sound_base, server.id,
                                   soundname + ".*"))

        if len(f) < 1:
            await self.bot.say(cf.error(
                "Sound file not found. Try `{}allsounds` for a list.".format(
                    ctx.prefix)))
            return
        elif len(f) > 1:
            await self.bot.say(cf.error(
                "There are {} sound files with the same name, but different"
                " extensions, and I can't deal with it. Please make filenames"
                " (excluding extensions) unique.".format(len(f))))
            return

        await self.bot.upload(f[0])


def check_folders():
    if not os.path.exists("data/playsound"):
        print("Creating data/playsound directory...")
        os.makedirs("data/playsound")


def check_files():
    f = "data/playsound/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating data/playsound/settings.json...")
        dataIO.save_json(f, {})


def setup(bot: commands.Bot):
    check_folders()
    check_files()

    bot.add_cog(PlaySound(bot))
