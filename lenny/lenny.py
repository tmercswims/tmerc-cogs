import logging
from random import choice

import aiohttp
from discord.ext import commands
from redbot.core import RedContext

__author__ = "tmerc"

log = logging.getLogger('red.tmerc.lenny')

LENNY_PARTS = {
  'ears': [
    "q{}p", "ʢ{}ʡ", "⸮{}?", "ʕ{}ʔ", "ᖗ{}ᖘ", "ᕦ{}ᕥ", "ᕦ({})ᕥ", "ᕙ({})ᕗ", "ᘳ{}ᘰ", "ᕮ{}ᕭ", "ᕳ{}ᕲ", "({})", "[{}]",
    "¯\\\_{}_/¯", "୧{}୨", "୨{}୧", "⤜({})⤏", "☞{}☞", "ᑫ{}ᑷ", "ᑴ{}ᑷ", "ヽ({})ﾉ", "\\\({})/", "乁({})ㄏ", "└[{}]┘",
    "(づ{})づ", "(ง{})ง", "|{}|"
  ],
  'eyes': [
    "⌐■{}■", " ͠°{} °", "⇀{}↼", "´• {} •`", "´{}`", "`{}´", "ó{}ò", "ò{}ó", ">{}<", "Ƹ̵̡ {}Ʒ", "ᗒ{}ᗕ", "⪧{}⪦", "⪦{}⪧",
    "⪩{}⪨", "⪨{}⪩", "⪰{}⪯", "⫑{}⫒", "⨴{}⨵", "⩿{}⪀", "⩾{}⩽", "⩺{}⩹", "⩹{}⩺", "◥▶{}◀◤", "≋{}≋", "૦ઁ{}૦ઁ", "  ͯ{}  ͯ",
    "  ̿{}  ̿", "  ͌{}  ͌", "ළ{}ළ", "◉{}◉", "☉{}☉", "・{}・", "▰{}▰", "ᵔ{}ᵔ", "□{}□", "☼{}☼", "*{}*", "⚆{}⚆", "⊜{}⊜",
    ">{}>", "❍{}❍", "￣{}￣", "─{}─", "✿{}✿", "•{}•", "T{}T", "^{}^", "ⱺ{}ⱺ", "@{}@", "ȍ{}ȍ", "x{}x", "-{}-", "${}$",
    "Ȍ{}Ȍ", "ʘ{}ʘ", "Ꝋ{}Ꝋ", "๏{}๏", "■{}■", "◕{}◕", "◔{}◔", "✧{}✧", "♥{}♥", " ͡°{} ͡°", "¬{}¬", " º {} º ", "⍜{}⍜",
    "⍤{}⍤", "ᴗ{}ᴗ", "ಠ{}ಠ", "σ{}σ"
  ],
  'mouths': [
    "v", "ᴥ", "ᗝ", "Ѡ", "ᗜ", "Ꮂ", "ヮ", "╭͜ʖ╮", " ͟ل͜", " ͜ʖ", " ͟ʖ", " ʖ̯", "ω", "³", " ε ", "﹏", "ل͜", "╭╮", "‿‿",
    "▾", "‸", "Д", "∀", "!", "人", ".", "ロ", "_", "෴", "ѽ", "ഌ", "⏏", "ツ", "益"
  ]
}


class Lenny:
  """乁(-ロ-)ㄏ"""

  def __init__(self):
    self.__url = 'http://lenny.today/api/v1/random?limit=1'
    self.__session = aiohttp.ClientSession()

  def __unload(self):
    if self.__session:
      self.__session.close()

  @commands.command()
  async def lenny(self, ctx: RedContext):
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
    except:
      log.warning("API call failed; falling back to local lenny")
      lenny = choice(LENNY_PARTS['ears']).format(choice(LENNY_PARTS['eyes'])).format(choice(LENNY_PARTS['mouths']))

    return lenny
