# amoorion-telegram

Telegram plugin of [amoorion](https://github.com/Sarverott/amoorion): a bot posts, reads, replies
and deletes in one chat (a group, a channel or a private chat) through the Bot
API.

Secrets in amoorion's vault: `telegram/token` (the bot's token from
@BotFather) and `telegram/chat` (the chat's id, e.g. `-1001234567890`, or
a public chat's `@username`); optional `telegram/uri` (default
https://api.telegram.org). The bot has to be a member of the chat, an
admin in a channel; in a group it sees messages of others only with
privacy mode off (@BotFather → /setprivacy) or when they mention it.
It deletes its own messages; others' only as an admin, and in groups only
within 48 hours of their sending.

Reading asks `getUpdates`: it sees what the chat said in the last 24 hours,
never the bot's own messages, and not at all while a webhook is set for the
bot. Text goes as it is (no Markdown), at most 4096 characters. The token
is part of every URL of the Bot API; errors never show it.

## Links

- [Documentation](https://amoorion.readthedocs.io/en/latest/platforms/telegram.html) · [as Markdown](https://amoorion.readthedocs.io/en/latest/platforms/telegram.html.md)
- [PyPI](https://pypi.org/project/amoorion-telegram/)
- [GitHub](https://github.com/Sarverott/amoorion/tree/master/packages/amoorion-telegram) · [issues](https://github.com/Sarverott/amoorion/issues)
- [What its vault entry holds](https://github.com/Sarverott/amoorion/blob/master/packages/amoorion-telegram/src/amoorion_telegram/schema.vault.json)
- [amoorion](https://github.com/Sarverott/amoorion) · [its documentation](https://amoorion.readthedocs.io/en/latest/) · [its web page](https://sarverott.github.io/amoorion/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
