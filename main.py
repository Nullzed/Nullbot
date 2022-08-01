import discord
from discord.ext import commands
import json
from helper import *
from config import *
import time
import random
import time
import typing
import datetime


bot = commands.Bot(command_prefix='_', help_command=None, intents=discord.Intents.all())

discord.Intents.reactions   = True
discord.Intents.guilds      = True

waiting_message_cache   = [] # voting messages being waited one
id_user_dict            = {} # rename voting messages
server_settings         = {} # voting settings for each server
henry_messages          = [] # messages henry has sent
henry_time              = 0.0 # last time since henry was updated
drexel_messages_all     = {} # all the drexel messages
drexel_messages_owners  = {} # all the drexel messages sorted by owner
drexel_messages_channel = {} # all the drexel messages sorted by channel
drexel_last_update      = 0.0 #last time since drexel was updated


# Sets how many votes the bot should look for before closing a vote.
@bot.command()
async def setvoterequirements(ctx: commands.Context, arg: int):

    if ctx.author.guild_permissions.manage_guild == True:
        # set server vote pass/fail requirement numbers.
        with open(SERVER_SETTINGS_PATH, 'w') as file:
            # if arg < 1: arg = 1

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

    guild: discord.Guild    = bot.get_guild(HENRY_GUILD_ID)
    henry: discord.Member   = guild.get_member(HENRY_ID)
    henry_messages          = []
    timestart               = time.time()

    async with ctx.typing():
        i = 0

        for channel in guild.text_channels:
            print(f"Channel is {channel.name}")

            if channel.permissions_for(henry).read_messages and channel.name != "bot-commands":
                print(f"henry is allowed")

                async for message in channel.history(limit=arg):
                    if message.author == henry and len(message.content) > 0:
                        i += 1
                        print(f"message {i} added")

                        henry_messages.append(message.content)
        
        with open(HENRY_PATH, 'w') as file:
            json.dump(henry_messages, file, indent=4)

        curtime     = time.time()
        henry_time  = curtime
        with open(HENRY_TIME_PATH, 'w') as file:
            datetimedict = {'time updated': curtime}
            json.dump(datetimedict, file, indent=4)

        timeend    = time.time()
        timedeltas = timeend - timestart
        timedeltam = timedeltas / 60
        
        await ctx.send(embed=str_to_embed(f"Henry has been updated, which took about {int(timedeltas)} seconds or about {int(timedeltam)}:{int(timedeltas - (timedeltam * 60))} minutes, and loaded {len(henry_messages)} messages."))


@bot.command()
@commands.check(is_owner)
async def fullupdatedrexel(ctx: commands.Context, arg: int):

    print("fullupdatedrexel called")

    global drexel_messages_owners
    global drexel_messages_all
    global drexel_messages_channel

    drexel_messages_owners  = {}
    drexel_messages_all     = {}
    guild: discord.Guild    = bot.get_guild(DREXEL_GUILD_ID)
    timestart               = time.time()

    async with ctx.typing():
        i = 0

        for channel in guild.text_channels:
            if channel.name not in DREXEL_IGNORED_CHANNELS and channel.name in DREXEL_APPROVED_CHANNELS:
                async for message in channel.history(limit=arg):
                    if len(message.content) > 0:
                        i += 1

                        member      = message.author
                        memberid    = str(member.id)
                        channelid   = str(message.channel.id)
                        
                        if memberid in drexel_messages_owners.keys():
                            drexel_messages_owners[memberid].append(message.content)
                        else:
                            drexel_messages_owners[memberid] = [message.content]

                        if channelid in drexel_messages_channel.keys():
                            drexel_messages_channel[channelid][message.content] = memberid
                        else:
                            drexel_messages_channel[channelid] = {message.content: memberid}
                        
                        drexel_messages_all[message.content] = memberid
                        
                        print(f"message {i} added")

        print("messages scraped")
        with open(DREXEL_OWNERS_PATH, 'w') as file:
            json.dump(drexel_messages_owners, file, indent=4)
        with open(DREXEL_ALL_PATH, 'w') as file:
            json.dump(drexel_messages_all, file, indent=4)
        with open(DREXEL_CHANNEL_PATH, 'w') as file:
            json.dump(drexel_messages_channel, file, indent=4)
        print("messages saved")

        curtime = time.time()
        with open(DREXEL_TIME_PATH, 'w') as file:
            json.dump({'time updated': curtime}, file)
        print("time saved")

        timeend    = time.time()
        timedeltas = timeend - timestart
        timedeltam = timedeltas // 60
        
        await ctx.send(embed=str_to_embed(f"Drexel has been updated, which took about {int(timedeltas)} seconds or {int(timedeltam)}:{int(timedeltas - (timedeltam * 60))} minutes, and loaded {i} messages."))


