from discord.ext import commands
from discord import app_commands
from config import *
from helper import *
import json

class Interactions(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot                    = bot
        self.waiting_message_cache  = [] # voting messages being waited on
        self.id_user_dict           = {} # rename voting messages
        self.defaultVR              = 3

        self.server_settings        = readjsondict(SERVER_SETTINGS_PATH)
        with open(SERVER_SETTINGS_PATH, 'w', encoding='utf-8') as file:
            botguilds: list[discord.Guild] = bot.guilds

            for guild in botguilds:
                id = str(guild.id)

                if id not in list(self.server_settings.keys()):
                    self.server_settings[id] = {'Vote Requirements': self.defaultVR}

            json.dump(self.server_settings, file, indent = 4)


    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        with open(SERVER_SETTINGS_PATH, 'w', encoding='utf-8') as file:
            id = str(guild.id)

            if id not in self.server_settings.keys():
                self.server_settings[id] = {'Vote Requirements': self.defaultVR}

            json.dump(self.server_settings, file, indent=4)

    
    # Sets how many votes the bot should look for before closing a vote.
    @commands.hybrid_command(description="Change vote requirements")
    async def setvoterequirements(self, ctx: commands.Context, votes: int):

        if ctx.author.guild_permissions.manage_guild:
            # set server vote pass/fail requirement numbers.
            with open(SERVER_SETTINGS_PATH, 'w') as file:
                self.server_settings[str(ctx.guild.id)]['Vote Requirements'] = votes

                json.dump(self.server_settings, file, indent = 4)

            await ctx.send(embed = str_to_embed(f"Server vote requirements updated to a majority by **{votes}** votes."))
        else:
            await ctx.send(embed = str_to_embed("Invalid permissions. You must have manage server permissions to use this command."))


    # renames a user using the power of a voting majority
    @commands.command()
    async def rename(self, ctx: commands.Context, member: discord.Member, *args):

        name                            = ' '.join(args)
        message: discord.Message        = await ctx.send(embed = str_to_embed(f"Rename {member.mention} to `{name}`?"))
        self.id_user_dict[message.id]   = [member, name, ctx.author]
        self.waiting_message_cache.append(message.id)    

        await message.add_reaction('👍')
        await message.add_reaction('👎')


    @app_commands.command(description="Rename another user")
    async def rename(self, interaction: discord.Interaction, member: discord.Member, name: str):

        await interaction.response.send_message(embed = str_to_embed(f"Rename {member.mention} to `{name}`?"))
        message: discord.Message        = await interaction.original_message()
        self.id_user_dict[message.id]   = [member, name, interaction.user]
        self.waiting_message_cache.append(message.id)    

        await message.add_reaction('👍')
        await message.add_reaction('👎')

    
    @commands.hybrid_command(description="Show vote requirements")
    async def showvoterequirements(self, ctx: commands.Context):

        votereqs = self.server_settings[str(ctx.guild.id)]['Vote Requirements']

        await ctx.send(embed = str_to_embed(f"Server requires a majority by {votereqs} votes."))


    @commands.command()
    @commands.check(is_owner)
    async def showsettings(self, ctx: commands.Context):
        await ctx.send(embed = str_to_embed(str(self.server_settings)))

    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, emoji: discord.Emoji):

        message: discord.Message = reaction.message

        # if we're waiting on the message for a vote then calculate
        if message.id in self.waiting_message_cache and reaction.count > 1:

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

            sVoteReq: int               = self.server_settings[str(message.guild.id)]['Vote Requirements']
            vars                        = self.id_user_dict[message.id]
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

                        newemb = discord.Embed(description = f"`{oldName}`'s name change to {member.mention} **APPROVED** by {users}.")
                        newemb.set_author(icon_url = str(requester.avatar.url), name = f"Requested by {requester.display_name}")

                        await channel.send(embed = newemb)
                    except discord.errors.Forbidden:
                        await channel.send(embed = str_to_embed(f"This bot doesn't have permissions to change {member.mention}'s name. This could be because that user is the server owner."))

                # remove unneeded entries from lists to conserve memory
                self.waiting_message_cache.remove(id)
                self.id_user_dict.pop(id)

            elif reactiondown.count - reactionup.count == sVoteReq:

                users = [user async for user in reactionup.users()] if reactionup.count > reactiondown.count else [user async for user in reactiondown.users()]
                users = remove_nullbot(users)
                users = make_user_list(users)
                
                # delete the original bot's message
                channel: discord.TextChannel    = message.channel
                id                              = message.id

                await message.delete()

                async with channel.typing():
                    newemb = discord.Embed(description = f"{member.mention}'s name change to `{newName}` **REJECTED** by {users}.")
                    newemb.set_author(icon_url = str(requester.avatar.url), name = f"Requested by {requester.display_name}")

                    await channel.send(embed = newemb)
                
                # remove unneeded entries from lists to conserve memory
                self.waiting_message_cache.remove(id)
                self.id_user_dict.pop(id)


async def setup(bot: commands.Bot):
    await bot.add_cog(Interactions(bot))