import asyncio
import re

import discord
from discord.ext import commands

import deepl
import guild
import weblio

class Translate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def usage(self, ctx):
        '''Display remaining translation letters'''
        usage = deepl.Deepl.usage()
        await ctx.send(f"I can translate {usage['character_limit'] - usage['character_count']} letters this month!")

    @commands.command(name='english-us', aliases=['us', 'american'])
    async def translate_us(self, ctx, *, sentence):
        '''Translate to American (English)'''
        await ctx.send(deepl.Deepl(sentence, target_lang="EN-US").get())

    @commands.command(name='english-gb', aliases=['gb', 'uk', 'british'])
    async def translate_gb(self, ctx, *, sentence):
        '''Translate to British (English)'''
        await ctx.send(deepl.Deepl(sentence, target_lang="EN-GB").get())

    @commands.command(name='german', aliases=['de', 'ge'])
    async def translate_de(self, ctx, *, sentence):
        '''Translate to German (Deutsch)'''
        await ctx.send(deepl.Deepl(sentence, target_lang="DE").get())

    @commands.command(name='greek', aliases=['el', 'gr'])
    async def translate_el(self, ctx, *, sentence):
        '''Translate to Greek'''
        await ctx.send(deepl.Deepl(sentence, target_lang="EL").get())

    @commands.command(name='french', aliases=['fr'])
    async def translate_fr(self, ctx, *, sentence):
        '''Translate to French'''
        await ctx.send(deepl.Deepl(sentence, target_lang="FR").get())

    @commands.command(name='russian', aliases=['ru'])
    async def translate_ru(self, ctx, *, sentence):
        '''Translate to Russian'''
        await ctx.send(deepl.Deepl(sentence, target_lang="RU").get())

    @commands.command(name='russianmore', aliases=['rum'])
    async def translate_rum(self, ctx, *, sentence):
        '''Translate to Russian more formality'''
        await ctx.send(deepl.Deepl(sentence, target_lang="RU", formality="more").get())

    @commands.command(name='russianless', aliases=['rul'])
    async def translate_rul(self, ctx, *, sentence):
        '''Translate to Russian less formality'''
        await ctx.send(deepl.Deepl(sentence, target_lang="RU", formality="less").get())

    @commands.command(name='spanish', aliases=['es', 'sp'])
    async def translate_es(self, ctx, *, sentence):
        '''Translate to Spanish'''
        await ctx.send(deepl.Deepl(sentence, target_lang="ES").get())

    @commands.command(name='italian', aliases=['it'])
    async def translate_it(self, ctx, *, sentence):
        '''Translate to Italian'''
        await ctx.send(deepl.Deepl(sentence, target_lang="IT").get())

    @commands.command(name='chinese', aliases=['zh', 'ch'])
    async def translate_zh(self, ctx, *, sentence):
        '''Translate to Chinese'''
        await ctx.send(deepl.Deepl(sentence, target_lang="ZH").get())

    @commands.command(name='japanese', aliases=['ja'])
    async def translate_ja(self, ctx, *, sentence):
        '''Translate to Japanese (日本語)'''
        await ctx.send(deepl.Deepl(sentence, target_lang="JA").get())

async def setup(bot):
    await bot.add_cog(Translate(bot))