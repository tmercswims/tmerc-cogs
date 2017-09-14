from copy import deepcopy
import os
import os.path

import discord
from discord.ext import commands
from discord.utils import find

from .utils.dataIO import dataIO
from .utils import checks, chat_formatting as cf


default_settings = {
    "enabled": False,
    "role": None,
    "only": None
}


class StreamRole:

    """Assign a configurable role to anyone who is streaming."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.settings_path = "data/streamrole/settings.json"
        self.settings = dataIO.load_json(self.settings_path)

    @commands.group(pass_context=True, no_pm=True, name="streamroleset")
    @checks.admin_or_permissions(manage_server=True)
    async def _streamroleset(self, ctx: commands.Context):
        """Sets StreamRole settings."""

        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = deepcopy(default_settings)
            dataIO.save_json(self.settings_path, self.settings)
        if "only" not in self.settings[server.id]:
            self.settings[server.id]["only"] = None
            dataIO.save_json(self.settings_path, self.settings)
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @_streamroleset.command(pass_context=True, no_pm=True, name="toggle")
    @checks.admin_or_permissions(manage_server=True)
    async def _toggle(self, ctx: commands.Context):
        """Toggles StreamRole on/off."""

        await self.bot.type()

        server = ctx.message.server
        if (not self.settings[server.id]["enabled"] and
                self.settings[server.id]["role"] is None):
            await self.bot.reply(cf.warning(
                "You need to set the role before turning on StreamRole."
                " Use `{}streamroleset role`".format(ctx.prefix)))
            return

        self.settings[server.id][
            "enabled"] = not self.settings[server.id]["enabled"]
        if self.settings[server.id]["enabled"]:
            await self.bot.reply(
                cf.info("StreamRole is now enabled."))
        else:
            await self.bot.reply(
                cf.info("StreamRole is now disabled."))
        dataIO.save_json(self.settings_path, self.settings)

    @_streamroleset.command(pass_context=True, no_pm=True, name="only")
    @checks.admin_or_permissions(manage_server=True)
    async def _only(self, ctx: commands.Context, role: discord.Role):
        """Sets the role from which to update streamers.

        Only members with this role will be given the streaming
        role when streaming. Set to '@everyone' to reset it."""

        await self.bot.type()

        server = ctx.message.server
        if role.id == server.id:
            self.settings[server.id]["only"] = None
        else:
            self.settings[server.id]["only"] = role.id
        dataIO.save_json(self.settings_path, self.settings)

        await self.bot.reply(
            cf.info("Only members with the role `{}` will be given the "
                    "streaming role now. Set it to `@everyone` to "
                    "reset it.".format(role.name)))

    @_streamroleset.command(pass_context=True, no_pm=True, name="role")
    @checks.admin_or_permissions(manage_server=True)
    async def _role(self, ctx: commands.Context, role: discord.Role):
        """Sets the role that StreamRole assigns to
        members that are streaming.
        """

        await self.bot.type()

        server = ctx.message.server
        self.settings[server.id]["role"] = role.id
        dataIO.save_json(self.settings_path, self.settings)

        await self.bot.reply(
            cf.info("Any member who is streaming will now be given the "
                    "role `{}`. Ensure you also toggle the cog on with "
                    "`{}streamroleset toggle`.".format(role.name, ctx.prefix)))

    async def stream_listener(self, before: discord.Member,
                              after: discord.Member):
        if before.server.id not in self.settings:
            self.settings[before.server.id] = deepcopy(default_settings)
            dataIO.save_json(self.settings_path, self.settings)
        elif "only" not in self.settings[before.server.id]:
            self.settings[before.server.id]["only"] = None
            dataIO.save_json(self.settings_path, self.settings)

        server_settings = self.settings[before.server.id]
        if server_settings["enabled"] and server_settings["role"] is not None:
            streamer_role = find(lambda m: m.id == server_settings["role"],
                                 before.server.roles)
            only_role = find(lambda l: l.id == server_settings["only"],
                             before.server.roles)
            if streamer_role is None:
                return

            # is streaming
            if (after.game is not None and
                    after.game.type == 1 and
                    streamer_role not in after.roles):
                if (only_role is None or only_role in after.roles):
                    try:
                        await self.bot.add_roles(after, streamer_role)
                    except discord.Forbidden:
                        print("StreamRole: forbidden error\n"
                              "Server: {}, Role: {}, Member: {}".format(
                                  before.server.id, streamer_role.id, after.id)
                              )

            # is not
            elif ((after.game is None or after.game.type != 1) and
                  streamer_role in after.roles):
                try:
                    await self.bot.remove_roles(after, streamer_role)
                except discord.Forbidden:
                    print("StreamRole: forbidden error\n"
                          "Server: {}, Role: {}, Member: {}".format(
                              before.server.id, streamer_role.id, after.id))


def check_folders():
    if not os.path.exists("data/streamrole"):
        print("Creating data/streamrole directory...")
        os.makedirs("data/streamrole")


def check_files():
    f = "data/streamrole/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating data/streamrole/settings.json...")
        dataIO.save_json(f, {})


def setup(bot: commands.Bot):
    check_folders()
    check_files()
    n = StreamRole(bot)
    bot.add_listener(n.stream_listener, "on_member_update")

    bot.add_cog(n)
