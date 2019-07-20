import logging

import discord
from discord.utils import get
from redbot.core import Config, commands, checks
from redbot.core.utils.chat_formatting import box

__author__ = "tmerc"

log = logging.getLogger('red.tmerc.streamrole')


class StreamRole(getattr(commands, "Cog", object)):
  """Assign a configurable role to anyone who is streaming."""

  guild_defaults = {
    'enabled': False,
    'role': None,
    'promote': False,
    'promote_from': None,
    'lax_promote': False
  }

  def __init__(self):
    self.config = Config.get_conf(self, 34507445)
    self.config.register_guild(**self.guild_defaults)

  @commands.group()
  @commands.guild_only()
  @checks.admin_or_permissions(manage_guild=True)
  async def streamroleset(self, ctx: commands.Context):
    """Change StreamRole settings."""

    if ctx.invoked_subcommand is None:
      guild = ctx.guild
      config = await self.config.guild(guild).all()
      enabled = config['enabled']
      role = config['role']
      if role is not None:
        role = get(ctx.guild.roles, id=role)
      promote = config['promote']
      promote_from = config['promote_from']
      if promote_from is not None:
        promote_from = get(ctx.guild.roles, id=promote_from)
      lax_promote = config['lax_promote']

      msg = box(
        ("  Enabled: {}\n"
         "  Streaming role: {}\n"
         "  Only promote members with prerequisite role: {}\n"
         "  Promotion prerequisite role: {}\n"
         "  Promote from prerequisite and above: {}"
         "").format(enabled, role and role.name, promote, promote_from and promote_from.name, lax_promote),
        "Current StreamRole settings:"
      )

      await ctx.send(msg)

  @streamroleset.command(name='toggle')
  async def streamroleset_toggle(self, ctx: commands.Context, on_off: bool = None):
    """Turns StreamRole on or off.

    If `on_off` is not provided, the state will be flipped.
    """

    await ctx.trigger_typing()

    guild = ctx.guild
    target_state = on_off if on_off is not None else not (await self.config.guild(guild).enabled())

    streaming_role = await self.config.guild(guild).role()
    if streaming_role is None and target_state:
      await ctx.send(
        ("You need to set a role with `{}streamroleset role` before you can enable StreamRole."
         "").format(ctx.prefix)
      )
      return

    await self.config.guild(guild).enabled.set(target_state)

    if target_state:
      await ctx.send("StreamRole is now enabled.")
    else:
      await ctx.send("StreamRole is now disabled.")

  @streamroleset.command(name='role')
  async def streamroleset_role(self, ctx: commands.Context, *, role: discord.Role):
    """Sets the role which will be assigned to members who are streaming."""

    await ctx.trigger_typing()

    await self.config.guild(ctx.guild).role.set(role.id)

    await ctx.send(
      ("Done. Members who are streaming will now be given the role `{}`. Ensure you also turn on StreamRole with "
       "`{}streamroleset toggle`."
       "").format(role.name, ctx.prefix)
    )

  @streamroleset.group(name='promote')
  async def streamroleset_promote(self, ctx: commands.Context):
    """Changes promotion settings."""

    pass

  @streamroleset_promote.command(name='toggle')
  async def streamroleset_promote_toggle(self, ctx: commands.Context, on_off: bool = None):
    """Turns promote role prerequisite on or off.

    If `on_off` is not provided, the state will be flipped.
    """

    await ctx.trigger_typing()

    guild = ctx.guild
    target_state = on_off if on_off is not None else not (await self.config.guild(guild).promote())

    prereq_role = await self.config.guild(guild).promote_from()
    if prereq_role is None and target_state:
      await ctx.send(
        ("You need to set a role with `{}streamroleset promote role` before you can enable promotion role prerequisite."
         "").format(ctx.prefix)
      )
      return
    prereq_role = get(guild.roles, id=prereq_role)

    await self.config.guild(guild).promote.set(target_state)

    if target_state:
      await ctx.send(
        ("Done. Promote role prerequisite is now enabled. Only members with the role `{}` will be given the streaming "
         "role."
         "").format(prereq_role.name)
      )
    else:
      await ctx.send(
        ("Done. Promote role prerequisite is now disabled. All members who are streaming will be given the streaming "
         "role."
         "")
      )

  @streamroleset_promote.command(name='role')
  async def streamroleset_promote_role(self, ctx: commands.Context, *, role: discord.Role):
    """Sets the prerequisite role for streaming promotion.

    If this role is set and promote is toggled on, only members with this role will be given the streaming role.
    """

    await ctx.trigger_typing()

    await self.config.guild(ctx.guild).promote_from.set(role.id)

    await ctx.send(
      ("Done. Only members with the role `{}` will be given the streaming role."
       "").format(role.name)
    )

  @streamroleset_promote.command(name='lax')
  async def streamroleset_promote_lax(self, ctx: commands.Context, on_off: bool = None):
    """Turns lax promote role prerequisite on or off.

    If this is on, members with the prerequisite role or any role above it in the hierarchy will be given the streaming
    role. If it is off, only members with exactly the prerequisite role will be given the streaming role.

    If `on_off` is not provided, the state will be flipped.
    """

    await ctx.trigger_typing()

    guild = ctx.guild
    target_state = on_off if on_off is not None else not (await self.config.guild(guild).lax_promote())

    await self.config.guild(guild).lax_promote.set(target_state)

    if target_state:
      await ctx.send(
        ("Lax promotion is now on. If promotion prerequisite is enabled, any member with the prerequisite role or any "
         "role above it in the hierarchy will be given the streaming role."
         "")
      )
    else:
      await ctx.send(
        ("Lax promotion is now off. If promotion prerequisite is enabled, only members with exactly the prerequisite "
         "role will be given the streaming role."
         "")
      )

  @commands.Cog.listener()
  async def on_member_update(self, before: discord.Member, after: discord.Member):
    """Listens to member updates to detect starting/stopping streaming."""

    guild = after.guild
    config = await self.config.guild(guild).all()
    is_streaming = any(a.type == discord.ActivityType.streaming for a in after.activities)
    if config['enabled'] and config['role'] is not None:
      streaming_role = get(guild.roles, id=config['role'])

      if streaming_role is None:
        log.error(
          ("Failed to find streaming role with ID {} (server ID {}); this likely means that the role has been deleted"
           "").format(config['role'], guild.id)
        )
        return

      # is not streaming; attempt to remove streaming role if present
      if not is_streaming and streaming_role in after.roles:
        try:
          await after.remove_roles(streaming_role,
                                   reason='Member is not streaming.')
        except discord.Forbidden:
          log.warning(
            ("Failed to remove role ID {} from member ID {} (server ID {}): insufficient permissions"
             "").format(streaming_role.id, after.id, guild.id)
          )
        except:
          log.warning(
            ("Failed to remove role ID {} from member ID {} (server ID {})"
             "").format(streaming_role.id, after.id, guild.id)
          )

      # is streaming; attempt to add streaming role if not present
      # and if allowed by promotion settings
      elif is_streaming and streaming_role not in after.roles:
        if self.__can_promote(after, config):
          try:
            await after.add_roles(streaming_role,
                                  reason="Member is streaming.")
          except discord.Forbidden:
            log.warning(
              ("Failed to add role ID {} to member ID {} (server ID {}): insufficient permissions"
               "").format(streaming_role.id, after.id, guild.id)
            )
          except:
            log.warning(
              ("Failed to add role ID {} to member ID {} (server ID {})"
               "").format(streaming_role.id, after.id, guild.id)
            )

  def __can_promote(self, member: discord.Member, config: dict) -> bool:
    """Indicates whether member can be given the streaming role based on the promotion rules defined in config."""

    if not config['promote'] or not config['promote_from']:
      return True

    promote_role = get(member.guild.roles, id=config['promote_from'])

    if promote_role in member.roles:
      return True

    if not config['lax_promote']:
      return False

    return self.__has_role_above(member, promote_role)

  @staticmethod
  def __has_role_above(member: discord.Member, role: discord.Role) -> bool:
    """Indicates whether member has a role which is higher than role in the hierarchy."""

    # if their top role is high enough, then they have a role that's high enough; if not, they don't
    return member.top_role > role
