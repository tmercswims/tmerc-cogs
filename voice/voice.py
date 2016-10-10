import discord
from discord.ext import commands
from .utils import checks
from __main__ import send_cmd_help

class Voice:
    """Tools for controlling the bot's voice connections."""
    def __init__(self, bot: commands.bot.Bot):
        self.bot = bot
        self.audio_player = False

    def voice_connected(self, server: discord.Server) -> bool:
        return self.bot.is_voice_connected(server)

    def voice_client(self, server: discord.Server) -> discord.VoiceClient:
        return self.bot.voice_client_in(server)

    @commands.group(pass_context=True, no_pm=True, name="voice", aliases=["vc"])
    async def _voice(self, context: commands.context.Context):
        """[join/leave]"""
        if context.invoked_subcommand is None:
            await send_cmd_help(context)

    @_voice.command(hidden=True, pass_context=True, no_pm=True, name="join", aliases=["connect"])
    @checks.admin_or_permissions(administrator=True)
    async def _join(self, context: commands.context.Context):
        """Joins your voice channel."""
        author = context.message.author
        server = context.message.server
        channel = author.voice_channel
        if not self.voice_connected(server):
            await self.bot.join_voice_channel(channel)

    @_voice.command(hidden=True, pass_context=True, no_pm=True, name="leave", aliases=["disconnect"])
    @checks.admin_or_permissions(administrator=True)
    async def _leave(self, context: commands.context.Context):
        """Leaves your voice channel."""
        server = context.message.server
        if not self.voice_connected(server):
            return
        voice_client = self.voice_client(server)
        if self.audio_player:
            self.audio_player.stop()
        await voice_client.disconnect()

def setup(bot: commands.bot.Bot):
    bot.add_cog(Voice(bot))
