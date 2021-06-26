import asyncio
import datetime
import dateparser
import discord
import logging
import re
import shlex
from typing import Callable, Dict, List, Optional, Tuple, Union

from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.utils.common_filters import normalize_smartquotes

from .errors import UserCancelledCreation, UserSkippedValue
from .event import Event
from .utils import find_index

__author__ = "tmerc"

log = logging.getLogger("red.tmerc.communitycalendar")


class CommunityCalendar(commands.Cog):
    """Create events for your community."""

    guild_defaults = {"id": 1, "events": []}

    def __init__(self, bot: Red, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = Config.get_conf(self, 68950810)
        self.config.register_guild(**self.guild_defaults)

        self.bot: Red = bot

        self.events: Dict[int, List[Event]] = {}
        self.bot.loop.create_task(self.__load_events())

    @commands.group(aliases=["ccal", "cal", "calendar"])
    @commands.guild_only()
    async def comcal(self, ctx: commands.Context) -> None:
        """Use Community Calendar."""

        if ctx.invoked_subcommand is not None:
            await ctx.trigger_typing()

    @comcal.command(name="clear")
    @commands.is_owner()
    async def comcal_clear(self, ctx: commands.Context) -> None:
        """[DEBUG ONLY] Clear config."""

        await self.config.guild(ctx.guild).clear()
        await ctx.send("Cleared.")

    @comcal.command(name="create")
    async def comcal_create(self, ctx: commands.Context) -> None:
        """Create a new event."""

        try:
            event = await self.__create_interactive(ctx)
        except asyncio.TimeoutError:
            await ctx.send("Timed out. Try again, and next time be quicker!")
            return
        except UserCancelledCreation:
            await ctx.send("Event creation cancelled.")
            return

        await CommunityCalendar.__delete_message(ctx.message)

        event.activate(loop=self.bot.loop)
        await event.send_invites(loop=self.bot.loop)

        await self.__add_event(event)
        await self.__save_event(event)

    @comcal.command(name="close", aliases=["cancel"])
    async def comcal_close(self, ctx: commands.Context, event_id: int) -> None:
        """Cancel an event.

        Only accessible to the creator of the event and Red mods (and above).
        """

        guild_events = self.events[ctx.guild.id]

        event: Event = discord.utils.get(guild_events, id=event_id)
        if event is None:
            await ctx.send(f"I could not find an event with ID {event_id}.")
            return

        if not await event.is_editable_by(self.bot, ctx.author):
            await ctx.send("You are not allowed to close this event.")
            return

        if not event.open:
            await ctx.send(f"I cannot close event {event_id}, **{event.name}**, because it is already closed.")
            return

        await event.close()
        await self.__save_event(event)

        await ctx.send(f"Cancelled event {event_id}, **{event.name}**.")

    @comcal.command(name="message", aliases=["msg", "alert", "ping"])
    async def comcal_message(self, ctx: commands.Context, event_id: int, *, message: str) -> None:
        """Send a message to all the "going" and "maybe" respondents of an event.

        Only accessible to the creator of the event and Red mods (and above).
        """

        guild_events = self.events[ctx.guild.id]

        event: Event = discord.utils.get(guild_events, id=event_id)
        if event is None:
            await ctx.send(f"I could not find an event with ID {event_id}.")
            return

        if not await event.is_editable_by(self.bot, ctx.author):
            await ctx.send("You are not allowed to message the attendees of this event.")
            return

        await event.message_attendees(message, ctx.author, include_maybes=True)
        await ctx.send("Sent.")

    @comcal.command(name="join", aliases=["going"])
    async def comcal_join(self, ctx: commands.Context, event_id: int) -> None:
        """Join an event.

        This is functionally the same as clicking the ✅ reaction on the event.
        """

        guild_events = self.events[ctx.guild.id]

        event: Event = discord.utils.get(guild_events, id=event_id)
        if event is None:
            await ctx.send(f"I could not find an event with ID {event_id}.")
            return

        if not event.open:
            await ctx.send(f"You cannot join event {event_id}, **{event.name}**, because it is closed.")
            return

        await event.add_going(ctx.author)
        await self.__save_event(event)

        await ctx.send(f"You have joined event {event_id}, **{event.name}**.")

    @comcal.command(name="maybe")
    async def comcal_maybe(self, ctx: commands.Context, event_id: int) -> None:
        """Join an event as a maybe.

        This is functionally the same as clicking the ❔ reaction on the event.
        """

        guild_events = self.events[ctx.guild.id]

        event: Event = discord.utils.get(guild_events, id=event_id)
        if event is None:
            await ctx.send(f"I could not find an event with ID {event_id}.")
            return

        if not event.open:
            await ctx.send(f"You cannot join event {event_id}, **{event.name}**, because it is closed.")
            return

        await event.add_maybe(ctx.author)
        await self.__save_event(event)

        await ctx.send(f"You have responded maybe to event {event_id}, **{event.name}**.")

    @comcal.command(name="decline", aliases=["leave"])
    async def comcal_decline(self, ctx: commands.Context, event_id: int) -> None:
        """Decline (or leave) an event.

        This is functionally the same as clicking the ❌ reaction on the event.
        """

        guild_events = self.events[ctx.guild.id]

        event: Event = discord.utils.get(guild_events, id=event_id)
        if event is None:
            await ctx.send(f"I could not find an event with ID {event_id}.")
            return

        if not event.open:
            await ctx.send(f"You cannot decline event {event_id}, **{event.name}**, because it is closed.")
            return

        await event.add_not_going(ctx.author)
        await self.__save_event(event)

        await ctx.send(f"You have declined event {event_id}, **{event.name}**.")

    @comcal.command(name="invite", aliases=["add"])
    async def comcal_invite(self, ctx: commands.Context, event_id: int) -> None:
        """Invite additional members or roles to an existing event.

        Only accessible to the creator of the event and Red mods (and above).
        """

        guild: discord.Guild = ctx.guild
        member: discord.Member = ctx.author

        evs = self.events[guild.id]
        event: Event = discord.utils.get(evs, id=event_id)

        if event is None:
            await ctx.send(f"I could not find an event with ID {event_id}.")
            return

        if not await event.is_editable_by(self.bot, member):
            await ctx.send("You are not allowed to invite people to this event.")
            return

        if not event.open:
            await ctx.send(f"You cannot invite people to event {event_id}, **{event.name}**, because it is closed.")
            return

        try:
            new_members, new_roles = await CommunityCalendar.__get_invitees(ctx)
        except (asyncio.TimeoutError, UserCancelledCreation, UserSkippedValue):
            await ctx.send("No changes made.")
            return

        await ctx.trigger_typing()
        await event.add_invitees(new_members, new_roles, loop=self.bot.loop)
        await self.__save_event(event)
        await event.refresh()

        await ctx.send("Invites sent.")

    @comcal.group(name="edit")
    async def comcal_edit(self, ctx: commands.Context) -> None:
        """Edit existing events.

        Only accessible to the creator of the event and Red mods (and above).
        """

        pass

    @comcal_edit.command(name="name")
    async def comcal_edit_name(self, ctx: commands.Context, event_id: int) -> None:
        """Edit the name of an event."""

        guild: discord.Guild = ctx.guild
        member: discord.Member = ctx.author

        evs = self.events[guild.id]
        event: Event = discord.utils.get(evs, id=event_id)

        if event is None:
            await ctx.send(f"I could not find an event with ID {event_id}.")
            return

        if not await event.is_editable_by(self.bot, member):
            await ctx.send("You are not allowed to edit this event.")
            return

        if not event.open:
            await ctx.send(f"You cannot edit event {event_id}, **{event.name}**, because it is closed.")
            return

        try:
            event.name = await CommunityCalendar.__get_name(ctx)
        except (asyncio.TimeoutError, UserCancelledCreation):
            await ctx.send("No changes made.")
            return

        await ctx.trigger_typing()
        await self.__save_event(event)
        await event.refresh()

        await ctx.send("Event name has been updated.")

    @comcal_edit.command(name="description")
    async def comcal_edit_description(self, ctx: commands.Context, event_id: int) -> None:
        """Edit the description of an event."""

        guild: discord.Guild = ctx.guild
        member: discord.Member = ctx.author

        evs = self.events[guild.id]
        event: Event = discord.utils.get(evs, id=event_id)

        if event is None:
            await ctx.send(f"I could not find an event with ID {event_id}.")
            return

        if not await event.is_editable_by(self.bot, member):
            await ctx.send("You are not allowed to edit this event.")
            return

        if not event.open:
            await ctx.send(f"You cannot edit event {event_id}, **{event.name}**, because it is closed.")
            return

        try:
            event.description = await CommunityCalendar.__get_description(ctx)
        except (asyncio.TimeoutError, UserCancelledCreation):
            await ctx.send("No changes made.")
            return
        except UserSkippedValue:
            event.description = ""

        await ctx.trigger_typing()
        await self.__save_event(event)
        await event.refresh()

        await ctx.send("Event description has been updated.")

    @comcal_edit.command(name="when", aliases=["time"])
    async def comcal_edit_when(self, ctx: commands.Context, event_id: int) -> None:
        """Edit the date/time of an event."""

        guild: discord.Guild = ctx.guild
        member: discord.Member = ctx.author

        evs = self.events[guild.id]
        event: Event = discord.utils.get(evs, id=event_id)

        if event is None:
            await ctx.send(f"I could not find an event with ID {event_id}.")
            return

        if not await event.is_editable_by(self.bot, member):
            await ctx.send("You are not allowed to edit this event.")
            return

        if not event.open:
            await ctx.send(f"You cannot edit event {event_id}, **{event.name}**, because it is closed.")
            return

        try:
            event.name = await self.__get_when(ctx)
        except (asyncio.TimeoutError, UserCancelledCreation):
            await ctx.send("No changes made.")
            return

        await ctx.trigger_typing()
        await self.__save_event(event)
        await event.refresh()

        await ctx.send("Event date/time has been updated.")

    @comcal_edit.command(name="limit")
    async def comcal_edit_limit(self, ctx: commands.Context, event_id: int) -> None:
        """Edit the attendee limit of an event."""

        guild: discord.Guild = ctx.guild
        member: discord.Member = ctx.author

        evs = self.events[guild.id]
        event: Event = discord.utils.get(evs, id=event_id)

        if event is None:
            await ctx.send(f"I could not find an event with ID {event_id}.")
            return

        if not await event.is_editable_by(self.bot, member):
            await ctx.send("You are not allowed to edit this event.")
            return

        if not event.open:
            await ctx.send(f"You cannot edit event {event_id}, **{event.name}**, because it is closed.")
            return

        try:
            event.limit = await self.__get_limit(ctx)
        except (asyncio.TimeoutError, UserCancelledCreation):
            await ctx.send("No changes made.")
            return
        except UserSkippedValue:
            event.limit = 0

        await ctx.trigger_typing()
        await self.__save_event(event)
        await event.refresh()

        await ctx.send("Event attendee limit has been updated.")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: Union[discord.Member, discord.User]) -> None:
        """Handler for when reactions are added."""

        # first, try to short-circuit
        if user.bot:
            return
        if reaction.emoji not in Event.RESPONSE_EMOJIS:
            return
        if isinstance(user, discord.Member) and user.guild.id not in self.events:
            return
        if len(reaction.message.embeds) != 1:
            return

        # okay, try to find it!
        # we can extract the event ID from the embed (tricky!)
        message: discord.Message = reaction.message
        embed: discord.Embed = message.embeds[0]
        event_id = int(re.search(r"\d+", embed.footer.text).group())

        guild: Optional[discord.Guild] = None
        event: Optional[Event] = None
        member: Optional[discord.Member] = None
        if isinstance(user, discord.Member):
            # can immediately filter down to the guild level
            evs = self.events[user.guild.id]
            guild = user.guild
            event = discord.utils.get(evs, id=event_id)
            member = user
        else:
            for guild_id, events in self.events.items():
                matching_event: Event = discord.utils.get(events, id=event_id)
                if matching_event is None:
                    continue
                matching_message = discord.utils.get(matching_event.messages, id=message.id)
                if matching_message is None:
                    continue
                guild = self.bot.get_guild(guild_id)
                event = matching_event
                member = guild.get_member(user.id)

        if guild is None or event is None:
            # failed to find it
            log.warning(f"Failed to resolve event for reaction from user {user} (ID {user.id})")
            return

        emoji = reaction.emoji
        if emoji == Event.GOING_EMOJI:
            await event.add_going(member)
        elif emoji == Event.MAYBE_EMOJI:
            await event.add_maybe(member)
        elif emoji == Event.NOT_GOING_EMOJI:
            await event.add_not_going(member)

        try:
            await reaction.remove(user)
        except discord.DiscordException:
            pass

        await self.__save_event(event)

    async def __create_interactive(self, ctx: commands.Context) -> Event:
        """Interactively create a new event."""

        cancel_msg = f"Reply with `{ctx.prefix}cancel` at any time to abort event creation."

        welcome_msg = await ctx.send("Creating a new event.")
        await ctx.trigger_typing()

        new_event = Event(
            **{
                "id": await self.__next_id(ctx.guild),
                "creator": ctx.author,
                "guild": ctx.guild,
                "messages": [welcome_msg],
                "going": {ctx.author},
            }
        )

        await new_event.refresh(content=cancel_msg)

        # name
        try:
            new_event.name = await CommunityCalendar.__get_name(ctx)
        except (asyncio.TimeoutError, UserCancelledCreation):
            await CommunityCalendar.__delete_message(welcome_msg)
            raise

        await ctx.trigger_typing()
        await new_event.refresh(content=cancel_msg)

        # description
        try:
            new_event.description = await CommunityCalendar.__get_description(ctx)
        except UserSkippedValue:
            pass
        except (asyncio.TimeoutError, UserCancelledCreation):
            await CommunityCalendar.__delete_message(welcome_msg)
            raise

        await ctx.trigger_typing()
        await new_event.refresh(content=cancel_msg)

        # when
        try:
            new_event.when = await self.__get_when(ctx)
        except (asyncio.TimeoutError, UserCancelledCreation):
            await CommunityCalendar.__delete_message(welcome_msg)
            raise

        await ctx.trigger_typing()
        await new_event.refresh(content=cancel_msg)

        # limit
        try:
            new_event.limit = await self.__get_limit(ctx)
        except UserSkippedValue:
            pass
        except (asyncio.TimeoutError, UserCancelledCreation):
            await CommunityCalendar.__delete_message(welcome_msg)
            raise

        await ctx.trigger_typing()
        await new_event.refresh(content=cancel_msg)

        # invitees
        try:
            new_members, new_roles = await CommunityCalendar.__get_invitees(ctx)
            await new_event.add_invitees(new_members, new_roles, send_invites=False)
        except UserSkippedValue:
            pass
        except (asyncio.TimeoutError, UserCancelledCreation):
            await CommunityCalendar.__delete_message(welcome_msg)
            raise

        await new_event.refresh()
        return new_event

    async def __add_event(self, event: Event) -> None:
        guild_id = event.guild.id

        if guild_id not in self.events:
            self.events[guild_id] = [event]
        else:
            self.events[guild_id].append(event)

    async def __next_id(self, guild: discord.Guild) -> int:
        guild_settings = self.config.guild(guild)

        next_id = await guild_settings.id()
        await guild_settings.id.set(next_id + 1)

        return next_id

    async def __save_event(self, event: Event) -> None:
        """Saves the given event to Config."""

        as_dict = event.to_dict()

        async with self.config.guild(event.guild).events() as events:
            try:
                idx = find_index(lambda x: x["id"] == event.id, events)
            except ValueError:
                events.append(as_dict)
            else:
                events[idx] = as_dict

    async def __load_events(self) -> None:
        """Load events from storage on startup."""

        # { guild_id: <config> }
        saved = await self.config.all_guilds()

        for (key, value) in saved.items():
            resolved: List[Event] = []
            for ev in value["events"]:
                try:
                    e = await Event.from_dict(self.bot, ev)
                    await e.refresh()
                    resolved.append(e)
                except discord.DiscordException:
                    log.warning(f"Failed to parse guild for saved event (guild {ev['guild']}, event {ev['id']})")
                    continue
            self.events[key] = resolved

    @staticmethod
    async def __get_name(ctx: commands.Context) -> str:
        """Gets user input for the event name."""

        msg = await ctx.send("Please reply with the name of your event.")
        try:
            ret = await CommunityCalendar.__get_user_input(ctx)
        except (asyncio.TimeoutError, UserCancelledCreation):
            raise
        finally:
            await CommunityCalendar.__delete_message(msg)

        return ret

    @staticmethod
    async def __get_description(ctx: commands.Context) -> str:
        """Gets user input for the event description."""

        msg = await ctx.send("Please reply with a description of your event.\nReply `none` for no description.")
        try:
            ret = await CommunityCalendar.__get_user_input(ctx, timeout=120.0)
        except (asyncio.TimeoutError, UserCancelledCreation):
            raise
        finally:
            await CommunityCalendar.__delete_message(msg)

        if ret.lower() == "none":
            raise UserSkippedValue()

        return ret

    async def __get_when(self, ctx: commands.Context) -> datetime.datetime:
        """Gets user input for the event time and date."""

        msg = await ctx.send(
            "Please reply with the time and date of your event.\n"
            "The recommended format is `hh:mm [am/pm] tz m/d[/y]`. "
            "Dates and/or times in the past will not be accepted.\n"
            "Relative times are allowed, such as `in 1 hour`.\n"
            "Reply `now` to start right now."
        )

        def check(m: discord.Message) -> bool:
            now: datetime.datetime = dateparser.parse("now", settings={"RETURN_AS_TIMEZONE_AWARE": True})
            try:
                d: datetime.datetime = dateparser.parse(m.content, settings={"RETURN_AS_TIMEZONE_AWARE": True})
            except ValueError:
                good = m.content == f"{ctx.prefix}cancel"
                if not good:
                    self.bot.loop.create_task(CommunityCalendar.__delete_message(m))
                return good

            if d is None:
                good = m.content == f"{ctx.prefix}cancel"
                if not good:
                    self.bot.loop.create_task(CommunityCalendar.__delete_message(m))
                return good

            if d < now:
                self.bot.loop.create_task(CommunityCalendar.__delete_message(m))
                return False

            return True

        try:
            ret = await CommunityCalendar.__get_user_input(ctx, check=check)
        except (asyncio.TimeoutError, UserCancelledCreation):
            raise
        finally:
            await CommunityCalendar.__delete_message(msg)

        ret = dateparser.parse(ret, settings={"RETURN_AS_TIMEZONE_AWARE": True})
        return ret

    async def __get_limit(self, ctx: commands.Context) -> int:
        """Gets user input for the event attendee limit."""

        msg = await ctx.send(
            "Please reply with a number indicating the maximum number of attendees for your event. "
            "Reply `none` or `0` to indicate no limit."
        )

        def check(m: discord.Message) -> bool:
            try:
                num = int(m.content)
            except ValueError:
                good = m.content == f"{ctx.prefix}cancel" or m.content == "none"
                if not good:
                    self.bot.loop.create_task(CommunityCalendar.__delete_message(m))
                return good

            good = num >= 0
            if not good:
                self.bot.loop.create_task(CommunityCalendar.__delete_message(m))
            return good

        try:
            ret = await CommunityCalendar.__get_user_input(ctx, check=check)
        except (asyncio.TimeoutError, UserCancelledCreation):
            raise
        finally:
            await CommunityCalendar.__delete_message(msg)

        if ret.lower() == "none" or ret == "0":
            raise UserSkippedValue()

        return int(ret)

    @staticmethod
    async def __get_invitees(ctx: commands.Context) -> Tuple[List[discord.Member], List[discord.Role]]:
        """Gets user input for the event invitees (members and roles)."""

        msg = await ctx.send(
            "Please reply with any members or roles which you wish to invite to your event. "
            "You may mention them, give just their name, or give their ID.\n"
            "Individual entities are separated by spaces. "
            'If you are giving a plain name (not a mention) which has spaces, quote it, `"like this."`\n'
            "Members who are not invited will still be able to join your event, "
            "they just won't be notified of its creation.\n"
            "Reply `none` to skip."
        )

        try:
            raw_invitees = await CommunityCalendar.__get_user_input(ctx)
        except (asyncio.TimeoutError, UserCancelledCreation):
            raise
        finally:
            await CommunityCalendar.__delete_message(msg)

        if raw_invitees.lower() == "none":
            raise UserSkippedValue()

        split_invitees: List[str] = shlex.split(normalize_smartquotes(raw_invitees))

        roles: List[discord.Role] = []
        members: List[discord.Member] = []
        failures: List[str] = []
        for thing in split_invitees:
            # generic check - can be used to find roles or members
            def check(x: Union[discord.Member, discord.Role]) -> bool:
                try:
                    as_int = int(thing)
                except ValueError:
                    as_int = None
                return x.name.lower() == thing.lower() or x.mention == thing or (as_int is not None and x.id == as_int)

            # is it a role?
            role = discord.utils.find(check, ctx.guild.roles)
            if role is not None:
                roles.append(role)
                continue

            # is it a member?
            member: discord.Member = discord.utils.find(check, ctx.guild.members)
            if member is not None and not member.bot:
                members.append(member)
                continue

            # it's neither
            failures.append(thing)

        if len(failures) > 0:
            log.warning(
                f"Failed to resolve the following things as invitees (guild {ctx.guild.id}, channel {ctx.channel.id}): "
                f"{', '.join(failures)}"
            )

        return members, roles

    @staticmethod
    async def __get_user_input(
        ctx: commands.Context, *, timeout: float = 60.0, check: Callable[[discord.Message], bool] = None
    ) -> str:
        """Gets some input from the author of the message in `ctx` and deletes the message."""

        author = ctx.author
        channel = ctx.channel

        def basic_check(m: discord.Message) -> bool:
            return m.author == author and m.channel == channel

        def comp_check(m: discord.Message) -> bool:
            return basic_check(m) and (check(m) if check is not None else True)

        try:
            msg: discord.Message = await ctx.bot.wait_for("message", check=comp_check, timeout=timeout)
        except asyncio.TimeoutError:
            raise

        await CommunityCalendar.__delete_message(msg)

        content = msg.content.strip()
        if content == f"{ctx.prefix}cancel":
            raise UserCancelledCreation()
        else:
            return content

    @staticmethod
    async def __delete_message(message: discord.Message) -> None:
        """Attempts to delete the given message. Fails silently."""

        try:
            await message.delete()
        except discord.NotFound:
            log.warning(f"Failed to delete message (ID {message.id}): not found")
        except discord.Forbidden:
            log.warning(f"Failed to delete message (ID {message.id}): insufficient permissions")
        except discord.DiscordException:
            log.warning(f"Failed to delete message (ID {message.id})")
