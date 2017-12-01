######
#
# Telebagger - Simple Telegram to Discord relay service
#
######

from discord_hooks import Webhook
from telethon import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import UpdateShortMessage, UpdateNewChannelMessage, PeerUser, PeerChat, PeerChannel, InputPeerEmpty, Channel
from time import sleep
import json
import logging
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('telebagger')

with open('config.json') as config_file:
    config = json.load(config_file)

try:
    url = config['discord']['url']
    api_id = config['telegram']['api_id']
    api_hash = config['telegram']['api_hash']
    phone = config['telegram']['phone']
    channel_id = config['telegram']['channel_id']
except:
    logger.error('Error processing config file')

print('Connecting to Telegram...')

tclient = TelegramClient('session_name', api_id, api_hash, update_workers=4, spawn_read_thread=False)
tclient.connect()
if not tclient.is_user_authorized():
    tclient.send_code_request(phone)
    myself = tclient.sign_in(phone, input('Enter code: '))

def callback(update):
    if type(update) is UpdateNewChannelMessage:
        try:
            print(update)
            print("Channel ID: {}".format(update.message.to_id.channel_id))
            if update.message.to_id.channel_id == channel_id:
                if not update.message.message == '':
                    msgText = "*{}*: @everyone {}".format(channel_name, update.message.message)
                    msg = Webhook(url,msg=msgText)
                    msg.post()
            else:
                logger.info('ignoring message to wrong channel')
        except:
            logger.info('no message')

#msg = Webhook(url,msg="Telebagger ready to bag yo telegrams")
#msg.post()

tclient.add_update_handler(callback)

last_date = None
chunk_size = 20
result = tclient(GetDialogsRequest(
                 offset_date=last_date,
                 offset_id=0,
                 offset_peer=InputPeerEmpty(),
                 limit=chunk_size
             ))
print("\nAvailable Channels:")
for p in result.chats:
    if type(p) is Channel:
        print(str(p.id)+": "+p.title)
        if p.id == channel_id:
            channel_name = p.title

try:
    logger.info("\nListening for messages from channel '{}' with ID '{}'".format(channel_name,channel_id))
except:
    logger.error("Whoops! Couldn't find channel ID '{}'".format(channel_id))

tclient.idle()
tclient.disconnect()