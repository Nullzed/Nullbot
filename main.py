import discord
from discord.ext import commands
from helper import *
from config import *
import time
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = commands.Bot(command_prefix='_', help_command=None, intents=discord.Intents.all())

discord.Intents.reactions   = True
discord.Intents.guilds      = True


# turns off the bot
@bot.command()
@commands.check(is_owner)
async def close(ctx: commands.Context):
    if ctx.author.id == NEIL_ID:
        await ctx.send(embed = str_to_embed("Bot will now stop!"))
        await bot.close()


@bot.command()
@commands.check(is_owner)
async def sync(ctx: commands.Context):
    await bot.tree.sync()
    await bot.tree.sync(guild=bot.get_guild(TEST_GUILD_ID))
    await ctx.send(embed=str_to_embed(f"Synced slash commands on <t:{int(time.time())}>"))


# help command
@bot.hybrid_command(description="List all commands")
async def help(ctx: commands.Context):
    print("help called")

    mesEmb = discord.Embed(description=HELP)
    mesEmb.set_author(icon_url = str(bot.user.avatar.url), name = "Nullbot commands overview")

    await ctx.send(embed = mesEmb)


@bot.command()
async def adminhelp(ctx: commands.Context):
    print("adminhelp called")

    mesEmb = discord.Embed(description=ADMINHELP, color = DEF_COLOR)
    mesEmb.set_author(icon_url = str(bot.user.avatar.url), name = "Nullbot commands overview")

    await ctx.send(embed = mesEmb)


@bot.listen()
async def on_ready():
    testchannel = bot.get_guild(TEST_GUILD_ID).get_channel(TEST_CHANNEL_ID)

    # load queries cog
    try: 
        await bot.load_extension('cogs.queries')
        await testchannel.send(embed = str_to_embed(f"Nullbot has initialized queries cog on <t:{int(time.time())}>"))
    except Exception as e: 
        logger.error(e, exc_info=True)
        await testchannel.send(embed=str_to_embed(f"{e} error has occured."))

    # load interactions cog
    try:
        await bot.load_extension('cogs.interactions')
        await testchannel.send(embed = str_to_embed(f"Nullbot has initialized interactions cog on <t:{int(time.time())}>"))
    except Exception as e: 
        logger.error(e, exc_info=True)
        await testchannel.send(embed=str_to_embed(f"{e} error has occured."))

    """ # load casino cog
    try:
        await bot.load_extension('cogs.casino')
        await testchannel.send(embed = str_to_embed(f"Nullbot has initialized casino cog on <t:{int(time.time())}>"))
    except Exception as e: await testchannel.send(embed=str_to_embed(f"{e} error has occured."))
    """

    # load and save json of guild preferences, including vote pass/fail requirements

    await bot.tree.sync()
    await bot.tree.sync(guild=bot.get_guild(TEST_GUILD_ID))

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for _help"))
    await testchannel.send(embed = str_to_embed(f"Nullbot has fully initialized on <t:{int(time.time())}>"))


@bot.command()
@commands.check(is_owner)
async def reload(ctx: commands.Context, arg: str):
    try: 
        await bot.reload_extension(f"cogs.{arg}")
        await ctx.send(embed=str_to_embed(f"Successfully reloaded extension `{arg}` on <t:{int(time.time())}>"))
    except Exception as e: 
        logger.error(e, exc_info=True)
        await ctx.send(embed=str_to_embed(f"{e}"))


@bot.command()
@commands.check(is_owner)
async def load(ctx: commands.Context, arg: str):
    try: 
        await bot.load_extension(f"cogs.{arg}")
        await ctx.send(embed=str_to_embed(f"Successfully loaded extension `{arg}` on <t:{int(time.time())}>"))
    except Exception as e: 
        logger.error(e, exc_info=True)
        await ctx.send(embed=str_to_embed(f"{e}"))


@bot.command()
@commands.check(is_owner)
async def unload(ctx: commands.Context, arg: str):
    try: 
        await bot.unload_extension(f"cogs.{arg}")
        await ctx.send(embed=str_to_embed(f"Successfully unloaded extension `{arg}` on <t:{int(time.time())}>"))
    except Exception as e: await ctx.send(embed=str_to_embed(f"{e}"))


@bot.listen()
async def on_command_error(ctx: commands.Context, error):
    if ctx.invoked_with     == "rename":
        await ctx.send(embed = str_to_embed("Incorrect usage. Proper usage of the command is `{0}rename @[member] [new name]`".format(bot.command_prefix)))
    elif ctx.invoked_with   == "setvoterequirements":
        await ctx.send(embed = str_to_embed("Incorrect usage. Proper usage of the command is `{0}setvoterequirements [integer]`".format(bot.command_prefix)))


bot.run(TOKEN)