@bot.command()
@commands.check(is_owner)
async def updatehenry(ctx: commands.Context):

    global henry_messages
    global henry_time

    guild: discord.Guild    = bot.get_guild(config.HENRY_GUILD_ID)
    henry: discord.Member   = guild.get_member(HENRY_ID)
    timestart               = time.time()

    async with ctx.typing():
        i = 0
        for channel in guild.text_channels:
            print(f"Channel is {channel.name}")
            if channel.permissions_for(henry).read_messages and channel.name != "bot-commands":
                print(f"henry is allowed")
                async for message in channel.history(after=datetime.datetime.fromtimestamp(henry_time)):
                    if message.author == henry and len(message.content) > 0:
                        i += 1
                        print(f"message {i} added")
                        henry_messages.append(message.content)
        
    curtime     = time.time()
    henry_time  = curtime
    with open(HENRY_TIME_PATH, 'w') as file:
        datetimedict = {'time updated': curtime}
        json.dump(datetimedict, file)

    timeend    = time.time()
    timedeltas = timeend - timestart
    timedeltam = timedeltas / 60

    await ctx.send(embed=str_to_embed(f"Henry has been updated, which took about {int(timedeltas)} seconds or {int(timedeltam)}:{int(timedeltas - (timedeltam * 60))} minutes, and loaded {i} new messages."))
    

@bot.command()
@commands.check(is_owner)
async def updatedrexel(ctx: commands.Context):

    global drexel_messages_owners
    global drexel_messages_all
    global drexel_messages_channel
    global drexel_last_update
    
    guild: discord.Guild            = bot.get_guild(DREXEL_GUILD_ID)
    timestart                       = time.time()
    drexelLastDT: datetime.datetime = datetime.datetime.fromtimestamp(drexel_last_update)

    async with ctx.typing():
        i = 0
        for channel in guild.channels:
            if channel.name not in DREXEL_IGNORED_CHANNELS and channel.name in DREXEL_APPROVED_CHANNELS:
                async for message in channel.history(after=drexelLastDT):
                    i += 1

                    member      = message.author
                    memberid    = str(member.id)
                    channelid   = str(message.channel.id)
                    
                    if memberid in drexel_messages_owners.keys():
                        drexel_messages_owners[memberid].append(message.content)
                    else:
                        drexel_messages_owners[memberid] = [message.content]

                    if channelid in drexel_messages_channel.keys():
                        drexel_messages_channel[channelid][message.content] = memberid
                    else:
                        drexel_messages_channel[channelid] = {message.content: memberid}                
                    
                    drexel_messages_all[message.content] = memberid
                    
                    print(f"message {i} added")

        print("messages scraped")
        with open(DREXEL_OWNERS_PATH, 'w') as file:
            json.dump(drexel_messages_owners, file, indent=4)
        with open(DREXEL_ALL_PATH, 'w') as file:
            json.dump(drexel_messages_all, file, indent=4)
        with open(DREXEL_CHANNEL_PATH, 'w') as file:
            json.dump(drexel_messages_channel, file, indent=4)
        print("messages saved")

        curtime = time.time()
        with open(DREXEL_TIME_PATH, 'w') as file:
            json.dump({'time updated': curtime}, file)
        print("time saved")

        timeend    = time.time()
        timedeltas = timeend - timestart
        timedeltam = timedeltas / 60
        
        await ctx.send(embed=str_to_embed(f"Drexel has been updated since the last timestamp, which took about {int(timedeltas)} seconds or {int(timedeltam)}:{int(timedeltas - (timedeltam * 60))} minutes, and loaded {i} new messages."))


@bot.command()
async def askhenry(ctx: commands.Context, *args):

    print("askhenry called")

    async with ctx.typing():
        henry = bot.get_user(HENRY_ID)
        if len(henry_messages) > 0:
            print("Henry has messages")

            message = discord.Embed(description=random.choice(henry_messages))
            message.set_author(name="Henry says:", icon_url=henry.avatar.url)

            print("random message selected")

            await ctx.send(embed=message)
        else:
            await ctx.send(embed=str_to_embed("There are no saved messages from henry."))


@bot.command()
async def askdrexel(ctx: commands.Context, member: typing.Optional[discord.Member] = None, channel: typing.Optional[discord.TextChannel] = None):

    print("askdrexel called")
    name    = ""
    message = ""
    if member:
        print("member found")

        id              = str(member.id)
        memberMessages  = drexel_messages_owners[id]
        message         = random.choice(memberMessages)

        name = f"{member.nick} says:"
    elif channel:
        print("channel found")

        id                      = str(channel.id)
        channelMessages: dict   = drexel_messages_channel[id]
        message                 = random.choice(list(channelMessages.keys()))
        member: discord.Member  = ctx.guild.get_member(int(drexel_messages_channel[id][message]))

        print(channel)
        print(message)

        name = f"{member.nick} in #{channel.name} says:"
    else:
        print("member or channel not found")

        message                 = random.choice(list(drexel_messages_all.keys()))
        member: discord.Member  = bot.get_guild(DREXEL_GUILD_ID).get_member(int(drexel_messages_all[message]))
        
        print(message)
        print(member.nick)

        name = f"{member.nick} says:"

    message = discord.Embed(description=message)
    message.set_author(name=name, icon_url=member.avatar.url)

    await ctx.send(embed=message)


