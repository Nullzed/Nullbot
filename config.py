import os
import bot_token

TEST_GUILD_ID   = bot_token.TEST_GUILD_ID
TEST_CHANNEL_ID = bot_token.TEST_CHANNEL_ID
NEIL_ID         = bot_token.NEIL_ID
HENRY_ID        = bot_token.HENRY_ID
HENRY_GUILD_ID  = bot_token.HENRY_GUILD_ID
DREXEL_GUILD_ID = bot_token.DREXEL_GUILD_ID

TOKEN           = bot_token.TOKEN

DEF_COLOR       = 0x704214

DREXEL_IGNORED_CHANNELS     = [ 'bots', 
                                'hombies',
                                'wordle-games' ]

DREXEL_APPROVED_CHANNELS    = [ 'general', 
                                'media', 
                                'paparazzi-sightings', 
                                'movies', 
                                'roles', 
                                'bdays', 
                                'music-chat', 
                                'song-recommendations', 
                                'bars', 
                                'band-names', 
                                'self-promo', 
                                'anagrams', 
                                'portmanteaus', 
                                'vc-chat' ]

script_path             = os.path.normpath(__file__) # i.e. /path/to/dir/foobar.py
script_dir              = os.path.split(script_path)[0] #i.e. /path/to/dir/
script_dir              = os.path.join(script_dir, 'data')
SERVER_SETTINGS_PATH    = os.path.join(script_dir, 'server_settings.json')

HENRY_PATH              = os.path.join(script_dir, 'henry_messages.json')
HENRY_TIME_PATH         = os.path.join(script_dir, 'last_henry_update.json')

DREXEL_OWNERS_PATH      = os.path.join(script_dir, 'drexel_messages_owners.json')
DREXEL_ALL_PATH         = os.path.join(script_dir, 'drexel_messages_all.json')
DREXEL_CHANNEL_PATH     = os.path.join(script_dir, 'drexel_messages_channels.json')
DREXEL_TIME_PATH        = os.path.join(script_dir, 'last_drexel_update.json')

HELP = """
`_help`:
*Shows this message.*

`_rename @[user] [new name]`:
*Allows a user to rename their friends using the power of community.*

`_setvoterequirements [number]`:
*Allows a user with manage server perms to change how many votes are required to pass/fail a poll.*

`_askhenry [question]`:
*Ask our great oracle, Henry, for an answer to any of your burning questions.*

`_askdrexel [*user or channel]`:
*Ask the entire Drexel University MIP program what they think! Optionally, you can ping or name Drexel users, but please don't ping people too much. You can also specify a channel to pull from.*
"""