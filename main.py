import discord
from discord.ext import commands
import json
from helper import *
from config import *
import typing
import time
import random
import asyncio
import time

bot = commands.Bot(command_prefix='_', help_command=None, intents=discord.Intents.all())

discord.Intents.reactions = True
discord.Intents.guilds = True

waiting_message_cache = []
id_user_dict = {}
server_settings = {} 
henry_messages = []
henry_time = 0.0

# Sets how many votes the bot should look for before closing a vote.
@bot.command()
async def setvoterequirements(ctx: commands.Context, arg: int):
    if ctx.author.guild_permissions.manage_guild == True:
        # set server vote pass/fail requirement numbers.
        with open(SERVER_SETTINGS_PATH, 'w') as file:
            global server_settings

            server_settings[str(ctx.guild.id)]['Vote Requirements'] = arg

            json.dump(server_settings, file, indent = 4)

        await ctx.send(embed = str_to_embed(f"Server vote requirements updated to a majority by {arg} votes."))
    else:
        await ctx.send(embed = str_to_embed("Invalid permissions. You must have manage server permissions to use this command."))

@bot.command()
@commands.check(is_owner)
async def fullupdatehenry(ctx: commands.Context, arg: int):
    global henry_messages
    global henry_time
    guild: discord.Guild = bot.get_guild(HENRY_GUILD_ID)
    henry: discord.Member = guild.get_member(HENRY_ID)
    henry_messages = []

    print("1")

    async with ctx.typing():
        i = 0
        for channel in guild.text_channels:
            print(f"Channel is {channel.name}")
            if channel.permissions_for(henry).read_messages:
                print(f"henry is allowed")
                async for message in channel.history(limit=arg):
                    if message.author == henry and len(message.content) > 0 and message.content.count(" ") > 0:
                        i += 1
                        print(f"message {i} added")
                        henry_messages.append(message.content)
    
        print("2")
        
        with open(HENRY_PATH, 'w') as file:
            json.dump(henry_messages, file)

        curtime = time.time()
        henry_time = curtime
        with open(HENRY_TIME_PATH, 'w') as file:
            datetimedict = {'time updated': curtime}
            json.dump(datetimedict, file)
        
        print("3")
        
        await ctx.send(embed=str_to_embed("Henry has been reloaded."))

@bot.command()
async def updatehenry(ctx: commands.Context):
    global henry_messages
    global henry_time
    guild: discord.Guild = bot.get_guild(config.HENRY_GUILD_ID)
    henry: discord.Member = guild.get_member(HENRY_ID)

    async with ctx.typing():
        i = 0
        for channel in guild.text_channels:
            print(f"Channel is {channel.name}")
            if channel.permissions_for(henry).read_messages:
                print(f"henry is allowed")
                async for message in channel.history(after=datetime.datetime.fromtimestamp(henry_time)):
                    if message.author == henry and len(message.content) > 0:
                        i += 1
                        print(f"message {i} added")
                        henry_messages.append(message.content)
        
    curtime = time.time()
    henry_time = curtime
    with open(HENRY_TIME_PATH, 'w') as file:
        datetimedict = {'time updated': curtime}
        json.dump(datetimedict, file)

    await ctx.send(embed=str_to_embed("Henry has been updated."))
    

@bot.command()
async def askhenry(ctx: commands.Context, *args):
    henry = bot.get_user(HENRY_ID)
    if len(henry_messages) > 0:
        message = discord.Embed(description=random.choice(henry_messages))
        message.set_author(name="Henry says:", icon_url=henry.avatar.url)

        await ctx.send(embed=message)
    else:
        await ctx.send(embed=str_to_embed("There are no saved messages from henry."))

# renames a user using the power of a voting majority
@bot.command()
async def rename(ctx: commands.Context, member: discord.Member, *args):
    name = ' '.join(args)
    message: discord.Message = await ctx.send(embed = str_to_embed(f"Rename {member.mention} to `{name}`?"))
    await message.add_reaction('👍')
    await message.add_reaction('👎')

    waiting_message_cache.append(message.id)
    id_user_dict[message.id] = [member, name, ctx.author]

# turns off the bot
@bot.command()
@commands.check(is_owner)
async def close(ctx: commands.Context):
    if ctx.author.id == NEIL_ID:
        await ctx.send(embed = str_to_embed("Bot will now stop!"))
        await bot.close()

