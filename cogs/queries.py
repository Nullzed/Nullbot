from discord.ext import commands
from helper import *
from config import *
import time
import random
import time
import typing
import datetime
import json
import discord


class Queries(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot                        = bot
        self.henry_messages             = [] # messages henry has sent
        self.henry_time                 = 0.0 # last time since henry was updated
        self.drexel_messages_all        = {} # all the drexel messages
        self.drexel_messages_owners     = {} # all the drexel messages sorted by owner
        self.drexel_messages_channel    = {} # all the drexel messages sorted by channel
        self.drexel_last_update         = 0.0 #last time since drexel was updated

        # load and save json of guild preferences, including vote pass/fail requirements
        self.henry_messages, self.henry_time    = load_henry_from_file(HENRY_PATH)
        self.drexel_messages_all                = readjsondict(DREXEL_ALL_PATH)
        self.drexel_messages_owners             = readjsondict(DREXEL_OWNERS_PATH)
        self.drexel_messages_channel            = readjsondict(DREXEL_CHANNEL_PATH)
        if readjsondict(DREXEL_TIME_PATH): self.drexel_last_update = float(readjsondict(DREXEL_TIME_PATH)['time updated'])


    @commands.command()
    @commands.check(is_owner)
    async def fullupdatehenry(self, ctx: commands.Context, arg: int):

        guild: discord.Guild    = self.bot.get_guild(HENRY_GUILD_ID)
        henry: discord.Member   = guild.get_member(HENRY_ID)
        self.henry_messages     = []
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

                            self.henry_messages.append(message.content)
            
            with open(HENRY_PATH, 'w') as file:
                json.dump(self.henry_messages, file, indent=4)

            curtime     = time.time()
            self.henry_time  = curtime
            with open(HENRY_TIME_PATH, 'w') as file:
                datetimedict = {'time updated': curtime}
                json.dump(datetimedict, file, indent=4)

            timeend    = time.time()
            timedeltas = timeend - timestart
            timedeltam = timedeltas / 60
            
            await ctx.send(embed=str_to_embed(f"Henry has been updated, which took about {int(timedeltas)} seconds or about {int(timedeltam)}:{int(timedeltas - (timedeltam * 60))} minutes, and loaded {len(self.henry_messages)} messages."))


    @commands.command()
    @commands.check(is_owner)
    async def fullupdatedrexel(self, ctx: commands.Context, arg: int):

        print("fullupdatedrexel called")

        self.drexel_messages_owners = {}
        self.drexel_messages_all    = {}
        guild: discord.Guild        = self.bot.get_guild(DREXEL_GUILD_ID)
        timestart                   = time.time()

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
                            
                            if memberid in self.drexel_messages_owners.keys():
                                self.drexel_messages_owners[memberid].append(message.content)
                            else:
                                self.drexel_messages_owners[memberid] = [message.content]

                            if channelid in self.drexel_messages_channel.keys():
                                self.drexel_messages_channel[channelid][message.content] = memberid
                            else:
                                self.drexel_messages_channel[channelid] = {message.content: memberid}
                            
                            self.drexel_messages_all[message.content] = memberid
                            
                            print(f"message {i} added")

            print("messages scraped")
            with open(DREXEL_OWNERS_PATH, 'w') as file:
                json.dump(self.drexel_messages_owners, file, indent=4)
            with open(DREXEL_ALL_PATH, 'w') as file:
                json.dump(self.drexel_messages_all, file, indent=4)
            with open(DREXEL_CHANNEL_PATH, 'w') as file:
                json.dump(self.drexel_messages_channel, file, indent=4)
            print("messages saved")

            curtime = time.time()
            with open(DREXEL_TIME_PATH, 'w') as file:
                json.dump({'time updated': curtime}, file)
            print("time saved")

            timeend    = time.time()
            timedeltas = timeend - timestart
            timedeltam = timedeltas // 60
            
            await ctx.send(embed=str_to_embed(f"Drexel has been updated, which took about {int(timedeltas)} seconds or {int(timedeltam)}:{int(timedeltas - (timedeltam * 60))} minutes, and loaded {i} messages."))


    @commands.command()
    @commands.check(is_owner)
    async def updatehenry(self, ctx: commands.Context):

        guild: discord.Guild    = self.bot.get_guild(config.HENRY_GUILD_ID)
        henry: discord.Member   = guild.get_member(HENRY_ID)
        timestart               = time.time()

        async with ctx.typing():
            i = 0
            for channel in guild.text_channels:
                print(f"Channel is {channel.name}")
                if channel.permissions_for(henry).read_messages and channel.name != "bot-commands":
                    print(f"henry is allowed")
                    async for message in channel.history(after=datetime.datetime.fromtimestamp(self.henry_time)):
                        if message.author == henry and len(message.content) > 0:
                            i += 1
                            print(f"message {i} added")
                            self.henry_messages.append(message.content)
            
        curtime     = time.time()
        self.henry_time  = curtime
        with open(HENRY_TIME_PATH, 'w') as file:
            datetimedict = {'time updated': curtime}
            json.dump(datetimedict, file)

        timeend    = time.time()
        timedeltas = timeend - timestart
        timedeltam = timedeltas / 60

        await ctx.send(embed=str_to_embed(f"Henry has been updated, which took about {int(timedeltas)} seconds or {int(timedeltam)}:{int(timedeltas - (timedeltam * 60))} minutes, and loaded {i} new messages."))
        

    @commands.command()
    @commands.check(is_owner)
    async def updatedrexel(self, ctx: commands.Context):
        
        guild: discord.Guild            = self.bot.get_guild(DREXEL_GUILD_ID)
        timestart                       = time.time()
        drexelLastDT: datetime.datetime = datetime.datetime.fromtimestamp(self.drexel_last_update)

        async with ctx.typing():
            i = 0
            for channel in guild.channels:
                if channel.name not in DREXEL_IGNORED_CHANNELS and channel.name in DREXEL_APPROVED_CHANNELS:
                    async for message in channel.history(after=drexelLastDT):
                        i += 1

                        member      = message.author
                        memberid    = str(member.id)
                        channelid   = str(message.channel.id)
                        
                        if memberid in self.drexel_messages_owners.keys():
                            self.drexel_messages_owners[memberid].append(message.content)
                        else:
                            self.drexel_messages_owners[memberid] = [message.content]

                        if channelid in self.drexel_messages_channel.keys():
                            self.drexel_messages_channel[channelid][message.content] = memberid
                        else:
                            self.drexel_messages_channel[channelid] = {message.content: memberid}                
                        
                        self.drexel_messages_all[message.content] = memberid
                        
                        print(f"message {i} added")

            print("messages scraped")
            with open(DREXEL_OWNERS_PATH, 'w') as file:
                json.dump(self.drexel_messages_owners, file, indent=4)
            with open(DREXEL_ALL_PATH, 'w') as file:
                json.dump(self.drexel_messages_all, file, indent=4)
            with open(DREXEL_CHANNEL_PATH, 'w') as file:
                json.dump(self.drexel_messages_channel, file, indent=4)
            print("messages saved")

            curtime = time.time()
            with open(DREXEL_TIME_PATH, 'w') as file:
                json.dump({'time updated': curtime}, file)
            print("time saved")

            timeend    = time.time()
            timedeltas = timeend - timestart
            timedeltam = timedeltas / 60
            
            await ctx.send(embed=str_to_embed(f"Drexel has been updated since the last timestamp, which took about {int(timedeltas)} seconds or {int(timedeltam)}:{int(timedeltas - (timedeltam * 60))} minutes, and loaded {i} new messages."))


    @commands.command()
    async def askhenry(self, ctx: commands.Context, *args):

        print("askhenry called")

        async with ctx.typing():
            henry = self.bot.get_user(HENRY_ID)
            if len(self.henry_messages) > 0:
                print("Henry has messages")

                message = discord.Embed(description=random.choice(self.henry_messages))
                message.set_author(name="Henry says:", icon_url=henry.avatar.url)

                print("random message selected")

                await ctx.send(embed=message)
            else:
                await ctx.send(embed=str_to_embed("There are no saved messages from henry."))


    @commands.command()
    async def askdrexel(self, ctx: commands.Context, member: typing.Optional[discord.Member] = None, channel: typing.Optional[discord.TextChannel] = None):

        print("askdrexel called")
        name    = ""
        message = ""
        if member:
            print("member found")

            id              = str(member.id)
            memberMessages  = self.drexel_messages_owners[id]
            message         = random.choice(memberMessages)

            name = f"{member.nick} says:"
        elif channel:
            print("channel found")

            id                      = str(channel.id)
            channelMessages: dict   = self.drexel_messages_channel[id]
            message                 = random.choice(list(channelMessages.keys()))
            member: discord.Member  = ctx.guild.get_member(int(self.drexel_messages_channel[id][message]))

            print(channel)
            print(message)

            name = f"{member.nick} in #{channel.name} says:"
        else:
            print("member or channel not found")

            message                 = random.choice(list(self.drexel_messages_all.keys()))
            member: discord.Member  = self.bot.get_guild(DREXEL_GUILD_ID).get_member(int(self.drexel_messages_all[message]))
            
            print(message)
            print(member.nick)

            name = f"{member.nick} says:"

        message = discord.Embed(description=message)
        message.set_author(name=name, icon_url=member.avatar.url)

        await ctx.send(embed=message)


async def setup(bot: commands.Bot):
    await bot.add_cog(Queries(bot))