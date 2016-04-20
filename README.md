# IMAPBot
Telegram bot for watching an IMAP account and sending a message when you receive
a new email.

The bot only sends messages, it does not respond or listen.

## Configuration
There is only one configuration file. Copy `config.TEMPLATE.py` to `config.py`
and fill in the details. Note that you have to create an individual bot, the
details of the process can be found at https://core.telegram.org/bots .

- `bot_token`: When the bot is regsitered via [@botfather](https://telegram.me/botfather)
  it will get a unique and long token. This is that token.
- `chat_ids`: This bot posts messages only to predefined chats, which can be a
groupchat or individual. The easiest way to get the id of the chat is to add the
bot to the chat and then check https://api.telegram.org/<bot_token>/getUpdates
on your [browser](http://www.getfirefox.com). Bot should be added to the chat to
be able to post.
- `email.{host,port}`: Settings of the IMAP server.
- `email.{email,password}`: Username and password for the account. On many
servers email/username should be in format `user@hostname.com`. If you enable
2-factor authentication for GMail, you have to create and application password
for the bot, it does not support 2-factor authentication.
- `email.search`: This is an IMAP command. `(UNSEEN)` gets only the unread
messages and mark them as read.  You can put a search criterion here.
- `email.maxLen`: Email will be trimmed if it is longer than this value.

## Usage
After creating `config.py` and putting in the correct values, the bot can be
run with the command `./imapbot.py`. It will get the new messages, or the ones
that satisfy the search criterion, and post them to the specified chats.

Currently the bot is not memory resilient, i.e., it finishes its job and exits.
Therefore, a cron job should be created to regularly check the emails. If you
clone this repo into `/opt/imapbot/` then you can add the following line to your
`crontab` file to run the bot every 5 minutes.

    */5 * * * *     /opt/imapbot/imapbot.py
    
To open the crontab file type `crontab -e`.