# renames a user using the power of a voting majority
@bot.command()
async def rename(ctx: commands.Context, member: discord.Member, *args):

    name                        = ' '.join(args)
    message: discord.Message    = await ctx.send(embed = str_to_embed(f"Rename {member.mention} to `{name}`?"))
    id_user_dict[message.id]    = [member, name, ctx.author]
    waiting_message_cache.append(message.id)    

    await message.add_reaction('👍')
    await message.add_reaction('👎')


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

    print("help called")

    mesEmb = discord.Embed(description=HELP, color = DEF_COLOR)
    mesEmb.set_author(icon_url = str(bot.user.avatar.url), name = "Nullbot commands overview")

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
    global henry_time
    global drexel_messages_all
    global drexel_messages_owners
    global drexel_last_update
    global drexel_messages_channel

    henry_messages, henry_time  = load_henry_from_file(HENRY_PATH)
    drexel_messages_all         = readjsondict(DREXEL_ALL_PATH)
    drexel_messages_owners      = readjsondict(DREXEL_OWNERS_PATH)
    server_settings             = readjsondict(SERVER_SETTINGS_PATH)
    drexel_messages_channel     = readjsondict(DREXEL_CHANNEL_PATH)
    if readjsondict(DREXEL_TIME_PATH): drexel_last_update = float(readjsondict(DREXEL_TIME_PATH)['time updated'])

    with open(SERVER_SETTINGS_PATH, 'w', encoding='utf-8') as file:
        botguilds: list[discord.Guild] = bot.guilds

        for guild in botguilds:
            id = str(guild.id)

            if id not in server_settings.keys():
                server_settings[id] = {'Vote Requirements': 3}

        json.dump(server_settings, file, indent = 4)

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for _help"))
    await bot.get_guild(TEST_GUILD_ID).get_channel(TEST_CHANNEL_ID).send(embed = str_to_embed(f"Nullbot has initialized on <t:{int(time.time())}>"))


@bot.listen()
async def on_reaction_add(reaction: discord.Reaction, emoji: discord.Emoji):

    message: discord.Message = reaction.message

    # if we're waiting on the message for a vote then calculate
    if message.id in waiting_message_cache and reaction.count > 1:

        print("Reaction registered")

        reactions       = message.reactions
        reactionup      = None
        reactiondown    = None

        for reaction in reactions:
            if   str(reaction) == '👍': reactionup = reaction
            elif str(reaction) == '👎': reactiondown = reaction

        print(reactions)
        print(reactionup)
        print(reactiondown)

        sVoteReq: int               = server_settings[str(message.guild.id)]['Vote Requirements']
        vars                        = id_user_dict[message.id]
        member: discord.Member      = vars[0]
        newName                     = vars[1]
        requester: discord.Member   = vars[2]

        # if thumbs up greater than thumbs down by 3 members
        if reactionup.count - reactiondown.count == sVoteReq:

            users = [user async for user in reactionup.users()] if reactionup.count > reactiondown.count else [user async for user in reactiondown.users()]
            users = remove_nullbot(users)
            users = make_user_list(users)

            # delete the original bot's message
            channel: discord.TextChannel    = message.channel
            id                              = message.id

            await message.delete()

            async with channel.typing():
                try:
                    oldName = member.display_name
                    await member.edit(nick = newName)

                    newemb = discord.Embed(description = f"`{oldName}`'s name change to {member.mention} **APPROVED** by {users}.", color = DEF_COLOR)
                    newemb.set_author(icon_url = str(requester.avatar.url), name = f"Requested by {requester.display_name}")

                    await channel.send(embed = newemb)
                except discord.errors.Forbidden:
                    await channel.send(embed = str_to_embed(f"This bot doesn't have permissions to change {member.mention}'s name. This could be because that user is the server owner."))

            # remove unneeded entries from lists to conserve memory
            waiting_message_cache.remove(id)
            id_user_dict.pop(id)

        elif reactiondown.count - reactionup.count == sVoteReq:

            users = [user async for user in reactionup.users()] if reactionup.count > reactiondown.count else [user async for user in reactiondown.users()]
            users = remove_nullbot(users)
            users = make_user_list(users)
            
            # delete the original bot message
            channel = message.channel
            id      = message.id
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

    if ctx.command.name     == "rename":
        await ctx.send(embed = str_to_embed("Incorrect usage. Proper usage of the command is `{0}rename @[member] [new name]`".format(bot.command_prefix)))
    elif ctx.command.name   == "setvoterequirements":
        await ctx.send(embed = str_to_embed("Incorrect usage. Proper usage of the command is `{0}setvoterequirements [integer]`".format(bot.command_prefix)))


bot.run(TOKEN)