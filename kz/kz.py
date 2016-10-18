import discord
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks, chat_formatting as cf
from __main__ import send_cmd_help

import aiohttp
import ftplib
import json
import os
import sqlite3
from tabulate import tabulate

default_settings = {
    "ftp_server": None,
    "ftp_username": None,
    "ftp_password": None,
    "ftp_dbpath": None,
    "steam_api_key": None
}


class SteamUrlError(Exception):
    pass


class Kz:

    """Gets KZ stats from a server. Use [p]kzset to set parameters."""

    def __init__(self, bot: commands.bot.Bot):
        self.bot = bot
        self.settings_path = "data/kz/settings.json"
        self.settings = dataIO.load_json(self.settings_path)

    @commands.group(pass_context=True, no_pm=True, name="kzset")
    @checks.admin_or_permissions(manage_server=True)
    async def _kzset(self, ctx: commands.context.Context):
        """Sets KZ settings."""

        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            dataIO.save_json(self.settings_path, self.settings)
            os.makedirs("data/kz/{}".format(server.id))
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @_kzset.command(pass_context=True, no_pm=True, name="server")
    async def _server(self, ctx: commands.context.Context, server: str):
        """Set the FTP server."""

        serv = ctx.message.server
        self.settings[serv.id]["ftp_server"] = server
        dataIO.save_json(self.settings_path, self.settings)
        await self.bot.reply(cf.info("Server set."))

    @_kzset.command(pass_context=True, no_pm=True, name="username")
    async def _username(self, ctx: commands.context.Context,
                        username: str):
        """Set the FTP username."""

        server = ctx.message.server
        self.settings[server.id]["ftp_username"] = username
        dataIO.save_json(self.settings_path, self.settings)
        await self.bot.reply(cf.info("Username set."))

    @_kzset.command(pass_context=True, no_pm=True, name="password")
    async def _password(self, ctx: commands.context.Context,
                        password: str):
        """Set the FTP password."""

        server = ctx.message.server

        await self.bot.delete_message(ctx.message)

        self.settings[server.id]["ftp_password"] = password
        dataIO.save_json(self.settings_path, self.settings)

        await self.bot.reply(cf.info("Password set."))

    @_kzset.command(pass_context=True, no_pm=True, name="dbpath")
    async def _dbpath(self, ctx: commands.context.Context,
                      dbpath: str):
        """Set the server path to the database."""

        server = ctx.message.server
        self.settings[server.id]["ftp_dbpath"] = dbpath
        dataIO.save_json(self.settings_path, self.settings)
        await self.bot.reply(cf.info("Path to database set."))

    @_kzset.command(pass_context=True, no_pm=True, name="steamkey")
    async def _steamkey(self, ctx: commands.context.Context,
                        steamkey: str):
        """Sets the Steam API key."""

        server = ctx.message.server

        await self.bot.delete_message(ctx.message)

        self.settings[server.id]["steam_api_key"] = steamkey
        dataIO.save_json(self.settings_path, self.settings)

        await self.bot.reply(cf.info("Steam API key set."))

    def _check_settings(self, server_id: str) -> bool:
        server_settings = self.settings[server_id]
        return (server_settings["ftp_server"] and
                server_settings["ftp_username"] and
                server_settings["ftp_password"] and
                server_settings["ftp_dbpath"] and
                server_settings["steam_api_key"])

    async def _update_database(self, server_id: str):
        info = self.settings[server_id]

        with open(
            "data/kz/{}/kztimer-sqlite.sq3".format(server_id), "wb") as file, \
                ftplib.FTP() as ftp:
            ftp.connect(info["ftp_server"])
            ftp.login(info["ftp_username"], info["ftp_password"])
            ftp.retrbinary("RETR {}".format(info["ftp_dbpath"]), file.write)

    async def _steam_url_to_text_id(self, server_id: str,
                                    vanityurl: str) -> str:
        api_key = self.settings[server_id]["steam_api_key"]

        url = "http://api.steampowered.com/ISteamUser/"
        "ResolveVanityURL/v0001/?key={}&vanityurl={}".format(
            api_key, vanityurl)

        steam64_id = None
        async with aiohttp.get(url) as res:
            response = json.loads(await res.text())["response"]
            if response["success"] != 1:
                raise SteamUrlError(
                    "'{}' is not a Steam vanity URL.".format(vanityurl))
            steam64_id = int(response["steamid"])

        account_id = steam64_id & ((1 << 32) - 1)
        universe = (steam64_id >> 56) & ((1 << 8) - 1)

        I = universe
        J = account_id & 1
        K = (account_id >> 1) & ((1 << 31) - 1)

        return "STEAM_{}:{}:{}".format(I, J, K)

    def _seconds_to_time_string(self, seconds: int) -> str:
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)

        if h > 0:
            return "%d:%02d:%05.2f" % (h, m, s)
        else:
            return "%d:%05.2f" % (m, s)

    @commands.command(pass_context=True, no_pm=True, name="playerjumps")
    async def _playerjumps(self, ctx: commands.context.Context,
                           player_url: str):
        """Gets a player's best jumps.

        You must provide the STEAM VANITY URL of the player,
        NOT the in-game name.
        """

        await self.bot.type()

        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            dataIO.save_json(self.settings_path, self.settings)

        if not self._check_settings(server.id):
            await self.bot.reply(cf.error(
                "You need to set up this cog before you can use it."
                " Use `{}kzset`.".format(ctx.prefix)))
            return

        steamid = None
        try:
            steamid = await self._steam_url_to_text_id(server.id, player_url)
        except SteamUrlError as err:
            await self.bot.reply(
                cf.error("Could not resolve Steam vanity URL."))
            return

        await self._update_database(server.id)

        con = sqlite3.connect(
            "data/kz/{}/kztimer-sqlite.sq3".format(server.id))
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        cur.execute(player_jumps_query, (steamid,))

        stats = cur.fetchone()
        cur.close()
        con.close()

        if not stats:
            await self.bot.reply(cf.warning(
                "Player has no jumpstats in the server."))
            return

        title = "Jumpstats: {}".format(stats["name"])
        headers = [
            "Type", "Distance", "Strafes", "Pre", "Max", "Height", "Sync"]
        rows = []

        if stats["ljrecord"] != -1:
            rows.append(["LJ",
                         round(stats["ljrecord"], 3),
                         stats["ljstrafes"],
                         round(stats["ljpre"], 2),
                         round(stats["ljmax"], 2),
                         round(stats["ljheight"], 1),
                         "{}%".format(stats["ljsync"])])
        if stats["ljblockrecord"] != -1:
            rows.append(["BlockLJ",
                         "{}|{}".format(stats["ljblockdist"],
                                        round(stats["ljblockrecord"], 1)),
                         stats["ljblockstrafes"],
                         round(stats["ljblockpre"], 2),
                         round(stats["ljblockmax"], 2),
                         round(stats["ljblockheight"], 1),
                         "{}%".format(stats["ljblocksync"])])
        if stats["bhoprecord"] != -1:
            rows.append(["Bhop",
                         round(stats["bhoprecord"], 3),
                         stats["bhopstrafes"],
                         round(stats["bhoppre"], 2),
                         round(stats["bhopmax"], 2),
                         round(stats["bhopheight"], 1),
                         "{}%".format(stats["bhopsync"])])
        if stats["dropbhoprecord"] != -1:
            rows.append(["D.-Bhop",
                         round(stats["dropbhoprecord"], 3),
                         stats["dropbhopstrafes"],
                         round(stats["dropbhoppre"], 2),
                         round(stats["dropbhopmax"], 2),
                         round(stats["dropbhopheight"], 1),
                         "{}%".format(stats["dropbhopsync"])])
        if stats["multibhoprecord"] != -1:
            rows.append(["M.-Bhop",
                         round(stats["multibhoprecord"], 3),
                         stats["multibhopstrafes"],
                         round(stats["multibhoppre"], 2),
                         round(stats["multibhopmax"], 2),
                         round(stats["multibhopheight"], 1),
                         "{}%".format(stats["multibhopsync"])])
        if stats["wjrecord"] != -1:
            rows.append(["WJ",
                         round(stats["wjrecord"], 3),
                         stats["wjstrafes"],
                         round(stats["wjpre"], 2),
                         round(stats["wjmax"], 2),
                         round(stats["wjheight"], 1),
                         "{}%".format(stats["wjsync"])])
        if stats["cjrecord"] != -1:
            rows.append(["CJ",
                         round(stats["cjrecord"], 3),
                         stats["cjstrafes"],
                         round(stats["cjpre"], 2),
                         round(stats["cjmax"], 2),
                         round(stats["cjheight"], 1),
                         "{}%".format(stats["cjsync"])])
        if stats["ladderjumprecord"] != -1:
            rows.append(["LAJ",
                         round(stats["ladderjumprecord"], 3),
                         stats["ladderjumpstrafes"],
                         round(stats["ladderjumppre"], 2),
                         round(stats["ladderjumpmax"], 2),
                         round(stats["ladderjumpheight"], 1),
                         "{}%".format(stats["ladderjumpsync"])])

        if len(rows) == 0:
            await self.bot.reply(
                cf.warning("Player has no jumpstats in the server."))
            return

        table = tabulate(rows, headers, tablefmt="orgtbl")

        await self.bot.say(cf.box("{}\n{}".format(title, table)))

    @commands.command(pass_context=True, no_pm=True, name="playermap")
    async def _playermap(self, ctx: commands.context.Context,
                         player_url: str, mapname: str):
        """Gets a certain player's times on the given map."""

        await self.bot.type()

        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            dataIO.save_json(self.settings_path, self.settings)

        if not self._check_settings(server.id):
            await self.bot.reply(cf.error(
                "You need to set up this cog before you can use it."
                " Use `{}kzset`.".format(ctx.prefix)))
            return

        steamid = None
        try:
            steamid = await self._steam_url_to_text_id(server.id, player_url)
        except SteamUrlError as err:
            await self.bot.reply(
                cf.error("Could not resolve Steam vanity URL."))
            return

        mn = "%{}%".format(mapname)

        await self._update_database(server.id)

        con = sqlite3.connect(
            "data/kz/{}/kztimer-sqlite.sq3".format(server.id))
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        cur.execute(player_maptime_query, (steamid, mn))

        r = cur.fetchone()
        if not r:
            await self.bot.say(cf.box("Player has no times on the given map."))
            return

        real_mapname = r["mapname"]
        headers = ["Type", "Time", "Teleports", "Rank"]
        rows = []

        if r["runtime"] > -1.0:
            cur.execute(player_mapranktotal_queries["tp"],
                        (steamid, real_mapname, real_mapname, real_mapname))
            tpr = cur.fetchone()
            cur.close()
            rows.append(["TP",
                         self._seconds_to_time_string(r["runtime"]),
                         r["teleports"],
                         "{}/{}".format(tpr["rank"], tpr["tot"])])
        else:
            rows.append(["TP", "--", "--", "--"])

        if r["runtimepro"] > -1.0:
            cur.execute(player_mapranktotal_queries["pro"],
                        (steamid, real_mapname, real_mapname, real_mapname))
            pror = cur.fetchone()
            cur.close()
            rows.append(["PRO",
                         self._seconds_to_time_string(r["runtimepro"]),
                         r["teleports_pro"],
                         "{}/{}".format(pror["rank"],
                                        pror["tot"])])
        else:
            rows.append(["PRO", "--", "--", "--"])

        con.close()

        title = "Map times for {} on {}".format(r["name"], real_mapname)
        table = tabulate(rows, headers, tablefmt="orgtbl")

        await self.bot.say(cf.box("{}\n{}".format(title, table)))

    @commands.command(pass_context=True, no_pm=True, name="recent",
                      aliases=["latest"])
    async def _recent(self, ctx: commands.context.Context,
                      limit: str="10"):
        """Gets the recent runs per map and run type."""

        await self.bot.type()

        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            dataIO.save_json(self.settings_path, self.settings)

        if not self._check_settings(server.id):
            await self.bot.reply(
                cf.error("You need to set up this cog before you can use it."
                         " Use `{}kzset`.".format(ctx.prefix)))
            return

        lim = None
        try:
            lim = int(limit)
        except ValueError:
            await self.bot.reply(
                cf.error("The limit you provided is not a number."))
            return

        await self._update_database(server.id)

        con = sqlite3.connect(
            "data/kz/{}/kztimer-sqlite.sq3".format(server.id))
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        cur.execute(recent_query, (lim,))

        r = cur.fetchone()
        if not r:
            await self.bot.say(cf.box("No recent runs found."))
            return

        headers = ["Map", "Time", "Teleports", "Player"]

        rows = []
        count = 0
        while r:
            count += 1
            rows.append([r["map"],
                         self._seconds_to_time_string(r["runtime"]),
                         r["teleports"],
                         r["name"]])
            r = cur.fetchone()

        cur.close()
        con.close()

        title = "Recent {} record runs".format(min(count, lim))
        table = tabulate(rows, headers, tablefmt="orgtbl")

        await self.bot.say(cf.box("{}\n{}".format(title, table)))

    @commands.command(pass_context=True, no_pm=True, name="maptop")
    async def _maptop(self, ctx: commands.context.Context, mapname: str,
                      runtype: str="all", limit: str="10"):
        """Gets the top times for a map.

        Optionally provide the run type (all by default)
        and the limit (10 by default).
        """

        await self.bot.type()

        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            dataIO.save_json(self.settings_path, self.settings)

        if not self._check_settings(server.id):
            await self.bot.reply(
                cf.error("You need to set up this cog before you can use it."
                         " Use `{}kzset`.".format(ctx.prefix)))
            return

        lim = None
        try:
            lim = int(limit)
        except ValueError:
            await self.bot.reply(
                cf.error("The limit you provided is not a number."))
            return

        rt = runtype.strip().lower()

        if rt not in ["all", "tp", "pro"]:
            await self.bot.reply(
                cf.error("The runtype must be one of `all`, `tp`, or `pro`."))
            return

        mn = "%{}%".format(mapname)

        await self._update_database(server.id)

        con = sqlite3.connect(
            "data/kz/{}/kztimer-sqlite.sq3".format(server.id))
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        if rt == "all":
            cur.execute(maptop_queries[rt], (mn, mn, lim))
        else:
            cur.execute(maptop_queries[rt], (mn, lim))

        r = cur.fetchone()
        if not r:
            await self.bot.say(cf.box("No times found."))
            return

        real_mapname = r["mapname"]

        headers = None
        if rt == "pro":
            headers = ["Rank", "Time", "Player"]
        else:
            headers = ["Rank", "Time", "Teleports", "Player"]

        rank = 0
        rows = []
        while r:
            rank += 1
            if rt == "pro":
                rows.append([rank,
                             self._seconds_to_time_string(r["overall"]),
                             r["name"]])
            else:
                rows.append([rank,
                             self._seconds_to_time_string(r["overall"]),
                             r["tp"],
                             r["name"]])
            r = cur.fetchone()

        cur.close()
        con.close()

        title = "Top {} {}time{} on {}".format(min(rank, lim),
                                               ("" if rt == "all"
                                                else rt.upper() + " "),
                                               "s" if rank > 1 else "",
                                               real_mapname)
        table = tabulate(rows, headers, tablefmt="orgtbl")

        await self.bot.say(cf.box("{}\n{}".format(title, table)))

    @commands.group(pass_context=True, no_pm=True, name="jumptop")
    async def _jumptop(self, ctx: commands.context.Context):
        """Gets the top stats for the given jump type.

        Optionally provide a limit (default is 10).
        """

        await self.bot.type()

        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            dataIO.save_json(self.settings_path, self.settings)

        if not self._check_settings(server.id):
            await self.bot.reply(
                cf.error("You need to set up this cog before you can use it."
                         " Use `{}kzset`.".format(ctx.prefix)))
            return

        await self._update_database(server.id)

        if ctx.invoked_subcommand is None:
            await ctx.invoke(self._all)

    @_jumptop.command(pass_context=True, no_pm=True, name="all",
                      aliases=["records"])
    async def _all(self, ctx: commands.context.Context):
        """Gets the record for every type of jump."""

        con = sqlite3.connect(
            "data/kz/{}/kztimer-sqlite.sq3".format(
                ctx.message.server.id))
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        headers = ["Type", "Distance", "Strafes", "Player"]
        rows = []

        cur.execute(jumptop_queries["ljblock"], (1,))

        r = cur.fetchone()
        if r:
            rows.append(["BlockLJ",
                         "{}|{}".format(r["ljblockdist"],
                                        round(r["ljblockrecord"], 1)),
                         r["ljblockstrafes"],
                         r["name"]])
        else:
            rows.append(["BlockLJ", "--|--", "--" "--" "--", "--", "--"])

        cur.execute(jumprecords_query)
        r = cur.fetchone()
        while r:
            rows.append([r["jumptype"],
                         round(r["distance"], 3),
                         r["strafes"],
                         r["name"]])
            r = cur.fetchone()

        jumps = ["BlockLJ", "LJ", "Bhop", "CJ",
                 "D.-Bhop", "M.-Bhop", "LAJ", "WJ"]
        in_rows = [x[0] for x in rows]

        for j in jumps:
            if j not in in_rows:
                rows.append([j, "--", "--" "--" "--", "--", "--"])

        cur.close()
        con.close()

        title = "Jumpstat records"
        table = tabulate(rows, headers, tablefmt="orgtbl")

        await self.bot.say(cf.box("{}\n{}".format(title, table)))

    @_jumptop.command(pass_context=True, no_pm=True, name="blocklj",
                      aliases=["blocklongjump", "BlockLJ", "BlockLj",
                               "BlockLongJump", "BlockLongjump",
                               "Blocklongjump"])
    async def _blocklj(self, ctx: commands.context.Context,
                       limit: str="10"):
        """Gets the top BlockLJs."""

        lim = None
        try:
            lim = int(limit)
        except ValueError:
            await self.bot.reply(
                cf.error("The limit you provided is not a number."))
            return

        await self._jumptop_helper(ctx.message.server.id,
                                   "ljblock", "Block Longjump", lim)

    @_jumptop.command(pass_context=True, no_pm=True, name="lj",
                      aliases=["longjump", "LJ", "LongJump", "Longjump", "Lj"])
    async def _lj(self, ctx: commands.context.Context, limit: str="10"):
        """Gets the top LJs."""

        lim = None
        try:
            lim = int(limit)
        except ValueError:
            await self.bot.reply(
                cf.error("The limit you provided is not a number."))
            return

        await self._jumptop_helper(ctx.message.server.id,
                                   "lj", "Longjump", lim)

    @_jumptop.command(pass_context=True, no_pm=True, name="bhop",
                      aliases=["bunnyhop", "Bhop", "BHop",
                               "Bunnyhop", "BunnyHop"])
    async def _bhop(self, ctx: commands.context.Context, limit: str="10"):
        """Gets the top Bhops."""

        lim = None
        try:
            lim = int(limit)
        except ValueError:
            await self.bot.reply(
                cf.error("The limit you provided is not a number."))
            return

        await self._jumptop_helper(ctx.message.server.id,
                                   "bhop", "Bunnyhop", lim)

    @_jumptop.command(pass_context=True, no_pm=True, name="multibhop",
                      aliases=["multibunnyhop", "MultiBhop", "MultiBunnyhop",
                               "MultiBunnyHop", "Multibhop", "mbhop", "MBhop"])
    async def _multibhop(self, ctx: commands.context.Context,
                         limit: str="10"):
        """Gets the top MultiBhops."""

        lim = None
        try:
            lim = int(limit)
        except ValueError:
            await self.bot.reply(
                cf.error("The limit you provided is not a number."))
            return

        await self._jumptop_helper(ctx.message.server.id,
                                   "multibhop", "Multi-Bunnyhop", lim)

    @_jumptop.command(pass_context=True, no_pm=True, name="dropbhop",
                      aliases=["dropbunnyhop", "DropBhop", "DropBunnyhop",
                               "DropBunnyHop", "Dropbhop", "dbhop", "DBhop"])
    async def _dropbhop(self, ctx: commands.context.Context,
                        limit: str="10"):
        """Gets the top DropBhops."""

        lim = None
        try:
            lim = int(limit)
        except ValueError:
            await self.bot.reply(
                cf.error("The limit you provided is not a number."))
            return

        await self._jumptop_helper(ctx.message.server.id,
                                   "dropbhop", "Drop-Bunnyhop", lim)

    @_jumptop.command(pass_context=True, no_pm=True, name="wj",
                      aliases=["weirdjump", "WJ", "WeirdJump", "Weirdjump"])
    async def _wj(self, ctx: commands.context.Context, limit: str="10"):
        """Gets the top WJs."""

        lim = None
        try:
            lim = int(limit)
        except ValueError:
            await self.bot.reply(
                cf.error("The limit you provided is not a number."))
            return

        await self._jumptop_helper(ctx.message.server.id,
                                   "wj", "Weirdjump", lim)

    @_jumptop.command(pass_context=True, no_pm=True, name="laj",
                      aliases=["ladderjump", "LaJ", "LAJ",
                               "LadderJump", "Ladderjump"])
    async def _laj(self, ctx: commands.context.Context, limit: str="10"):
        """Gets the top LAJs."""

        lim = None
        try:
            lim = int(limit)
        except ValueError:
            await self.bot.reply(
                cf.error("The limit you provided is not a number."))
            return

        await self._jumptop_helper(ctx.message.server.id,
                                   "ladderjump", "Ladderjump", lim)

    @_jumptop.command(pass_context=True, no_pm=True, name="cj",
                      aliases=["countjump", "CJ", "CountJump", "Countjump"])
    async def _cj(self, ctx: commands.context.Context, limit: str="10"):
        """Gets the top CJs."""

        lim = None
        try:
            lim = int(limit)
        except ValueError:
            await self.bot.reply(
                cf.error("The limit you provided is not a number."))
            return

        await self._jumptop_helper(ctx.message.server.id,
                                   "cj", "Countjump", lim)

    async def _jumptop_helper(self, server_id: str, jumptype: str,
                              jumpname: str, lim: int):
        con = sqlite3.connect(
            "data/kz/{}/kztimer-sqlite.sq3".format(server_id))
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        cur.execute(jumptop_queries[jumptype], (lim,))

        r = cur.fetchone()
        if not r:
            await self.bot.say(cf.box("No jumps found."))
            return

        headers = None
        if jumptype == "ljblock":
            headers = ["Rank", "Block", "Distance", "Strafes", "Player"]
        else:
            headers = ["Rank", "Distance", "Strafes", "Player"]

        rank = 0
        rows = []
        while r:
            rank += 1
            if jumptype == "ljblock":
                rows.append([rank,
                             r["ljblockdist"],
                             r["ljblockrecord"],
                             r["ljblockstrafes"],
                             r["name"]])
            else:
                rows.append([rank,
                             r["{}record".format(jumptype)],
                             r["{}strafes".format(jumptype)],
                             r["name"]])
            r = cur.fetchone()

        cur.close()
        con.close()

        title = "Top {} {}".format(min(rank, lim), jumpname)
        table = tabulate(rows, headers, tablefmt="orgtbl")

        await self.bot.say(cf.box("{}\n{}".format(title, table)))


