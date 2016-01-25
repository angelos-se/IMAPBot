#!/usr/bin/python

from flask import Flask, request
import config
import requests
import sys
import json

TELEGRAM_API_BASE = "https://api.telegram.org/bot" + config.telegram['bot_token'] + "/"
PUBLIC_IP_API = "https://api.ipify.org"


def main():
    setwebhook()
    app = Flask(__name__)

    @app.route('/')
    def hello():
        return 'Hello World!'

    @app.route('/' + config.telegram['bot_token'], methods=['POST'])
    def webhook():
        update = request.get_json(force=True)
        print(update.message.chat_id)
        return 'OK'

    try:
        app.run(host='0.0.0.0',
                port=8443,
                debug=True)
    except OSError as err:
        print("[ERROR] " + err.strerror, file=sys.stderr)
        print("[ERROR] The program will now terminate.", file=sys.stderr)


def setwebhook():
    print("Setting webhook")
    requesturl = TELEGRAM_API_BASE + "setWebhook"
    publicip_response = requests.get(PUBLIC_IP_API)
    print(publicip_response.content)
    payload = {"url": publicip_response.content}

    response = requests.post(requesturl, data=payload)
    if not json.loads(response.text)['ok']:
        print("Setting the webhook was not successful. Terminating.", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
