#!/usr/bin/python

import imaplib
import email
import datetime
import config
import requests
import sys
import sqlite3

TELEGRAM_API_BASE = "https://api.telegram.org/bot" + config.telegram['bot_token'] + "/"


def main():
    print("main")
    conn = sqlite3.connect('imapbot.sqlite')
    create_database(conn)
    imap("imap.gmail.com", 993, config.test['email'], config.test['password'], "INBOX")


def create_database(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS imapbot (
        email VARCHAR(50),
        password VARCHAR(50),
        server VARCHAR(50),
        port INT,
        telegram_owner VARCHAR(50),
        telegram_send VARCHAR(50)
        )
    """)


def send_message(message):
    print("Sending message")
    requesturl = TELEGRAM_API_BASE + "sendMessage"
    payload = {"chat_id": config.telegram['chat_id'], "text": message}

    response = requests.post(requesturl, data=payload)
    print(response.text)
    return


def process_mailbox(M):
    """
    Do something with emails messages in the folder.
    For the sake of this example, print some headers.
    """

    rv, data = M.search(None, "ALL")
    if rv != 'OK':
        print("No messages found!")
        return

    for num in data[0].split():
        rv, data = M.fetch(num, '(RFC822)')
        if rv != 'OK':
            print("ERROR getting message", num)
            return

        msg = email.message_from_bytes(data[0][1])
        hdr = email.header.make_header(email.header.decode_header(msg['Subject']))
        subject = str(hdr)
        print('Message %s: %s' % (num, subject))
        print('Raw Date:', msg['Date'])
        # Now convert to local date-time
        date_tuple = email.utils.parsedate_tz(msg['Date'])
        if date_tuple:
            local_date = datetime.datetime.fromtimestamp(
                    email.utils.mktime_tz(date_tuple))
            print("Local Date:", local_date.strftime("%a, %d %b %Y %H:%M:%S"))


def imap(host, port, user, password, folder):
    M = imaplib.IMAP4_SSL(host=host, port=port)

    try:
        rv, data = M.login(user, password)
    except imaplib.IMAP4.error:
        print("LOGIN FAILED!!! ")
        sys.exit(1)

    print(rv, data)

    rv, mailboxes = M.list()
    if rv == 'OK':
        print("Mailboxes:")
        print(mailboxes)

    rv, data = M.select(folder)
    if rv == 'OK':
        print("Processing mailbox...\n")
        process_mailbox(M)
        M.close()
    else:
        print("ERROR: Unable to open mailbox ", rv)

    M.logout()


if __name__ == '__main__':
    main()
