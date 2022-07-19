import discord
import json
import config

def str_to_embed(input: str, incolor = config.DEF_COLOR) -> discord.Embed:
    return discord.Embed(description=input, color=incolor)

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

async def is_owner(ctx):
    return ctx.author.id == config.NEIL_ID