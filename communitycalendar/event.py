import asyncio
import contextlib
import dateparser
import datetime
import os
from typing import ClassVar, List, Set, Tuple

import discord
from redbot.core.bot import Red
from redbot.core.utils.menus import start_adding_reactions
from redbot.core.utils.mod import is_mod_or_superior


class Event:
    """Event object.

    After creation, this object is in the context of the guild in which it was created.
    """

    GOING_EMOJI = "\N{WHITE HEAVY CHECK MARK}"
    MAYBE_EMOJI = "\N{WHITE QUESTION MARK ORNAMENT}"
    NOT_GOING_EMOJI = "\N{CROSS MARK}"

    CALENDAR_EMOJI = "\N{CALENDAR}"

    RESPONSE_EMOJIS: ClassVar[Tuple[str, str, str]] = (
        GOING_EMOJI,
        MAYBE_EMOJI,
        NOT_GOING_EMOJI,
    )

    def __init__(self, **kwargs):
        self.id: int = kwargs.get("id")
        self.creator: discord.Member = kwargs.get("creator")
        self.guild: discord.Guild = kwargs.get("guild")

        self.name: str = kwargs.get("name", "Untitled Event")
        self.description: str = kwargs.get("description", "")
        self.when: datetime.datetime = kwargs.get(
            "when", dateparser.parse("now", settings={"RETURN_AS_TIMEZONE_AWARE": True})
        )

        self.roles: Set[discord.Role] = kwargs.get("roles", set())
        self.members: Set[discord.Member] = kwargs.get("members", set())

        self.going: Set[discord.Member] = kwargs.get("going", set())
        self.maybe: Set[discord.Member] = kwargs.get("maybe", set())
        self.not_going: Set[discord.Member] = kwargs.get("not_going", set())

        self.limit: int = kwargs.get("limit", 0)

        self.messages: List[discord.Message] = kwargs.get("messages", [])

        self.open: bool = kwargs.get("open", True)
        self.alerted: bool = kwargs.get("alerted", False)

    def __eq__(self, other: "Event") -> bool:
        return isinstance(other, Event) and other.id == self.id and other.guild.id == self.guild.id

    def __ne__(self, other: "Event") -> bool:
        return not self.__eq__(other)

    async def refresh(self, *, content=None) -> None:
        """Refreshes the displays of this event by editing the messages with the most up-to-date embeds."""

        if not self.open:
            return

        emb = self.get_embed()

        for message in self.messages:
            try:
                await message.edit(content=content, embed=emb)
            except discord.DiscordException:
                pass

    async def send_invites(
        self, *, members: Set[discord.Member] = None, loop: asyncio.AbstractEventLoop = None
    ) -> None:
        """Sends the invites to ALL formally invited members."""

        if members is None:
            members = self.members

        embed = self.get_embed()

        for member in members:
            try:
                msg = await member.send(embed=embed)
                self.messages.append(msg)
                start_adding_reactions(msg, Event.RESPONSE_EMOJIS, loop)
            except discord.DiscordException:
                pass

    def activate(self, *, loop: asyncio.AbstractEventLoop = None) -> None:
        """Activates an event for interaction.

        AKA adds the reactions to it.
        """

        for message in self.messages:
            try:
                start_adding_reactions(message, Event.RESPONSE_EMOJIS, loop)
            except discord.DiscordException:
                pass

    async def close(self) -> None:
        """Closes this event.

        Really just disallows all interaction with the event.
        """

        self.open = False

        for message in self.messages:
            try:
                await message.clear_reactions()
            except discord.Forbidden:
                try:
                    for emoji in Event.RESPONSE_EMOJIS:
                        await message.remove_reaction(emoji, message.author)
                except discord.DiscordException:
                    pass

    async def message_attendees(self, message: str, sender: discord.Member, *, include_maybes: bool = False) -> None:
        """Sends the given message to all attendees.

        Optionally includes maybes. Silently skips failures.

        `message` can contain the following placeholders:
          * {member} is the member being messaged
          * {event} is this event
        """

        emb = discord.Embed(title=f"__{self.name}__", description=message, color=discord.Color.lighter_grey())
        emb.set_author(name=sender.display_name, icon_url=sender.avatar_url_as(static_format="png"))
        emb.set_footer(text=f"{Event.CALENDAR_EMOJI} Event ID {self.id} | Your time")
        emb.timestamp = self.when

        to_message: Set[discord.Member] = self.going
        if include_maybes:
            to_message = to_message.union(self.maybe)

        for member in to_message:
            try:
                await member.send(embed=emb)
            except discord.DiscordException as e:
                print(e)
                continue

    async def add_going(self, member: discord.Member) -> None:
        """Add the given user to the 'going' list. Removes from the other lists."""

        if not self.open:
            return

        if 0 < self.limit <= len(self.going):
            return await self.add_maybe(member)

        with contextlib.suppress(KeyError):
            self.maybe.remove(member)
        with contextlib.suppress(KeyError):
            self.not_going.remove(member)

        self.going.add(member)
        await self.refresh()

    async def add_maybe(self, member: discord.Member) -> None:
        """Add the given user to the 'maybe' list. Removes from the other lists."""

        if not self.open:
            return

        with contextlib.suppress(KeyError):
            self.going.remove(member)
        with contextlib.suppress(KeyError):
            self.not_going.remove(member)

        self.maybe.add(member)
        await self.refresh()

    async def add_not_going(self, member: discord.Member) -> None:
        """Add the given user to the 'not going' list. Removes from the other lists."""

        if not self.open:
            return

        with contextlib.suppress(KeyError):
            self.going.remove(member)
        with contextlib.suppress(KeyError):
            self.maybe.remove(member)

        self.not_going.add(member)
        await self.refresh()

    async def add_invitees(
        self,
        members: List[discord.Member],
        roles: List[discord.Role],
        *,
        send_invites: bool = True,
        loop: asyncio.AbstractEventLoop = None,
    ) -> None:
        """Add additional invitees to this event.

        If `send_invites` is True, sends invites to people who had not already been invited.
        """

        # pull all members out of the roles given
        members_from_roles: Set[discord.Member] = set(
            member for role in roles for member in role.members if not member.bot
        )

        # add the new role members to the individual members
        all_added_members = set(members).union(members_from_roles)

        # these are the members that had not already been invited to this event
        new_members = all_added_members.difference(self.members)

        # add the new ones to the main sets
        self.members = self.members.union(all_added_members)
        self.roles = self.roles.union(set(roles))

        if send_invites:
            # send invites to the new people if we are supposed to
            await self.send_invites(members=new_members, loop=loop)

    async def is_editable_by(self, bot: Red, member: discord.Member) -> bool:
        """Tells whether the given member is allowed to affect this event.

        Used as a gate for editing and closing.
        """

        if self.creator.id == member.id:
            return True

        return await is_mod_or_superior(bot, member)

    def get_embed(self) -> discord.Embed:
        description = self.description or "*No description.*"
        emb = discord.Embed(title=f"__{self.name}__", description=description, color=discord.Color.lighter_grey())
        emb.set_author(name=self.creator.display_name, icon_url=self.creator.avatar_url_as(static_format="png"))

        emb.add_field(
            name="When",
            inline=False,
            value=self.when.strftime(f"%A %B %{'#' if os.name == 'nt' else '-'}d at %I:%M%p %Z"),
        )

        going_name = "Going"
        if self.limit > 0:
            going_name += f" ({len(self.going)}/{self.limit})"
        else:
            going_name += f" ({len(self.going)})"
        going = Event.str_and_truncate(list(self.going)) if len(self.going) > 0 else "*None yet!*"
        emb.add_field(name=going_name, value=going)

        maybe = Event.str_and_truncate(list(self.maybe)) if len(self.maybe) > 0 else "*None yet!*"
        emb.add_field(name=f"Maybe ({len(self.maybe)})", value=maybe)

        emb.set_footer(text=f"{Event.CALENDAR_EMOJI} Event ID {self.id} | Your time")
        emb.timestamp = self.when

        return emb

    def to_dict(self) -> dict:
        result = self.__dict__.copy()

        result["guild"] = self.guild.id
        result["creator"] = self.creator.id

        result["when"] = result["when"].isoformat()

        result["roles"] = [x.id for x in result["roles"]]
        result["members"] = [x.id for x in result["members"]]

        result["going"] = [x.id for x in result["going"]]
        result["maybe"] = [x.id for x in result["maybe"]]
        result["not_going"] = [x.id for x in result["not_going"]]

        result["messages"] = [x.id for x in result["messages"]]

        return result

    @staticmethod
    async def from_dict(bot: Red, data: dict) -> "Event":
        try:
            guild: discord.Guild = bot.get_guild(data["guild"])
        except discord.DiscordException:
            raise

        messages = []
        for message in data["messages"]:
            found = False
            for member in [m for m in guild.members if not m.bot]:
                try:
                    messages.append(await member.fetch_message(message))
                    found = True
                    break
                except discord.DiscordException:
                    continue
            if found:
                continue
            for channel in guild.text_channels:
                try:
                    messages.append(await channel.fetch_message(message))
                    break
                except discord.DiscordException:
                    continue

        data["guild"] = guild
        data["creator"] = discord.utils.get(guild.members, id=data["creator"])

        data["when"] = dateparser.parse(data["when"], settings={"RETURN_AS_TIMEZONE_AWARE": True})

        data["roles"] = set(filter(None, [discord.utils.get(guild.roles, id=x) for x in data.get("roles", [])]))
        data["members"] = set(filter(None, [discord.utils.get(guild.members, id=x) for x in data.get("members", [])]))

        data["going"] = set(filter(None, [discord.utils.get(guild.members, id=x) for x in data.get("going", [])]))
        data["maybe"] = set(filter(None, [discord.utils.get(guild.members, id=x) for x in data.get("maybe", [])]))
        data["not_going"] = set(
            filter(None, [discord.utils.get(guild.members, id=x) for x in data.get("not_going", [])])
        )

        data["messages"] = messages

        return Event(**data)

    @staticmethod
    def str_and_truncate(members: List[discord.Member], *, limit=1000) -> str:
        """Returns the equivalent of `", ".join(members)`, but with the string limited to the given length.
        Adds "and x more." to the end of the string to account for whatever couldn't make it into the list.
        """

        index = 0
        res = ""
        while len(res) < limit and index < len(members):
            res += f"{members[index].display_name}, "
            index += 1

        if index < len(members):
            res += f"and {len(members) - index} more."

        if res.endswith(", "):
            res = res[:-2]

        return res
