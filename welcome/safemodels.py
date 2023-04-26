import discord


class SafeMember:
    def __init__(self, member: discord.Member) -> None:
        self.name = str(member.name)
        self.display_name = str(member.display_name)
        self.nick = str(getattr(member, "nick", ""))
        self.id = str(member.id)
        self.mention = str(member.mention)
        self.discriminator = str(member.discriminator)
        self.color = str(member.color)
        self.colour = str(member.colour)
        self.created_at = str(member.created_at)

    def __str__(self):
        return self.name

    def __getattr__(self, name):
        return self


class SafeRole:
    def __init__(self, role: discord.Role) -> None:
        self.name = str(role.name)
        self.id = str(role.id)
        self.mention = str(role.mention)
        self.color = str(role.color)
        self.colour = str(role.colour)
        self.position = str(role.position)
        self.created_at = str(role.created_at)

    def __str__(self):
        return self.name

    def __getattr__(self, name):
        return self


class SafeGuild:
    def __init__(self, guild: discord.Guild) -> None:
        self.name = str(guild.name)
        self.id = str(guild.id)
        self.description = str(guild.description)
        self.created_at = str(guild.created_at)

    def __str__(self):
        return self.name

    def __getattr__(self, name):
        return self
