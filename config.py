import os
import bot_token

TEST_GUILD_ID = bot_token.TEST_GUILD_ID
TEST_CHANNEL_ID = bot_token.TEST_CHANNEL_ID
NEIL_ID = bot_token.NEIL_ID
HENRY_ID = bot_token.HENRY_ID
HENRY_GUILD_ID = bot_token.HENRY_GUILD_ID

DEF_COLOR = 0xfad6a5

script_path = os.path.normpath(__file__) # i.e. /path/to/dir/foobar.py
script_dir = os.path.split(script_path)[0] #i.e. /path/to/dir/
SERVER_SETTINGS_PATH = os.path.join(script_dir, 'server_settings.json').replace("\\", "/")
HENRY_PATH = os.path.join(script_dir, 'henry_messages.json')
HENRY_TIME_PATH = os.path.join(script_dir, 'last_henry_update.json')

HELP = """
`_help`:
*Shows this message.*

`_rename @[user] [new name]`:
*Allows a user to rename their friends using the power of community.*

`_setvoterequirements [number]`:
*Allows a user with manage server perms to change how many votes are required to pass/fail a poll.*

`_askhenry [question]`:
*Ask our great oracle, Henry, for an answer to any of your burning questions.*
"""

TOKEN = bot_token.REAL_TOKEN