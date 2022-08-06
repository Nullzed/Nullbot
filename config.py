import os
import bot_token

TEST_GUILD_ID           = bot_token.TEST_GUILD_ID
TEST_CHANNEL_ID         = bot_token.TEST_CHANNEL_ID
NEIL_ID                 = bot_token.NEIL_ID
HENRY_ID                = bot_token.HENRY_ID
HENRY_GUILD_ID          = bot_token.HENRY_GUILD_ID
DREXEL_GUILD_ID         = bot_token.DREXEL_GUILD_ID
UW_GUILD_ID             = bot_token.UW_GUILD_ID

TOKEN                   = bot_token.TOKEN

DEF_COLOR               = 0x00FFFF

DREXEL_IGNORED_CHANNELS = [ 'bots', 
                            'hombies',
                            'wordle-games' ]

UW_IGNORED_CHANNELS     = [ 'groovy-graveyard',
                            'schkloom-squad2therevival',
                            'askuw',
                            'happy-new-yore' ]

script_path             = os.path.normpath(__file__)
script_dir              = os.path.split(script_path)[0]
script_dir              = os.path.join(script_dir, 'data')
DATA_DIR                = script_dir

SERVER_SETTINGS_PATH    = os.path.join(script_dir, 'server_settings.json')

HENRY_PATH              = os.path.join(script_dir, 'henry_messages.json')
HENRY_TIME_PATH         = os.path.join(script_dir, 'last_henry_update.json')

drexel_script_dir       = os.path.join(script_dir, 'drexel')
DREXEL_OWNERS_PATH      = os.path.join(drexel_script_dir, 'drexel_messages_owners.json')
DREXEL_ALL_PATH         = os.path.join(drexel_script_dir, 'drexel_messages_all.json')
DREXEL_CHANNEL_PATH     = os.path.join(drexel_script_dir, 'drexel_messages_channels.json')
DREXEL_TIME_PATH        = os.path.join(drexel_script_dir, 'last_drexel_update.json')

uw_script_dir           = os.path.join(script_dir, 'uw')
UW_OWNERS_PATH          = os.path.join(uw_script_dir, 'uw_messages_owners.json')
UW_ALL_PATH             = os.path.join(uw_script_dir, 'uw_messages_all.json')
UW_CHANNEL_PATH         = os.path.join(uw_script_dir, 'uw_messages_channels.json')
UW_PINNED_PATH          = os.path.join(uw_script_dir, 'uw_messages_pinned.json')
UW_TIME_PATH            = os.path.join(uw_script_dir, 'last_uw_update.json')

BANK_PATH               = os.path.join(script_dir, 'bank.json')
STARTING_MONEY          = 500

HELP = """
**This bot now supports slash commands!**

`_help` | *Shows this message.*

`_rename [user] [new name]` | *Allows a user to rename their friends using the power of community.*

`_setvoterequirements [integer]` | *Allows a user with manage server perms to change how many votes are required to pass/fail a poll.*

`_showvoterequirements` | *Shows the required amount of votes on this server.*

`_askhenry [question]` | *Ask Henry his opinion on things.*

`_askdrexel [*user or channel]` | *Ask the entire Drexel University MIP program what they think! Optionally, you can ping or name Drexel users, but please don't ping people too much. You can also specify a channel to pull from, or if you want pinned message (or both).*

`_askuw [*user or channel]` | *Ask people from Washington about life. Optionally, you can ping or name users, but please don't ping people too much. You can also specify a channel to pull from, or if you want pinned message (or both).*
"""

ADMINHELP = """
`_adminhelp`:
*Shows this message.*

`_close`:
*Closes the bot.*

`_reload [string]`:
*Reloads a specified extension.*

`_load [string]`:
*Loads a specified extension.*

`_sync`:
*Syncs slash commands.*

`_showsettings`:
*Prints the dictionary of server settings.*

`_fullupdatehenry`:
*Fully caches through the specified server to scrape henry's messages.*

`_fullupdatedrexel`:
*Fully caches and scrapes the drexel server's messages.*

`_fullupdateuw`:
*Fully caches and scrapes the uw server's messages.*

`_updatehenry`:
*Updates henry's messages since the last timestamp.*

`_updatedrexel`:
*Updates drexel's messages since the last timestamp.*

`_updateuw`:
*Updates uw's messages since the last timestamp.*
"""