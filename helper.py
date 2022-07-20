import discord
import json
import config
import random
from discord.ext import commands
import datetime

def str_to_embed(input: str, incolor = config.DEF_COLOR) -> discord.Embed:
    return discord.Embed(description=input)

# makes a string list of users
def make_user_list(users: list[discord.Member]) -> str:
    output = ""
    
    if len(users) > 1:
        for i in range(len(users)):
            if not(i >= len(users) - 1):
                output += f"`{users[i].display_name}`, "
            else:
                output += f"and `{users[i].display_name}`"
    else:
        output = f"`{users[0].display_name}`"

    return output

# can't be in an async function so it's here
def readjson(path) -> dict:
    try:
        with open(path, 'r') as file:      
                server_settings = json.load(file)
                return server_settings
    except:
        server_settings = {}
        return server_settings

# TODO: load henry's messages from a file
async def load_henry_from_file(path, bot: commands.Bot):
    henrylist = []

    try:
        with open(path, 'r') as file:      
                henrylist = json.load(file)
                print("loaded henry")          
    except:
        henrylist = []
    
    try:
        with open(config.HENRY_TIME_PATH, 'r') as file:
            dt = json.load(file)
            dt = float(dt['time updated'])
    except:
        dt = None
    
    return henrylist, dt
        

async def is_owner(ctx):
    return ctx.author.id == config.NEIL_ID