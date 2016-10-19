[![Build Status](https://travis-ci.org/tmercswims/tmerc-cogs.svg?branch=master)](https://travis-ci.org/tmercswims/tmerc-cogs)

# tmerc-cogs

Cogs for Twentysix26's [Red Discord bot](https://github.com/Twentysix26/Red-DiscordBot).

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
    * `steamkey` - Sets the Steam API key, which is used to look up users' vanity URLs. It can be obtained from [here](https://steamcommunity.com/dev/apikey). The message containing the command (and password) is deleted immediately.
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
  * `tabulate`

#### Additional Information
  * Cog uses network to retrieve database from server.
  * Cog runs semi-complex SQL queries on the retrieved database to get information, which can potentially be processor intensive.


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
Play sounds in voice channels.
#### Commands
  * `playsound <soundname>` - Plays the specified sound in the voice channel in which the caller is currently. `soundname` must be the case-accurate filename of a sound in `data/playsound`, excluding the extension.
  * `allsounds` - Sends a DM to the caller with an alphabetical list of every sound.
  * `addsound [link]` (Bot mod only) - Adds the provided sound. Must be called either as the comment on an uploaded file (Discord attachment) **or** a direct link to a sound file must be provided.
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
  * `randimage <directory>` - Uploads a random image from the `directory`, which must be inside `data/randimage/`.

#### Extra Dependencies
  * None.

#### Additional Information
  * Cog can potentially use an *enormous* amount of disk space, but images must be added directly by the owner (for now), so it is easily controlled.


### Randimals
Shows random animals.
#### Commands
  * `cat` - Shows a random cat.
  * `dog` - Shows a random dog.

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


### Say
Echoes the input in a variety of ways.
#### Commands
  * `say <text>` - Says `text`.
  * `tts <text>` - Says `text` with TTS.
  * `reply <text>` - Says `text` as an @reply to the caller.
  * `pm <text>` - Sends `text` as a DM to the caller.

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
  * There is currently a bug with deadlines that are more than 24 hours in the future, which (I think) may be a limitation of Python itself. (I swear I remember reading something in some documentation that the limit for waiting was one day, but I could be wrong.) I will be investigating this at some point.
  * Cog creates a *lot* of background tasks to listen for answers from people. Most of the time they are sleeping, so it should not affect performance.


## Support
If you are having issues with any of these cogs, please [open an issue on GitHub](https://github.com/tmercswims/tmerc-cogs/issues/new) and I will do my best to help you out.

I am also available on Discord, `tmerc#2986`. I am a member of both TwentySix26's Red server and the Discord API server.
