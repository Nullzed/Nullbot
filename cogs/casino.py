from discord.ext import commands
from helper import *
import config
import discord
import random
import asyncio

# TODO: casino that allows you to gamble and spend money on cosmetics/your profile

class Casino(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot  = bot

        self.bank = readjsondict(config.BANK_PATH)
        for user in self.bank:
            self.bank[user] = int(self.bank[user])

    
    @commands.command()
    @commands.check(is_owner)
    async def setmoney(self, ctx: commands.Context, arg: int):
        self.bank[str(ctx.author.id)] = arg

        await ctx.send(embed=str_to_embed(f"Your current balance is now **${self.bank[str(ctx.author.id)]}**."))


    @commands.hybrid_command(description="Initialize casino on server")
    @commands.check(is_manager)
    async def initialize(self, ctx: commands.Context):
        members: list[discord.Member] = ctx.guild.members    

        for member in members:
            id = str(member.id)
            if id not in list(self.bank.keys()):
                self.bank[id] = config.STARTING_MONEY

        with open(config.BANK_PATH, 'w') as file:
            json.dump(self.bank, file)
            
        await ctx.send(embed=str_to_embed(f"Initialized bank accounts for **{len(list(self.bank.keys()))}** users."))


    @commands.hybrid_command(description="Check bank account balance")
    async def checkbalance(self, ctx: commands.Context):
        await ctx.send(embed=str_to_embed(f"Balance: **${self.bank[str(ctx.author.id)]}**"))


    @commands.hybrid_group()
    async def play(self, ctx: commands.Context):
        pass

    @play.command()
    async def doubleornothing(self, ctx: commands.Context, bet: int):

        print("Doubleornothing called")
        id = str(ctx.author.id)

        if bet <= self.bank[id]:
            self.bank[id] -= bet

            if ctx.interaction:
                print("interaction")
                embed = discord.Embed(title="Rolling...")
                embed.set_image(url="https://www.drafttournament.com/wp-content/uploads/2016/12/Roulette-Turning-89319.gif")
                await ctx.interaction.response.send_message(embed=embed)
                message = await ctx.interaction.original_message()
            else:
                print("message")
                embed = discord.Embed(title="Rolling...")
                embed.set_image(url="https://www.drafttournament.com/wp-content/uploads/2016/12/Roulette-Turning-89319.gif")
                message: discord.Message = await ctx.send(embed=embed)

            await asyncio.sleep(4)

            print("waited")
            if random.randint(1, 2) == 1:
                self.bank[id] += (bet * 2)
                await message.edit(embed=str_to_embed(f"You've won! Your bank balance is now **${self.bank[id]}**."))
            else: 
                await message.edit(embed=str_to_embed(f"You've lost! Your bank balance is now **${self.bank[id]}**."))
        else:
            await ctx.send(embed=str_to_embed("You don't have enough money!"))


async def setup(bot: commands.Bot):
    await bot.add_cog(Casino(bot))