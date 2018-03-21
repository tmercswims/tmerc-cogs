import asyncio
import re
import logging
from copy import copy

import discord
from discord.ext import commands
from discord.utils import get

from redbot.core import Config, RedContext, checks
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import box

log = logging.getLogger('red.tmerc.nestedcommands')


class NestedCommands:
  '''Experimental cog that allows you to use the
  output of one command as the input of another.
  '''

  guild_defaults = {
    'enabled': False,
    'channel': None
  }

  p = re.compile(r'\$\(.+\)')

  def __init__(self, bot: Red):
    self.bot = bot
    self.config = Config.get_conf(self, 36649125)
    self.config.register_guild(**self.guild_defaults)

    self.__init_before()

  @commands.command()
  async def say(self, ctx: RedContext, *, message: str):
    '''Echoes back what you say.'''

    await ctx.send(message)

  @commands.group()
  @commands.guild_only()
  @checks.guildowner()
  async def ncset(self, ctx: RedContext):
    '''Change NestedCommands settings.'''

    if ctx.invoked_subcommand is None:
      await ctx.send_help()

      config = await self.config.guild(ctx.guild).all()

      enabled = config['enabled']
      channel = config['channel']
      if channel is not None:
        channel = get(ctx.guild.text_channels, id=channel)

      msg = box(
          ('Enabled: {}\n'
           'Channel: {}\n'
           '').format(enabled, channel and channel.name),
          'Current NestedCommands settings:'
        )

      await ctx.send(msg)

  @ncset.command(name='toggle')
  async def ncset_toggle(self, ctx: RedContext, on_off: bool = None):
    '''Turns NestedCommand on or off.

    If `on_off` is not provided, the state will be flipped.
    '''

    await ctx.trigger_typing()

    guild = ctx.guild
    target_state = on_off if on_off is not None else not (await self.config.guild(guild).enabled())

    channel = await self.config.guild(guild).channel()
    if channel is None and target_state:
      await ctx.send(
        ('You need to set a channel with `{}ncset channel` '
         'before you can enable NestedCommands.'
         '').format(ctx.prefix)
      )
      return

    await self.config.guild(guild).enabled.set(target_state)
    await ctx.send(
      ('NestedCommands is now {}.'
       '').format('enabled' if target_state else 'disabled')
    )

  @ncset.command(name='channel')
  async def ncset_channel(self, ctx: RedContext, *, channel: discord.TextChannel):
    '''Sets the channel which will be used to print the output
    of all inner commands.

    It is highly recommended that you make this channel hidden
    and/or read-only to all users except Red, because this cog
    relies on the message history to function properly.
    '''

    await ctx.trigger_typing()

    await self.config.guild(ctx.guild).channel.set(channel.id)

    await ctx.send(
      ('Done. I will now use the channel {} for inner command outputs. '
       'Ensure you also turn on NestedCommand with `{}ncset toggle`.'
       '').format(channel.mention, ctx.prefix)
    )

  def __init_before(self):
    '''Sets up the before_invoke hook that makes this all work.'''

    @self.bot.before_invoke
    async def before_any_command(ctx: RedContext):
      if ctx.guild and await self.config.guild(ctx.guild).enabled():
        message = ctx.message
        channel = await self.config.guild(ctx.guild).channel()
        if channel is not None:
          channel = get(ctx.guild.text_channels, id=channel)
        else:
          return

        for matched_text in self.p.findall(message.content):
          inner_command = matched_text[2:-1]

          new_message = copy(message)
          new_message.content = '{}{}'.format(ctx.prefix, inner_command)
          new_message.channel = channel

          await self.bot.process_commands(new_message)

          inner_output = (await channel.history(limit=1).flatten())[0].content

          message.content = message.content.replace(matched_text, inner_output)

          for name, value in ctx.kwargs.items():
            if matched_text in value:
              ctx.kwargs[name] = value.replace(matched_text, inner_output)

          await asyncio.sleep(.1)
