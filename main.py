#!/usr/bin/env python3
from discord.ext import commands
from discord import Intents
import os

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
COMMAND_PREFIX = '~'

class Bot(commands.Bot):
    def __init__(self):
        intents = Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=COMMAND_PREFIX, intents=intents)
    
    async def setup_hook(self):
        # for filename in os.listdir("./cogs"):
        #     if filename.endswith(".py"):
        #         try:
        #             await bot.load_extension(f"cogs.{filename[:-3]}")
        #             print(f"Loaded {filename}")
        #         except Exception as e:
        #             print(f"Failed to load {filename}")
        #             print(f"[ERROR] {e}")
            
        await bot.load_extension('__cogs__')

        await self.tree.sync()
        print("Successfully synced commands")
        print(f"Logged onto {self.user}")

if __name__ == '__main__':
    
    bot=Bot()
        
    @bot.command(hidden=True, aliases=["reload", "r"])
    @commands.is_owner()
    async def fullreload(ctx):
        '''[OWNER]Reload extensions'''
        exts = bot.extensions.copy()
        for ext in exts:
            print(f'trying to unload {ext}')
            try:
                bot.unload_extension(ext)
            except Exception as e:
                print('{}: {}'.format(type(e).__name__, e))
                await ctx.message.add_reaction('🥺')
                return
        
        print(bot.extensions)
        bot.load_extension('__cogs__')
        await ctx.message.add_reaction('👍')
    
    @bot.command()
    async def say(ctx, msg):
        '''オウム返しをします'''
        await ctx.send(msg)
    
    print("Start Discord bot...")
    bot.run(DISCORD_TOKEN)
    