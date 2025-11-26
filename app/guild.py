import sqlite3

import discord
from discord.ext import commands

class DataContainer():
    def __init__(self):
        self.voice_channel = None
        self.monitoring_channels = []

class Guild():
    def __init__(self, guild_id):
        self.guild_id = int(guild_id)
        self.db = sqlite3.connect('guilds.db')
        self.c = self.db.cursor()
        self._init_db()

    def _init_db(self):
        '''データベースのテーブルを初期化'''
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS voice_channel (
                id INTEGER PRIMARY KEY,
                channel INTEGER
            )
        ''')
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS monitoring_channels (
                id INTEGER,
                channel INTEGER,
                PRIMARY KEY (id, channel)
            )
        ''')
        self.db.commit()
    
    def __del__(self):
        self.c.close()

    def get(self):
        data = DataContainer()
        if res := self.get_voice_channel():
            data.voice_channel = res[0][0]
        else:
            data.voice_channel = None
        if res := self.get_monitoring_channels():
            for taple in res:
                data.monitoring_channels.append(taple[0])
        return data
    
    def get_voice_channel(self):
        '''voice_channelのレコードを取得'''
        res = self.c.execute(f'SELECT channel FROM voice_channel WHERE id = {self.guild_id}')
        return res.fetchall()

    def set_voice_channel(self, channel_id: int):
        '''voice_channelのレコードを更新'''
        print(self.get_voice_channel())
        if self.get_voice_channel():
            self.c.execute(f'UPDATE voice_channel SET channel = {channel_id} WHERE id = {self.guild_id}')
        else:
            self.c.execute(f'INSERT INTO voice_channel VALUES (?,?)', (self.guild_id, channel_id))
        self.db.commit()
    
    def get_monitoring_channels(self):
        '''monitoring_channelsのレコードを取得'''
        res = self.c.execute(f'SELECT channel FROM monitoring_channels WHERE id = {self.guild_id}')
        return res.fetchall()

    def set_monitoring_channel(self, channel_id: int):
        '''monitoring_channelsにレコードを追加'''
        self.c.execute(f'INSERT INTO monitoring_channels VALUES (?,?)', (self.guild_id, channel_id))
        self.db.commit()
        
    def delete_monitoring_channel(self, channel_id: int):
        '''monitoring_channelsのレコードを削除'''
        self.c.execute(f'DELETE FROM monitoring_channels WHERE id = {self.guild_id} AND channel = {channel_id}')
        self.db.commit()