def check_folders():
    if not os.path.exists("data/kz"):
        print("Creating data/kz directory...")
        os.makedirs("data/kz")


def check_files():
    f = "data/kz/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating data/kz/settings.json...")
        dataIO.save_json(f, {})


def setup(bot: commands.bot.Bot):
    check_folders()
    check_files()

    bot.add_cog(Kz(bot))

# LIMIT
recent_query = "SELECT * FROM(SELECT name, runtime, teleports, map, date FROM LatestRecords WHERE teleports=0 GROUP BY map HAVING MIN(runtime) UNION SELECT name, runtime, teleports, map, date FROM LatestRecords WHERE teleports > 0 GROUP BY map HAVING MIN(runtime)) ORDER BY date DESC LIMIT ?"

jumprecords_query = "SELECT * FROM (SELECT 'LJ' as jumptype, db1.name as name, db2.ljrecord as distance, db2.ljstrafes as strafes, db2.ljpre as pre, db2.ljmax as max, db2.ljheight as height, db2.ljsync as sync FROM playerjumpstats3 as db2 INNER JOIN playerrank as db1 on db2.steamid = db1.steamid WHERE distance > -1.0 UNION SELECT 'Bhop' as jumptype, db1.name as name, db2.bhoprecord as distance, db2.bhopstrafes as strafes, db2.bhoppre as pre, db2.bhopmax as max, db2.bhopheight as height, db2.bhopsync as sync FROM playerjumpstats3 as db2 INNER JOIN playerrank as db1 on db2.steamid = db1.steamid WHERE distance > -1.0 UNION SELECT 'M.-Bhop' as jumptype, db1.name as name, db2.multibhoprecord as distance, db2.multibhopstrafes as strafes, db2.ljpre as pre, db2.multibhopmax as max, db2.multibhopheight as height, db2.multibhopsync as sync FROM playerjumpstats3 as db2 INNER JOIN playerrank as db1 on db2.steamid = db1.steamid WHERE distance > -1.0 UNION SELECT 'D.-Bhop' as jumptype, db1.name as name, db2.dropbhoprecord as distance, db2.dropbhopstrafes as strafes, db2.dropbhoppre as pre, db2.dropbhopmax as max, db2.dropbhopheight as height, db2.dropbhopsync as sync FROM playerjumpstats3 as db2 INNER JOIN playerrank as db1 on db2.steamid = db1.steamid WHERE distance > -1.0 UNION SELECT 'WJ' as jumptype, db1.name as name, db2.wjrecord as distance, db2.wjstrafes as strafes, db2.wjpre as pre, db2.wjmax as max, db2.wjheight as height, db2.wjsync as sync FROM playerjumpstats3 as db2 INNER JOIN playerrank as db1 on db2.steamid = db1.steamid WHERE distance > -1.0 UNION SELECT 'LAJ' as jumptype, db1.name as name, db2.ladderjumprecord as distance, db2.ladderjumpstrafes as strafes, db2.ladderjumppre as pre, db2.ladderjumpmax as max, db2.ladderjumpheight as height, db2.ladderjumpsync as sync FROM playerjumpstats3 as db2 INNER JOIN playerrank as db1 on db2.steamid = db1.steamid WHERE distance > -1.0 UNION SELECT 'CJ' as jumptype, db1.name as name, db2.cjrecord as distance, db2.cjstrafes as strafes, db2.cjpre as pre, db2.cjmax as max, db2.cjheight as height, db2.cjsync as sync FROM playerjumpstats3 as db2 INNER JOIN playerrank as db1 on db2.steamid = db1.steamid WHERE distance > -1.0) GROUP BY jumptype HAVING MAX(distance);"

