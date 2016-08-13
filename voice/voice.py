from discord.ext import commands
from __main__ import send_cmd_help
from .utils import checks

class Voice:
    """Tools for controlling the bot's voice connections."""
    def __init__(self, bot):
        self.bot = bot
        self.audio_player = False

    def voice_connected(self, server):
        return self.bot.is_voice_connected(server)

    def voice_client(self, server):
        return self.bot.voice_client_in(server)

    @commands.group(pass_context=True, no_pm=True, name='voice', aliases=['vc'])
    async def _voice(self, context):
        """[join/leave]"""
        if context.invoked_subcommand is None:
            await send_cmd_help(context)

    @_voice.command(hidden=True, pass_context=True, no_pm=True, name='join', aliases=['connect'])
    @checks.serverowner_or_permissions()
    async def _join(self, context):
        """Joins your voice channel."""
        author = context.message.author
        server = context.message.server
        channel = author.voice_channel
        if not self.voice_connected(server):
            await self.bot.join_voice_channel(channel)

    @_voice.command(hidden=True, pass_context=True, no_pm=True, name='leave', aliases=['disconnect'])
    @checks.serverowner_or_permissions()
    async def _leave(self, context):
        """Leaves your voice channel."""
        server = context.message.server
        if not self.voice_connected(server):
            return
        voice_client = self.voice_client(server)
        if self.audio_player:
            self.audio_player.stop()
        await voice_client.disconnect()

    @_voice.command(no_pm=True, name='stop')
    async def _stop(self):
        if self.audio_player:
            self.audio_player.stop()

def setup(bot):
    bot.add_cog(Voice(bot))
