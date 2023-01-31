from discord.ext import commands
from discord import app_commands
from helper import *
from config import *
import time
import random
import time
import typing
import datetime
import json
import discord
import logging

logger = logging.getLogger('discord')

class Queries(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("bot initialized")
        # load and save json of guild preferences, including vote pass/fail requirements
        self.henry_messages, self.henry_time = load_henry_from_file(HENRY_PATH)

        guilds_path = os.path.join(DATA_DIR, 'guilds.json')
        
        print("Loaded guilds")
        
        try:
            with open(guilds_path, 'r') as file: self.guilds = json.load(file)
        except:
            self.guilds = {}

            for guild in self.bot.guilds:
                if str(guild.id) not in self.guilds.keys(): self.guilds[str(guild.id)] = []

        print("Loaded guilds")
        self.guild_ignored_channels = {"956714146223775817": DREXEL_IGNORED_CHANNELS, "355717114197180417": UW_IGNORED_CHANNELS}  
        self.guild_messages_all, self.guild_messages_owners, self.guild_messages_channel, self.guild_messages_pinned, self.guild_last_update = ({}, {}, {}, {}, {})

        for guild in self.bot.guilds:
            guild_data_path = os.path.join(DATA_DIR, f'{guild.id}')
            os.makedirs(guild_data_path, exist_ok=True)

        for guildid in self.guilds.keys():
            guild_data_path = os.path.join(DATA_DIR, f'{guildid}')
            os.makedirs(guild_data_path, exist_ok=True)

            self.guild_messages_all[guildid]        = readjsondict(os.path.join(guild_data_path, f'{guildid}_messages_all.json'))
            self.guild_messages_owners[guildid]     = readjsondict(os.path.join(guild_data_path, f'{guildid}_messages_owners.json'))
            self.guild_messages_channel[guildid]    = readjsondict(os.path.join(guild_data_path, f'{guildid}_messages_channel.json'))
            self.guild_messages_pinned[guildid]     = readjsondict(os.path.join(guild_data_path, f'{guildid}_messages_pinned.json'))
            self.guild_last_update[guildid]         = float(readjsondict(os.path.join(guild_data_path, f'{guildid}_last_update.json'))) if readjsondict(os.path.join(guild_data_path, f'{guildid}_last_update.json')) else 0.0


    def _add_message(self, message: discord.Message, guildid: str) -> None:
        member      = message.author
        memberid    = str(member.id)
        channelid   = str(message.channel.id)

        if memberid in self.guild_messages_owners[guildid].keys():
            self.guild_messages_owners[guildid][memberid].append(message.content)
        else:
            self.guild_messages_owners[guildid][memberid] = [message.content]

        if channelid in self.guild_messages_channel[guildid].keys():
            self.guild_messages_channel[guildid][channelid][message.content] = memberid
        else:
            self.guild_messages_channel[guildid][channelid] = {message.content: memberid}

        if message.pinned:
            if channelid in self.guild_messages_pinned[guildid].keys():
                self.guild_messages_pinned[guildid][channelid][message.content] = memberid
            else:
                self.guild_messages_pinned[guildid][channelid] = {message.content: memberid}
        
        self.guild_messages_all[guildid][message.content] = memberid


    @app_commands.command(description="Update a guild")
    @app_commands.guilds(int(TEST_GUILD_ID))
    async def updateguild(self, interaction: discord.Interaction, guildid: str, limit: typing.Optional[int] = 50000, fromts: typing.Optional[bool] = False):
        if not fromts: 
                self.guild_messages_all[guildid], self.guild_messages_owners[guildid], self.guild_messages_channel[guildid], self.guild_messages_pinned[guildid] = ({}, {}, {}, {})
        
        guild, loadingemoji = (self.bot.get_guild(int(guildid)), self.bot.get_emoji(1005354899351015464))
        await interaction.response.send_message(embed=str_to_embed(f"{loadingemoji} Started scraping messages from `{guild.name}` <t:{int(time.time())}:R>..."))

        timestart                   = time.time()
        ts                          = datetime.datetime.fromtimestamp(self.guild_last_update[guildid]) if fromts else None
        ignored_channels: list[str] = self.guild_ignored_channels[guildid] if guildid in self.guild_ignored_channels.keys() else []

        i = 0
        for channel in guild.channels:
            if channel.name not in ignored_channels and isinstance(channel, discord.TextChannel):
                if fromts:
                    async for message in channel.history(limit=limit, after=ts):
                        if len(message.content) > 0:
                            i += 1
                            self._add_message(message, guildid)
                            logger.info(f"message {i} added")
                else:
                    async for message in channel.history(limit=limit):
                        if len(message.content) > 0:
                            i += 1
                            self._add_message(message, guildid)
                            logger.info(f"message {i} added")

        logger.info("messages scraped")
        guild_data_path = os.path.join(DATA_DIR, f'{guildid}')
        os.makedirs(guild_data_path, exist_ok=True)
        with open(os.path.join(guild_data_path, f'{guildid}_messages_all.json'), 'w+') as file:      json.dump(self.guild_messages_all[guildid], file, indent=4)
        with open(os.path.join(guild_data_path, f'{guildid}_messages_owners.json'), 'w+') as file:   json.dump(self.guild_messages_owners[guildid], file, indent=4)
        with open(os.path.join(guild_data_path, f'{guildid}_messages_channel.json'), 'w+') as file:  json.dump(self.guild_messages_channel[guildid], file, indent=4)
        with open(os.path.join(guild_data_path, f'{guildid}_messages_pinned.json'), 'w+') as file:   json.dump(self.guild_messages_pinned[guildid], file, indent=4)
        logger.info("messages saved")

        self.guild_last_update[guildid] = time.time()
        with open(os.path.join(guild_data_path, f'{guildid}_last_update.json'), 'w+') as file:       json.dump(self.guild_last_update[guildid], file)
        logger.info("time saved")

        timeend    = time.time()
        timedeltas = timeend - timestart
        timedeltam = timedeltas // 60

        await interaction.edit_original_response(embed=discord.Embed(description=f"<:white_check_mark:1008679684642455582> `{guild.name}` has been updated, which took about {int(timedeltam)} minutes and {int(timedeltas - (timedeltam * 60))} seconds, and loaded {i} messages.", color=0x39ff14))


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
    async def updatehenry(self, ctx: commands.Context):

        guild: discord.Guild    = self.bot.get_guild(config.HENRY_GUILD_ID)
        henry: discord.Member   = guild.get_member(HENRY_ID)
        timestart               = time.time()

        async with ctx.typing():
            i = 0
            for channel in guild.text_channels:
                print(f"Channel is {channel.name}")
                if channel.permissions_for(henry).read_messages and channel.name != "bot-commands" and isinstance(channel, discord.TextChannel):
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


    @commands.hybrid_command(description="Ask henry a question")
    async def askhenry(self, ctx: commands.Context, question: typing.Optional[str]):

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


    @commands.hybrid_command(description="Ask drexel a question")
    async def askdrexel(self, 
                        ctx: commands.Context, 
                        user: typing.Optional[discord.User] = None, 
                        channel: typing.Optional[discord.TextChannel] = None, 
                        pinned: typing.Optional[bool] = False, 
                        *, question: typing.Optional[str] = None):
        logger.info("askdrexel called")
        
        print(f"user: {user}")
        guild: discord.Guild    = self.bot.get_guild(DREXEL_GUILD_ID)
        member                  = guild.get_member(user.id) if user else None
        guildid                 = str(guild.id)
        print(f"member: {member}")

        if question:
            if "pinned" == question.split()[0].lower():
                pinned = True
        
        message = self._fetch_message(member, channel, pinned, guild, guildid)

        await ctx.send(embed=message)


    @commands.hybrid_command(description="Ask UW a question")
    async def askuw(self, 
                    ctx: commands.Context, 
                    user: typing.Optional[discord.User] = None, 
                    channel: typing.Optional[discord.TextChannel] = None, 
                    pinned: typing.Optional[bool] = False, 
                    *, question: typing.Optional[str] = None):

        logger.info("askuw called")

        print(f"user: {user}")
        guild: discord.Guild    = self.bot.get_guild(UW_GUILD_ID)
        member                  = guild.get_member(user.id) if user else None
        guildid                 = str(guild.id)

        print(f"member: {member}")

        if question:
            if "pinned" == question.split()[0].lower():
                pinned = True
        
        message = self._fetch_message(member, channel, pinned, guild, guildid)

        await ctx.send(embed=message)


    def _fetch_message( self, 
                        member: discord.Member, 
                        channel: discord.TextChannel, 
                        pinned: bool, 
                        guild: discord.Guild, 
                        guildid: str) -> discord.Embed:
        name                    = ""
        message                 = ""

        if member:
            print("member found")

            id              = str(member.id)
            memberMessages  = self.guild_messages_owners[guildid][id]
            message         = random.choice(memberMessages)

            name = member.nick if member.nick != None else member.name
            name = f"{name} says:"
        elif channel:
            print("channel found")

            id = str(channel.id)
            if pinned:
                print("pinned")
                channelMessages: dict  = self.guild_messages_pinned[guildid][id]
                message                = random.choice(list(channelMessages.keys()))
                member: discord.Member = guild.get_member(int(self.guild_messages_pinned[guildid][id][message]))
            else:
                channelMessages: dict  = self.guild_messages_channel[guildid][id]
                message                = random.choice(list(channelMessages.keys()))
                member: discord.Member = guild.get_member(int(self.guild_messages_channel[guildid][id][message]))

            print(channel)
            print(message)

            name = member.nick if member.nick != None else member.name
            name = f"{name} in #{channel.name} says:"
        elif pinned:
            print("pinned")

            pinnedMessages: dict            = self.guild_messages_pinned[guildid]
            pinnedMessagesList: list[dict]  = list(pinnedMessages.values())
            pinnedMessages                  = {}
            for d in pinnedMessagesList:
                for k, v, in d.items():
                    pinnedMessages[k] = v
            message                         = random.choice(list(pinnedMessages.keys()))
            member: discord.Member          = guild.get_member(int(pinnedMessages[message]))

            print(member)
            print(message)

            name = member.nick if member.nick != None else member.name
            name = f"{name} says:"
        else:
            print("member or channel not found")

            message                 = random.choice(list(self.guild_messages_all[guildid].keys()))
            member: discord.Member  = guild.get_member(int(self.guild_messages_all[guildid][message]))
            
            print(message)
            print(member.nick)

            name = member.nick if member.nick != None else member.name
            name = f"{name} says:"

        message = discord.Embed(description=message)
        if member.display_avatar:
            message.set_author(name=name, icon_url=member.display_avatar.url)
        else:
            message.set_author(name=name, icon_url=member.default_avatar.url)

        return message
        

async def setup(bot: commands.Bot):
    print("query setup called")
    await bot.add_cog(Queries(bot))