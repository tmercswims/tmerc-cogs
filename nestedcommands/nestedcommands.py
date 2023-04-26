import asyncio
import copy
import logging
import re
from typing import List

import discord
from redbot.core import Config, checks, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import box

from .errors import MismatchedParenthesesException

__author__ = "tmerc"

log = logging.getLogger("red.tmerc.nestedcommands")


class NestedCommands(commands.Cog):
    """Experimental cog that allows you to use the output of one command as the input of another."""

    guild_defaults = {"enabled": False, "channel": None}

    p = re.compile(r"\$\(.+\)")

    def __init__(self, bot: Red, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.bot = bot
        self.config = Config.get_conf(self, 36649125)
        self.config.register_guild(**self.guild_defaults)

        self.__init_before()

    @commands.hybrid_command()
    async def echo(self, ctx: commands.Context, *, message: str) -> None:
        """Says what you say. Does no filtering.

        Is there an echo in here?
        """

        await ctx.send(message)

    @commands.hybrid_group(fallback="state")
    @commands.guild_only()
    @checks.guildowner()
    async def ncset(self, ctx: commands.Context) -> None:
        """Get current NestedCommands settings."""

        if ctx.invoked_subcommand is None:
            config = await self.config.guild(ctx.guild).all()

            enabled = config["enabled"]
            channel = config["channel"]
            if channel is not None:
                channel: discord.TextChannel = discord.utils.get(ctx.guild.text_channels, id=channel)

            msg = box(
                f"  Enabled: {enabled}\n  Channel: {channel and channel.name}\n",
                "Current NestedCommands settings:",
            )

            await ctx.send(msg)

    @ncset.command(name="toggle")
    async def ncset_toggle(self, ctx: commands.Context, on_off: bool = None) -> None:
        """Turns NestedCommand on or off.

        If `on_off` is not provided, the state will be flipped.
        """

        await ctx.typing()

        guild = ctx.guild
        target_state = on_off if on_off is not None else not (await self.config.guild(guild).enabled())

        channel = await self.config.guild(guild).channel()
        if channel is None and target_state:
            await ctx.send(
                f"You need to set a channel with `{ctx.prefix}ncset channel` before you can enable NestedCommands."
            )
            return

        await self.config.guild(guild).enabled.set(target_state)

        if target_state:
            await ctx.send("NestedCommands is now enabled.")
        else:
            await ctx.send("NestedCommands is now disabled.")

    @ncset.command(name="channel")
    async def ncset_channel(self, ctx: commands.Context, *, channel: discord.TextChannel) -> None:
        """Sets the channel which will be used to print the output of all inner commands.

        It is highly recommended that you make this channel hidden and/or read-only to all users except Red,
        because this cog relies on the message history to function properly.
        """

        await ctx.typing()

        await self.config.guild(ctx.guild).channel.set(channel.id)

        await ctx.send(
            f"Done. I will now use the channel {channel.mention} for inner command outputs. "
            f"Ensure you also turn on NestedCommand with `{ctx.prefix}ncset toggle`."
        )

    def __init_before(self) -> None:
        """Sets up the before_invoke hook that makes this all work."""

        @self.bot.before_invoke
        async def before_any_command(ctx: commands.Context) -> None:
            if ctx.guild and await self.config.guild(ctx.guild).enabled():
                message = ctx.message
                channel_id = await self.config.guild(ctx.guild).channel()
                if channel_id is not None:
                    channel = ctx.guild.get_channel(channel_id)
                else:
                    return

                if channel is None:
                    log.error(
                        f"Failed to find channel with ID {channel_id} (server ID {ctx.guild.id}); "
                        "this likely means that the channel has been deleted"
                    )
                    return

                try:
                    top_level_commands = NestedCommands.__get_top_level_commands(message.content)
                except MismatchedParenthesesException as e:
                    log.error(
                        f"Problem resolving nested commands (server ID {ctx.guild.id}, channel ID {ctx.channel.id}, "
                        f"message ID {message.id}): {e.message}"
                    )
                    return

                replacements = {}
                for matched_text in top_level_commands:
                    inner_command = matched_text[2:-1]

                    new_message = copy.copy(message)
                    new_message.content = f"{ctx.prefix}{inner_command}"
                    new_message.channel = channel

                    await ctx.bot.process_commands(new_message)

                    inner_output = (await anext(channel.history(limit=1))).content

                    message.content = message.content.replace(matched_text, inner_output, 1)

                    replacements[matched_text] = inner_output

                    await asyncio.sleep(0.1)

                # log.info(f"ctx.kwargs 1: {ctx.kwargs}")
                # log.info(f"replacements: {replacements}")
                for name, value in ctx.kwargs.items():
                    for matched_text, inner_output in replacements.items():
                        if matched_text in value:
                            ctx.kwargs[name] = value.replace(matched_text, inner_output, 1)

                # log.info(f"ctx.kwargs 2: {ctx.kwargs}")
                # log.info(f"ctx.args: {ctx.args}")
                # log.info(f"ctx.args[1].message.content: {ctx.args[1].message.content}")
                # log.info(f"CONTENT AFTER ALL: {ctx.message.content}")

    @staticmethod
    def __get_top_level_commands(s: str) -> List[str]:
        ret = []

        depth = 0
        current = ""
        for i, c in enumerate(s):
            if c == "$" and s[i + 1] == "(":
                depth += 1

            if depth > 0:
                current += c

            if c == ")":
                depth -= 1

            if depth == 0 and current != "":
                ret.append(current)
                current = ""

        # if depth < 0:
        #     raise MismatchedParenthesesException(f"{abs(depth)} too many closing parentheses in nested commands")
        # elif depth > 0:
        #     raise MismatchedParenthesesException(f"{depth} too few closing parentheses in nested commands")

        return ret
