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
import logging

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

logger = logging.getLogger(__name__)

CONNECTIN_TIME_OUT = 30
DOWNLOAD_SAVE_DIR='app/src'
# ローカル環境用のパス（Docker環境では/app/setting.json）
# app/voice.py から見て、プロジェクトルートのsetting.jsonを指す
SETTING_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'setting.json')

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
        logger.info(f"play() called: url={url}, guild_id={guild_id}")
        data = guild.Guild(guild_id).get()
        logger.info(f"Guild data: voice_channel={data.voice_channel}")
        if data.voice_channel:
            channel = self.bot.get_channel(data.voice_channel)
            if channel:
                logger.info(f"Found voice channel: {channel.name} (ID: {channel.id})")
                try:
                    await channel.connect(reconnect=False)
                    logger.info("Connected to voice channel")
                    if not guild_id in self.queue:
                        self.queue
                except discord.ClientException as e:
                    logger.debug(f"Already connected to voice channel: {e}")
                    pass
                except Exception as e:
                    logger.error(f"Error connecting to voice channel: {type(e).__name__}: {e}", exc_info=True)
                    return
                finally:
                    for vc in self.bot.voice_clients:
                        if vc.guild.id == guild_id:
                            logger.info(f"Playing audio: {url}")
                            vc.play(discord.FFmpegPCMAudio(url))
                            logger.info("Audio playback started")
            else:
                logger.warning(f"Voice channel not found: {data.voice_channel}")
        else:
            logger.warning(f"Cannot find voice channel for guild_id: {guild_id}")
    
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
        if user is None:
            logger.warning(f"reaction_method called but user is None: emoji={emoji.name if emoji else 'None'}, message_id={message.id}")
            return
        if emoji is None:
            logger.warning(f"reaction_method called but emoji is None: user={user.name if user else 'None'}, message_id={message.id}")
            return
        logger.info(f"reaction_method called: emoji={emoji.name}, user={user.name}, message_id={message.id}")
        if emoji.name == '▶️':
            text = message.content
            if embeds := message.embeds:
                text = embeds[0].title
            text = re.sub(r'<.*?>', '', text)
            logger.info(f"Extracted text: {text[:100]}...")
            if text:
                # if re.search(r"[a-zA-Z]", text[0]):
                try:
                    ld = langdetect.detect(text).upper()[-2:]
                    logger.info(f"Detected language: {ld}")
                except Exception as e:
                    logger.error(f"Language detection failed: {e}")
                    ld = "UNKNOWN"
                
                if ld != "JA" and ld != "CH" and ld != "KO" and ld != "ZW":
                    logger.info(f"Non-Japanese text detected ({ld}), using Weblio")
                    wbl = weblio.Weblio(text, message.id)
                    audio_file = wbl.get_audio()
                    logger.info(f"Weblio audio file: {audio_file}")
                    await self.play(audio_file, message.guild.id)
                else:
                    logger.info(f"Japanese text detected ({ld}), using OpenJTalk")
                    text = re.sub(r'<.*?>', '', text)
                    logger.info(f"Processing text: {text[:100]}...")
                    if len(text) > 256:
                        text = text[:255]
                        logger.info(f"Text truncated to 255 characters")
                    try:
                        msg_id = str(message.id)
                        msg_aid = str(message.author.id)
                        logger.info(f"Message ID: {msg_id}, Author ID: {msg_aid}")
                        logger.info(f"User voices keys: {list(self.user_voices.keys())}")
                        
                        if msg_aid not in self.user_voices.keys():
                            logger.warning(f"User {msg_aid} not in user_voices, using default")
                            self._selfvoicedefault(msg_aid)
                        
                        voice_name = self.user_voices[msg_aid]['voice']
                        logger.info(f"Selected voice: {voice_name}")
                        
                        if voice_name in [x.name for x in openjtalk.Openjtalk.VOICE]:
                            voice = openjtalk.Openjtalk.VOICE[voice_name]
                            logger.info(f"Using OpenJTalk VOICE: {voice_name}")
                        else:
                            voice = openjtalk.Openjtalk.VOICEVOX[voice_name]
                            logger.info(f"Using OpenJTalk VOICEVOX: {voice_name}")
                        
                        oj = openjtalk.Openjtalk(text=text.replace('\n', ';'), name=msg_id)
                        logger.info(f"OpenJTalk instance created")
                        
                        if msg_aid in self.user_voices.keys():
                            logger.info(f"Setting voice parameters: pass={self.user_voices[msg_aid]['pass']}, speed={self.user_voices[msg_aid]['speed']}, volume={self.user_voices[msg_aid]['volume']}, pitch={self.user_voices[msg_aid]['pitch']}, intonation_scale={self.user_voices[msg_aid]['intonation_scale']}")
                            oj.set_voice(
                                voice=voice,\
                                all_pass=self.user_voices[msg_aid]['pass'],\
                                speed=self.user_voices[msg_aid]['speed'],\
                                volume=self.user_voices[msg_aid]['volume'],\
                                pitch=self.user_voices[msg_aid]['pitch'],\
                                intonation_scale=self.user_voices[msg_aid]['intonation_scale']
                                )
                        
                        mp3_file = oj.get_mp3()
                        logger.info(f"Generated MP3 file: {mp3_file}")
                        await self.play(mp3_file, message.guild.id)
                        logger.info(f"Play command sent for {mp3_file}")
                    except Exception as e:
                        logger.error(f"Error in Japanese text processing: {type(e).__name__}: {e}", exc_info=True)
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
        emoji_name = payload.emoji.name if payload.emoji else str(payload.emoji)
        logger.info(f"Reaction added: emoji={emoji_name}, user_id={payload.user_id}, message_id={payload.message_id}")
        if payload.user_id == self.bot.user.id:
            logger.debug("Ignoring reaction from bot itself")
            return
        try:
            channel = self.bot.get_channel(payload.channel_id)
            if channel is None:
                logger.warning(f"Channel not found: {payload.channel_id}")
                return
            message = await channel.fetch_message(payload.message_id)
            if message is None:
                logger.warning(f"Message not found: {payload.message_id}")
                return
            user = self.bot.get_user(payload.user_id)
            if user is None:
                try:
                    user = await self.bot.fetch_user(payload.user_id)
                    logger.info(f"Fetched user: {user.name} (ID: {user.id})")
                except Exception as e:
                    logger.error(f"Failed to fetch user {payload.user_id}: {e}")
                    return
            await self.reaction_method(message, user, payload.emoji)
        except Exception as e:
            logger.error(f"Error in on_reaction_add_weblio: {type(e).__name__}: {e}", exc_info=True)
    
    @commands.Cog.listener(name='on_raw_reaction_remove')
    async def on_reaction_remove_weblio(self, payload:discord.RawReactionActionEvent):
        emoji_name = payload.emoji.name if payload.emoji else str(payload.emoji)
        logger.info(f"Reaction removed: emoji={emoji_name}, user_id={payload.user_id}, message_id={payload.message_id}")
        if payload.user_id == self.bot.user.id:
            logger.debug("Ignoring reaction removal from bot itself")
            return
        try:
            channel = self.bot.get_channel(payload.channel_id)
            if channel is None:
                logger.warning(f"Channel not found: {payload.channel_id}")
                return
            message = await channel.fetch_message(payload.message_id)
            if message is None:
                logger.warning(f"Message not found: {payload.message_id}")
                return
            user = self.bot.get_user(payload.user_id)
            if user is None:
                try:
                    user = await self.bot.fetch_user(payload.user_id)
                    logger.info(f"Fetched user: {user.name} (ID: {user.id})")
                except Exception as e:
                    logger.error(f"Failed to fetch user {payload.user_id}: {e}")
                    return
            await self.reaction_method(message, user, payload.emoji)
        except Exception as e:
            logger.error(f"Error in on_reaction_remove_weblio: {type(e).__name__}: {e}", exc_info=True)
    
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
        try:
            with open(SETTING_FILE, mode='r') as f:
                data=json.load(f)
        except FileNotFoundError:
            # 設定ファイルが存在しない場合は空の辞書を返す
            data = {}
        return data
    
    def _setvoicesettings(self):
        data = self.user_voices
        # ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(SETTING_FILE), exist_ok=True)
        with open(SETTING_FILE, mode='w') as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=2))
        logger.info(f"Voice settings saved to {SETTING_FILE}")
    
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