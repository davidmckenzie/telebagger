######
#
# Telelooper - Simple Telegram to Discord relay service, but this one loops once a second
#
######

from discord_hooks import Webhook
from telethon import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest, GetHistoryRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.updates import GetChannelDifferenceRequest
from telethon.tl.types import UpdateShortMessage, UpdateNewChannelMessage, PeerUser, PeerChat, PeerChannel, InputPeerEmpty, Channel, ChannelMessagesFilter, ChannelMessagesFilterEmpty
from time import sleep
import json
import os
import requests
import logging
import pprint
pp = pprint.PrettyPrinter(indent=4)
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m-%d %H:%M')
logger = logging.getLogger('telebagger')

with open('config.json') as config_file:
    config = json.load(config_file)

try:
    url = config['discord']['url']
    api_id = config['telegram']['api_id']
    api_hash = config['telegram']['api_hash']
    phone = config['telegram']['phone']
    channel_id = config['telegram']['channel_id']
    everyone = config['telegram']['everyone']
    loglevel = config['telegram']['loglevel']
except:
    logger.error('Error processing config file')

logger.setLevel(loglevel)

print('Connecting to Telegram...')

tclient = TelegramClient('session_name', api_id, api_hash, update_workers=4, spawn_read_thread=False)
tclient.connect()
if not tclient.is_user_authorized():
    tclient.send_code_request(phone)
    myself = tclient.sign_in(phone, input('Enter code: '))

lastmessage = 0
last_date = None
chunk_size = 20
chan_type = 'channel'
result = tclient(GetDialogsRequest(
                 offset_date=last_date,
                 offset_id=0,
                 offset_peer=InputPeerEmpty(),
                 limit=chunk_size
             ))
pp.pprint(result)
print("\nAvailable Channels:")
for p in result.chats:
    if type(p) is Channel:
        print(str(p.id)+": "+p.title)
        if p.id == channel_id:
            channel_name = p.title
            print(p.stringify())
            chan_type = 'channel'
for u in result.users:
    print(str(u.id)+": "+u.first_name)
    if u.id == channel_id:
        channel_name = u.first_name
        print(u.stringify())
        chan_type = 'user'
# for d in result.dialogs:
#     print(d.stringify())

if chan_type == 'channel':
    channelEnt = tclient.get_input_entity(PeerChannel(channel_id))
else:
    channelEnt = tclient.get_input_entity(PeerUser(channel_id))

try:
    logger.info("\nListening for messages from channel '{}' with ID '{}'".format(channel_name,channel_id))
except:
    logger.error("Whoops! Couldn't find channel ID '{}'".format(channel_id))

history = tclient(GetHistoryRequest(peer=channelEnt,
                                            offset_date=last_date,
                                            offset_id=0,
                                            add_offset=0,
                                            limit=10,
                                            max_id=0,
                                            min_id=0,
                                            hash=0
                                        ))
history.messages.reverse()
logger.info("\nLast 10 Messages:\n")
for m in history.messages:
    datetime = m.date.strftime('%Y-%m-%d %H:%M:%S')
    try:
        logger.info(datetime+" "+str(m.id)+": "+m.message)
    except:
        continue
    if m.id > lastmessage:
        lastmessage = m.id
    try:
        logger.info("Relaying Message {}".format(m.id))
        media = m.media
        if media is not None:
            logger.info("Would download image")
            logger.debug(media)
            # download_res = tclient.download_media(
            #     media, './downloads/')
            # logger.info("Download done: {}".format(download_res))
            # files = {'file': (open(download_res, 'rb'))}
            # response = requests.post(url, files=files)
            # logger.debug(response.text)
            # os.remove(download_res)
            # logger.debug("File deleted")
        if not m.message == '':
            if everyone:
                msgText = "@noteveryone {}".format(m.message)
            else:
                msgText = "{}".format(m.message)
            #msg = Webhook(url,msg=msgText)
            #msg.post()
    except:
        logger.info('Ignoring empty message {} action: {}'.format(m.id, m.action))
    try:
        logger.info(datetime+" "+str(m.id)+": "+m.message)
    except:
        logger.debug(m)

while True:
    try:
        messages = tclient(GetHistoryRequest(peer=channelEnt,
                                            offset_date=last_date,
                                            offset_id=0,
                                            add_offset=0,
                                            limit=50,
                                            max_id=0,
                                            min_id=lastmessage,
                                            hash=0
                                        ))
        if len(messages.messages) > 0:
            logger.debug('New Messages: ')
            logger.debug(messages)
            for m in messages.messages:
                datetime = m.date.strftime('%Y-%m-%d %H:%M:%S')
                if m.id > lastmessage:
                    lastmessage = m.id
                try:
                    logger.info("Relaying Message {}".format(m.id))
                    media = m.media
                    if media is not None:
                        logger.info("Will download image")
                        logger.debug(media)
                        download_res = tclient.download_media(
                            media, './downloads/')
                        logger.info("Download done: {}".format(download_res))
                        files = {'file': (open(download_res, 'rb'))}
                        response = requests.post(url, files=files)
                        logger.debug(response.text)
                        os.remove(download_res)
                        logger.debug("File deleted")
                    if not m.message == '':
                        if everyone:
                            msgText = "@everyone {}".format(m.message)
                        else:
                            msgText = "{}".format(m.message)
                        msg = Webhook(url,msg=msgText)
                        msg.post()
                except:
                    logger.info('Ignoring empty message {} action: {}'.format(m.id, m.action))
                try:
                    logger.info(datetime+" "+str(m.id)+": "+m.message)
                except:
                    logger.debug(m)
        sleep(2)
        continue
    except KeyboardInterrupt:
        break

tclient.disconnect()
