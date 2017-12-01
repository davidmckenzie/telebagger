# telebagger
Simple Telegram to Discord one-way relay service. Uses the [Discord-Webhooks](https://github.com/kyb3r/Discord-Hooks) and [Telethon](https://github.com/LonamiWebs/Telethon) libraries.

Monitors a specified Telegram channel and relays any messages received in that channel to a Discord webhook. Designed to run as a human user for channels where bots are not permitted.

## Installation
```
pip install telethon
```
Then copy config.example.json and set the fields accordingly.
* discord.url - Should be set to a Discord webhook URL. Your Discord admin will need to create this.
* telegram.api_id & api_hash - [These can be obtained from Telegram](https://core.telegram.org/api/obtaining_api_id)
* telegram.phone - Should be the phone number of the user you wish to connect as (remember to include country code)
* telegram.channel_id - This is the ID of the channel you are monitoring. If you don't have this, you will be presented with a list of available channels on first run of the script.

Once config is set up, simply run:
```
python3 telebagger.py
```

For autorestarts, use pm2:
```
pm2 start telebagger.py --interpreter=python3
```