# tmerc-cogs
[![Actions Status](https://github.com/tmercswims/tmerc-cogs/workflows/Compile%20&%20Lint/badge.svg)][tmerc-build-status]

## What is this?
These are cogs (plugins) for the [Discord][discord] bot [Red][red-repo-readme].

Most of these cogs are ports of my Red v2 cogs, and there are more of those on the way. There are some others which are
new to v3 as well.

## How do I use this?
First, [set up Red][red-repo-install], if you haven't already. Then, you can add this repository to your bot by running
this command in Discord:
```
[p]repo add tmerc-cogs https://github.com/tmercswims/tmerc-cogs
```
(With `[p]` being your bot's prefix.)

## What cogs are available?
More detailed documentation will come at a later date, but the `info.json` file in each cog's folder provides some basic
information. If you add my repository (see [above](#how-do-i-use-this)) then you can run this command to list all the
cogs:
```
[p]cog list tmerc-cogs
```
And you can get more information on a cog with this command:
```
[p]cog info tmerc-cogs <cog-name>
```
(With `[p]` being your bot's prefix.)

## How can I get help?
The first step you should take is to join me in my [support channel][tmerc-support-discord] in the Red Cog Support
server. I check there as often as I can, and it's the best place to get help with problems.

If you know that you have come across a bug, please open a [bug report][tmerc-issue-bug] on GitHub. This makes it easier
for me to track problems.

## How can I contribute?
If you have an idea for an enhancement to an existing cog, please [submit it][tmerc-issue-feature]!

If you want to go one step further and propose the code change yourself (be it for an enhancement _or_ a bug fix!) my
[pull requests][tmerc-pulls] are open!

If you are just in the mood to fix a bug, feel free to browse the [open issues][tmerc-issues]. Be sure to comment on
whichever you choose so that two people (including myself!) do not work on the same thing.

Before contributing, please familiarize yourself with the [contribution guidelines][tmerc-contributing] and the
[code of conduct][tmerc-coc].

## Do you take cog requests/bounties?
Currently I do not. That being said, if you have an idea for a cog that you think I specifically might be interested in,
feel free to stop by my support channel and we can chat about it!

For all regular cog bounties, please see the [Red Cog Board][red-board-bounties].

## How can I support you?
Well, thank you very much for wanting to! However, I do not take donations. I have a full-time job which supports me,
and I maintain this project on my own time because I like to. If you really want to do something, make a small donation
to [Médecins Sans Frontières (Doctors Without Borders)][msf] for me.

## Useful Links
- [Red Repository][red-repo]
- [Red Documentation][red-docs]
- [Red Discord Server][red-discord]
- [Red Cog Support Server][red-support-discord]
- [Cog Board][red-board]

[tmerc-build-status]: https://github.com/tmercswims/tmerc-cogs/actions
[tmerc-support-discord]: https://discord.gg/HWfwYxN
[tmerc-issue-bug]: https://github.com/tmercswims/tmerc-cogs/issues/new?assignees=&labels=type%3A+bug&template=bug-report.md&title=
[tmerc-issue-feature]: https://github.com/tmercswims/tmerc-cogs/issues/new?assignees=&labels=type%3A+enhancement&template=cog-enhancement.md&title=
[tmerc-pulls]: https://github.com/tmercswims/tmerc-cogs/pulls
[tmerc-issues]: https://github.com/tmercswims/tmerc-cogs/issues
[tmerc-contributing]: .github/CONTRIBUTING.md
[tmerc-coc]: .github/CODE_OF_CONDUCT.md

[discord]: https://discordapp.com/
[msf]: https://www.msf.org/

[red-repo]: https://github.com/Cog-Creators/Red-DiscordBot
[red-repo-readme]: https://github.com/Cog-Creators/Red-DiscordBot#readme
[red-repo-install]: https://github.com/Cog-Creators/Red-DiscordBot#installation
[red-board-bounties]: https://cogboard.red/c/bounties
[red-board]: https://cogboard.red/
[red-docs]: https://red-discordbot.readthedocs.io/en/stable/
[red-discord]: https://discord.gg/red
[red-support-discord]: https://discord.gg/GET4DVk
