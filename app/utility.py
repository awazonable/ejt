import asyncio
import re

import discord
from discord.ext import commands

import deepl
import guild
import weblio

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='del')
    async def delete_by_botbot(self, ctx, num):
        '''Say ,del [num]'''
        await ctx.send(f",del {num}")
    
    @commands.command()
    async def echo(self, ctx, *, text):
        '''Repeat after you'''
        await ctx.send(text)
    
    @commands.command()
    async def delete(self, ctx, *, num):
        await ctx.channel.send(ctx.author)
        

async def setup(bot):
    await bot.add_cog(Utility(bot))