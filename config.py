import os
import bot_token

TEST_GUILD_ID = 264582377085337602
TEST_CHANNEL_ID = 487819730821054464
NEIL_ID = 86605650976571392

DEF_COLOR = 0xfad6a5

script_path = os.path.normpath(__file__) # i.e. /path/to/dir/foobar.py
script_dir = os.path.split(script_path)[0] #i.e. /path/to/dir/
SERVER_SETTINGS_PATH = os.path.join(script_dir, 'server_settings.json').replace("\\", "/")

HELP = """
`_help`:
*Shows this message.*

`_rename @[user] [new name]`:
*Allows a user to rename their friends using the power of community.*

`_setvoterequirements [number]`:
*Allows a user with manage server perms to change how many votes are required to pass/fail a poll.*
"""

TOKEN = bot_token.CONST_TOKEN