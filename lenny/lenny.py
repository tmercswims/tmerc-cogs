import aiohttp
import asyncio
import discord
import logging
import random
from typing import Dict, List

from redbot.core import commands

__author__ = "tmerc"

log = logging.getLogger("red.tmerc.lenny")

LENNY_PARTS: Dict[str, List[str]] = {
    "ears": [
        "q{}p",
        "ʢ{}ʡ",
        "⸮{}?",
        "ʕ{}ʔ",
        "ᖗ{}ᖘ",
        "ᕦ{}ᕥ",
        "ᕦ({})ᕥ",
        "ᕙ({})ᕗ",
        "ᘳ{}ᘰ",
        "ᕮ{}ᕭ",
        "ᕳ{}ᕲ",
        "({})",
        "[{}]",
        "¯\\\\_{}_/¯",
        "୧{}୨",
        "୨{}୧",
        "⤜({})⤏",
        "☞{}☞",
        "ᑫ{}ᑷ",
        "ᑴ{}ᑷ",
        "ヽ({})ﾉ",
        "\\\\({})/",
        "乁({})ㄏ",
        "└[{}]┘",
        "(づ{})づ",
        "(ง{})ง",
        "|{}|",
    ],
    "eyes": [
        "⌐■{}■",
        " ͠°{} °",
        "⇀{}↼",
        "´• {} •`",
        "´{}`",
        "`{}´",
        "ó{}ò",
        "ò{}ó",
        ">{}<",
        "Ƹ̵̡ {}Ʒ",
        "ᗒ{}ᗕ",
        "⪧{}⪦",
        "⪦{}⪧",
        "⪩{}⪨",
        "⪨{}⪩",
        "⪰{}⪯",
        "⫑{}⫒",
        "⨴{}⨵",
        "⩿{}⪀",
        "⩾{}⩽",
        "⩺{}⩹",
        "⩹{}⩺",
        "◥▶{}◀◤",
        "≋{}≋",
        "૦ઁ{}૦ઁ",
        "  ͯ{}  ͯ",
        "  ̿{}  ̿",
        "  ͌{}  ͌",
        "ළ{}ළ",
        "◉{}◉",
        "☉{}☉",
        "・{}・",
        "▰{}▰",
        "ᵔ{}ᵔ",
        "□{}□",
        "☼{}☼",
        "*{}*",
        "⚆{}⚆",
        "⊜{}⊜",
        ">{}>",
        "❍{}❍",
        "￣{}￣",
        "─{}─",
        "✿{}✿",
        "•{}•",
        "T{}T",
        "^{}^",
        "ⱺ{}ⱺ",
        "@{}@",
        "ȍ{}ȍ",
        "x{}x",
        "-{}-",
        "${}$",
        "Ȍ{}Ȍ",
        "ʘ{}ʘ",
        "Ꝋ{}Ꝋ",
        "๏{}๏",
        "■{}■",
        "◕{}◕",
        "◔{}◔",
        "✧{}✧",
        "♥{}♥",
        " ͡°{} ͡°",
        "¬{}¬",
        " º {} º ",
        "⍜{}⍜",
        "⍤{}⍤",
        "ᴗ{}ᴗ",
        "ಠ{}ಠ",
        "σ{}σ",
    ],
    "mouths": [
        "v",
        "ᴥ",
        "ᗝ",
        "Ѡ",
        "ᗜ",
        "Ꮂ",
        "ヮ",
        "╭͜ʖ╮",
        " ͟ل͜",
        " ͜ʖ",
        " ͟ʖ",
        " ʖ̯",
        "ω",
        "³",
        " ε ",
        "﹏",
        "ل͜",
        "╭╮",
        "‿‿",
        "▾",
        "‸",
        "Д",
        "∀",
        "!",
        "人",
        ".",
        "ロ",
        "_",
        "෴",
        "ѽ",
        "ഌ",
        "⏏",
        "ツ",
        "益",
    ],
}


def protect_against_emojification(text) -> str:
    res = ""
    for symbol in text:
        if symbol == "\\":
            res += symbol
        else:
            res += symbol + "\N{VARIATION SELECTOR-15}"

    return res


class Lenny(commands.Cog):
    """乁(-ロ-)ㄏ"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__url: str = "http://api.lenny.today/v1/random?limit=1"
        self.__session = aiohttp.ClientSession()

    def cog_unload(self) -> None:
        if self.__session:
            asyncio.get_event_loop().create_task(self.__session.close())

    @commands.command(aliases=["donger"])
    async def lenny(self, ctx: commands.Context) -> None:
        """☞⇀‿↼☞"""

        await ctx.trigger_typing()

        await ctx.send(await self.__get_lenny())

    async def __get_lenny(self) -> str:
        try:
            async with self.__session.get(self.__url) as response:
                # grab the face
                lenny = (await response.json())[0]["face"]
                # escape markdown characters
                lenny = discord.utils.escape_markdown(lenny)
                # protect against discord transforming symbol in emoji
                lenny = protect_against_emojification(lenny)
        # if the API call fails, make a (more limited) lenny locally instead
        except aiohttp.ClientError:
            log.warning("API call failed; falling back to local lenny")
            lenny = (
                random.choice(LENNY_PARTS["ears"])
                .format(random.choice(LENNY_PARTS["eyes"]))
                .format(random.choice(LENNY_PARTS["mouths"]))
            )

        return lenny
