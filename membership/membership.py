import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils import checks, chat_formatting as cf
from __main__ import send_cmd_help

import os

default_settings = {
    "join_message": "{0.mention} has joined the server.",
    "leave_message": "{0.mention} has left the server.",
    "ban_message": "{0.mention} has been banned.",
    "unban_message": "{0.mention} has been unbanned.",
    "on": False,
    "channel": None
}

class Membership:
    """Announces membership events on the server."""

    def __init__(self, bot):
        self.bot = bot
        self.settings_path = "data/membership/settings.json"
        self.settings = fileIO(self.settings_path, "load")

    @commands.group(pass_context=True, no_pm=True, name="membershipset")
    @checks.admin_or_permissions(manage_server=True)
    async def _membershipset(self, context):
        """Sets membership settings."""
        server = context.message.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            self.settings[server.id]["channel"] = server.default_channel.id
            fileIO(self.settings_path, "save", self.settings)
        if context.invoked_subcommand is None:
            await send_cmd_help(context)

    @_membershipset.command(pass_context=True, no_pm=True, name="join", aliases=["greeting", "welcome"])
    async def _join(self, context, *, format_str):
        """Sets the join/greeting/welcome message for the server.
        {0} is the member
        {1} is the server
        """

        await self.bot.type()
        server = context.message.server
        self.settings[server.id]["join_message"] = format_str
        fileIO(self.settings_path, "save", self.settings)
        await self.bot.reply(cf.info("Join message set."))

    @_membershipset.command(pass_context=True, no_pm=True, name="leave", aliases=["farewell"])
    async def _leave(self, context, *, format_str):
        """Sets the leave/farewell message for the server.
        {0} is the member
        {1} is the server
        """

        await self.bot.type()
        server = context.message.server
        self.settings[server.id]["leave_message"] = format_str
        fileIO(self.settings_path, "save", self.settings)
        await self.bot.reply(cf.info("Leave message set."))

    @_membershipset.command(pass_context=True, no_pm=True, name="ban")
    async def _ban(self, context, *, format_str):
        """Sets the ban message for the server.
        {0} is the member
        {1} is the server
        """

        await self.bot.type()
        server = context.message.server
        self.settings[server.id]["ban_message"] = format_str
        fileIO(self.settings_path, "save", self.settings)
        await self.bot.reply(cf.info("Ban message set."))

    @_membershipset.command(pass_context=True, no_pm=True, name="unban")
    async def _unban(self, context, *, format_str):
        """Sets the unban message for the server.
        {0} is the member
        {1} is the server
        """

        await self.bot.type()
        server = context.message.server
        self.settings[server.id]["unban_message"] = format_str
        fileIO(self.settings_path, "save", self.settings)
        await self.bot.reply(cf.info("Unban message set."))

    @_membershipset.command(pass_context=True, no_pm=True, name="toggle")
    async def _toggle(self, context):
        """Turns membership event commands on or off."""

        await self.bot.type()
        server = context.message.server
        self.settings[server.id]["on"] = not self.settings[server.id]["on"]
        if self.settings[server.id]["on"]:
            await self.bot.reply(cf.info("Membership events will now be announced."))
        else:
            await self.bot.reply(cf.info("Membership events will no longer be announced."))
        fileIO(self.settings_path, "save", self.settings)

    @_membershipset.command(pass_context=True, no_pm=True, name="channel")
    async def _channel(self, context, channel: discord.Channel=None):
        """Sets the text channel to which the announcements will be sent. If none is specified, the default will be used."""

        await self.bot.type()
        server = context.message.server
        
        if not channel:
            channel = server.default_channel

        if not self.speak_permissions(server, channel):
            await self.bot.reply("I don't have permission to send messages in {0.mention}.".format(channel))
            return
        self.settings[server.id]["channel"] = channel.id
        fileIO(self.settings_path, "save", self.settings)
        channel = self.get_welcome_channel(server)
        await self.bot.send_message(channel, ("{0.mention}, " + cf.info("I will now send membership announcements to {1.mention}.")).format(context.message.author, channel))

    async def member_join(self, member):
        await self.bot.type()

        server = member.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            self.settings[server.id]["channel"] = server.default_channel.id
            fileIO(self.settings_path, "save", self.settings)

        if not self.settings[server.id]["on"]:
            return

        if server == none:
            print("The server was None, so this was either a PM or an error. The user was {}.".format(member.name))
            return

        channel = self.get_welcome_channel(server)
        if self.speak_permissions(server, channel):
            await self.bot.send_message(channel, self.settings[server.id]["join_message"].format(member, server))
        else:
            print("Tried to send message to channel, but didn't have permission. User was {}.".format(member.name))

    async def member_leave(self, member):
        await self.bot.type()

        server = member.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            self.settings[server.id]["channel"] = server.default_channel.id
            fileIO(self.settings_path, "save", self.settings)

        if not self.settings[server.id]["on"]:
            return

        if server == none:
            print("The server was None, so this was either a PM or an error. The user was {}.".format(member.name))
            return

        channel = self.get_welcome_channel(server)
        if self.speak_permissions(server, channel):
            await self.bot.send_message(channel, self.settings[server.id]["leave_message"].format(member, server))
        else:
            print("Tried to send message to channel, but didn't have permission. User was {}.".format(member.name))

    async def member_ban(self, member):
        await self.bot.type()

        server = member.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            self.settings[server.id]["channel"] = server.default_channel.id
            fileIO(self.settings_path, "save", self.settings)

        if not self.settings[server.id]["on"]:
            return

        if server == none:
            print("The server was None, so this was either a PM or an error. The user was {}.".format(member.name))
            return

        channel = self.get_welcome_channel(server)
        if self.speak_permissions(server, channel):
            await self.bot.send_message(channel, self.settings[server.id]["ban_message"].format(member, server))
        else:
            print("Tried to send message to channel, but didn't have permission. User was {}.".format(member.name))

    async def member_unban(self, member):
        await self.bot.type()

        server = member.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            self.settings[server.id]["channel"] = server.default_channel.id
            fileIO(self.settings_path, "save", self.settings)

        if not self.settings[server.id]["on"]:
            return

        if server == none:
            print("The server was None, so this was either a PM or an error. The user was {}.".format(member.name))
            return

        channel = self.get_welcome_channel(server)
        if self.speak_permissions(server, channel):
            await self.bot.send_message(channel, self.settings[server.id]["unban_message"].format(member, server))
        else:
            print("Tried to send message to channel, but didn't have permission. User was {}.".format(member.name))

    def get_welcome_channel(self, server):
        return server.get_channel(self.settings[server.id]["channel"])

    def speak_permissions(self, server, channel=None):
        if not channel:
            channel = self.get_welcome_channel(server)
        return server.get_member(self.bot.user.id).permissions_in(channel).send_messages

def check_folders():
    if not os.path.exists("data/membership"):
        print("Creating data/membership directory...")
        os.makedirs("data/membership")

def check_files():
    f = "data/membership/settings.json"
    if not fileIO(f, "check"):
        print("Creating data/membership/settings.json...")
        fileIO(f, "save", {})

def setup(bot):
    check_folders()
    check_files()
    n = Membership(bot)
    bot.add_listener(n.member_join, "on_member_join")
    bot.add_listener(n.member_leave, "on_member_remove")
    bot.add_listener(n.member_ban, "on_member_ban")
    bot.add_listener(n.member_unban, "on_member_unban")

    bot.add_cog(n)
