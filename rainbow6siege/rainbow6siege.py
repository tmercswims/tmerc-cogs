import asyncio
from copy import deepcopy
import os
import os.path

import discord
from discord.ext import commands
try:
    import r6sapi
    r6sapi_available = True
except:
    r6sapi_available = False

from .utils.dataIO import dataIO
from .utils import checks, chat_formatting as cf


class BadPlatformError(Exception):
    pass


class Rainbow6Siege:

    """Get Rainbow 6: Siege player information:
    rank, operator and weapon stats, and more.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.settings_path = "data/rainbow6siege/settings.json"
        self.settings = dataIO.load_json(self.settings_path)

        self.platform_map = {
            "uplay": r6sapi.Platforms.UPLAY,
            "xbox": r6sapi.Platforms.XBOX,
            "playstation": r6sapi.Platforms.PLAYSTATION
        }
        self.region_map = {
            "na": r6sapi.RankedRegions.NA,
            "eu": r6sapi.RankedRegions.EU,
            "asia": r6sapi.RankedRegions.ASIA
        }
        self.operator_list = [
            x.lower() for x in r6sapi.OperatorIcons if x != 'DEFAULT'
        ]

    async def get_player(self, player: str, platform: str) -> r6sapi.Player:
        if platform not in r6sapi.valid_platforms:
            await self.bot.reply(cf.error("Unknown platform `{}`. Must be one "
                                          "of `uplay`, `xbox`, or "
                                          "`playstation`.".format(platform)))
            return None

        plat = self.platform_map[platform]

        try:
            p = await r6sapi.Auth(email=self.settings["email"],
                                  password=self.settings["password"]
                                  ).get_player(player, plat)
        except r6sapi.InvalidRequest:
            await self.bot.reply(cf.error(
                "Player `{}` not found on platform `{}`.".format(
                    player, platform)))
            return None

        return p

    @commands.group(pass_context=True, no_pm=False, name="r6sset")
    @checks.is_owner()
    async def _r6sset(self, ctx: commands.Context):
        """Change cog settings."""

        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @_r6sset.command(no_pm=False, name="credentials")
    async def _credentials(self, email: str, password: str):
        """Sets the credentials used to access Ubisoft.

        Use this command in direct message to keep your
        credentials secret.
        """

        self.settings["email"] = email
        self.settings["password"] = password

        dataIO.save_json(self.settings_path, self.settings)

        await self.bot.say("Credentials set.")

    @commands.group(pass_context=True, no_pm=True, name="r6s",
                    aliases=["rsixs", "rainbow6", "rainbowsix"])
    async def _r6s(self, ctx: commands.Context):
        """Get Rainbow 6: Siege player information."""

        await self.bot.type()

        if self.settings["email"] is None or \
                self.settings["password"] is None:
            await self.bot.reply(
                cf.error("The owner needs to set credentials first.\n"
                         "See: `{}r6sset`".format(ctx.prefix)))
            return

        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @_r6s.command(pass_context=True, no_pm=True, name="profile")
    async def _profile(self, ctx: commands.Context,
                       player: str, platform: str="uplay"):
        """Get the profile for the given player.

        'platform' must be one of 'uplay', 'xbox', or 'playstation', and
        defaults to 'uplay'.
        """

        p = await self.get_player(player, platform)
        if p is None:
            return

        await p.check_general()
        await p.check_level()

        e = discord.Embed(description="Player Summary")
        e.set_author(name=p.name, url=p.url)
        e.set_thumbnail(url=p.icon_url)
        e.add_field(name="Level", value=p.level)
        e.add_field(name="XP", value=p.xp)
        e.add_field(name="Platform", value=p.platform)

        await self.bot.say(embed=e)

    @_r6s.command(pass_context=True, no_pm=True, name="stats")
    async def _stats(self, ctx: commands.Context,
                     player: str, platform: str="uplay"):
        """Get stats for the given player.

        'platform' must be one of 'uplay', 'xbox', or 'playstation', and
        defaults to 'uplay'.
        """

        p = await self.get_player(player, platform)
        if p is None:
            return

        await p.check_general()

        e = discord.Embed(description="Player Stats")
        e.set_author(name=p.name, url=p.url, icon_url=p.icon_url)
        e.add_field(name="Kill/Death",
                    value="**Kills:** {}\n"
                    "**Deaths:** {}\n"
                    "**Assists:** {}\n"
                    "**K/D:** {}".format(p.kills, p.deaths, p.kill_assists,
                                         "{0:.2f}".format(
                                             p.kills /
                                             (p.deaths if p.deaths > 0 else 1)
                                         ))
                    )
        e.add_field(name="Win/Loss",
                    value="**Wins:** {}\n"
                    "**Losses:** {}\n"
                    "**Win Percent:** {}%\n".format(
                        p.matches_won, p.matches_lost,
                        "{0:.2f}".format(
                            (p.matches_won /
                             (p.matches_won + p.matches_lost)) * 100))
                    )
        e.add_field(name="Shots",
                    value="**Fired:** {}\n"
                    "**Hit:**: {}\n"
                    "**Accuracy:** {}%\n"
                    "**Headshots:** {}".format(
                        p.bullets_fired, p.bullets_hit,
                        "{0:.2f}".format(
                            (p.bullets_hit /
                                (p.bullets_fired if p.bullets_fired > 0 else 1)) * 100),
                        p.headshots)
                    )
        e.add_field(name="Other",
                    value="**Injures:** {}\n"
                    "**Injure Assists:** {}\n"
                    "**Penetration Kills:** {}\n"
                    "**Melee Kills:** {}\n"
                    "**Blind Kills:** {}\n"
                    "**Revives:** {}\n"
                    "**Revives Denied:** {}".format(
                        p.dbnos, p.dbno_assists, p.penetration_kills,
                        p.melee_kills, p.blind_kills, p.revives,
                        p.revives_denied)
                    )
        e.add_field(name="Other",
                    value="**Suicides:** {}\n"
                    "**Barricades:** {}\n"
                    "**Reinforcements:** {}\n"
                    "**Gadgets Destroyed:** {}\n"
                    "**Rappel Breaches:** {}\n"
                    "**Distance Travelled:** {}km\n"
                    "**Playtime:** {}".format(
                        p.suicides, p.barricades_deployed,
                        p.reinforcements_deployed, p.gadgets_destroyed,
                        p.rappel_breaches,
                        "{0:.2f}".format(p.distance_travelled / 1000),
                        "{}h, {}m".format(*divmod(
                            divmod(p.time_played, 60)[0], 60)))
                    )

        await self.bot.say(embed=e)

    @_r6s.command(pass_context=True, no_pm=True, name="rank")
    async def _rank(self, ctx: commands.Context,
                    player: str, season: int=-1, region: str="na",
                    platform: str="uplay"):
        """Get rank for the given player.

        'season' should be a number indicating the season, or -1 to
        get the current season.

        'region' must be one of 'na', 'eu', or 'asia', and defaults to 'na'.

        'platform' must be one of 'uplay', 'xbox', or 'playstation', and
        defaults to 'uplay'.
        """

        p = await self.get_player(player, platform)
        if p is None:
            return

        if region not in r6sapi.valid_regions:
            await self.bot.reply(cf.error("Unknown region `{}`. Must be one "
                                          "of `na`, `eu`, or "
                                          "`asia`.".format(region)))
            return

        r = await p.get_rank(self.region_map[region], season)

        e = discord.Embed(
            description="Ranked Information for season {} in the {} "
            "region on {}".format(r.season, r.region, p.platform))
        e.set_author(name=p.name, url=p.url, icon_url=p.icon_url)
        e.set_thumbnail(url=r.get_icon_url())
        e.add_field(name="Rank",
                    value="**Current:** {}\n"
                    "**Best:** {}".format(r.rank,
                                          r6sapi.Rank.RANKS[r.max_rank])
                    )
        e.add_field(name="MMR",
                    value="**Current:** {}\n"
                    "**Next Rank:** {}\n"
                    "**Best:** {}".format(round(r.mmr), round(r.next_rank_mmr),
                                          round(r.max_mmr))
                    )
        e.add_field(name="Stats",
                    value="**Wins:** {}\n"
                    "**Losses:** {} \n"
                    "**Abandons:** {}\n"
                    "**Win Percent:** {}%".format(
                        r.wins, r.losses, r.abandons,
                        "{0:.2f}".format(
                            (r.wins / (r.wins + r.losses) if
                                (r.wins + r.losses) > 0 else 1) * 100))
                    )
        e.add_field(name="Skill",
                    value="**Mean:** {0:.2f}\n"
                    "**Standard Deviation:** {1:.2f}".format(
                        r.skill_mean, r.skill_stdev)
                    )

        await self.bot.say(embed=e)

    @_r6s.command(pass_context=True, no_pm=True, name="operator")
    async def _operator(self, ctx: commands.Context,
                        player: str, operator: str, platform: str="uplay"):
        """Get operator stats for the given player and operator.

        'platform' must be one of 'uplay', 'xbox', or 'playstation', and
        defaults to 'uplay'.
        """

        if operator not in self.operator_list:
            await self.bot.reply(cf.error(
                "Unknown operator `{}`. Must be one of {}.".format(
                    operator,
                    ", ".join(["`" + x + "`" for x in self.operator_list]))))
            return

        p = await self.get_player(player, platform)
        if p is None:
            return

        o = await p.get_operator(operator)

        e = discord.Embed(
            description="Player Information for {}".format(
                o.name.capitalize()))
        e.set_author(name=p.name, url=p.url, icon_url=p.icon_url)
        e.set_thumbnail(url=r6sapi.OperatorIcons[o.name.upper()])
        e.add_field(name="Win/Loss",
                    value="**Wins:** {}\n"
                    "**Losses:** {}\n"
                    "**Win Percent:** {}%".format(
                        o.wins, o.losses,
                        "{0:.2f}".format(
                            (o.wins / (o.wins + o.losses) if
                             (o.wins + o.losses) > 0 else 1) * 100))
                    )
        e.add_field(name="Kill/Death",
                    value="**Kills:** {}\n"
                    "**Deaths:** {}\n"
                    "**K/D:** {}".format(
                        o.kills, o.deaths,
                        "{0:.2f}".format(o.kills /
                                         (o.deaths if o.deaths > 0 else 1)))
                    )
        e.add_field(name=o.statistic_name, value=o.statistic)
        e.add_field(name="Other",
                    value="**Injures:** {}\n"
                    "**Headshots:** {}\n"
                    "**Melee Kills:** {}\n"
                    "**Time Played:** {}".format(
                        o.dbnos, o.headshots, o.melees,
                        "{}h, {}m".format(*divmod(
                            divmod(o.time_played, 60)[0], 60)))
                    )

        await self.bot.say(embed=e)

    @_r6s.command(pass_context=True, no_pm=True, name="weapons")
    async def _weapons(self, ctx: commands.Context,
                       player: str, platform: str="uplay"):
        """Get weapon stats for the given player.

        'platform' must be one of 'uplay', 'xbox', or 'playstation', and
        defaults to 'uplay'.
        """

        p = await self.get_player(player, platform)
        if p is None:
            return

        weapons = await p.check_weapons()

        e = discord.Embed(
            description="Player Weapon Statistics")
        e.set_author(name=p.name, url=p.url, icon_url=p.icon_url)

        for w in weapons:
            e.add_field(name=w.name,
                        value="**Kills:** {}\n"
                        "**Headshots:** {}\n"
                        "**Shots:** {}\n"
                        "**Hits:** {}\n"
                        "**Accuracy:** {}%".format(
                            w.kills, w.headshots, w.shots, w.hits,
                            "{0:.2f}".format((w.hits / w.shots if
                                              w.shots > 0 else 1) * 100))
                        )

        await self.bot.say(embed=e)

    @_r6s.command(pass_context=True, no_pm=True, name="gametypes")
    async def _gametypes(self, ctx: commands.Context,
                         player: str, platform: str="uplay"):
        """Get gametype information for the given player.

        'platform' must be one of 'uplay', 'xbox', or 'playstation', and
        defaults to 'uplay'.
        """

        p = await self.get_player(player, platform)
        if p is None:
            return

        gamemodes = await p.check_gamemodes()

        e = discord.Embed(
            description="Player Gametype Statistics")
        e.set_author(name=p.name, url=p.url, icon_url=p.icon_url)

        for g in gamemodes.values():
            e.add_field(name=g.name,
                        value="**Wins:** {}\n"
                        "**Losses:** {}\n"
                        "**Win Percent:** {}%\n"
                        "**Best Score:** {}".format(
                            g.won, g.lost,
                            "{0:.2f}".format((g.won / g.played if
                                              g.played > 0 else 1) * 100),
                            g.best_score)
                        )

        await self.bot.say(embed=e)

    @_r6s.command(pass_context=True, no_pm=True, name="ranked")
    async def _ranked(self, ctx: commands.Context,
                      player: str, platform: str="uplay"):
        """Get ranked stats for the given player.

        'platform' must be one of 'uplay', 'xbox', or 'playstation', and
        defaults to 'uplay'.
        """

        p = await self.get_player(player, platform)
        if p is None:
            return

        await p.check_queues()

        q = p.ranked

        e = discord.Embed(
            description="Player Ranked Queue Statistics")
        e.set_author(name=p.name, url=p.url, icon_url=p.icon_url)

        e.add_field(name="Win/Loss",
                    value="**Wins:** {}\n"
                    "**Losses:** {}\n"
                    "**Win Percent:** {}%\n"
                    "**Playtime:** {}".format(
                        q.won, q.lost,
                        "{0:.2f}".format((q.won / q.played if
                                          q.played > 0 else 1) * 100),
                        "{}h, {}m".format(*divmod(
                            divmod(q.time_played, 60)[0], 60)))
                    )
        e.add_field(name="Kill/Death",
                    value="**Kills:** {}\n"
                    "**Deaths:** {}\n"
                    "**K/D:** {}".format(
                        q.kills, q.deaths,
                        "{0:.2f}".format(q.kills /
                                         (q.deaths if q.deaths > 0 else 1)))
                    )

        await self.bot.say(embed=e)

    @_r6s.command(pass_context=True, no_pm=True, name="casual")
    async def _casual(self, ctx: commands.Context,
                      player: str, platform: str="uplay"):
        """Get casual stats for the given player.

        'platform' must be one of 'uplay', 'xbox', or 'playstation', and
        defaults to 'uplay'.
        """

        p = await self.get_player(player, platform)
        if p is None:
            return

        await p.check_queues()

        q = p.casual

        e = discord.Embed(
            description="Player Casual Queue Statistics")
        e.set_author(name=p.name, url=p.url, icon_url=p.icon_url)

        e.add_field(name="Win/Loss",
                    value="**Wins:** {}\n"
                    "**Losses:** {}\n"
                    "**Win Percent:** {}%\n"
                    "**Playtime:** {}".format(
                        q.won, q.lost,
                        "{0:.2f}".format((q.won / q.played if
                                          q.played > 0 else 1) * 100),
                        "{}h, {}m".format(*divmod(
                            divmod(q.time_played, 60)[0], 60)))
                    )
        e.add_field(name="Kill/Death",
                    value="**Kills:** {}\n"
                    "**Deaths:** {}\n"
                    "**K/D:** {}".format(
                        q.kills, q.deaths,
                        "{0:.2f}".format(q.kills /
                                         (q.deaths if q.deaths > 0 else 1)))
                    )

        await self.bot.say(embed=e)

    @_r6s.command(pass_context=True, no_pm=True, name="thunt")
    async def _thunt(self, ctx: commands.Context,
                     player: str, platform: str="uplay"):
        """Get terrorist hunt stats for the given player.

        'platform' must be one of 'uplay', 'xbox', or 'playstation', and
        defaults to 'uplay'.
        """

        p = await self.get_player(player, platform)
        if p is None:
            return

        await p.check_terrohunt()

        q = p.terrorist_hunt

        e = discord.Embed(
            description="Player Terrorist Hunt Queue Statistics")
        e.set_author(name=p.name, url=p.url, icon_url=p.icon_url)

        e.add_field(name="Win/Loss",
                    value="**Wins:** {}\n"
                    "**Losses:** {}\n"
                    "**Win Percent:** {}%\n"
                    "**Playtime:** {}".format(
                        q.won, q.lost,
                        "{0:.2f}".format((q.won / q.played if
                                          q.played > 0 else 1) * 100),
                        "{}h, {}m".format(*divmod(
                            divmod(q.time_played, 60)[0], 60)))
                    )
        e.add_field(name="Kill/Death",
                    value="**Kills:** {}\n"
                    "**Deaths:** {}\n"
                    "**K/D:** {}".format(
                        q.kills, q.deaths,
                        "{0:.2f}".format(q.kills /
                                         (q.deaths if q.deaths > 0 else 1)))
                    )

        await self.bot.say(embed=e)


def check_folders():
    if not os.path.exists("data/rainbow6siege"):
        print("Creating data/rainbow6siege directory...")
        os.makedirs("data/rainbow6siege")


def check_files():
    f = "data/rainbow6siege/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating data/rainbow6siege/settings.json...")
        dataIO.save_json(f, {"email": None, "password": None})


def setup(bot: commands.Bot):
    check_folders()
    check_files()
    if r6sapi_available:
        bot.add_cog(Rainbow6Siege(bot))
    else:
        raise RuntimeError(
            "You need to install `r6sapi`: `pip install r6sapi`.")
