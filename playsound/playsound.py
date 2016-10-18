import discord
from discord.ext import commands
from .utils import checks, chat_formatting as cf
from __main__ import send_cmd_help

from typing import List

import aiohttp
import asyncio
import glob
import os
import os.path


class Playsound:

    """Play a sound byte."""

    def __init__(self, bot):
        self.bot = bot
        self.audio_player = False
        self.sound_base = "data/playsound"

    def voice_channel_full(self, voice_channel: discord.Channel) -> bool:
        return (voice_channel.user_limit != 0 and
                len(voice_channel.voice_members) >= voice_channel.user_limit)

    def list_sounds(self) -> List[str]:
        return sorted(
            [os.path.splitext(s)[0] for s in os.listdir(self.sound_base)],
            key=lambda s: s.lower())

    def voice_connected(self, server: discord.Server) -> bool:
        return self.bot.is_voice_connected(server)

    def voice_client(self, server: discord.Server) -> discord.VoiceClient:
        return self.bot.voice_client_in(server)

    async def _join_voice_channel(self, ctx: commands.context.Context):
        channel = ctx.message.author.voice_channel
        if channel:
            await self.bot.join_voice_channel(channel)

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

    async def sound_init(self, ctx: commands.context.Context, path: str):
        server = ctx.message.server
        options = "-filter \"volume=volume=0.25\""
        voice_client = self.voice_client(server)
        self.audio_player = voice_client.create_ffmpeg_player(
            path, options=options)

    async def sound_play(self, ctx: commands.context.Context, p: str):
        server = ctx.message.server
        if not ctx.message.author.voice_channel:
            await self.bot.reply(
                cf.warning("You need to join a voice channel first."))
            return

        if self.voice_channel_full(ctx.message.author.voice_channel):
            return

        if not ctx.message.channel.is_private:
            if self.voice_connected(server):
                if not self.audio_player:
                    await self.sound_init(ctx, p)
                    self.audio_player.start()
                    await self.wait_for_disconnect(server)
                else:
                    if self.audio_player.is_playing():
                        self.audio_player.stop()
                    await self.sound_init(ctx, p)
                    self.audio_player.start()
                    await self.wait_for_disconnect(server)
            else:
                await self._join_voice_channel(ctx)
                if not self.audio_player:
                    await self.sound_init(ctx, p)
                    self.audio_player.start()
                    await self.wait_for_disconnect(server)
                else:
                    if self.audio_player.is_playing():
                        self.audio_player.stop()
                    await self.sound_init(ctx, p)
                    self.audio_player.start()
                    await self.wait_for_disconnect(server)

    @commands.command(no_pm=True, pass_context=True, name="playsound")
    async def _playsound(self, ctx: commands.context.Context, soundname: str):
        """Plays the specified sound."""

        f = glob.glob(os.path.join(self.sound_base, soundname + ".*"))
        if len(f) < 1:
            await self.bot.reply(cf.error(
                "Sound file not found. Try `{}allsounds` for a list."
                .format(ctx.prefix)))
            return
        elif len(f) > 1:
            await self.bot.reply(cf.error(
                "There are {} sound files with the same name, but different"
                " extensions, and I can't deal with it. Please make filenames"
                " (excluding extensions) unique.".format(len(f))))
            return

        await self.sound_play(ctx, f[0])

    @commands.command(pass_context=True, name="allsounds")
    async def _allsounds(self, ctx: commands.context.Context):
        """Sends a list of every sound in a PM."""

        await self.bot.type()
        strbuffer = self.list_sounds()
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
    async def _addsound(self, ctx: commands.context.Context, link: str):
        """Adds a new sound.

        Either upload the file as a Discord attachment and make your comment
        "[p]addsound", or use "[p]addsound direct-URL-to-file".
        """

        await self.bot.type()
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

        filepath = os.path.join(self.sound_base, filename)

        if os.path.splitext(filename)[0] in self.list_sounds():
            await self.bot.reply(
                cf.error("A sound with that filename already exists."
                         " Please change the filename and try again."))
            return

        async with aiohttp.get(url) as new_sound:
            f = open(filepath, "wb")
            f.write(await new_sound.read())
            f.close()

        await self.bot.reply(
            cf.info("Sound {} added.".format(os.path.splitext(filename)[0])))

    @commands.command(no_pm=True, pass_context=True, name="delsound")
    @checks.mod_or_permissions(administrator=True)
    async def _delsound(self, ctx: commands.context.Context, soundname: str):
        """Deletes an existing sound."""

        await self.bot.type()
        f = glob.glob(os.path.join(self.sound_base, soundname + ".*"))
        if len(f) < 1:
            await self.bot.say(
                cf.error("Sound file not found! Try `{}allsounds` for a list."
                         .format(ctx.prefix)))
            return
        elif len(f) > 1:
            await self.bot.say(cf.error(
                "There are {} sound files with the same name, but different"
                " extensions, and I can't deal with it. Please make filenames"
                " (excluding extensions) unique.".format(len(f))))
            return

        os.remove(f[0])
        await self.bot.reply(cf.info("Sound {} deleted.".format(soundname)))

    @commands.command(no_pm=True, pass_context=True, name="getsound")
    async def _getsound(self, ctx: commands.context.Context, soundname: str):
        """Gets the given sound."""

        await self.bot.type()
        f = glob.glob(os.path.join(self.sound_base, soundname + ".*"))
        if len(f) < 1:
            await self.bot.say(
                cf.error("Sound file not found! Try `{}allsounds` for a list."
                         .format(ctx.prefix)))
            return
        elif len(f) > 1:
            await self.bot.say(cf.error(
                "There are {} sound files with the same name, but different"
                " extensions, and I can't deal with it. Please make filenames"
                " (excluding extensions) unique.".format(len(f))))
            return

        await self.bot.upload(f[0])


def setup(bot: commands.bot.Bot):
    bot.add_cog(Playsound(bot))