# help command
@bot.command()
async def help(ctx: commands.Context):
    async with ctx.typing():
        mesEmb = discord.Embed(description=HELP, color = DEF_COLOR)
        mesEmb.set_author(icon_url = str(bot.user.avatar_url), name = "Nullbot commands overview")

        await ctx.send(embed = mesEmb)

@bot.command()
async def showvoterequirements(ctx: commands.Context):
    votereqs = server_settings[str(ctx.guild.id)]['Vote Requirements']

    await ctx.send(embed = str_to_embed(str(votereqs)))

@bot.listen()
async def on_ready():
    # load and save json of guild preferences, including vote pass/fail requirements
    global server_settings
    global henry_messages
    server_settings = readjson(SERVER_SETTINGS_PATH)

    with open(SERVER_SETTINGS_PATH, 'w', encoding='utf-8') as file:
        botguilds: list[discord.Guild] = bot.guilds

        for guild in botguilds:
            id = str(guild.id)

            if id not in server_settings.keys():
                server_settings[id] = {'Vote Requirements': 3}

        json.dump(server_settings, file, indent = 4)

    henry_messages = await load_henry_from_file(HENRY_PATH, bot)


    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for _help"))
    await bot.get_guild(TEST_GUILD_ID).get_channel(TEST_CHANNEL_ID).send(embed = str_to_embed("Bot is ready!"))

@bot.listen()
async def on_reaction_add(reaction: discord.Reaction, emoji: discord.Emoji):
    message: discord.Message = reaction.message

    # if we're waiting on the message for a vote then calculate
    if message.id in waiting_message_cache:
        reactions = message.reactions

        sVoteReq: int = server_settings[str(message.guild.id)]['Vote Requirements']

        vars = id_user_dict[message.id]
        member: discord.Member = vars[0]
        newName = vars[1]
        requester: discord.Member = vars[2]

        # if thumbs up greater than thumbs down by 3 members
        if reactions[0].count >= reactions[1].count + sVoteReq:

            users = [user async for user in reactions[0].users()]
            users.pop(0)
            users = make_user_list(users)

            # delete the original bot's message
            channel: discord.TextChannel = message.channel
            id = message.id
            await message.delete()

            async with channel.typing():
                try:
                    oldName = member.display_name
                    await member.edit(nick = newName)

                    newemb = discord.Embed(description = f"`{oldName}`'s name change to {member.mention} **APPROVED** by {users}.", color = DEF_COLOR)
                    newemb.set_author(icon_url = str(requester.avatar.url), name = f"Requested by {requester.display_name}")

                    await channel.send(embed = newemb)
                except discord.errors.Forbidden:
                    await channel.send(embed = str_to_embed("This bot doesn't have permissions to change this user's name. This could be because that user is the server owner."))

            # remove unneeded entries from lists to conserve memory
            waiting_message_cache.remove(id)
            id_user_dict.pop(id)

        elif reactions[0].count + sVoteReq <= reactions[1].count:

            users = [user async for user in reactions[1].users()]
            users.pop(0)
            users = make_user_list(users)
            
            # delete the original bot message
            channel = message.channel
            id = message.id
            await message.delete()

            async with channel.typing():
                newemb = discord.Embed(description = f"{member.mention}'s name change to `{newName}` **REJECTED** by {users}.", color = DEF_COLOR)
                newemb.set_author(icon_url = str(requester.avatar.url), name = f"Requested by {requester.display_name}")

                await channel.send(embed = newemb)
            
            # remove unneeded entries from lists to conserve memory
            waiting_message_cache.remove(id)
            id_user_dict.pop(id)

@bot.listen()
async def on_command_error(ctx: commands.Context, error):
    if ctx.command.name == "rename":
        await ctx.send(embed = str_to_embed("Incorrect usage. Proper usage of the command is `{0}rename @[member] [new name]`, without the braces.".format(bot.command_prefix)))
    elif ctx.command.name == "setvoterequirements":
        await ctx.send(embed = str_to_embed("Incorrect usage. Proper usage of the command is `{0}setvoterequirements [integer]`, without the braces.".format(bot.command_prefix)))


bot.run(TOKEN)