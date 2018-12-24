import asyncio
import logging
import random
from datetime import date
from typing import Union

import discord
from redbot.core import Config, commands, checks
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import box, pagify

from .enums import WhisperType

__author__ = "tmerc"

log = logging.getLogger('red.tmerc.welcome')

ENABLED = 'enabled'
DISABLED = 'disabled'


class Welcome(getattr(commands, "Cog", object)):
  """Announce when users join or leave a server."""

  default_join = "Welcome {member.mention} to {server.name}!"
  default_leave = "{member.name} has left {server.name}!"
  default_ban = "{member.name} has been banned from {server.name}!"
  default_unban = "{member.name} has been unbanned from {server.name}!"
  default_whisper = "Hey there {member.name}, welcome to {server.name}!"

  guild_defaults = {
    'enabled': False,
    'channel': None,
    'date': None,
    'join': {
      'enabled': True,
      'delete': False,
      'last': None,
      'counter': 0,
      'whisper': {
        'state': 'off',
        'message': default_whisper
      },
      'messages': [default_join],
      'bot': None
    },
    'leave': {
      'enabled': True,
      'delete': False,
      'last': None,
      'messages': [default_leave],
    },
    'ban': {
      'enabled': True,
      'delete': False,
      'last': None,
      'messages': [default_ban],
    },
    'unban': {
      'enabled': True,
      'delete': False,
      'last': None,
      'messages': [default_unban],
    }
  }

  def __init__(self, bot: Red):
    self.bot = bot
    self.config = Config.get_conf(self, 86345009)
    self.config.register_guild(**self.guild_defaults)

  @commands.group()
  @commands.guild_only()
  @checks.admin_or_permissions(manage_guild=True)
  async def welcomeset(self, ctx: commands.Context):
    """Change Welcome settings."""

    await ctx.trigger_typing()

    if ctx.invoked_subcommand is None:
      guild = ctx.guild
      c = await self.config.guild(guild).all()

      channel = await self.__get_channel(ctx.guild)

      j = c['join']
      jw = j['whisper']
      v = c['leave']
      b = c['ban']
      u = c['unban']

      if await ctx.embed_requested():
        emb = discord.Embed(color=await ctx.embed_color(), title="Current Welcome Settings")
        emb.add_field(name="General", value=(
          "**Enabled:** {}\n"
          "**Channel:** #{}\n"
        ).format(c['enabled'], channel))
        emb.add_field(name="Join", value=(
          "**Enabled:** {}\n"
          "**Delete previous:** {}\n"
          "**Whisper state:** {}\n"
          "**Whisper message:** {}\n"
          "**Messages:** {}; do `{prefix}welcomeset join msg list` for a list\n"
          "**Bot message:** {}"
        ).format(j['enabled'], j['delete'], jw['state'], jw['message'], len(j['messages']), j['bot'],
                 prefix=ctx.prefix))
        emb.add_field(name="Leave", value=(
          "**Enabled:** {}\n"
          "**Delete previous:** {}\n"
          "**Messages:** {}; do `{prefix}welcomeset leave msg list` for a list\n"
        ).format(v['enabled'], v['delete'], len(v['messages']), prefix=ctx.prefix))
        emb.add_field(name="Ban", value=(
          "**Enabled:** {}\n"
          "**Delete previous:** {}\n"
          "**Messages:** {}; do `{prefix}welcomeset ban msg list` for a list\n"
        ).format(b['enabled'], b['delete'], len(b['messages']), prefix=ctx.prefix))
        emb.add_field(name="Leave", value=(
          "**Enabled:** {}\n"
          "**Delete previous:** {}\n"
          "**Messages:** {}; do `{prefix}welcomeset unban msg list` for a list\n"
        ).format(u['enabled'], u['delete'], len(u['messages']), prefix=ctx.prefix))

        await ctx.send(embed=emb)
      else:
        msg = box(
          ("  Enabled: {}\n"
           "  Channel: {}\n"
           "  Join:\n"
           "    Enabled: {}\n"
           "    Delete previous: {}\n"
           "    Whisper:\n"
           "      State: {}\n"
           "      Message: {}\n"
           "    Messages: {}; do '{prefix}welcomeset join msg list' for a list\n"
           "    Bot message: {}\n"
           "  Leave:\n"
           "    Enabled: {}\n"
           "    Delete previous: {}\n"
           "    Messages: {}; do '{prefix}welcomeset leave msg list' for a list\n"
           "  Ban:\n"
           "    Enabled: {}\n"
           "    Delete previous: {}\n"
           "    Messages: {}; do '{prefix}welcomeset ban msg list' for a list\n"
           "  Unban:\n"
           "    Enabled: {}\n"
           "    Delete previous: {}\n"
           "    Messages: {}; do '{prefix}welcomeset unban msg list' for a list\n"
           "").format(c['enabled'], channel,
                      j['enabled'], j['delete'], jw['state'], jw['message'], len(j['messages']), j['bot'],
                      v['enabled'], v['delete'], len(v['messages']),
                      b['enabled'], b['delete'], len(b['messages']),
                      u['enabled'], u['delete'], len(u['messages']),
                      prefix=ctx.prefix),
          "Current Welcome settings:"
        )

        await ctx.send(msg)

  @welcomeset.command(name='toggle')
  async def welcomeset_toggle(self, ctx: commands.Context, on_off: bool = None):
    """Turns Welcome on or off.

    If `on_off` is not provided, the state will be flipped.
    """

    guild = ctx.guild
    target_state = on_off if on_off is not None else not (await self.config.guild(guild).enabled())

    await self.config.guild(guild).enabled.set(target_state)

    await ctx.send(
      ("Welcome is now {}."
       "").format(ENABLED if target_state else DISABLED)
    )

  @welcomeset.command(name='channel')
  async def welcomeset_channel(self, ctx: commands.Context, channel: discord.TextChannel):
    """Sets the channel to be used for event notices."""

    if not self.__can_speak_in(channel):
      await ctx.send(
        ("I do not have permission to send messages in {0.mention}. Check your permission settings and try again."
         "").format(channel)
      )
      return

    guild = ctx.guild
    await self.config.guild(guild).channel.set(channel.id)

    await ctx.send(
      ("I will now send event notices to {0.mention}."
       "").format(channel)
    )

  @welcomeset.group(name='join')
  async def welcomeset_join(self, ctx: commands.Context):
    """Change settings for join notices."""

    pass

  @welcomeset_join.command(name='toggle')
  async def welcomeset_join_toggle(self, ctx: commands.Context, on_off: bool = None):
    """Turns join notices on or off.

    If `on_off` is not provided, the state will be flipped.
    """

    await self.__toggle(ctx, on_off, 'join')

  @welcomeset_join.command(name='toggledelete')
  async def welcomeset_join_toggledelete(self, ctx: commands.Context, on_off: bool = None):
    """Turns deletion of previous join notice on or off.

    If `on_off` is not provided, the state will be flipped.
    """

    await self.__toggledelete(ctx, on_off, 'join')

  @welcomeset_join.group(name='whisper')
  async def welcomeset_join_whisper(self, ctx: commands.Context):
    """Change settings for join whispers."""

    pass

  @welcomeset_join_whisper.command(name='type')
  async def welcomeset_join_whisper_type(self, ctx: commands.Context, choice: WhisperType):
    """Set if a DM is sent to the new member.

    Options:
      off - no DM is sent
      only - only send a DM to the member, do not send a message to the channel
      both - send a DM to the member and a message to the channel
    """

    guild = ctx.guild
    whisper_type = choice.value
    channel = await self.__get_channel(ctx.guild)

    await self.config.guild(guild).join.whisper.state.set(whisper_type)

    if choice == WhisperType.OFF:
      await ctx.send(
        ("I will no longer DM new members, and will send a notice to {0.mention}."
         "").format(channel)
      )
    elif choice == WhisperType.ONLY:
      await ctx.send(
        ("I will now only DM new members, and will not send a notice to {0.mention}."
         "").format(channel)
      )
    elif choice == WhisperType.BOTH:
      await ctx.send(
        ("I will now send a DM to new members, as well as send a notice to {0.mention}."
         "").format(channel)
      )

  @welcomeset_join_whisper.command(name='msg')
  async def welcomeset_join_whisper_msg(self, ctx: commands.Context, *, msg_format: str):
    """Set the message DM'd to new members when they join.

    Allows for the following customizations:
      `{member}` is the member who joined
      `{server}` is the server
    """

    await self.config.guild(ctx.guild).join.whisper.message.set(msg_format)

    await ctx.send(
      ("I will now use that message format when whispering new members, if whisper is enabled."
       "")
    )

  @welcomeset_join.group(name='msg')
  async def welcomeset_join_msg(self, ctx: commands.Context):
    """Manage join message formats."""

    pass

  @welcomeset_join_msg.command(name='add')
  async def welcomeset_join_msg_add(self, ctx: commands.Context, *, msg_format: str):
    """Add a new join message format to be chosen.

    Allows for the following customizations:
      `{member}` is the new member
      `{server}` is the server
      `{count}` is the number of members who have joined today
      `{plural}` is an 's' if `count` is not 1, and nothing if it is

    For example:
      {member.mention}... What are you doing here???
      {server.name} has a new member! {member.name}#{member.discriminator} - {member.id}
      Someone new has joined! Who is it?! D: IS HE HERE TO HURT US?!
    """

    await self.__msg_add(ctx, msg_format, 'join')

  @welcomeset_join_msg.command(name='del')
  async def welcomeset_join_msg_del(self, ctx: commands.Context):
    """Delete an existing join message format from the list."""

    await self.__msg_del(ctx, 'join')

  @welcomeset_join_msg.command(name='list')
  async def welcomeset_join_msg_list(self, ctx: commands.Context):
    """Lists the available join message formats."""

    await self.__msg_list(ctx, 'join')

  @welcomeset_join.command(name='botmsg')
  async def welcomeset_join_botmsg(self, ctx: commands.Context, *, msg_format: str=None):
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
      await ctx.send(
        ("Bot join message format set. I will now greet bots with that message."
         "")
      )
    else:
      await ctx.send(
        ("Bot join message format removed. I will now greet bots like normal members."
         "")
      )

  @welcomeset.group(name='leave')
  async def welcomeset_leave(self, ctx: commands.Context):
    """Change settings for leave notices."""

    pass

  @welcomeset_leave.command(name='toggle')
  async def welcomeset_leave_toggle(self, ctx: commands.Context, on_off: bool = None):
    """Turns leave notices on or off.

    If `on_off` is not provided, the state will be flipped.
    """

    await self.__toggle(ctx, on_off, 'leave')

  @welcomeset_leave.command(name='toggledelete')
  async def welcomeset_leave_toggledelete(self, ctx: commands.Context, on_off: bool = None):
    """Turns deletion of previous leave notice on or off.

    If `on_off` is not provided, the state will be flipped.
    """

    await self.__toggledelete(ctx, on_off, 'leave')

  @welcomeset_leave.group(name='msg')
  async def welcomeset_leave_msg(self, ctx: commands.Context):
    """Manage leave message formats."""

    pass

  @welcomeset_leave_msg.command(name='add')
  async def welcomeset_leave_msg_add(self, ctx: commands.Context, *, msg_format: str):
    """Add a new leave message format to be chosen.

    Allows for the following customizations:
      `{member}` is the member who left
      `{server}` is the server

    For example:
      {member.name}... Why did you leave???
      {server.name} has lost a member! {member.name}#{member.discriminator} - {member.id}
      Someone has left... Aww... Bye :(
    """

    await self.__msg_add(ctx, msg_format, 'leave')

  @welcomeset_leave_msg.command(name='del')
  async def welcomeset_leave_msg_del(self, ctx: commands.Context):
    """Delete an existing leave message format from the list."""

    await self.__msg_del(ctx, 'leave')

  @welcomeset_leave_msg.command(name='list')
  async def welcomeset_leave_msg_list(self, ctx: commands.Context):
    """Lists the available leave message formats."""

    await self.__msg_list(ctx, 'leave')

  @welcomeset.group(name='ban')
  async def welcomeset_ban(self, ctx: commands.Context):
    """Change settings for ban notices."""

    pass

  @welcomeset_ban.command(name='toggle')
  async def welcomeset_ban_toggle(self, ctx: commands.Context, on_off: bool = None):
    """Turns ban notices on or off.

    If `on_off` is not provided, the state will be flipped.
    """

    await self.__toggle(ctx, on_off, 'ban')

  @welcomeset_ban.command(name='toggledelete')
  async def welcomeset_ban_toggledelete(self, ctx: commands.Context, on_off: bool = None):
    """Turns deletion of previous ban notice on or off.

    If `on_off` is not provided, the state will be flipped.
    """

    await self.__toggledelete(ctx, on_off, 'ban')

  @welcomeset_ban.group(name='msg')
  async def welcomeset_ban_msg(self, ctx: commands.Context):
    """Manage ban message formats."""

    pass

  @welcomeset_ban_msg.command(name='add')
  async def welcomeset_ban_msg_add(self, ctx: commands.Context, *, msg_format: str):
    """Add a new ban message format to be chosen.

    Allows for the following customizations:
      `{member}` is the banned member
      `{server}` is the server

    For example:
      {member.name} was banned... What did you do???
      A member of {server.name} has been banned! {member.name}#{member.discriminator} - {member.id}
      Someone has been banned. Good riddance!
    """

    await self.__msg_add(ctx, msg_format, 'ban')

  @welcomeset_ban_msg.command(name='del')
  async def welcomeset_ban_msg_del(self, ctx: commands.Context):
    """Delete an existing ban message format from the list."""

    await self.__msg_del(ctx, 'ban')

  @welcomeset_ban_msg.command(name='list')
  async def welcomeset_ban_msg_list(self, ctx: commands.Context):
    """Lists the available ban message formats."""

    await self.__msg_list(ctx, 'ban')

  @welcomeset.group(name='unban')
  async def welcomeset_unban(self, ctx: commands.Context):
    """Change settings for unban notices."""

    pass

  @welcomeset_unban.command(name='toggle')
  async def welcomeset_unban_toggle(self, ctx: commands.Context, on_off: bool = None):
    """Turns unban notices on or off.

    If `on_off` is not provided, the state will be flipped.
    """

    await self.__toggle(ctx, on_off, 'unban')

  @welcomeset_unban.command(name='toggledelete')
  async def welcomeset_unban_toggledelete(self, ctx: commands.Context, on_off: bool = None):
    """Turns deletion of previous unban notice on or off.

    If `on_off` is not provided, the state will be flipped.
    """

    await self.__toggledelete(ctx, on_off, 'unban')

  @welcomeset_unban.group(name='msg')
  async def welcomeset_unban_msg(self, ctx: commands.Context):
    """Manage unban message formats."""

    pass

  @welcomeset_unban_msg.command(name='add')
  async def welcomeset_unban_msg_add(self, ctx: commands.Context, *, msg_format: str):
    """Add a new unban message format to be chosen.

    Allows for the following customizations:
      `{member}` is the unbanned member
      `{server}` is the server

    For example:
      {member.name} was unbanned... Did you learn your lesson???
      A member of {server.name} has been unbanned! {member.name}#{member.discriminator} - {member.id}
      Someone has been unbanned. Don't waste your second chance!
    """

    await self.__msg_add(ctx, msg_format, 'unban')

  @welcomeset_unban_msg.command(name='del')
  async def welcomeset_unban_msg_del(self, ctx: commands.Context):
    """Delete an existing unban message format from the list."""

    await self.__msg_del(ctx, 'unban')

  @welcomeset_unban_msg.command(name='list')
  async def welcomeset_unban_msg_list(self, ctx: commands.Context):
    """Lists the available unban message formats."""

    await self.__msg_list(ctx, 'unban')

  async def on_member_join(self, member: discord.Member):
    """Listens for member joins."""

    guild = member.guild
    guild_settings = self.config.guild(guild)

    if await guild_settings.enabled() and await guild_settings.join.enabled():
      # join notice should be sent
      message_format = None
      if member.bot:
        # bot
        message_format = await guild_settings.join.bot()

      else:
        # only increment when it isn't a bot
        await self.__increment_count(guild, 'join')

        whisper_type = await guild_settings.join.whisper.state()
        if whisper_type != 'off':
          await self.__dm_user(member)

          if whisper_type == 'only':
            # we're done here
            return

      await self.__handle_event(guild, member, 'join', message_format=message_format)

  async def on_member_remove(self, member: discord.Member):
    """Listens for member leaves."""

    await self.__handle_event(member.guild, member, 'leave')

  async def on_member_ban(self, guild: discord.Guild, member: discord.Member):
    """Listens for user bans."""

    await self.__handle_event(guild, member, 'ban')

  async def on_member_unban(self, guild: discord.Guild, user: discord.User):
    """Listens for user unbans."""

    await self.__handle_event(guild, user, 'unban')

  #
  # concrete handlers for settings changes and events
  #

  async def __toggle(self, ctx: commands.Context, on_off: bool, event: str):
    """Handler for setting toggles."""

    guild = ctx.guild
    target_state = on_off if on_off is not None else not (await self.config.guild(guild).get_attr(event).enabled())

    await self.config.guild(guild).get_attr(event).enabled.set(target_state)

    await ctx.send(
      ("{} notices are now {}."
       "").format(event.capitalize(), ENABLED if target_state else DISABLED)
    )

  async def __toggledelete(self, ctx: commands.Context, on_off: bool, event: str):
    """Handler for setting delete toggles."""

    guild = ctx.guild
    target_state = on_off if on_off is not None else not (await self.config.guild(guild).get_attr(event).delete())

    await self.config.guild(guild).get_attr(event).delete.set(target_state)

    await ctx.send(
      ("Deletion of previous {} notice is now {}."
       "").format(event, ENABLED if target_state else DISABLED)
    )

  async def __msg_add(self, ctx: commands.Context, msg_format: str, event: str):
    """Handler for adding message formats."""

    guild = ctx.guild

    async with self.config.guild(guild).get_attr(event).messages() as messages:
      messages.append(msg_format)

    await ctx.send(
      ("New message format for {} notices added."
       "").format(event)
    )

  async def __msg_del(self, ctx: commands.Context, event: str):
    """Handler for deleting message formats."""

    guild = ctx.guild

    async with self.config.guild(guild).get_attr(event).messages() as messages:
      if len(messages) == 1:
        await ctx.send(
          ("I only have one {} message format, so I can't let you delete it."
           "").format(event)
        )
        return

      await self.__msg_list(ctx, event)
      await ctx.send(
        ("Please enter the number of the {} message format you wish to delete."
         "").format(event)
      )

      try:
        num = await self.__get_number_input(ctx, len(messages))
      except asyncio.TimeoutError:
        await ctx.send(
          ("Okay, I won't remove any of the {} message formats."
           "").format(event)
        )
        return
      else:
        removed = messages.pop(num - 1)

    await ctx.send(
      ("Done. This {} message format was deleted:\n"
       "`{}`"
       "").format(event, removed)
    )

  async def __msg_list(self, ctx: commands.Context, event: str):
    """Handler for listing message formats."""

    guild = ctx.guild

    msg = "{} message formats:\n".format(event.capitalize())
    async with self.config.guild(guild).get_attr(event).messages() as messages:
      for n, m in enumerate(messages, start=1):
        msg += '  {}. {}\n'.format(n, m)

    for page in pagify(msg, ['\n', ' '], shorten_by=20):
      await ctx.send(box(page))

  async def __handle_event(self, guild: discord.guild, user: Union[discord.Member, discord.User], event: str, *,
                           message_format=None):
    """Handler for actual events."""

    guild_settings = self.config.guild(guild)

    if await guild_settings.enabled():
      settings = await guild_settings.get_attr(event).all()
      if settings['enabled']:
        # notices for this event are enabled

        if settings['delete'] and settings['last'] is not None:
          # we need to delete the previous message
          await self.__delete_message(guild, settings['last'])
          # regardless of success, remove reference to that message
          await guild_settings.get_attr(event).last.set(None)

        # send a notice to the channel
        new_message = await self.__send_notice(guild, user, event, message_format=message_format)
        # store it for (possible) deletion later
        await guild_settings.get_attr(event).last.set(new_message and new_message.id)

  async def __get_channel(self, guild: discord.Guild) -> discord.TextChannel:
    """Gets the best text channel to use for event notices.

    Order of priority:
    1. User-defined channel
    2. Guild's system channel (if bot can speak in it)
    3. First channel that the bot can speak in
    """

    channel = None

    channel_id = await self.config.guild(guild).channel()
    if channel_id is not None:
      channel = guild.get_channel(channel_id)

    if channel is None or not self.__can_speak_in(channel):
      channel = guild.system_channel

    if channel is None or not self.__can_speak_in(channel):
      for ch in guild.text_channels:
        if self.__can_speak_in(ch):
          channel = ch
          break

    return channel

  async def __get_number_input(self, ctx: commands.Context, maximum: int, minimum: int=0) -> int:
    """Gets a number from the user, minimum < x <= maximum."""

    author = ctx.author
    channel = ctx.channel

    def check(m: discord.Message):
      num = None
      try:
        num = int(m.content)
      except ValueError:
        pass

      return num is not None \
          and minimum < num <= maximum \
          and m.author == author \
          and m.channel == channel

    try:
      msg = await self.bot.wait_for('message', check=check, timeout=15.0)
    except asyncio.TimeoutError:
      raise
    else:
      return int(msg.content)

  async def __delete_message(self, guild: discord.Guild, message_id: int):
    """Attempts to delete the message with the given ID."""

    try:
      await (await (await self.__get_channel(guild)).get_message(message_id)).delete()
    except discord.NotFound:
      log.warning(
        ("Failed to delete message (ID {}): not found"
         "").format(message_id)
      )
    except discord.Forbidden:
      log.warning(
        ("Failed to delete message (ID {}): insufficient permissions"
         "").format(message_id)
      )
    except:
      log.warning(
        ("Failed to delete message (ID {})"
         "").format(message_id)
      )

  async def __send_notice(self, guild: discord.guild, user: Union[discord.Member, discord.User], event: str, *,
                          message_format=None) -> Union[discord.Message, None]:
    """Sends the notice for the event."""

    format_str = message_format or await self.__get_random_message_format(guild, event)

    count = event == 'join' and await self.config.guild(guild).get_attr(event).counter()
    plural = ''
    if count and count != 1:
      plural = 's'

    channel = await self.__get_channel(guild)

    try:
      return await channel.send(
        format_str.format(member=user, server=guild, bot=user, count=count or '', plural=plural)
      )
    except discord.Forbidden:
      log.error(
        ("Failed to send {} message to channel ID {1.id} (server ID {2.id}): insufficient permissions"
         "").format(event, channel, guild)
      )
      return None
    except:
      log.error(
        ("Failed to send {} message to channel ID {1.id} (server ID {2.id})"
         "").format(event, channel, guild)
      )
      return None

  async def __get_random_message_format(self, guild: discord.guild, event: str) -> str:
    """Gets a random message for event of type event."""

    async with self.config.guild(guild).get_attr(event).messages() as messages:
      return random.choice(messages)

  async def __increment_count(self, guild: discord.Guild, event: str):
    """Increments the counter for <event>s today. Handles date changes."""

    guild_settings = self.config.guild(guild)

    if await guild_settings.date() is None:
      await guild_settings.date.set(self.__today())

    if self.__today() > await guild_settings.date():
      await guild_settings.date.set(self.__today())
      await guild_settings.get_attr(event).counter.set(0)

    count = await guild_settings.get_attr(event).counter()
    await guild_settings.get_attr(event).counter.set(count + 1)

  async def __dm_user(self, member: discord.Member):
    """Sends a DM to the user with a filled-in message_format."""

    message_format = await self.config.guild(member.guild).join.whisper.message()

    try:
      await member.send(message_format.format(member=member, server=member.guild))
    except discord.Forbidden:
      log.error(
        ("Failed to send DM to member ID {0.id} (server ID {1.id}): insufficient permissions"
         "").format(member, member.guild)
      )
    except:
      log.error(
        ("Failed to send DM to member ID {0.id} (server ID {1.id})"
         "").format(member, member.guild)
      )

  @staticmethod
  def __can_speak_in(channel: discord.TextChannel) -> bool:
    """Indicates whether the bot has permission to speak in channel."""

    return channel.permissions_for(channel.guild.me).send_messages

  @staticmethod
  def __today() -> int:
    """Gets today's date in ordinal form."""

    return date.today().toordinal()
