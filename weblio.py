# coding: utf-8

import asyncio
import os
from pathlib import Path
import re
import urllib
import json
import random

from bs4 import BeautifulSoup
import requests

CONNECTIN_TIME_OUT = 30
DOWNLOAD_SAVE_DIR='src/'
SETTING_FILE='setting.json'

class DataContainer():
    pass

class Weblio():
    def __init__(self, msg, msg_id):
        self.id = msg_id
        self.raw_word = msg
        self.word = self.space_to_plus(msg)
        self.filepath_mp3 = DOWNLOAD_SAVE_DIR + str(msg_id) + '.mp3'
        self.filepath_wav = DOWNLOAD_SAVE_DIR + str(msg_id) + '.wav'

    def get_audio(self):
        '''音声ファイルを返す'''
        if not os.path.exists(self.filepath_mp3):
            if not os.path.exists(self.filepath_wav):
                if not self._get_word_audio():
                    if not self._get_trans_audio():
                        return False
                    else:
                        return self.filepath_wav
                else:
                    return self.filepath_mp3
            else:
                return self.filepath_wav
        else:
            return self.filepath_mp3
    
    def get_data(self):
        ''' .text: translations\n
            .more: more infomations
        '''
        data = DataContainer()
        data.text = self._get_trans_text()
        data.more = self._get_trans_text_more()
        return data

    def space_to_plus(self, word):
        if ' ' in word:
            word.replace(' ', '+')
        if '?' in word:
            word.replace('?', '%3F')
        if "’" in word:
            word.replace("’", "'")
        if "‘" in word:
            word.replace("‘", "'")
        return word
    
    def _write_from_url(self, url, filepath, content_type):
        try:
            req = requests.get(url)
        except Exception as e:
            print(e)

        if req.headers['Content-Type'] == content_type:
            with open(filepath, 'wb') as file:
                file.write(req.content)
            return True
        else:
            print(f"file is not expected:{req.headers['Content-Type']}")
        return False

    def _write_mpeg_from_url(self, url):
        return self._write_from_url(url, self.filepath_mp3, 'audio/mpeg')
    
    def _write_wav_from_url(self, url):
        return self._write_from_url(url, self.filepath_wav, 'audio/x-wav')
        
    def _get_word_audio(self):
        '''単語の音声を取得する'''
        url = 'https://ejje.weblio.jp/content/' + self.word
        print(url)
        try:
            req = requests.get(url)
        except Exception as e:
            print(e)

        soup = BeautifulSoup(req.content, 'html.parser')
        content = soup.find(id='audioDownloadPlayUrl')
        if content:
            if content['href']:
                mp3_url = content['href']
                return self._write_mpeg_from_url(mp3_url)
        return False
    
    def _get_weblio_hash(self):
        url = 'https://translate.weblio.jp'
        try:
            req = requests.get(url)
        except Exception as e:
            print(e)
            return None
        
        soup = BeautifulSoup(req.content, 'html.parser')
        content = soup.find(id='traSpA')
        if content:
            if content['value']:
                return content['value']
        return None

    def _get_trans_audio(self):
        # url = f'https://translate.weblio.jp/tts?query={self.word}&ar=e5b0e52e78aab69b&c=1&lp=EJ'
        url = f'https://translate.weblio.jp/tts?query={urllib.parse.quote(self.word)}&ar={self._get_weblio_hash()}&c=1&lp=EJ'
        return self._write_wav_from_url(url)
    
    def _get_trans_text(self):
        '''訳文を取得'''
        params = {
            'lp': 'EJ',
            'originalText': self.raw_word
        }
        params = urllib.parse.urlencode(params)
        response = requests.post(
            'https://translate.weblio.jp/',
            data=params,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        res = []
        soup = BeautifulSoup(response.content, 'html.parser')
        content = soup.find(class_='transExpB')
        if content is not None:
            content = content.ul
            if content is not None:
                res += [', '.join(map(lambda x: x.text, content.children))]
                # return '\n'.join(map(lambda x: x.text, content.children))
        content = soup.find(class_='transResultMain')
        if content is not None:
            content = content.ol
            if content is not None:
                res += list(map(lambda x: f'`{x.text}`', content.children))
                # return '\n'.join(map(lambda x: x.text, content.children))
        content = soup.find(class_='transResultMain')
        if content is not None:
            content = content.ul
            if content is not None:
                res += list(map(lambda x: f'`{x.text}`', content.children))
                # return '\n'.join(map(lambda x: x.text, content.children))
        if res:
            return res
        return '[NOT FATAL ERROR]'
    
    def _get_trans_text_more(self):
        '''近隣情報を取得'''
        params = {
            'lp': 'EJ',
            'originalText': self.raw_word
        }
        params = urllib.parse.urlencode(params)
        response = requests.post(
            'https://translate.weblio.jp/',
            data=params,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        content = soup.find(class_='nrCntSgKw')
        if content is not None:
            res = []
            for d in content.children:
                r = {
                    'word': d.find(class_='nrCntSgT').a.text,
                    'href': d.find(class_='nrCntSgT').a['href'],
                    'caption': d.find(class_='nrCntSgB').text
                }
                res.append(r)
            if res:
                return res
        return None