jumptop_queries = {
    # LIMIT
    "ljblock": "SELECT db1.name, db2.ljblockdist, db2.ljblockrecord, db2.ljblockstrafes, db2.ljblockpre, db2.ljblockmax, db2.ljblockheight, db2.ljblocksync FROM playerjumpstats3 as db2 INNER JOIN playerrank as db1 on db2.steamid = db1.steamid WHERE db2.ljblockdist > -1.0 ORDER BY db2.ljblockdist DESC, db2.ljblockrecord DESC LIMIT ?;",
    # LIMIT
    "lj": "SELECT db1.name, db2.ljrecord, db2.ljstrafes, db2.ljpre, db2.ljmax, db2.ljheight, db2.ljsync FROM playerjumpstats3 as db2 INNER JOIN playerrank as db1 on db2.steamid = db1.steamid WHERE db2.ljrecord > -1.0 ORDER BY db2.ljrecord DESC LIMIT ?;",
    # LIMIT
    "bhop": "SELECT db1.name, db2.bhoprecord, db2.bhopstrafes, db2.bhoppre, db2.bhopmax, db2.bhopheight, db2.bhopsync FROM playerjumpstats3 as db2 INNER JOIN playerrank as db1 on db2.steamid = db1.steamid WHERE db2.bhoprecord > -1.0 ORDER BY db2.bhoprecord DESC LIMIT ?;",
    # LIMIT
    "multibhop": "SELECT db1.name, db2.multibhoprecord, db2.multibhopstrafes, db2.multibhoppre, db2.multibhopmax, db2.multibhopheight, db2.ljblocksync FROM playerjumpstats3 as db2 INNER JOIN playerrank as db1 on db2.steamid = db1.steamid WHERE db2.multibhoprecord > -1.0 ORDER BY db2.multibhoprecord DESC LIMIT ?;",
    # LIMIT
    "dropbhop": "SELECT db1.name, db2.dropbhoprecord, db2.dropbhopstrafes, db2.dropbhoppre, db2.dropbhopmax, db2.dropbhopheight, db2.dropbhopsync FROM playerjumpstats3 as db2 INNER JOIN playerrank as db1 on db2.steamid = db1.steamid WHERE db2.dropbhoprecord > -1.0 ORDER BY db2.dropbhoprecord DESC LIMIT ?;",
    # LIMIT
    "wj": "SELECT db1.name, db2.wjrecord, db2.wjstrafes, db2.wjpre, db2.wjmax, db2.wjheight, db2.wjsync FROM playerjumpstats3 as db2 INNER JOIN playerrank as db1 on db2.steamid = db1.steamid WHERE db2.wjrecord > -1.0 ORDER BY db2.wjrecord DESC LIMIT ?;",
    # LIMIT
    "ladderjump": "SELECT db1.name, db2.ladderjumprecord, db2.ladderjumpstrafes, db2.ladderjumppre, db2.ladderjumpmax, db2.ladderjumpheight, db2.ladderjumpsync FROM playerjumpstats3 as db2 INNER JOIN playerrank as db1 on db2.steamid = db1.steamid WHERE db2.ladderjumprecord > -1.0 ORDER BY db2.ladderjumprecord DESC LIMIT ?;",
    # LIMIT
    "cj": "SELECT db1.name, db2.cjrecord, db2.cjstrafes, db2.cjpre, db2.cjmax, db2.cjheight, db2.cjsync FROM playerjumpstats3 as db2 INNER JOIN playerrank as db1 on db2.steamid = db1.steamid WHERE db2.cjrecord > -1.0 ORDER BY db2.cjrecord DESC LIMIT ?;"
}

