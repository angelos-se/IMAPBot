#!/usr/bin/python

import imaplib
import email
import datetime
import config
import requests
import sys
import json
import time
import traceback


TELEGRAM_API_BASE = "https://api.telegram.org/bot" + config.telegram['bot_token'] + "/"

ftime = "%Y%m%d%H%M%S%f"
def main():
    print("main")
    cfgfile = dict(fromdate=datetime.datetime(1980, 1, 1).strftime(ftime))
    fromdate = datetime.datetime.min
    try:
        with open("config.json","rt") as f:
            cfgfile = json.load(f)
        fromdate = datetime.datetime.strptime(cfgfile["fromdate"], ftime)
    except BaseException as e:
        print ("error while loading config.json:\n%r" % e)
    lastdate = imap("imap.gmail.com", 993, config.temp['email'], config.temp['password'], "INBOX", fromdate)
    cfgfile["fromdate"] = lastdate.strftime(ftime)
    with open("config.json", "wt") as f:
        f.write(json.dumps(cfgfile))
    




def send_message(message):
    print("Sending message")
    requesturl = TELEGRAM_API_BASE + "sendMessage"
    payload = {"chat_id": config.telegram['chat_id'], "text": message}

    response = requests.post(requesturl, data=payload)
    print(response.text)
    return


def process_mailbox(M, fromdate):
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
        #print('Message %s: %s' % (num, subject))
        #print('Raw Date:', msg['Date'])
        # Now convert to local date-time
        date_tuple = email.utils.parsedate_tz(msg['Date'])
        local_date = None
        if date_tuple:
            local_date = datetime.datetime.fromtimestamp(
                    email.utils.mktime_tz(date_tuple))
            #print("Local Date:", local_date.strftime("%a, %d %b %Y %H:%M:%S"))
        if not local_date or local_date > fromdate:
            body = decode_body(msg)
            print(body)
            send_message(subject+"\n"+str(body))

def decode_body(msg):

    if msg.is_multipart():
        html = None
        for part in msg.get_payload():

            print ("%s, %s" % (part.get_content_type(), part.get_content_charset()))

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
        
def imap(host, port, user, password, folder, fromdate):
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
        print("Processing mailbox from date %r"%fromdate)
        process_mailbox(M, fromdate)
        M.close()
    else:
        print("ERROR: Unable to open mailbox ", rv)

    M.logout()
    
    return datetime.datetime.now()

if __name__ == '__main__':
    logger.warning("WARN!!")
    main()
