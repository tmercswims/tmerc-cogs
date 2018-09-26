import logging

import discord
from redbot.core import commands, checks

__author__ = "tmerc"

log = logging.getLogger('red.tmerc.massdm')


class MassDM:
  """Send a direct message to all members of the specified Role."""

  def __init__(self):
    pass

  @commands.command(aliases=['mdm'])
  @commands.guild_only()
  @checks.admin_or_permissions(manage_guild=True)
  async def massdm(self, ctx: commands.Context, role: discord.Role, *, message: str):
    """Sends a DM to all Members with the given Role.

    Allows for the following customizations:
      `{member}` is the member being messaged
      `{role}` is the role through which they are being messaged
      `{server}` is the server through which they are being messaged
      `{sender}` is you, the person sending the message
    """

    try:
      await ctx.message.delete()
    except discord.Forbidden:
      log.warning("Failed to delete command message: insufficient permissions")
    except:
      log.warning("Failed to delete command message")

    for member in role.members:
      try:
        await member.send(message.format(member=member, role=role, server=ctx.guild, sender=ctx.author))
      except discord.Forbidden:
        log.warning("Failed to DM user {0} (ID {0.id}): insufficient permissions".format(member))
        continue
      except:
        log.warning("Failed to DM user {0} (ID {0.id})".format(member))
        continue
