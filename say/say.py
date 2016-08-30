import discord
from discord.ext import commands

class Say:
    """Echoes back the input."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(no_pm=True, pass_context=True, name="say")
    async def _say(self, context, *, text):
        """Says what you tell it."""

        self.bot.type()
        user = context.message.author
        if hasattr(user, "bot") and user.bot is True:
            return
        try:
            if "__" in text:
                raise ValueError
            evald = eval(text, {}, {"message": context.message,
                                    "channel": context.message.channel,
                                    "server": context.message.server})
        except:
            evald = text
        if len(str(evald)) > 2000:
            evald = str(evald)[-1990:] + " you fuck."
        await self.bot.say(evald)

    @commands.command(no_pm=True, pass_context=True, name="tts")
    async def _tts(self, context, *, text):
        """TTS's what you tell it."""

        self.bot.type()
        user = context.message.author
        if hasattr(user, "bot") and user.bot is True:
            return
        try:
            if "__" in text:
                raise ValueError
            evald = eval(text, {}, {"message": context.message,
                                    "channel": context.message.channel,
                                    "server": context.message.server})
        except:
            evald = text
        if len(str(evald)) > 2000:
            evald = str(evald)[-1990:] + " you fuck."
        await self.bot.send_message(context.message.channel, evald, tts=True)

    @commands.command(no_pm=True, pass_context=True, name="reply")
    async def _reply(self, context, *, text):
        """Replies to you with what you tell it."""

        self.bot.type()
        user = context.message.author
        if hasattr(user, "bot") and user.bot is True:
            return
        try:
            if "__" in text:
                raise ValueError
            evald = eval(text, {}, {"message": context.message,
                                    "channel": context.message.channel,
                                    "server": context.message.server})
        except:
            evald = text
        if len(str(evald)) > 2000:
            evald = str(evald)[-1990:] + " you fuck."
        await self.bot.reply(evald)

    @commands.command(no_pm=False, pass_context=True, name="pm")
    async def _pm(self, context, *, text):
        """PMs you what you tell it."""

        self.bot.type()
        user = context.message.author
        if hasattr(user, "bot") and user.bot is True:
            return
        try:
            if "__" in text:
                raise ValueError
            evald = eval(text, {}, {"message": context.message,
                                    "channel": context.message.channel,
                                    "server": context.message.server})
        except:
            evald = text
        if len(str(evald)) > 2000:
            evald = str(evald)[-1990:] + " you fuck."
        await self.bot.whisper(evald)

def setup(bot):
    bot.add_cog(Say(bot))
