import asyncio
import logging
from random import choice

import aiohttp
from redbot.core import commands

__author__ = "tmerc"

log = logging.getLogger('red.tmerc.lenny')

LENNY_PARTS = {
    'ears': [
        'q{}p', 'ʢ{}ʡ', '⸮{}?', 'ʕ{}ʔ', 'ᖗ{}ᖘ', 'ᕦ{}ᕥ', 'ᕦ({})ᕥ', 'ᕙ({})ᕗ', 'ᘳ{}ᘰ', 'ᕮ{}ᕭ', 'ᕳ{}ᕲ', '({})', '[{}]',
        '¯\\\_{}_/¯', '୧{}୨', '୨{}୧', '⤜({})⤏', '☞{}☞', 'ᑫ{}ᑷ', 'ᑴ{}ᑷ', 'ヽ({})ﾉ', '\\\({})/', '乁({})ㄏ', '└[{}]┘',
        '(づ{})づ', '(ง{})ง', '|{}|',
    ],
    'eyes': [
        '⌐■{}■', ' ͠°{} °', '⇀{}↼', '´• {} •`', '´{}`', '`{}´', 'ó{}ò', 'ò{}ó', '>{}<', 'Ƹ̵̡ {}Ʒ', 'ᗒ{}ᗕ', '⪧{}⪦',
        '⪦{}⪧', '⪩{}⪨', '⪨{}⪩', '⪰{}⪯', '⫑{}⫒', '⨴{}⨵', '⩿{}⪀', '⩾{}⩽', '⩺{}⩹', '⩹{}⩺', '◥▶{}◀◤', '≋{}≋', '૦ઁ{}૦ઁ',
        '  ͯ{}  ͯ', '  ̿{}  ̿', '  ͌{}  ͌', 'ළ{}ළ', '◉{}◉', '☉{}☉', '・{}・', '▰{}▰', 'ᵔ{}ᵔ', '□{}□', '☼{}☼', '*{}*',
        '⚆{}⚆', '⊜{}⊜', '>{}>', '❍{}❍', '￣{}￣', '─{}─', '✿{}✿', '•{}•', 'T{}T', '^{}^', 'ⱺ{}ⱺ', '@{}@', 'ȍ{}ȍ', 'x{}x',
        '-{}-', '${}$', 'Ȍ{}Ȍ', 'ʘ{}ʘ', 'Ꝋ{}Ꝋ', '๏{}๏', '■{}■', '◕{}◕', '◔{}◔', '✧{}✧', '♥{}♥', ' ͡°{} ͡°', '¬{}¬',
        ' º {} º ', '⍜{}⍜', '⍤{}⍤', 'ᴗ{}ᴗ', 'ಠ{}ಠ', 'σ{}σ',
    ],
    'mouths': [
        'v', 'ᴥ', 'ᗝ', 'Ѡ', 'ᗜ', 'Ꮂ', 'ヮ', '╭͜ʖ╮', ' ͟ل͜', ' ͜ʖ', ' ͟ʖ', ' ʖ̯', 'ω', '³', ' ε ', '﹏', 'ل͜', '╭╮', '‿‿',
        '▾', '‸', 'Д', '∀', '!', '人', '.', 'ロ', '_', '෴', 'ѽ', 'ഌ', '⏏', 'ツ', '益',
    ]
}


class Lenny(commands.Cog):
    """乁(-ロ-)ㄏ"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__url = 'http://lenny.today/api/v1/random?limit=1'
        self.__session = aiohttp.ClientSession()

    def cog_unload(self):
        if self.__session:
            asyncio.get_event_loop().create_task(self.__session.close())

    @commands.command(aliases=['donger'])
    async def lenny(self, ctx: commands.Context):
        """☞⇀‿↼☞"""

        await ctx.trigger_typing()

        await ctx.send(await self.__get_lenny())

    async def __get_lenny(self) -> str:
        try:
            async with self.__session.get(self.__url) as response:
                # grab the face
                lenny = (await response.json())[0]['face']
                # escape markdown characters
                lenny = lenny.replace('*', '\*').replace('`', '\`').replace('_', '\_').replace('~', '\~')
        # if the API call fails, make a (more limited) lenny locally instead
        except aiohttp.ClientError:
            log.warning("API call failed; falling back to local lenny")
            lenny = choice(LENNY_PARTS['ears']).format(choice(LENNY_PARTS['eyes'])).format(
                choice(LENNY_PARTS['mouths']))

        return lenny
