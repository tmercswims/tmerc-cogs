# Contributing

Thank you for your interest in contributing! See the sections below for some relevant information about the different
ways that you may contribute.

## Issues
1. Use the templates provided when filing a [new issue][tmerc-new-issue].
2. When contributing to existing issues, keep the conversation on-topic.
3. Comments such as "Me too." or "+1" are not helpful and detract from the conversation. If you are experiencing an
   issue which is already open, a ":+1:" reaction is the best way to express that.
4. If you have additional information that you think could be helpful in solving an issue, are aware of a workaround, or
   have some other information to contribute, definitely share.
5. Do not comment on a closed issue if you are experiencing the same problem. Open a new issue, but feel free to
   reference the old one in your description.

## Code Contributions (Pull Requests)
1. Before spending the time to implement a feature, please consult with me in my
   [support channel][tmerc-support-discord] in the Red Cog Support server.
2. When submitting a fix for a reported issue, be sure to mention "fixes #\<issue number>" somewhere in your pull
   request and/or in a commit message. This ensures that issues and the commits/pull requests which fix them are linked
   together.
3. All code is linted using [Black][black-repo]. The automated builds will ensure that your code is passing, but you can
   save some time by checking it yourself. A Makefile, as well as batch, PowerShell, and Bash scripts, are provided for
   convenience. The flags set in those scripts are the same as the ones used by the automated builds.
4. I reserve the right to request any and all changes which I see fit on your pull request. That being said, I will
   always do my best to be fair and reasonable.
5. If your pull request is for i18n support/translations, please read more [here][tmerc-repo-translating].

[tmerc-new-issue]: https://github.com/tmercswims/tmerc-cogs/issues/new/choose
[tmerc-support-discord]: https://discord.gg/HWfwYxN
[tmerc-repo-translating]: TRANSLATING.md

[black-repo]: https://github.com/psf/black
