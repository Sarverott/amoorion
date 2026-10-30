# amoorion-discord

Discord plugins of [amoorion](https://github.com/Sarverott/amoorion), both ways of decision Q12:

- **`discord`**: a bot posts, reads, replies and deletes in one channel, through
  the REST API. Secrets in amoorion's vault: `discord/token` (the bot's
  token, Developer Portal → the application → Bot) and `discord/channel`
  (the channel id: Developer Mode on, right click → Copy Channel ID);
  optional `discord/uri` (default https://discord.com/api/v10). The bot
  needs the permissions View Channel, Send Messages and Read Message
  History in that channel, and the **Message Content** intent switched on
  in the Developer Portal, or it reads messages of others as empty.
  Deleting others' messages needs Manage Messages too.
- **`discord-webhook`**: posts, and deletes what it posted; no bot. Secret
  `discord-webhook/url`: the channel's webhook URL (channel settings →
  Integrations → Webhooks).

Both send at most 2000 characters and never ping: mentions like
`@everyone` stay plain text. Live listening through the gateway comes with
the daemon's listeners.

## Links

- [Documentation](https://amoorion.readthedocs.io/en/latest/platforms/discord.html) · [as Markdown](https://amoorion.readthedocs.io/en/latest/platforms/discord.html.md)
- [PyPI](https://pypi.org/project/amoorion-discord/)
- [GitHub](https://github.com/Sarverott/amoorion/tree/master/packages/amoorion-discord) · [issues](https://github.com/Sarverott/amoorion/issues)
- [What its vault entry holds](https://github.com/Sarverott/amoorion/blob/master/packages/amoorion-discord/src/amoorion_discord/schema.vault.json)
- [amoorion](https://github.com/Sarverott/amoorion) · [its documentation](https://amoorion.readthedocs.io/en/latest/) · [its web page](https://sarverott.github.io/amoorion/)
- [Discord API](https://discord.com/developers/docs)
