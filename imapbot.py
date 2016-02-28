#!/usr/bin/python

import imaplib
import email
import datetime
import config
import requests
import sys
import time
import logging
import traceback


TELEGRAM_API_BASE = "https://api.telegram.org/bot" + config.telegram['bot_token'] + "/"

logging.basicConfig(format='%(asctime)s %(message)s')
logging.captureWarnings(True)
logger = logging.getLogger();


def main():
    logger.info("Starting the bot.")
    folder = "INBOX"
    imap(config.email['host'], config.email['port'], config.email['email'], config.email['password'], folder)


def send_message(message):
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

    rv, data = M.search(None, config.email['search'])
    if rv != 'OK':
        logger.info("No messages found!")
        return

    for num in data[0].split():
        rv, data = M.fetch(num, '(RFC822)')
        if rv != 'OK':
            logger.error("ERROR getting message", num)
            return

        msg = email.message_from_string(data[0][1])

        content = decode_body(msg)
        if len(content) > config.email['maxLen']:
            content = content[:config.email['maxLen']] + "... _trimmed_"
        emailText = "*From:* " + msg['From'] +"\n*Subject:* " + msg['Subject'] + "\n==========\n" + content

        send_message(emailText)

def decode_body(msg):

    if msg.is_multipart():
        html = None
        for part in msg.get_payload():

            if part.get_content_charset() is None:
                # We cannot know the character set, so return decoded "something"
                text = part.get_payload(decode=True)
                continue

            charset = part.get_content_charset()

            if part.get_content_type() == 'text/plain':
                text = str(part.get_payload(decode=True), str(charset), "ignore")

            if part.get_content_type() == 'text/html':
                html = str(part.get_payload(decode=True), str(charset), "ignore")

        if text is not None:
            return text.strip()
        else:
            return html.strip()
    else:
        text = str(msg.get_payload(decode=True), msg.get_content_charset(), 'ignore')
        return text.strip()

def imap(host, port, user, password, folder):
    M = imaplib.IMAP4_SSL(host=host, port=port)

    try:
        rv, data = M.login(user, password)
    except imaplib.IMAP4.error:
        logger.error("LOGIN FAILED!!! ")
        sys.exit(1)

    rv, mailboxes = M.list()
    if rv != 'OK':
        M.close()
        M.logout()
        return
    else:
        log.info("Mailboxes:")
        log.info(mailboxes)

    rv, data = M.select(folder)
    if rv == 'OK':
        logger.info("Processing mailbox...\n")
        process_mailbox(M)
        M.close()
    else:
        logger.error("ERROR: Unable to open mailbox ", rv)

    M.logout()

if __name__ == '__main__':
    logger.warning("WARN!!")
    main()
