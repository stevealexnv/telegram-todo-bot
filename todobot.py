#! /usr/bin/python3
import json
import requests
import time
import urllib
from dbhelper import DBHelper

db = DBHelper()

TOKEN = "751013247:AAHDXGvBtiZA9MSyWOlohHP1SDKbfFQFrjI"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset = None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)

def handle_updates(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            items = db.get_items(chat)
            if text == "/start":
                send_message("Welcome! I'm TuTuDu, your personal To Do list bot. Send any text to me and I'll store it as an item. Send the text again to delete it from the list.", chat)
            elif text in items:
                db.delete_item(text, chat)
                items = db.get_items(chat)
            else:
                db.add_item(text, chat)
                items = db.get_items(chat)
            message = "\n".join(items)
            send_message(message, chat)
        except KeyError:
            pass

def main():
    db.setup()
    last_update_id = None
    while True:
        print("getting updates")
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)

if __name__ == '__main__':
    main()
