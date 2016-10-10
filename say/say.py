import discord
from discord.ext import commands

class Say:
    """Echoes back the input."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(no_pm=True, pass_context=True, name="say")
    async def _say(self, context, *, text):
        """Says what you tell it."""

        await self.bot.type()
        await self.bot.say(text)

    @commands.command(no_pm=True, pass_context=True, name="tts")
    async def _tts(self, context, *, text):
        """TTS's what you tell it."""

        await self.bot.type()
        await self.bot.send_message(context.message.channel, text, tts=True)

    @commands.command(no_pm=True, pass_context=True, name="reply")
    async def _reply(self, context, *, text):
        """Replies to you with what you tell it."""

        await self.bot.type()
        await self.bot.reply(text)

    @commands.command(no_pm=False, pass_context=True, name="pm")
    async def _pm(self, context, *, text):
        """PMs you what you tell it."""

        await self.bot.type()
        await self.bot.whisper(text)

def setup(bot):
    bot.add_cog(Say(bot))
