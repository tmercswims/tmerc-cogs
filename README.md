[![Build Status](https://travis-ci.org/tmercswims/tmerc-cogs.svg?branch=master)](https://travis-ci.org/tmercswims/tmerc-cogs)

# tmerc-cogs

Cogs for Twentysix26's [Red Discord bot](https://github.com/Twentysix26/Red-DiscordBot).

## Table of Contents

- [Installation](#installation)
- [The Cogs](#the-cogs)
  - [CatFact](#catfact)
  - [CustomJoinLeave](#customjoinleave)
  - [KZ](#kz)
  - [Lenny](#lenny)
  - [MassDM](#massdm)
  - [Membership](#membership)
  - ~[PlaySound](#playsound)~ (Deprecated.)
  - [Quotes](#quotes)
  - [RandGame](#randgame)
  - [RandImage](#randimage)
  - [Randimals](#randimals)
  - [ReviewEmoji](#reviewemoji)
  - [StreamRole](#streamrole)
  - [Survey](#survey)
- [Support](#support)

## Installation
To add this repository to your bot, use the following command:
```
[p]cog repo add tmerc-cogs https://github.com/tmercswims/tmerc-cogs
```

## The Cogs

### CatFact
Gets random cat facts.
#### Commands
  * `catfact [number]` - Gets `number` random facts about cats. `number` defaults to `1`, and must be no greater than `10`.

#### Extra Dependencies
  * None.

#### Additional Information
  * Cog uses a small amount of network traffic to retrieve facts.


### CustomJoinLeave
Plays user-customizable sounds when joining or leaving a voice channel.

Each user may set their own join/leave sounds. Bot admins may set or delete sounds for other people, and control whether sounds are played at all.
#### Commands
  * `joinleaveset <command>` (Bot admin only) - Changes settings for the cog.
    * `togglejoin` - Toggles playing of custom join sounds on or off.
    * `toggleleave` - Toggles playing of custom leave sounds on or off.
  * `setjoinsound [link]` - Sets the join sound for the calling user. Must be called either as the comment on an uploaded file (Discord attachment) **or** a direct link to a sound file must be provided.
  * `setleavesound [link]` - Sets the leave sound for the calling user. Must be called either as the comment on an uploaded file (Discord attachment) **or** a direct link to a sound file must be provided.
  * `deljoinsound` - Deletes the calling user's join sound.
  * `delleavesound` - Deletes the calling user's leave sound.
  * `setjoinsoundfor <user> [link]` (Bot admin only) - Sets the join sound for the specified user (must be an @mention). Same file rules apply as with `setjoinsound`.
  * `setleavesoundfor <user> [link]` (Bot admin only) - Sets the leave sound for the specified user (must be an @mention). Same file rules apply as with `setleavesound`.
  * `deljoinsoundfor <user>` (Bot admin only) - Deletes the join sound for the specified user (must be an @mention).
  * `delleavesoundfor <user>` (Bot admin only) - Deletes the leave sound for the specified user (must be an @mention).

#### Extra Dependencies
  * None.

#### Additional Information
  * Cog can use quite a lot of disk space, depending on how many users set sounds, as the sound files must be saved. This is something to consider as a bot owner who plans to make the bot public.
  * Cog uses network to retrieve sound files.


### KZ
Get KZ (CS:GO Kreedz Mod) stats from a server (via FTP) and show them in Discord.

Note that commands which specify a player must be given the player's Steam Vanity URL, **not** their in-game name.
#### Commands
  * `kzset <command>` (Bot admin only) - Changes settings for the cog.
    * `server` - Sets the hostname of the KZ server.
    * `username` - Sets the FTP username with which to log into the server.
    * `password` - Sets the FTP password with which to log into the server. The message containing the command (and password) is deleted immediately.
    * `dbpath` - Sets the path, from root, to the database file on the FTP server. Must include the file itself, e.g. `/path/to/db.sq3` not `/path/to`.
    * `steamkey` - Sets the Steam API key, which is used to look up users' vanity URLs. It can be obtained from [here](https://steamcommunity.com/dev/apikey). The message containing the command (and key) is deleted immediately.
    * `rcon_password` - Sets the RCON password for the server. The message containing the command (and password) is deleted immediately.
    * `mapcyclepath` - Sets the path, from root, to the `mapcycle.txt` file on the FTP server. Must include the file itself, e.g. `/path/to/mapcycle.txt` not `/path/to`.
  * `addmap <map_id_or_url>` (Bot admin only) - Adds the given map to the server. Must provide either a workshop ID (e.g. `784686492`) or a full workshop link (e.g. `https://steamcommunity.com/sharedfiles/filedetails/?id=784686492&searchtext=kz_minimalism`).
  * `recent [limit]` - Gets the `limit` most recent record-setting runs. Retrieves a maximum of one per map, per run type. `limit` defaults to `10`.
  * `playermap <player_url> <mapname>` - Gets the specified player's time(s) on the specified map.
  * `playerjumps <player_url>` - Gets the specified player's jump records.
  * `maptop <mapname> [runtype] [limit]` - Gets the top `limit` times on the specified map. `runtype` specifies the type of run, one of `all`, `tp`, or `pro`, and defaults to `all`. `limit` defaults to `10`.
  * `jumptop` - Gets the top stats for a jump type.
    * `all` - Gets the server record for each jump type.
    * `blocklj [limit]` - Gets the top `limit` block longjumps. `limit` defaults to `10`.
    * `lj [limit]` - Gets the top `limit` longjumps. `limit` defaults to `10`.
    * `bhop [limit]` - Gets the top `limit` bunnyhops. `limit` defaults to `10`.
    * `multibhop [limit]` - Gets the top `limit` multi-bunnyhops. `limit` defaults to `10`.
    * `dropbhop [limit]` - Gets the top `limit` drop-bunnyhops. `limit` defaults to `10`.
    * `wj [limit]` - Gets the top `limit` weirdjumps. `limit` defaults to `10`.
    * `laj [limit]` - Gets the top `limit` ladderjumps. `limit` defaults to `10`.
    * `cj [limit]` - Gets the top `limit` countjumps. `limit` defaults to `10`.

#### Extra Dependencies
  * `beautifulsoup4`
  * `python-valve` (from GitHub: `git+git://github.com/Holiverh/python-valve.git`)
  * `rfc3987`
  * `tabulate`

#### Additional Information
  * Cog uses network to retrieve database from server.
  * Cog runs semi-complex SQL queries on the retrieved database to get information, which can potentially be processor intensive.


### Lenny
Displays a random ASCII face.
#### Commands
  * `lenny` - Sends a random ASCII face.

#### Extra Dependencies
  * None.

#### Additional Information
  * None.


### MassDM
Send a personalizable DM to all members of a Role.
#### Commands
  * `mdm <role> <message>` (Bot mod only) - Sends `message` to all members of the server that have `role`. `message` is personalizable: `{0}` is the member being messaged; `{1}` is the role through which they are being messaged; `{2}` is the person sending the message.

#### Extra Dependencies
  * None.

#### Additional Information
  * None.


### Membership
Announce membership-related events (join, leave, ban, unban) in chat.

All message format strings have the following personalizations available: `{0}` is the member in question; `{1}` is the server in question.
#### Commands
  * `membershipset <command>` (Bot admin only) - Changes settings for the cog.
    * `toggle` - Toggles membership event announcement on or off.
    * `channel <channel>` - Sets the channel to which announcements are sent. If this is not set manually, the default text channel will be used.
    * `join <format_str>` - Sets the join message.
    * `leave <format_str>` - Sets the leave message.
    * `ban <format_str>` - Sets the ban message.
    * `unban <format_str>` - Sets the unban message.

#### Extra Dependencies
  * None.

#### Additional Information
  * Cog adds listeners for the following events: `on_member_join`, `on_member_remove`, `on_member_ban`, and `on_member_unban`.


### PlaySound
THIS COG IS DEPRECATED AND NO LONGER MAINTAINED. Please use ['sfx' by FlapJack instead](https://cogs.red/cogs/flapjax/FlapJack-Cogs/sfx/).
Play sounds in voice channels.
#### Commands
  * `playsound <soundname>` - Plays the specified sound in the voice channel in which the caller is currently. `soundname` must be the case-accurate filename of a sound in `data/playsound`, excluding the extension.
  * `allsounds` - Sends a DM to the caller with an alphabetical list of every sound.
  * `addsound [link]` (Bot mod only) - Adds the provided sound. Must be called either as the comment on an uploaded file (Discord attachment) **or** a direct link to a sound file must be provided.
  * `soundvol <soundname> [percent]` (Bot mod only) - Sets or gets the volume for the specified sound. If `percent` is given, the volume for the specified sound is set to it. If it is not, the current volume for the sound is returned. If a sound's volume is never explicitly set, it defaults to 25%.
  * `getsound <soundname>` - Sends the specified sound file as a Discord attachment.
  * `delsound <filename>` - Deletes the specified sound.

#### Extra Dependencies
  * None.

#### Additional Information
  * Cog can use a lot of disk space, depending on how many sounds you have. Worth noting for bot owners.
  * Cog uses network to retrieve new sounds.


### Quotes
Store quotes, and get back random ones.
#### Commands
  * `addquote <new_quote>` - Adds a new quote to the list.
  * `delquote <number>` - Deletes the quote with the specified number.
  * `allquotes` - Sends a DM to the calling user with all the quotes in number order.
  * `quote [number]` - Sends a random quote if `number` is not specified, or the quote corresponding to `number` if it is.

#### Extra Dependencies
  * None.

#### Additional Information
  * None.


### RandGame
Cycles the bot's game randomly among a list at a regular interval.
#### Commands
  * `randgame <command>` (Bot mod only) - Changes cog settings.
    * `delay <seconds>` - Sets the delay, in seconds, between game changes.
    * `add <game>` - Adds a new game to the list.
    * `del <game>` - Removes a game from the list.
    * `set <games...>` - Replaces the current game list with the specified one.
    * `get` - Shows the current list of games.
    * `cycle` - Forces choosing a new game, bypassing the delay.

#### Extra Dependencies
  * None.

#### Additional Information
  * Adds a persistent event to the bot which is used to change the game at interval, but it spends the vast majority of its time asleep, so it will not have an impact on performance.


### RandImage
Gets a random image from a local directory.
#### Commands
  * `randimage <category> [delete]` - Uploads a random image from `category` (and optionally deletes it). `delete` defaults to `False`.
  * `addcategory <new_category>` (Bot mod only) - Creates a new category.
  * `delcategory <category>` (Bot mod only) - Deletes a category and all images in it.
  * `allcategories` - Sends a DM to the calling user with a list of all the categories, and the number of images in each.
  * `addimage <category> [image_url]` (Bot mod only) - Adds a new image to the specified category. Must be called either as the comment on an uploaded file (Discord attachment) **or** a direct link to an image file must be provided.

#### Extra Dependencies
  * None.

#### Additional Information
  * Cog can potentially use an *enormous* amount of disk space, depending on how many images are uploaded.


### Randimals
Shows random animals.
#### Commands
  * `cat` - Shows a random cat.
  * `dog` - Shows a random dog.
  * `fox` - Shows a random fox.
  * `bird` - Shows a random bird.

#### Extra Dependencies
  * None.

#### Additional Information
  * Cog uses network to retrieve images.


### ReviewEmoji
Allows for users to submit emoji, and then moderators to approve/reject them.
#### Commands
  * `submitemoji <name> [img_url]` - Submits a new emoji for review. Must be called either as the comment on an uploaded image (Discord attachment) **or** a direct link to an image must be provided.
  * `checkemoji <submission_id>` - Checks the status of an emoji submission.
  * `reviewemoji` (Bot admin only) - Shows each submission, allowing the caller to approve or reject each.

#### Extra Dependencies
  * `python-dateutil`

#### Additional Information
  * Cog will only be able to add emojis if your bot is whitelisted for emoji creation. I was unable to get my own bot whitelisted, as Discord told me they don't actually do this anymore. So unless that changes, this cog will never actually be useful.
  * Cog uses network to retrieve images for new emoji.


### StreamRole
Assign a configurable role to anyone who is streaming.
#### Commands
  * `streamroleset <command>` (Bot admin only) - Changes cog settings.
    * `toggle` - Turns role assignment for streamers on or off.
    * `role <role>` - Sets the role that should be assigned to members who are currently streaming.

#### Extra Dependencies
  * None.

#### Additional Information
  * None.


### Survey
Run surveys via Discord DMs, and display the results in a text channel. Can be used for surveys, polls, or signups for an event.
#### Commands
  * `startsurvey <role> <channel> <question> <options> <deadline>` (Bot admin only) - Starts a new survey.
  * `closesurvey <survey_id>` (Bot admin only) - Closes the survey with the specified ID immediately.
  * `changeanswer <survey_id>` - Allows the calling user to answer the survey with the specified ID again, replacing their previous answer.

#### Extra Dependencies
  * `python-dateutil`
  * `pytz`
  * `tabulate`

#### Additional Information
  * The deadline for the survey specifies an absolute point in time at which the survey should automatically close. If a timezone is provided, that is taken into account. If one is not, UTC is assumed. If we say that it is currently 10:00AM PST on June 15, 2016, the rules for deadlines are the following:
    * If a time of day is given, but a date is not, the deadline will be set to the next time the given time of day will occur. In our situation, if the deadline is set to `9:OOAM PST`, the deadline will be 9:00AM PST, June 16, 2016. If it is set to `11:00AM PST`, it will be 11:00AM PST, June 16, 2016.
    * `10:00AM PST` is `18:00 UTC`. If the deadline is given without a timezone, such as `6:00PM`, is assumed to be `6:00PM UTC`.
    * If a date is given, but a time of day is not, the deadline will be 00:00 (12:00 midnight) on the given date.
    * If both a time of day and date are given, the deadline will be set to that exact point in time.
    * For any deadline that includes a date, if the absolute point in time is more than one day in the past, an error will occur.
    * There is a situation where, if a given deadline has a date (and has or does not have a time of day), but is less than one day in the past, it will be pushed forward one day instead of erroring. This is a [known issue](https://github.com/tmercswims/tmerc-cogs/issues/31).
  * There is currently a problem with deadlines that are too far in the future. This is a limitation of Python itself, and I can do nothing to get around it. The documentation states delays should not be over one day, but the actual limitation is integer overflow, so delays can be longer than that. See https://docs.python.org/3/library/asyncio-eventloop.html#delayed-calls and https://bugs.python.org/issue20493 for more information.
  * Cog creates a *lot* of background tasks to listen for answers from people. Most of the time they are sleeping, so it should not affect performance.


## Support
If you find a reproducible bug with any of my cogs, or have a suggestion for an enhancement or new feature, please [open an issue on GitHub](https://github.com/tmercswims/tmerc-cogs/issues/new) and I will do my best to help you out.

If you are running into issues, please [join my support channel in the Red-Cogs server](https://discord.gg/HWfwYxN) and ask there.
