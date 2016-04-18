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
import re
import sys

reload(sys)
sys.setdefaultencoding('utf8')

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
    for chatId in config.telegram['chat_ids']:
        payload = {"parse_mode": "Markdown", "chat_id": chatId, "text": message}
        response = requests.post(requesturl, data=payload)
    if response.text.find("error_code") > 0:
        logger.warning("There was an error during send message: " + response.text)
        logger.warning("Message is: " + message)
        msg = "*Error!* Cannot send message. Check the log for details."
        payload = {"parse_mode": "Markdown", "chat_id": chatId, "text": msg}
        response = requests.post(requesturl, data=payload)
        if response.text.find("error_code") > 0:
            logger.warning("Failception :(")
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

        content, extras = decode_body(msg)
        extraText = ""
        if extras:
            extraText = "\n " + unichr(10133) +" **" + str(len(extras)) + " attachments:**"
            for (name, cont) in extras:
                extraText += "\n- " + str(name)
        # remove markdown which would confuse the parser
        content = re.sub('[\*_]', '', content)
        if len(content) > config.email['maxLen']:
            content = content[:config.email['maxLen']] + "... _trimmed_"
        subject, encoding = email.Header.decode_header(msg['Subject'])[0]
        emailText = "*From:* " + msg['From'] + "\n*Subject:* " + subject + "\n==========\n" + content + " " + extraText

        send_message(emailText)

def decode_body(msg):
    extras = []
    if msg.is_multipart():
        html = None
        text = None
        
        for part in msg.walk():

            if part.get_content_type().startswith('multipart/'):
                continue
            elif part.get_content_type() == 'text/plain':
                text = part.get_payload(decode=True)
            elif part.get_content_type() == 'text/html':
                html = part.get_payload(decode=True)
            elif part.get_content_charset() is None:
                # We cannot know the character set, so return decoded "something"
                extras.append((part.get_filename(), part.get_payload(decode=True)))

        if text is not None:
            return (text.strip(), extras)
        elif html is not None:
            return (html.strip(), extras)
        return ("", extras)
    else:
        text = msg.get_payload(decode=True)
        return (text.strip(), extras)

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
        logger.info("Mailboxes:")
        logger.info(mailboxes)

    rv, data = M.select(folder)
    if rv == 'OK':
        logger.info("Processing mailbox...\n")
        process_mailbox(M)
        M.close()
    else:
        logger.error("ERROR: Unable to open mailbox ", rv)

    M.logout()

if __name__ == '__main__':
    main()