# STEAMID
player_jumps_query = "SELECT db1.name, db2.bhoprecord, db2.bhoppre, db2.bhopmax, db2.bhopstrafes, db2.bhopsync, db2.bhopheight, db2.ljrecord, db2.ljpre, db2.ljmax, db2.ljstrafes, db2.ljsync, db2.ljheight, db2.multibhoprecord, db2.multibhoppre, db2.multibhopmax, db2.multibhopstrafes, db2.multibhopcount, db2.multibhopsync, db2.multibhopheight, db2.wjrecord, db2.wjpre, db2.wjmax, db2.wjstrafes, db2.wjsync, db2.wjheight, db2.dropbhoprecord, db2.dropbhoppre, db2.dropbhopmax, db2.dropbhopstrafes, db2.dropbhopsync, db2.dropbhopheight, db2.ljblockdist, db2.ljblockrecord, db2.ljblockpre, db2.ljblockmax, db2.ljblockstrafes, db2.ljblocksync, db2.ljblockheight, db2.ladderjumprecord, db2.ladderjumppre, db2.ladderjumpmax, db2.ladderjumpstrafes, db2.ladderjumpsync, db2.ladderjumpheight, db2.cjrecord, db2.cjpre, db2.cjmax, db2.cjstrafes, db2.cjsync, db2.cjheight FROM playerjumpstats3 as db2 INNER JOIN playerrank as db1 on db2.steamid = db1.steamid WHERE (db2.ladderjumprecord > -1.0 OR db2.wjrecord > -1.0 OR db2.dropbhoprecord > -1.0 OR db2.ljrecord > -1.0 OR db2.bhoprecord > -1.0 OR db2.multibhoprecord > -1.0 OR db2.cjrecord > -1.0) AND db2.steamid = ?;"
# STEAMID, MAPNAME
player_maptime_query = "SELECT name, mapname, runtime, teleports, runtimepro, teleports_pro FROM playertimes WHERE steamid = ? AND mapname LIKE ? AND (runtime  > -1.0 OR runtimepro  > -1.0);"

