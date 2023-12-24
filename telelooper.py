######
#
# Telelooper - Simple Telegram to Discord relay service, but this one loops once a second
#
######
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from discord_hooks import Webhook
import logging
import json
import os
import requests
from time import sleep

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m-%d %H:%M')
logger = logging.getLogger('telebagger')

# Load configuration
with open('config.json') as config_file:
    config = json.load(config_file)

async def main():
    tclient = TelegramClient('session_name', config['telegram']['api_id'], config['telegram']['api_hash'])
    await tclient.connect()

    if not await tclient.is_user_authorized():
        await tclient.send_code_request(config['telegram']['phone'])
        await tclient.sign_in(config['telegram']['phone'], input('Enter code: '))

    lastmessage = 0
    channel_id = config['telegram']['channel_id']

    while True:
        try:
            channelEnt = await tclient.get_input_entity(channel_id)
            messages = await tclient(GetHistoryRequest(
                peer=channelEnt,
                offset_date=None,
                offset_id=0,
                add_offset=0,
                limit=50,
                max_id=0,
                min_id=lastmessage,
                hash=0
            ))

            for m in messages.messages:
                if m.id > lastmessage:
                    lastmessage = m.id
                    try:
                        # Process and relay the message
                        if m.message:
                            msgText = f"@everyone {m.message}" if config['telegram']['everyone'] else m.message
                            Webhook(config['discord']['url'], msg=msgText).post()
                    except Exception as e:
                        logger.error(f"Error processing message {m.id}: {e}")

            sleep(2)

        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"An error occurred: {e}")

    await tclient.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
