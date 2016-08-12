from discord.ext import commands
from __main__ import send_cmd_help
from .utils import checks
from os.path import join

class Quakesounds:
    """Play some Quake sounds."""
    def __init__(self, bot):
        self.bot = bot
        self.audio_player = False
        self.sound_base = 'data/downloader/tmerc-cogs/quakesounds/data/sounds'

    def voice_connected(self, server):
        if self.bot.is_voice_connected(server):
            return True
        return False

    def voice_client(self, server):
        return self.bot.voice_client_in(server)

    @commands.group(pass_context=True, no_pm=True, name='voice', aliases=['vc'])
    async def _vc(self, context):
        """[join/leave]"""
        if context.invoked_subcommand is None:
            await send_cmd_help(context)

    @_vc.command(hidden=True, pass_context=True, no_pm=True, name='join', aliases=['connect'])
    @checks.serverowner_or_permissions()
    async def _join(self, context):
        """Joins your voice channel"""
        author = context.message.author
        server = context.message.server
        channel = author.voice_channel
        if not self.voice_connected(server):
            await self.bot.join_voice_channel(channel)

    @_vc.command(hidden=True, pass_context=True, no_pm=True, name='leave', aliases=['disconnect'])
    @checks.serverowner_or_permissions()
    async def _leave(self, context):
        """Leaves your voice channel"""
        server = context.message.server
        if not self.voice_connected(server):
            return
        voice_client = self.voice_client(server)
        if self.audio_player:
            self.audio_player.stop()
        await voice_client.disconnect()

    @_vc.command(no_pm=True, name='stop')
    async def _stop(self):
        if self.audio_player:
            self.audio_player.stop()

    @commands.command(no_pm=True, pass_context=True, name='fbottomfeeder')
    async def _fbottomfeeder(self, context):
        gender = 'female'
        sound = 'bottomfeeder'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='fdominating')
    async def _fdominating(self, context):
        gender = 'female'
        sound = 'dominating'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='ffirstblood')
    async def _ffirstblood(self, context):
        gender = 'female'
        sound = 'firstblood'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='fgodlike')
    async def _fgodlike(self, context):
        gender = 'female'
        sound = 'godlike'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='fheadshot')
    async def _fheadshot(self, context):
        gender = 'female'
        sound = 'headshot'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='fholyshit')
    async def _fholyshit(self, context):
        gender = 'female'
        sound = 'holyshit'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='fkillingspree')
    async def _fkillingspree(self, context):
        gender = 'female'
        sound = 'killingspree'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='fmonsterkill')
    async def _fmonsterkill(self, context):
        gender = 'female'
        sound = 'monsterkill'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='fmultikill')
    async def _fmultikill(self, context):
        gender = 'female'
        sound = 'multikill'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='fprepare')
    async def _fprepare(self, context):
        gender = 'female'
        sound = 'prepare'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='frampage')
    async def _frampage(self, context):
        gender = 'female'
        sound = 'rampage'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='fultrakill')
    async def _fultrakill(self, context):
        gender = 'female'
        sound = 'ultrakill'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='funstoppable')
    async def _funstoppable(self, context):
        gender = 'female'
        sound = 'unstoppable'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='fwickedsick')
    async def _fwickedsick(self, context):
        gender = 'female'
        sound = 'wickedsick'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='combobreaker')
    async def _combobreaker(self, context):
        gender = 'male'
        sound = 'combobreaker'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='combowhore')
    async def _combowhore(self, context):
        gender = 'male'
        sound = 'combowhore'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='dominating')
    async def _dominating(self, context):
        gender = 'male'
        sound = 'dominating'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='doublekill')
    async def _doublekill(self, context):
        gender = 'male'
        sound = 'doublekill'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='firstblood')
    async def _firstblood(self, context):
        gender = 'male'
        sound = 'firstblood'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='godlike')
    async def _godlike(self, context):
        gender = 'male'
        sound = 'godlike'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='hattrick')
    async def _hattrick(self, context):
        gender = 'male'
        sound = 'hattrick'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='headhunter')
    async def _headhunter(self, context):
        gender = 'male'
        sound = 'headhunter'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='headshot')
    async def _headshot(self, context):
        gender = 'male'
        sound = 'headshot'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='holyshit')
    async def _holyshit(self, context):
        gender = 'male'
        sound = 'holyshit'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='humiliation')
    async def _humiliation(self, context):
        gender = 'male'
        sound = 'humiliation'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='impressive')
    async def _impressive(self, context):
        gender = 'male'
        sound = 'impressive'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='killingspree')
    async def _killingspree(self, context):
        gender = 'male'
        sound = 'killingspree'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='ludicrouskill')
    async def _ludicrouskill(self, context):
        gender = 'male'
        sound = 'ludicrouskill'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='monsterkill')
    async def _monsterkill(self, context):
        gender = 'male'
        sound = 'monsterkill'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='multikill')
    async def _multikill(self, context):
        gender = 'male'
        sound = 'multikill'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='perfect')
    async def _perfect(self, context):
        gender = 'male'
        sound = 'perfect'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='prepare')
    async def _prepare(self, context):
        gender = 'male'
        sound = 'prepare'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='rampage')
    async def _rampage(self, context):
        gender = 'male'
        sound = 'rampage'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='teamkiller')
    async def _teamkiller(self, context):
        gender = 'male'
        sound = 'teamkiller'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='triplekill')
    async def _triplekill(self, context):
        gender = 'male'
        sound = 'triplekill'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='ultrakill')
    async def _ultrakill(self, context):
        gender = 'male'
        sound = 'ultrakill'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='unstoppable')
    async def _unstoppable(self, context):
        gender = 'male'
        sound = 'unstoppable'
        await self.sound_play(context, sound)
        await self._leave(context)

    @commands.command(no_pm=True, pass_context=True, name='wickedsick')
    async def _wickedsick(self, context):
        gender = 'male'
        sound = 'wickedsick'
        await self.sound_play(context, sound)
        await self._leave(context)

    async def sound_init(self, server, path):
        voice_client = self.voice_client(server)
        self.audio_player = voice_client.create_ffmpeg_player(path)

    async def sound_play(self, context, gender, sound):
        path = join(self.sound_base, gender, sound + '.mp3')
        server = context.message.server
        if not context.message.channel.is_private:
            if self.voice_connected(server) and not self.audio_player:
                await self.sound_init(server, path)
                self.audio_player.start()
            elif self.audio_player:
                if not self.audio_player.is_playing():
                    await self.sound_init(server, path)
                    self.audio_player.start()

def setup(bot):
    bot.add_cog(Quakesounds(bot))