player_mapranktotal_queries = {
    # STEAMID, MAPNAME, MAPNAME, MAPNAME
    "tp": "SELECT * FROM ((SELECT COUNT(*) as rank FROM playertimes WHERE runtime <= (SELECT runtime FROM playertimes WHERE steamid = ? AND mapname LIKE ? AND runtime > -1.0) AND mapname LIKE ? AND runtime > -1.0) JOIN (SELECT COUNT(*) as tot FROM playertimes WHERE mapname LIKE ? AND runtime  > -1.0));",
    # STEAMID, MAPNAME, MAPNAME, MAPNAME
    "pro": "SELECT * FROM ((SELECT COUNT(*) as rank FROM playertimes WHERE runtimepro <= (SELECT runtimepro FROM playertimes WHERE steamid = ? AND mapname LIKE ? AND runtimepro > -1.0) AND mapname LIKE ? AND runtimepro > -1.0) JOIN (SELECT COUNT(*) as tot FROM playertimes WHERE mapname LIKE ? AND runtimepro  > -1.0));"
}

maptop_queries = {
    # MAPNAME, MAPNAME, LIMIT
    "all": "SELECT * FROM (SELECT db1.name, db1.steamid, db2.mapname, db2.runtime as overall, db2.teleports AS tp FROM playertimes as db2 INNER JOIN playerrank as db1 on db2.steamid = db1.steamid WHERE db2.mapname LIKE ? AND db2.runtime > -1.0 AND db2.teleports >= 0 UNION SELECT db1.name, db1.steamid, db2.mapname, db2.runtimepro as overall, db2.teleports_pro AS tp FROM playertimes as db2 INNER JOIN playerrank as db1 on db2.steamid = db1.steamid WHERE db2.mapname LIKE ? AND db2.runtimepro > -1.0) GROUP BY steamid HAVING MIN(overall) ORDER BY overall ASC LIMIT ?;",
    # MAPNAME, LIMIT
    "tp": "SELECT db1.name, db2.mapname, db2.runtime as overall, db2.teleports AS tp FROM playertimes as db2 INNER JOIN playerrank as db1 on db2.steamid = db1.steamid WHERE db2.mapname LIKE ? AND db2.runtime > -1.0 ORDER BY db2.runtime ASC LIMIT ?;",
    # MAPNAME, LIMIT
    "pro": "SELECT db1.name, db2.mapname, db2.runtimepro as overall, db2.teleports_pro as tp FROM playertimes as db2 INNER JOIN playerrank as db1 on db1.steamid = db2.steamid WHERE db2.mapname LIKE ? AND db2.runtimepro > -1.0 ORDER BY db2.runtimepro ASC LIMIT ?;"
}
