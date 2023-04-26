import asyncio
import datetime
import logging
import random
from typing import Optional, Union

import discord
from redbot.core import Config, checks, commands
from redbot.core.utils.chat_formatting import box, humanize_list, pagify

from .enums import WhisperType
from .errors import WhisperError
from .safemodels import SafeGuild, SafeMember

__author__ = "tmerc"

log = logging.getLogger("red.tmerc.welcome")

ENABLED = "enabled"
DISABLED = "disabled"


class Welcome(commands.Cog):
    """Announce when users join or leave a server."""

    default_join = "Welcome {member.mention} to {server.name}!"
    default_leave = "{member.name} has left {server.name}!"
    default_ban = "{member.name} has been banned from {server.name}!"
    default_unban = "{member.name} has been unbanned from {server.name}!"
    default_whisper = "Hey there {member.name}, welcome to {server.name}!"

    guild_defaults = {
        "enabled": False,
        "channel": None,
        "date": None,
        "join": {
            "enabled": True,
            "channel": None,
            "delete": False,
            "last": None,
            "counter": 0,
            "whisper": {"state": "off", "message": default_whisper},
            "messages": [default_join],
            "bot": None,
        },
        "leave": {
            "enabled": True,
            "channel": None,
            "delete": False,
            "last": None,
            "counter": 0,
            "messages": [default_leave],
        },
        "ban": {
            "enabled": True,
            "channel": None,
            "delete": False,
            "last": None,
            "counter": 0,
            "messages": [default_ban],
        },
        "unban": {
            "enabled": True,
            "channel": None,
            "delete": False,
            "last": None,
            "counter": 0,
            "messages": [default_unban],
        },
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.config = Config.get_conf(self, 86345009)
        self.config.register_guild(**self.guild_defaults)

    @commands.group(aliases=["welcomeset"], fallback="state")
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    async def welcome(self, ctx: commands.Context) -> None:
        """Get current Welcome settings."""

        await ctx.typing()

        if ctx.invoked_subcommand is None:
            guild: discord.Guild = ctx.guild
            c = await self.config.guild(guild).all()

            channel = await self.__get_channel(guild, "default")
            join_channel = await self.__get_channel(guild, "join")
            leave_channel = await self.__get_channel(guild, "leave")
            ban_channel = await self.__get_channel(guild, "ban")
            unban_channel = await self.__get_channel(guild, "unban")

            j = c["join"]
            jw = j["whisper"]
            v = c["leave"]
            b = c["ban"]
            u = c["unban"]

            whisper_message = jw["message"] if len(jw["message"]) <= 50 else jw["message"][:50] + "..."

            if await ctx.embed_requested():
                emb = discord.Embed(color=await ctx.embed_color(), title="Current Welcome Settings")
                emb.add_field(
                    name="General",
                    inline=False,
                    value=f"**Enabled:** {c['enabled']}\n**Channel:** {channel.mention}\n",
                )
                emb.add_field(
                    name="Join",
                    inline=False,
                    value=(
                        f"**Enabled:** {j['enabled']}\n"
                        f"**Channel:** {join_channel.mention}\n"
                        f"**Delete previous:** {j['delete']}\n"
                        f"**Whisper state:** {jw['state']}\n"
                        f"**Whisper message:** {whisper_message}\n"
                        f"**Messages:** {len(j['messages'])}; do `{ctx.prefix}welcomeset join msg list` for a list\n"
                        f"**Bot message:** {j['bot']}"
                    ),
                )
                emb.add_field(
                    name="Leave",
                    inline=False,
                    value=(
                        f"**Enabled:** {v['enabled']}\n"
                        f"**Channel:** {leave_channel.mention}\n"
                        f"**Delete previous:** {v['delete']}\n"
                        f"**Messages:** {len(v['messages'])}; do `{ctx.prefix}welcomeset leave msg list` for a list\n"
                    ),
                )
                emb.add_field(
                    name="Ban",
                    inline=False,
                    value=(
                        f"**Enabled:** {b['enabled']}\n"
                        f"**Channel:** {ban_channel.mention}\n"
                        f"**Delete previous:** {b['delete']}\n"
                        f"**Messages:** {len(b['messages'])}; do `{ctx.prefix}welcomeset ban msg list` for a list\n"
                    ),
                )
                emb.add_field(
                    name="Unban",
                    inline=False,
                    value=(
                        f"**Enabled:** {u['enabled']}\n"
                        f"**Channel:** {unban_channel.mention}\n"
                        f"**Delete previous:** {u['delete']}\n"
                        f"**Messages:** {len(u['messages'])}; do `{ctx.prefix}welcomeset unban msg list` for a list\n"
                    ),
                )

                await ctx.send(embed=emb)
            else:
                msg = box(
                    f"  Enabled: {c['enabled']}\n"
                    f"  Channel: {channel}\n"
                    f"  Join:\n"
                    f"    Enabled: {j['enabled']}\n"
                    f"    Channel: {join_channel}\n"
                    f"    Delete previous: {j['delete']}\n"
                    f"    Whisper:\n"
                    f"      State: {jw['state']}\n"
                    f"      Message: {whisper_message}\n"
                    f"    Messages: {len(j['messages'])}; do '{ctx.prefix}welcomeset join msg list' for a list\n"
                    f"    Bot message: {j['bot']}\n"
                    f"  Leave:\n"
                    f"    Enabled: {v['enabled']}\n"
                    f"    Channel: {leave_channel}\n"
                    f"    Delete previous: {v['delete']}\n"
                    f"    Messages: {len(v['messages'])}; do '{ctx.prefix}welcomeset leave msg list' for a list\n"
                    f"  Ban:\n"
                    f"    Enabled: {b['enabled']}\n"
                    f"    Channel: {ban_channel}\n"
                    f"    Delete previous: {b['delete']}\n"
                    f"    Messages: {len(b['messages'])}; do '{ctx.prefix}welcomeset ban msg list' for a list\n"
                    f"  Unban:\n"
                    f"    Enabled: {u['enabled']}\n"
                    f"    Channel: {unban_channel}\n"
                    f"    Delete previous: {u['delete']}\n"
                    f"    Messages: {len(u['messages'])}; do '{ctx.prefix}welcomeset unban msg list' for a list\n",
                    "Current Welcome Settings",
                )

                await ctx.send(msg)

    @welcome.command(name="toggle")
    async def welcome_toggle(self, ctx: commands.Context, on_off: bool = None) -> None:
        """Turns Welcome on or off.

        If `on_off` is not provided, the state will be flipped.
        """

        guild = ctx.guild
        target_state = on_off if on_off is not None else not (await self.config.guild(guild).enabled())

        await self.config.guild(guild).enabled.set(target_state)

        await ctx.send(f"Welcome is now {ENABLED if target_state else DISABLED}.")

    @welcome.command(name="channel")
    async def welcome_channel(self, ctx: commands.Context, channel: discord.TextChannel) -> None:
        """Sets the channel to be used for event notices."""

        if not Welcome.__can_speak_in(channel):
            await ctx.send(
                f"I do not have permission to send messages in {channel.mention}. "
                "Check your permission settings and try again."
            )
            return

        guild = ctx.guild
        await self.config.guild(guild).channel.set(channel.id)

        await ctx.send(f"I will now send event notices to {channel.mention}.")

    @welcome.group(name="join")
    async def welcome_join(self, ctx: commands.Context) -> None:
        """Change settings for join notices."""

        pass

    @welcome_join.command(name="toggle")
    async def welcome_join_toggle(self, ctx: commands.Context, on_off: bool = None) -> None:
        """Turns join notices on or off.

        If `on_off` is not provided, the state will be flipped.
        """

        await self.__toggle(ctx, on_off, "join")

    @welcome_join.command(name="channel")
    async def welcome_join_channel(self, ctx: commands.Context, channel: discord.TextChannel = None) -> None:
        """Sets the channel to be used specifically for join notices.

        If `channel` is not provided, the join-specific channel is cleared.
        """

        await self.__set_channel(ctx, channel, "join")

    @welcome_join.command(name="toggledelete")
    async def welcome_join_toggledelete(self, ctx: commands.Context, on_off: bool = None) -> None:
        """Turns deletion of previous join notice on or off.

        If `on_off` is not provided, the state will be flipped.
        """

        await self.__toggledelete(ctx, on_off, "join")

    @welcome_join.group(name="whisper")
    async def welcome_join_whisper(self, ctx: commands.Context) -> None:
        """Change settings for join whispers."""

        pass

    @welcome_join_whisper.command(name="type")
    async def welcome_join_whisper_type(self, ctx: commands.Context, choice: WhisperType) -> None:
        """Set if a DM is sent to the new member.

        Options:
          off - no DM is sent
          only - only send a DM to the member, do not send a message to the channel
          both - send a DM to the member and a message to the channel
          fall - send a DM to the member, if it fails send the whisper message to the channel instead
        """

        guild = ctx.guild
        whisper_type = choice.value
        channel = await self.__get_channel(ctx.guild, "join")

        await self.config.guild(guild).join.whisper.state.set(whisper_type)

        if choice == WhisperType.OFF:
            await ctx.send(f"I will no longer DM new members, and will send a notice to {channel.mention}.")
        elif choice == WhisperType.ONLY:
            await ctx.send(f"I will now only DM new members, and will not send a notice to {channel.mention}.")
        elif choice == WhisperType.BOTH:
            await ctx.send(f"I will now send a DM to new members, as well as send a notice to {channel.mention}.")
        elif choice == WhisperType.FALLBACK:
            await ctx.send(
                f"I will now send a DM to new members, and if that fails I will send the message to {channel.mention}."
            )

    @welcome_join_whisper.command(name="message", aliases=["msg"])
    async def welcome_join_whisper_message(self, ctx: commands.Context, *, msg_format: str) -> None:
        """Set the message DM'd to new members when they join.

        Allows for the following customizations:
          `{member}` is the member who joined
          `{server}` is the server
        """

        await self.config.guild(ctx.guild).join.whisper.message.set(msg_format)

        await ctx.send("I will now use that message format when whispering new members, if whisper is enabled.")

    @welcome_join.group(name="message", aliases=["msg"])
    async def welcome_join_message(self, ctx: commands.Context) -> None:
        """Manage join message formats."""

        pass

    @welcome_join_message.command(name="add")
    async def welcome_join_message_add(self, ctx: commands.Context, *, msg_format: str) -> None:
        """Add a new join message format to be chosen.

        Allows for the following customizations:
          `{member}` is the new member
          `{server}` is the server
          `{count}` is the number of members who have joined today
          `{plural}` is an 's' if `count` is not 1, and nothing if it is
          `{roles}` is a list of all the roles that the member has at the time

        For example:
          {member.mention}... What are you doing here???
          {server.name} has a new member! {member.name}#{member.discriminator} - {member.id}
          Someone new has joined! Who is it?! D: IS HE HERE TO HURT US?!
        """

        await self.__message_add(ctx, msg_format, "join")

    @welcome_join_message.command(name="delete", aliases=["del"])
    async def welcome_join_message_delete(self, ctx: commands.Context) -> None:
        """Delete an existing join message format from the list."""

        await self.__message_delete(ctx, "join")

    @welcome_join_message.command(name="list", aliases=["ls"])
    async def welcome_join_message_list(self, ctx: commands.Context) -> None:
        """Lists the available join message formats."""

        await self.__message_list(ctx, "join")

    @welcome_join.command(name="botmessage", aliases=["botmsg"])
    async def welcome_join_botmessage(self, ctx: commands.Context, *, msg_format: str = None) -> None:
        """Sets the message format to use for join notices for bots.

        Supply no format to use normal join message formats for bots.
        Allows for the following customizations:
          `{bot}` is the bot
          `{server}` is the server
          `{count}` is the number of members who have joined today
          `{plural}` is an 's' if `count` is not 1, and nothing if it is

        For example:
          {bot.mention} beep boop.
        """

        await self.config.guild(ctx.guild).join.bot.set(msg_format)

        if msg_format is not None:
            await ctx.send("Bot join message format set. I will now greet bots with that message.")
        else:
            await ctx.send("Bot join message format removed. I will now greet bots like normal members.")

    @welcome.group(name="leave")
    async def welcome_leave(self, ctx: commands.Context) -> None:
        """Change settings for leave notices."""

        pass

    @welcome_leave.command(name="toggle")
    async def welcome_leave_toggle(self, ctx: commands.Context, on_off: bool = None) -> None:
        """Turns leave notices on or off.

        If `on_off` is not provided, the state will be flipped.
        """

        await self.__toggle(ctx, on_off, "leave")

    @welcome_leave.command(name="channel")
    async def welcome_leave_channel(self, ctx: commands.Context, channel: discord.TextChannel = None) -> None:
        """Sets the channel to be used specifically for leave notices.

        If `channel` is not provided, the leave-specific channel is cleared.
        """

        await self.__set_channel(ctx, channel, "leave")

    @welcome_leave.command(name="toggledelete")
    async def welcome_leave_toggledelete(self, ctx: commands.Context, on_off: bool = None) -> None:
        """Turns deletion of previous leave notice on or off.

        If `on_off` is not provided, the state will be flipped.
        """

        await self.__toggledelete(ctx, on_off, "leave")

    @welcome_leave.group(name="message", aliases=["msg"])
    async def welcome_leave_message(self, ctx: commands.Context) -> None:
        """Manage leave message formats."""

        pass

    @welcome_leave_message.command(name="add")
    async def welcome_leave_message_add(self, ctx: commands.Context, *, msg_format: str) -> None:
        """Add a new leave message format to be chosen.

        Allows for the following customizations:
          `{member}` is the member who left
          `{server}` is the server
          `{count}` is the number of members who have left today
          `{plural}` is an 's' if `count` is not 1, and nothing if it is
          `{roles}` is a list of all the roles that the member has at the time

        For example:
          {member.name}... Why did you leave???
          {server.name} has lost a member! {member.name}#{member.discriminator} - {member.id}
          Someone has left... Aww... Bye :(
        """

        await self.__message_add(ctx, msg_format, "leave")

    @welcome_leave_message.command(name="delete", aliases=["del"])
    async def welcome_leave_message_delete(self, ctx: commands.Context) -> None:
        """Delete an existing leave message format from the list."""

        await self.__message_delete(ctx, "leave")

    @welcome_leave_message.command(name="list", aliases=["ls"])
    async def welcome_leave_message_list(self, ctx: commands.Context) -> None:
        """Lists the available leave message formats."""

        await self.__message_list(ctx, "leave")

    @welcome.group(name="ban")
    async def welcome_ban(self, ctx: commands.Context) -> None:
        """Change settings for ban notices."""

        pass

    @welcome_ban.command(name="toggle")
    async def welcome_ban_toggle(self, ctx: commands.Context, on_off: bool = None) -> None:
        """Turns ban notices on or off.

        If `on_off` is not provided, the state will be flipped.
        """

        await self.__toggle(ctx, on_off, "ban")

    @welcome_ban.command(name="channel")
    async def welcome_ban_channel(self, ctx: commands.Context, channel: discord.TextChannel = None) -> None:
        """Sets the channel to be used specifically for ban notices.

        If `channel` is not provided, the ban-specific channel is cleared.
        """

        await self.__set_channel(ctx, channel, "ban")

    @welcome_ban.command(name="toggledelete")
    async def welcome_ban_toggledelete(self, ctx: commands.Context, on_off: bool = None) -> None:
        """Turns deletion of previous ban notice on or off.

        If `on_off` is not provided, the state will be flipped.
        """

        await self.__toggledelete(ctx, on_off, "ban")

    @welcome_ban.group(name="message", aliases=["msg"])
    async def welcome_ban_message(self, ctx: commands.Context) -> None:
        """Manage ban message formats."""

        pass

    @welcome_ban_message.command(name="add")
    async def welcome_ban_message_add(self, ctx: commands.Context, *, msg_format: str) -> None:
        """Add a new ban message format to be chosen.

        Allows for the following customizations:
          `{member}` is the banned member
          `{server}` is the server
          `{count}` is the number of members who have been banned today
          `{plural}` is an 's' if `count` is not 1, and nothing if it is
          `{roles}` is a list of all the roles that the member has at the time

        For example:
          {member.name} was banned... What did you do???
          A member of {server.name} has been banned! {member.name}#{member.discriminator} - {member.id}
          Someone has been banned. Good riddance!
        """

        await self.__message_add(ctx, msg_format, "ban")

    @welcome_ban_message.command(name="delete", aliases=["del"])
    async def welcome_ban_message_delete(self, ctx: commands.Context) -> None:
        """Delete an existing ban message format from the list."""

        await self.__message_delete(ctx, "ban")

    @welcome_ban_message.command(name="list", aliases=["ls"])
    async def welcome_ban_message_list(self, ctx: commands.Context) -> None:
        """Lists the available ban message formats."""

        await self.__message_list(ctx, "ban")

    @welcome.group(name="unban")
    async def welcome_unban(self, ctx: commands.Context) -> None:
        """Change settings for unban notices."""

        pass

    @welcome_unban.command(name="toggle")
    async def welcome_unban_toggle(self, ctx: commands.Context, on_off: bool = None) -> None:
        """Turns unban notices on or off.

        If `on_off` is not provided, the state will be flipped.
        """

        await self.__toggle(ctx, on_off, "unban")

    @welcome_unban.command(name="channel")
    async def welcome_unban_channel(self, ctx: commands.Context, channel: discord.TextChannel = None) -> None:
        """Sets the channel to be used specifically for unban notices.

        If `channel` is not provided, the unban-specific channel is cleared.
        """

        await self.__set_channel(ctx, channel, "unban")

    @welcome_unban.command(name="toggledelete")
    async def welcome_unban_toggledelete(self, ctx: commands.Context, on_off: bool = None) -> None:
        """Turns deletion of previous unban notice on or off.

        If `on_off` is not provided, the state will be flipped.
        """

        await self.__toggledelete(ctx, on_off, "unban")

    @welcome_unban.group(name="message", aliases=["msg"])
    async def welcome_unban_message(self, ctx: commands.Context) -> None:
        """Manage unban message formats."""

        pass

    @welcome_unban_message.command(name="add")
    async def welcome_unban_message_add(self, ctx: commands.Context, *, msg_format: str) -> None:
        """Add a new unban message format to be chosen.

        Allows for the following customizations:
          `{member}` is the unbanned member
          `{server}` is the server
          `{count}` is the number of members who have been unbanned today
          `{plural}` is an 's' if `count` is not 1, and nothing if it is
          `{roles}` is a list of all the roles that the member has at the time

        For example:
          {member.name} was unbanned... Did you learn your lesson???
          A member of {server.name} has been unbanned! {member.name}#{member.discriminator} - {member.id}
          Someone has been unbanned. Don't waste your second chance!
        """

        await self.__message_add(ctx, msg_format, "unban")

    @welcome_unban_message.command(name="delete", aliases=["del"])
    async def welcome_unban_message_delete(self, ctx: commands.Context) -> None:
        """Delete an existing unban message format from the list."""

        await self.__message_delete(ctx, "unban")

    @welcome_unban_message.command(name="list", aliases=["ls"])
    async def welcome_unban_message_list(self, ctx: commands.Context) -> None:
        """Lists the available unban message formats."""

        await self.__message_list(ctx, "unban")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """Listens for member joins."""

        guild: discord.Guild = member.guild
        guild_settings = self.config.guild(guild)

        if await guild_settings.enabled() and await guild_settings.join.enabled():
            # join notice should be sent
            message_format: Optional[str] = None
            if member.bot:
                # bot
                message_format = await guild_settings.join.bot()

            else:
                whisper_type: str = await guild_settings.join.whisper.state()
                if whisper_type != "off":
                    try:
                        await self.__dm_user(member)
                    except WhisperError:
                        if whisper_type == "fall":
                            message_format = await self.config.guild(member.guild).join.whisper.message()
                            await self.__handle_event(guild, member, "join", message_format=message_format)
                            return

                    if whisper_type == "only" or whisper_type == "fall":
                        # we're done here
                        return

            await self.__handle_event(guild, member, "join", message_format=message_format)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        """Listens for member leaves."""

        await self.__handle_event(member.guild, member, "leave")

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, member: discord.Member) -> None:
        """Listens for user bans."""

        await self.__handle_event(guild, member, "ban")

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User) -> None:
        """Listens for user unbans."""

        await self.__handle_event(guild, user, "unban")

    #
    # concrete handlers for settings changes and events
    #

    async def __toggle(self, ctx: commands.Context, on_off: bool, event: str) -> None:
        """Handler for setting toggles."""

        guild: discord.Guild = ctx.guild
        target_state = on_off if on_off is not None else not (await self.config.guild(guild).get_attr(event).enabled())

        await self.config.guild(guild).get_attr(event).enabled.set(target_state)

        await ctx.send(f"{event.capitalize()} notices are now {ENABLED if target_state else DISABLED}.")

    async def __set_channel(self, ctx: commands.Context, channel: discord.TextChannel, event: str) -> None:
        """Handler for setting channels."""

        guild: discord.Guild = ctx.guild

        store_this = channel.id if channel is not None else None

        await self.config.guild(guild).get_attr(event).channel.set(store_this)

        if store_this is not None:
            await ctx.send(f"I will now send {event} notices to {channel.mention}.")
        else:
            default_channel = await self.__get_channel(guild, "default")
            await ctx.send(f"I will now send {event} messages to the default channel, {default_channel.mention}.")

    async def __toggledelete(self, ctx: commands.Context, on_off: bool, event: str) -> None:
        """Handler for setting delete toggles."""

        guild: discord.Guild = ctx.guild
        target_state = on_off if on_off is not None else not (await self.config.guild(guild).get_attr(event).delete())

        await self.config.guild(guild).get_attr(event).delete.set(target_state)

        await ctx.send(f"Deletion of previous {event} notice is now {ENABLED if target_state else DISABLED}")

    async def __message_add(self, ctx: commands.Context, msg_format: str, event: str) -> None:
        """Handler for adding message formats."""

        guild: discord.Guild = ctx.guild

        async with self.config.guild(guild).get_attr(event).messages() as messages:
            messages.append(msg_format)

        await ctx.send(f"New message format for {event} notices added.")

    async def __message_delete(self, ctx: commands.Context, event: str) -> None:
        """Handler for deleting message formats."""

        guild: discord.Guild = ctx.guild

        async with self.config.guild(guild).get_attr(event).messages() as messages:
            if len(messages) == 1:
                await ctx.send(f"I only have one {event} message format, so I can't let you delete it.")
                return

            await self.__message_list(ctx, event)
            await ctx.send(f"Please enter the number of the {event} message format you wish to delete.")

            try:
                num = await Welcome.__get_number_input(ctx, len(messages))
            except asyncio.TimeoutError:
                await ctx.send(f"Okay, I won't remove any of the {event} message formats.")
                return
            else:
                removed = messages.pop(num - 1)

        await ctx.send(f"Done. This {event} message format was deleted:\n`{removed}`")

    async def __message_list(self, ctx: commands.Context, event: str) -> None:
        """Handler for listing message formats."""

        guild: discord.Guild = ctx.guild

        msg = f"{event.capitalize()} message formats:\n"
        messages = await self.config.guild(guild).get_attr(event).messages()
        for n, m in enumerate(messages, start=1):
            msg += f"  {n}. {m}\n"

        for page in pagify(msg, shorten_by=20):
            await ctx.send(box(page))

    async def __handle_event(
        self, guild: discord.guild, user: Union[discord.Member, discord.User], event: str, *, message_format=None
    ) -> None:
        """Handler for actual events."""

        guild_settings = self.config.guild(guild)

        # always increment, even if we aren't sending a notice
        await self.__increment_count(guild, event)

        if await guild_settings.enabled():
            settings = await guild_settings.get_attr(event).all()
            if settings["enabled"]:
                # notices for this event are enabled

                if settings["delete"] and settings["last"] is not None:
                    # we need to delete the previous message
                    await self.__delete_message(guild, settings["last"], event)
                    # regardless of success, remove reference to that message
                    await guild_settings.get_attr(event).last.set(None)

                # send a notice to the channel
                new_message = await self.__send_notice(guild, user, event, message_format=message_format)
                # store it for (possible) deletion later
                await guild_settings.get_attr(event).last.set(new_message and new_message.id)

    async def __get_channel(self, guild: discord.Guild, event: str) -> discord.TextChannel:
        """Gets the best text channel to use for event notices.

        Order of priority:
        1. User-defined channel
        2. Guild's system channel (if bot can speak in it)
        3. First channel that the bot can speak in
        """

        channel = None

        if event == "default":
            channel_id: int = await self.config.guild(guild).channel()
        else:
            channel_id = await self.config.guild(guild).get_attr(event).channel()

        if channel_id is not None:
            channel = guild.get_channel(channel_id)

        if channel is None or not Welcome.__can_speak_in(channel):
            channel = guild.get_channel(await self.config.guild(guild).channel())

        if channel is None or not Welcome.__can_speak_in(channel):
            channel = guild.system_channel

        if channel is None or not Welcome.__can_speak_in(channel):
            for ch in guild.text_channels:
                if Welcome.__can_speak_in(ch):
                    channel = ch
                    break

        return channel

    async def __delete_message(self, guild: discord.Guild, message_id: int, event: str) -> None:
        """Attempts to delete the message with the given ID."""

        try:
            await (await (await self.__get_channel(guild, event)).fetch_message(message_id)).delete()
        except discord.NotFound:
            log.warning("Failed to delete message (ID {message_id}): not found")
        except discord.Forbidden:
            log.warning("Failed to delete message (ID {message_id}): insufficient permissions")
        except discord.DiscordException:
            log.warning("Failed to delete message (ID {message_id})")

    async def __send_notice(
        self, guild: discord.guild, user: Union[discord.Member, discord.User], event: str, *, message_format=None
    ) -> Optional[discord.Message]:
        """Sends the notice for the event."""

        format_str = message_format or await self.__get_random_message_format(guild, event)

        count = await self.config.guild(guild).get_attr(event).counter()
        plural = ""
        if count and count != 1:
            plural = "s"

        channel = await self.__get_channel(guild, event)

        role_str: str = ""
        if isinstance(user, discord.Member):
            roles = [r.name for r in user.roles if r.name != "@everyone"]
            if len(roles) > 0:
                role_str = humanize_list(roles)

        try:
            return await channel.send(
                format_str.format(
                    member=SafeMember(user),
                    server=SafeGuild(guild),
                    bot=SafeMember(user),
                    count=count or "",
                    plural=plural,
                    roles=role_str,
                )
            )
        except discord.Forbidden:
            log.error(
                f"Failed to send {event} message to channel ID {channel.id} (server ID {guild.id}): "
                "insufficient permissions"
            )
            return None
        except discord.DiscordException:
            log.error(f"Failed to send {event} message to channel ID {channel.id} (server ID {guild.id})")
            return None

    async def __get_random_message_format(self, guild: discord.guild, event: str) -> str:
        """Gets a random message for event of type event."""

        async with self.config.guild(guild).get_attr(event).messages() as messages:
            return random.choice(messages)

    async def __increment_count(self, guild: discord.Guild, event: str) -> None:
        """Increments the counter for <event>s today. Handles date changes."""

        guild_settings = self.config.guild(guild)

        if await guild_settings.date() is None:
            await guild_settings.date.set(Welcome.__today())

        if Welcome.__today() > await guild_settings.date():
            await guild_settings.date.set(Welcome.__today())
            await guild_settings.get_attr(event).counter.set(0)

        count: int = await guild_settings.get_attr(event).counter()
        await guild_settings.get_attr(event).counter.set(count + 1)

    async def __dm_user(self, member: discord.Member) -> None:
        """Sends a DM to the user with a filled-in message_format."""

        message_format = await self.config.guild(member.guild).join.whisper.message()

        try:
            await member.send(message_format.format(member=member, server=member.guild))
        except discord.Forbidden:
            log.error(
                f"Failed to send DM to member ID {member.id} (server ID {member.guild.id}): insufficient permissions"
            )
            raise WhisperError()
        except discord.DiscordException:
            log.error(f"Failed to send DM to member ID {member.id} (server ID {member.guild.id})")
            raise WhisperError()

    @staticmethod
    async def __get_number_input(ctx: commands.Context, maximum: int, minimum: int = 0) -> int:
        """Gets a number from the user, minimum < x <= maximum."""

        author = ctx.author
        channel = ctx.channel

        def check(m: discord.Message) -> bool:
            try:
                num = int(m.content)
            except ValueError:
                return False

            return num is not None and minimum < num <= maximum and m.author == author and m.channel == channel

        try:
            msg = await ctx.bot.wait_for("message", check=check, timeout=15.0)
        except asyncio.TimeoutError:
            raise
        else:
            return int(msg.content)

    @staticmethod
    def __can_speak_in(channel: discord.TextChannel) -> bool:
        """Indicates whether the bot has permission to speak in channel."""

        return channel.permissions_for(channel.guild.me).send_messages

    @staticmethod
    def __today() -> int:
        """Gets today's date in ordinal form."""

        return datetime.date.today().toordinal()
