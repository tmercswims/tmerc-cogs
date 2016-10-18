import discord
from discord.ext import commands


class Say:

    """Echoes back the input."""

    def __init__(self, bot: commands.bot.Bot):
        self.bot = bot

    @commands.command(no_pm=True, pass_context=True, name="say")
    async def _say(self, ctx: commands.context.Context, *, text: str):
        """Says what you tell it."""

        await self.bot.type()
        await self.bot.say(text)

    @commands.command(no_pm=True, pass_context=True, name="tts")
    async def _tts(self, ctx: commands.context.Context, *, text: str):
        """TTS's what you tell it."""

        await self.bot.type()
        await self.bot.send_message(ctx.message.channel, text, tts=True)

    @commands.command(no_pm=True, pass_context=True, name="reply")
    async def _reply(self, ctx: commands.context.Context, *, text: str):
        """Replies to you with what you tell it."""

        await self.bot.type()
        await self.bot.reply(text)

    @commands.command(no_pm=False, pass_context=True, name="pm", aliases=["dm"])
    async def _pm(self, ctx: commands.context.Context, *, text: str):
        """PMs you what you tell it."""

        await self.bot.type()
        await self.bot.whisper(text)


def setup(bot: commands.bot.Bot):
    bot.add_cog(Say(bot))
