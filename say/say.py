from discord.ext import commands


class Say:

    """Echoes back the input."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(no_pm=True, pass_context=True, name="say")
    async def _say(self, ctx: commands.Context, *, text: str):
        """Says what you tell it."""

        await self.bot.type()
        await self.bot.say(text)

    @commands.command(no_pm=True, pass_context=True, name="tts")
    async def _tts(self, ctx: commands.Context, *, text: str):
        """TTS's what you tell it."""

        await self.bot.type()
        await self.bot.send_message(ctx.message.channel, text, tts=True)

    @commands.command(no_pm=True, pass_context=True, name="reply")
    async def _reply(self, ctx: commands.Context, *, text: str):
        """Replies to you with what you tell it."""

        await self.bot.type()
        await self.bot.reply(text)

    @commands.command(no_pm=True, pass_context=True, name="pm",
                      aliases=["dm"])
    async def _pm(self, ctx: commands.Context, *, text: str):
        """PMs you what you tell it."""

        await self.bot.type()
        await self.bot.whisper(text)


def setup(bot: commands.Bot):
    bot.add_cog(Say(bot))
