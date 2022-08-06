import discord
from discord.ext import commands
import json
import config


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
def readjsondict(path) -> dict:

    try:
        with open(path, 'r') as file: 
                output = json.load(file)
                print(f"Successfully loaded {file.name}")
                return output
    except FileNotFoundError:
        print(f"Unable to load file from {path}, returning blank dictionary.")
        return {}
    except Exception as e:
        print(f"Unspecific error {e}, returning blank dictionary.")
        return {}


# load henry's messages from a file
def load_henry_from_file(path):

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
        dt = 0.0
    
    return henrylist, dt


def remove_nullbot(members: list[discord.Member]) -> list[discord.Member]:

    # Nullbot id: 264560337003479060 testbot id: 999002203014570054
    for member in members:
        if member.id == 264560337003479060:
            members.remove(member)
    
    return members


def is_owner(ctx: commands.Context):
    return ctx.author.id == config.NEIL_ID

def app_is_owner(interaction: discord.Interaction):
    return interaction.user.id == config.NEIL_ID

def is_manager(ctx: commands.Context):
    return ctx.author.guild_permissions.manage_guild