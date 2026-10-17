import asyncio
import logging

import discord
from redbot.core import Config, checks, commands

from .safemodels import SafeGuild, SafeMember, SafeRole

__author__ = "tmerc"
log = logging.getLogger("red.tmerc.massdm")


class MassDM(commands.Cog):
    """Send a direct message to all members of the specified Role."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.config = Config.get_conf(self, identifier=5432453235468645642)
        default_member = {"opted_out": False}
        self.config.register_member(**default_member)

    async def get_opted_out_users(self, guild_id: int) -> set:
        """Get set of user IDs who have opted out of mass DMs"""
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return set()

        opted_out = set()
        for member in guild.members:
            if await self.config.member(member).opted_out():
                opted_out.add(member.id)
        return opted_out

    @commands.hybrid_command(aliases=["mdm"])
    @discord.app_commands.describe(
        role="The role whose members are to be messaged.",
        message="The message to send. Allows for customizations using {member}, {role}, {server}, and {sender}.",
    )
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    async def massdm(
        self, ctx: commands.Context, role: discord.Role, *, message: str
    ) -> None:
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
        except discord.DiscordException:
            log.warning("Failed to delete command message")

        opted_out_users = await self.get_opted_out_users(ctx.guild.id)

        for member in [
            m for m in role.members if not m.bot and m.id not in opted_out_users
        ]:
            try:
                await member.send(
                    message.format(
                        member=SafeMember(member),
                        role=SafeRole(role),
                        server=SafeGuild(ctx.guild),
                        guild=SafeGuild(ctx.guild),
                        sender=SafeMember(ctx.author),
                    )
                )
                await asyncio.sleep(1.5)
            except discord.Forbidden:
                log.warning(
                    f"Failed to DM user {member} (ID {member.id}): insufficient permissions"
                )
                continue
            except discord.DiscordException:
                log.warning(f"Failed to DM user {member} (ID {member.id})")
                continue

    @commands.command()
    async def massdmoptout(self, ctx: commands.Context) -> None:
        """Opt out of receiving mass DMs from this bot."""
        await self.config.member(ctx.author).opted_out.set(True)
        await ctx.send(
            "You have opted out of mass DMs. Use `massdmoptin` to re-enable.",
            delete_after=10,
        )

    @commands.command()
    async def massdmoptin(self, ctx: commands.Context) -> None:
        """Opt back in to receiving mass DMs from this bot."""
        await self.config.member(ctx.author).opted_out.set(False)
        await ctx.send(
            "You have opted back in to mass DMs. Use `massdmoptout` to disable.",
            delete_after=10,
        )
