telegram = dict(
	bot_token="",  # register via @botmaster
	chat_ids = [123,345], # telegram account that will get the emails
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
