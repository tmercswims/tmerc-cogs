import logging

import discord
from redbot.core import Config, checks, commands
from redbot.core.utils.chat_formatting import box

__author__ = "tmerc"

log = logging.getLogger("red.tmerc.streamrole")


class StreamRole(commands.Cog):
    """Assign a configurable role to anyone who is streaming."""

    guild_defaults = {
        "enabled": False,
        "role": None,
        "promote": False,
        "promote_from": None,
        "lax_promote": False,
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.config = Config.get_conf(self, 34507445)
        self.config.register_guild(**self.guild_defaults)

    @commands.hybrid_group(aliases=["streamroleset"], fallback="state")
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    async def streamrole(self, ctx: commands.Context) -> None:
        """Get current StreamRole settings."""

        await ctx.typing()

        if ctx.invoked_subcommand is None:
            guild: discord.Guild = ctx.guild
            config = await self.config.guild(guild).all()
            enabled = config["enabled"]
            role = config["role"]
            if role is not None:
                role: discord.Role = discord.utils.get(ctx.guild.roles, id=role)
            promote = config["promote"]
            promote_from = config["promote_from"]
            if promote_from is not None:
                promote_from: discord.Role = discord.utils.get(ctx.guild.roles, id=promote_from)
            lax_promote = config["lax_promote"]

            if await ctx.embed_requested():
                emb = discord.Embed(color=await ctx.embed_color(), title="Current StreamRole Settings")
                emb.add_field(name="Enabled", value=enabled)
                emb.add_field(name="Streaming Role", value=(role and role.name))
                emb.add_field(name="Only Promote Members With Prerequisite Role", value=promote)
                emb.add_field(name="Promotion Prerequisite Role", value=(promote_from and promote_from.name))
                emb.add_field(name="Promote from Prerequisite and Above", value=lax_promote)

                await ctx.send(embed=emb)
            else:
                msg = box(
                    f"  Enabled: {enabled}\n"
                    f"  Streaming role: {role and role.name}\n"
                    f"  Only promote members with prerequisite role: {promote}\n"
                    f"  Promotion prerequisite role: {promote_from and promote_from.name}\n"
                    f"  Promote from prerequisite and above: {lax_promote}",
                    "Current StreamRole Settings",
                )

                await ctx.send(msg)

    @streamrole.command(name="toggle")
    async def streamrole_toggle(self, ctx: commands.Context, on_off: bool = None) -> None:
        """Turns StreamRole on or off.

        If `on_off` is not provided, the state will be flipped.
        """

        await ctx.typing()

        guild: discord.Guild = ctx.guild
        target_state = on_off if on_off is not None else not (await self.config.guild(guild).enabled())

        streaming_role = await self.config.guild(guild).role()
        if streaming_role is None and target_state:
            await ctx.send(
                f"You need to set a role with `{ctx.prefix}streamroleset role` before you can enable StreamRole."
            )
            return

        await self.config.guild(guild).enabled.set(target_state)

        if target_state:
            await ctx.send("StreamRole is now enabled.")
        else:
            await ctx.send("StreamRole is now disabled.")

    @streamrole.command(name="role")
    async def streamrole_role(self, ctx: commands.Context, *, role: discord.Role) -> None:
        """Sets the role which will be assigned to members who are streaming."""

        await self.config.guild(ctx.guild).role.set(role.id)

        await ctx.send(
            f"Done. Members who are streaming will now be given the role `{role.name}`. "
            f"Ensure you also turn on StreamRole with `{ctx.prefix}streamroleset toggle`."
        )

    @streamrole.group(name="promote")
    async def streamrole_promote(self, ctx: commands.Context) -> None:
        """Changes promotion settings."""

        pass

    @streamrole_promote.command(name="toggle")
    async def streamrole_promote_toggle(self, ctx: commands.Context, on_off: bool = None) -> None:
        """Turns promote role prerequisite on or off.

        If `on_off` is not provided, the state will be flipped.
        """

        guild: discord.Guild = ctx.guild
        target_state = on_off if on_off is not None else not (await self.config.guild(guild).promote())

        prereq_role = await self.config.guild(guild).promote_from()
        if prereq_role is None and target_state:
            await ctx.send(
                f"You need to set a role with `{ctx.prefix}streamroleset promote role` before you can enable "
                "promotion role prerequisite."
            )
            return
        prereq_role: discord.Role = discord.utils.get(guild.roles, id=prereq_role)

        await self.config.guild(guild).promote.set(target_state)

        if target_state:
            await ctx.send(
                "Done. Promote role prerequisite is now enabled. "
                f"Only members with the role `{prereq_role.name}` will be given the streaming role."
            )
        else:
            await ctx.send(
                "Done. Promote role prerequisite is now disabled. "
                "All members who are streaming will be given the streaming role."
            )

    @streamrole_promote.command(name="role")
    async def streamrole_promote_role(self, ctx: commands.Context, *, role: discord.Role) -> None:
        """Sets the prerequisite role for streaming promotion.

        If this role is set and promote is toggled on, only members with this role will be given the streaming role.
        """

        await self.config.guild(ctx.guild).promote_from.set(role.id)

        await ctx.send(f"Done. Only members with the role `{role.name}` will be given the streaming role.")

    @streamrole_promote.command(name="lax")
    async def streamrole_promote_lax(self, ctx: commands.Context, on_off: bool = None) -> None:
        """Turns lax promote role prerequisite on or off.

        If this is on, members with the prerequisite role or any role above it in the hierarchy will be given the
        streaming role. If it is off, only members with exactly the prerequisite role will be given the streaming role.

        If `on_off` is not provided, the state will be flipped.
        """

        guild: discord.Guild = ctx.guild
        target_state = on_off if on_off is not None else not (await self.config.guild(guild).lax_promote())

        await self.config.guild(guild).lax_promote.set(target_state)

        if target_state:
            await ctx.send(
                "Lax promotion is now on. If promotion prerequisite is enabled, any member with the prerequisite "
                "role or any role above it in the hierarchy will be given the streaming role."
            )
        else:
            await ctx.send(
                "Lax promotion is now off. If promotion prerequisite is enabled, only members with exactly the "
                "prerequisite role will be given the streaming role."
            )

    @commands.Cog.listener()
    async def on_presence_update(self, _, after: discord.Member) -> None:
        """Listens to member updates to detect starting/stopping streaming."""

        guild: discord.Guild = after.guild
        config = await self.config.guild(guild).all()
        is_streaming = any(a.type == discord.ActivityType.streaming for a in after.activities)
        if config["enabled"] and config["role"] is not None:
            streaming_role: discord.Role = discord.utils.get(guild.roles, id=config["role"])

            if streaming_role is None:
                log.error(
                    f"Failed to find streaming role with ID {config['role']} (server ID {guild.id}); "
                    "this likely means that the role has been deleted"
                )
                return

            # is not streaming; attempt to remove streaming role if present
            if not is_streaming and streaming_role in after.roles:
                try:
                    await after.remove_roles(streaming_role, reason="Member is not streaming.")
                except discord.Forbidden:
                    log.warning(
                        f"Failed to remove role ID {streaming_role.id} from member ID {after.id} "
                        f"(server ID {guild.id}): insufficient permissions"
                    )
                except discord.DiscordException:
                    log.warning(
                        f"Failed to remove role ID {streaming_role.id} from member ID {after.id} (server ID {guild.id})"
                    )

            # is streaming; attempt to add streaming role if not present
            # and if allowed by promotion settings
            elif is_streaming and streaming_role not in after.roles:
                if StreamRole.__can_promote(after, config):
                    try:
                        await after.add_roles(streaming_role, reason="Member is streaming.")
                    except discord.Forbidden:
                        log.warning(
                            f"Failed to add role ID {streaming_role.id} to member ID {after.id} "
                            f"(server ID {guild.id}): insufficient permissions"
                        )
                    except discord.DiscordException:
                        log.warning(
                            f"Failed to add role ID {streaming_role.id} to member ID {after.id} (server ID {guild.id})"
                        )

    @staticmethod
    def __can_promote(member: discord.Member, config: dict) -> bool:
        """Indicates whether member can be given the streaming role based on the promotion rules defined in config."""

        if not config["promote"] or not config["promote_from"]:
            return True

        promote_role: discord.Role = discord.utils.get(member.guild.roles, id=config["promote_from"])

        if promote_role in member.roles:
            return True

        if not config["lax_promote"]:
            return False

        return StreamRole.__has_role_above(member, promote_role)

    @staticmethod
    def __has_role_above(member: discord.Member, role: discord.Role) -> bool:
        """Indicates whether member has a role which is higher than role in the hierarchy."""

        # if their top role is high enough, then they have a role that's high enough; if not, they don't
        return member.top_role > role
