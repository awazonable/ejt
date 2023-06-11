# coding: utf-8

import asyncio
import os
from pathlib import Path
import re
import urllib
import json
import random
import queue
import math

from bs4 import BeautifulSoup
import requests
import discord
from discord.ext import commands
import langdetect
import flag as flagcode
# from emoji import emojize

import weblio
import guild
import deepl
from openjtalk import openjtalk

CONNECTIN_TIME_OUT = 30
DOWNLOAD_SAVE_DIR='app/src'
SETTING_FILE='/app/setting.json'

class Voice(commands.Cog):
    VOICE_SETTINGS = {
        'pass':{'scale': (0.0, 1.0), 'is_exp':False},
        'speed':{'scale': (0.5, 2.0), 'is_exp':True},
        'volume':{'scale': (-10.0, 10.0), 'is_exp':False},
        'pitch':{'scale': (-0.15, 0.15), 'is_exp':False},
        'intonation_scale':{'scale': (0.0, 2.0), 'is_exp':False},
    }    
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.queue = {}
        self.user_voices = self._getvoicesettings()
    
    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel = None):
        '''Join a voice channel'''
        if channel is None:
            if not ctx.author.voice.channel: # not ctx.author.voice or 
                return await ctx.send('You should join a voice channel before (or send a channel).')
            await ctx.author.voice.channel.connect(reconnect=False)
            guild.Guild(ctx.guild.id).set_voice_channel(ctx.author.voice.channel.id)
        else:
            if ctx.voice_client is not None:
                await ctx.voice_client.move_to(channel)
                guild.Guild(ctx.guild.id).set_voice_channel(channel.id)
                return
            await channel.connect(reconnect=False)
            guild.Guild(ctx.guild.id).set_voice_channel(channel.id)
    
    @commands.command()
    async def leave(self, ctx):
        '''Leave a voice channel'''
        for vc in self.bot.voice_clients:
            if vc.guild.id == ctx.guild.id:
                await vc.disconnect()

    async def play(self, url, guild_id):
        data = guild.Guild(guild_id).get()
        print('try to play music')
        if data.voice_channel:
            channel = self.bot.get_channel(data.voice_channel)
            if channel:
                try:
                    await channel.connect(reconnect=False)
                    if not guild_id in self.queue:
                        self.queue
                except discord.ClientException:
                    pass
                except Exception as e:
                    return print(e)
                finally:
                    for vc in self.bot.voice_clients:
                        if vc.guild.id == guild_id:
                            vc.play(discord.FFmpegPCMAudio(url))
            else:
                print(data.voice_channel)
                print('channel is none')
        else:
            print(f'cannot find a voice channel at {guild_id}')
    
    @commands.command(aliases=['mo'])
    async def monitoring(self, ctx):
        '''Start monitoring on this channel'''
        gld = guild.Guild(ctx.guild.id)
        data = gld.get()
        if data.monitoring_channels and ctx.channel.id in data.monitoring_channels:
            gld.delete_monitoring_channel(ctx.channel.id)
            await ctx.send('``Weblio monitoring end``')
        else:
            gld.set_monitoring_channel(ctx.channel.id)
            await ctx.send('``Weblio monitoring start on this channel``')

    @commands.Cog.listener(name='on_message')
    async def on_message_weblio(self, message):
        if not message.author.bot\
        and not message.content.startswith(self.bot.command_prefix):
            data = guild.Guild(message.guild.id).get()
            if message.channel.id in data.monitoring_channels:
                msg = message.content
                if len(msg) != 0\
                and not msg.startswith('http://')\
                and not msg.startswith('https://'):
                    await message.add_reaction('▶️')
                    await message.add_reaction('🤷')
                    
    @commands.command(aliases=['ld', 'lang'])
    async def langdetect(self, ctx, *, msg):
        text = msg
        res = langdetect.detect(text)
        # await ctx.message.add_reaction('<:flag_'+res.lower()[-2:]+':>')
        await ctx.channel.send(res, delete_after=30)
    
    async def reaction_method(self, message, user, emoji):
        print("reaction_method has called.")
        if emoji.name == '▶️':
            text = message.content
            if embeds := message.embeds:
                text = embeds[0].title
            text = re.sub(r'<.*?>', '', text)
            if text:
                # if re.search(r"[a-zA-Z]", text[0]):
                ld = langdetect.detect(text).upper()[-2:]
                print(ld)
                if ld != "JA" and ld != "CH" and ld != "KO" and ld != "ZW":
                    wbl = weblio.Weblio(text, message.id)
                    print(wbl.get_audio())
                    await self.play(wbl.get_audio(), message.guild.id)
                else:
                    text = re.sub(r'<.*?>', '', text)
                    print(text)
                    if len(text) > 256:
                        text = text[:255]
                    try:
                        msg_id = str(message.id)
                        msg_aid = str(message.author.id)
                        if self.user_voices[msg_aid]['voice'] in [x.name for x in openjtalk.Openjtalk.VOICE]:
                            voice = openjtalk.Openjtalk.VOICE[self.user_voices[msg_aid]['voice']]
                        else:
                            voice = openjtalk.Openjtalk.VOICEVOX[self.user_voices[msg_aid]['voice']]
                        oj = openjtalk.Openjtalk(text=text.replace('\n', ';'), name=msg_id)
                        if msg_aid in self.user_voices.keys():
                            oj.set_voice(
                                voice=voice,\
                                all_pass=self.user_voices[msg_aid]['pass'],\
                                speed=self.user_voices[msg_aid]['speed'],\
                                volume=self.user_voices[msg_aid]['volume'],\
                                pitch=self.user_voices[msg_aid]['pitch'],\
                                intonation_scale=self.user_voices[msg_aid]['intonation_scale']
                                )
                        await self.play(oj.get_mp3(), message.guild.id)
                    except Exception as e:
                        print(e)
        elif emoji.name == '🤷':
            text = message.content
            if embeds := message.embeds:
                text = embeds[0].title
            text = re.sub(r'<.*?>', '', text)
            if text:
                # if re.search(r"[a-zA-Z]", text[0]):
                ld = langdetect.detect(text).upper()[-2:]
                if ld != "JA" and ld != "CH":
                    data = weblio.Weblio(text, message.id).get_data()
                    ddesc = deepl.Deepl(text).get_list()
                    desc = '\n'.join(data.text+ddesc)
                    words = data.more
                    if words:
                        for w in words:
                            desc += f'\n[{w["word"]}]({w["href"]}) : '+w['caption']
                    if len(text) >= 256:
                        shortmsg = text[:253]
                        target = shortmsg.rfind(' ')
                        shortmsg = text[:target]+'...'
                        desc = text[target+1:]+'\n'+desc
                        text = shortmsg
                    embed = discord.Embed(title=text, description=desc)
                    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar)
                    embed.set_thumbnail(url=message.author.avatar)
                    new_msg = await message.channel.send(embed=embed, delete_after=30)
                else:
                    # 上戸ほぼおなじ
                    data = weblio.Weblio(text, message.id).get_data()
                    ddesc = deepl.Deepl(text, target_lang="EN").get_list()
                    desc = '\n'.join(data.text+ddesc)
                    words = data.more
                    if words:
                        for w in words:
                            desc += f'\n[{w["word"]}]({w["href"]}) : '+w['caption']
                    if len(text) >= 256:
                        shortmsg = text[:253]
                        target = shortmsg.rfind(' ')
                        shortmsg = text[:target]+'...'
                        desc = text[target+1:]+'\n'+desc
                        text = shortmsg
                    embed = discord.Embed(title=text, description=desc)
                    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar)
                    embed.set_thumbnail(url=message.author.avatar)
                    new_msg = await message.channel.send(embed=embed, delete_after=30)
                    

    @commands.Cog.listener(name='on_raw_reaction_add')
    async def on_reaction_add_weblio(self, payload:discord.RawReactionActionEvent):
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = self.bot.get_user(payload.user_id)
        await self.reaction_method(message, user, payload.emoji)
    
    @commands.Cog.listener(name='on_raw_reaction_remove')
    async def on_reaction_remove_weblio(self, payload:discord.RawReactionActionEvent):
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = self.bot.get_user(payload.user_id)
        await self.reaction_method(message, user, payload.emoji)
    
    @commands.command(name='dictionary',aliases=['dict'])
    async def add_dictionary(self, ctx, surface, pronounce, accent_type = None):
        if openjtalk.Openjtalk.add_dictionary(surface, pronounce, accent_type):
            await ctx.send(f'辞書に{surface}（{pronounce}）を追加しました')
        else:
            await ctx.send('辞書に追加できませんでした')
        
    #### 移植した部分 ####
    def _selfvoicedefault(self, aid):
        self.user_voices[aid] = {'voice': openjtalk.Openjtalk.VOICE.NITECH.name, 'pass': '0.55', 'speed': '1.0', 'volume': '0.0', 'pitch': '0.0', 'intonation_scale': '1.0'}
        self._setvoicesettings()

    def _getvoicesettings(self):
        with open(SETTING_FILE, mode='r') as f:
            data=json.load(f)
        return data
    
    def _setvoicesettings(self):
        data = self.user_voices
        with open(SETTING_FILE, mode='w') as f:
            f.write(json.dumps(data))
    
    @classmethod
    def param_normalize(cls, param, min_, max_, lower_=-1.0, upper_=1.0):
        if not (min_ <= float(param) <= max_):
            raise ValueError
        return lower_+(float(param)-min_)*(upper_-lower_)/(max_-min_)

    @classmethod
    def param_denormalize(cls, param, min_, max_, lower_=-1.0, upper_=1.0):
        if not (lower_ <= float(param) <= upper_):
            raise ValueError
        return min_+(float(param)-lower_)*(max_-min_)/(upper_-lower_)

    @classmethod
    def param_normalize_exp(cls, param, min_, max_, lower_=-1.0, upper_=1.0):
        if not (min_ <= float(param) <= max_):
            raise ValueError
        params = math.log2(float(param)), math.log2(min_), math.log2(max_)
        return cls.param_normalize(*params, lower_, upper_)

    @classmethod
    def param_denormalize_exp(cls, param, min_, max_, lower_=-1.0, upper_=1.0):
        if not (lower_ <= float(param) <= upper_):
            raise ValueError
        params = float(param), math.log2(min_), math.log2(max_)
        return 2 ** cls.param_denormalize(*params, lower_, upper_)

    @commands.command(aliases=['sv'], brief=f"Set your voice", help=f"Set your voice from {','.join([x.name for x in openjtalk.Openjtalk.VOICE])} or {','.join([x.name for x in openjtalk.Openjtalk.VOICEVOX])}")
    async def setvoice(self, ctx, msg):
        aid = str(ctx.author.id)
        print(msg)
        if not aid in self.user_voices.keys():
            self._selfvoicedefault(aid)
        if msg.isdigit() and (0 <= int(msg) <= 50):
            for x in openjtalk.Openjtalk.VOICEVOX:
                if int(msg) == int(x.value):
                    msg = x.name
                    break
        if str(msg).upper() in [x.name for x in openjtalk.Openjtalk.VOICE] or\
            str(msg).upper() in [x.name for x in openjtalk.Openjtalk.VOICEVOX]:
            # self._selfvoicedefault(aid)
            self.user_voices[aid]['voice'] = str(msg).upper()
            self._setvoicesettings()
            print('setting end')
            await ctx.send(f'Set your voice to {str(msg).upper()}')
        else:
            await ctx.send(f'Voice not found')
    
    @commands.command(aliases=['gv', 'gvs'], brief=f"Get your voice settings")
    async def getvoicesettings(self, ctx):
        # {'voice': openjtalk.Openjtalk.VOICE.NITECH.name, 'pass': '0.55', 'speed': '1.0', 
        # 'volume': '0.0', 'pitch': '0.0', 'intonation_scale': '1.0'}
        aid = str(ctx.author.id)
        if not aid in self.user_voices.keys():
            self._selfvoicedefault(aid)
        else:
            data = {}
            embed = discord.Embed()
            embed.title=ctx.author.display_name
            for d in self.user_voices[aid]:
                if d=='voice':
                    if self.user_voices[aid][d] in [x.name for x in openjtalk.Openjtalk.VOICE]:
                        data[d] = openjtalk.Openjtalk.VOICE[self.user_voices[aid][d]].name
                    else:
                        data[d] = openjtalk.Openjtalk.VOICEVOX[self.user_voices[aid][d]].name
                else:
                    if self.VOICE_SETTINGS[d]['is_exp']:
                        data[d] = str(round(self.param_normalize_exp(self.user_voices[aid][d], *self.VOICE_SETTINGS[d]['scale']), 2))+f'({round(float(self.user_voices[aid][d]),2)})'
                    else:
                        data[d] = str(round(self.param_normalize(self.user_voices[aid][d], *self.VOICE_SETTINGS[d]['scale']), 2))+f'({round(float(self.user_voices[aid][d]),2)})'
                
            embed.description = '\n'.join([x+' : '+str(y) for x, y in data.items()])
            embed.set_footer(text='all rights reserved.')
            await ctx.channel.send(embed=embed, delete_after=60)
    
    @commands.command(aliases=['vvl'])
    async def voicevoxlist(self, ctx):
        ls = [f'{x.value}:{x.name}' for x in openjtalk.Openjtalk.VOICEVOX]
        ls.sort()
        await ctx.send('\n'.join(ls))
    
    async def setvoice_template(self, ctx, num_f:float, key_, scale:tuple,
                                text_ok="Success!", text_ng="Out of range", is_exp=False):
        aid = str(ctx.author.id)
        if not aid in self.user_voices.keys():
            self._selfvoicedefault(aid)

        try:
            if is_exp:
                val = self.param_denormalize_exp(num_f, *scale)
            else:
                val = self.param_denormalize(num_f, *scale)
        except ValueError:
            await ctx.send(text_ng, delete_after=30)
        else:
            self.user_voices[aid][key_] = str(val)
            self._setvoicesettings()
            await ctx.send(text_ok, delete_after=30)
    
    @commands.command(brief=f"Set your voice pass (-1 ~ 1) default:0.1")
    async def setvoicepass(self, ctx, msg):
        '''Set your voice pass (-1 ~ 1) default:0.1'''
        await self.setvoice_template(ctx, float(msg), 'pass', (0.0, 1.0),
                               text_ok=f"Set your voice pass to {str(msg)}")
    
    @commands.command(aliases=['svspeed', 'svs'], brief=f"Set your voice speed (-1 ~ 1) default:1.0")
    async def setvoicespeed(self, ctx, msg):
        '''Set your voice speed (-1 ~ 1) default:0.1'''
        await self.setvoice_template(ctx, float(msg), 'speed', (0.5, 2.0),
                               text_ok=f"Set your voice speed to {str(msg)}", is_exp=True)
    
    @commands.command(brief=f"Set your voice volume default:0.0")
    async def setvoicevolume(self, ctx, msg):
        await self.setvoice_template(ctx, float(msg), 'volume', (-10.0, 10.0),
                               text_ok=f"Set your voice volume to {str(msg)}")
    
    @commands.command(aliases=['svpitch', 'svp'], brief=f"Set your voice pitch default:0.0(-0.15 ~ +0.15)")
    async def setvoicepitch(self, ctx, msg):
        await self.setvoice_template(ctx, float(msg), 'pitch', (-0.15, 0.15),
                               text_ok=f"Set your voice pitch to {str(msg)}")
            
    @commands.command(aliases=['svint', 'svi'], brief=f"Set your voice intonation scale default:1.0(0 ~ 2)")
    async def setvoiceintonationscale(self, ctx, msg):
        await self.setvoice_template(ctx, float(msg), 'intonation_scale', (0.0, 2.0),
                               text_ok=f"Set your voice intonation scale to {str(msg)}")
    
    @commands.command(aliases=['svdef', 'svd'], brief=f"Set your voice to the default")
    async def setvoicedefault(self, ctx):
        aid = str(ctx.author.id)
        self._selfvoicedefault(aid)
        await ctx.send(f'Your voice settings are set to the default')
    
    @commands.command(aliases=['usagevv', 'usagev'])
    async def usagevoicevox(self, ctx):
        '''Display remaining translation letters'''
        letters = openjtalk.Openjtalk.get_usage_vv()
        await ctx.send(f"I can say less than {letters} letters this month!")
            
async def setup(bot):
    await bot.add_cog(Voice(bot))

async def teardown(bot):
    print('voice teardown')
    for i in bot.voice_clients:
        asyncio.run(i.disconnect())
    print('voice teardowned')