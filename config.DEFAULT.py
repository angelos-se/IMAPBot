telegram = dict(
    bot_token="",
)
email = dict(
	host = "imap.gmail.com",
	port = "993",
	email = "MYUSER",
	password = "SuperSecret",
	# This is from IMAP, "ALL" is also useful. Check IMAP specs for more info.
	search = "(UNSEEN)",
	maxLen = 500,
)
chats = dict(
		targetChatIds = [123,345],
)
