import json
import urllib
import os
from logging import getLogger

import requests
import wanakana
import mojimoji

CHUNK_SIZE = 1024
API_KEY = os.environ.get('VOICEVOX_API_KEY')

class Voicevox():
    def __init__(self, text: str, speaker: int, file_name: str, pitch=0.0, intonation_scale=1.0, speed=1.0):
        self.text = Voicevox._check_surface(text)
        self.query = None
        self.speaker = speaker
        self.file_name = file_name
        self.pitch = pitch
        self.intonation_scale = intonation_scale
        self.speed = speed
        self.logger = getLogger(__name__)
    
    def _get_query(self):
        text = urllib.parse.quote_plus(self.text)
        url = f"http://localhost:50021/audio_query?text={text}&speaker={self.speaker}"
        headers = {
            "accept": "application/json"
        }
        try:
            req = requests.post(
                url = url,
                headers=headers
            )
        except Exception as e:
            self.logger.error(f"Error at voicevox: {e}")
            return False
        else:
            self.query = req.json()
            return True
        
    def _get_wav(self):
        url = f"http://localhost:50021/synthesis?speaker={self.speaker}&enable_interrogative_upspeak=true"
        headers = {
            "accept": "audio/wav",
            "Content-Type": "application/json"
        }
        try:
            with requests.post(url, json=self.query, headers=headers, stream=True) as res:
                if res.status_code == 200:
                    file_size = int(res.headers.get('content-length'))
                    with open(self.file_name, 'wb') as file:
                        i = 0
                        for chunk in res.iter_content(chunk_size=CHUNK_SIZE):
                            i += CHUNK_SIZE
                            file.write(chunk)
                        if i >= file_size:
                            return True
                else:
                    self.logger.error('Http error. Skip download.')
                    return True
        except Exception as e:
            self.logger.error(f"Error at voicevox: {e}")
            return False
    
    def get_wav_api(self):
        text = urllib.parse.quote_plus(self.text)
        url = f"https://api.su-shiki.com/v2/voicevox/audio/?speaker={self.speaker}&key={API_KEY}&text={text}&pitch={self.pitch}&intonationScale={self.intonation_scale}&speed={self.speed}"
        headers = {
            "accept": "audio/wav",
        }
        self.logger.info(url)
        try:
            with requests.post(url, headers=headers, timeout=60) as res:
                if res.status_code == 200:
                    # ディレクトリが存在しない場合は作成
                    os.makedirs(os.path.dirname(self.file_name), exist_ok=True)
                    with open(self.file_name, 'wb') as file:
                        file.write(res.content)
                    self.logger.info(f"Audio file saved: {self.file_name}")
                    return True
                else:
                    self.logger.error('Http error. Skip download.'+str(res))
            return False
        except Exception as e:
            self.logger.error(f"Error in get_wav_api: {type(e).__name__}: {e}", exc_info=True)
            return False
        # except Exception as e:
        #     print(f"Error at voicevox: {e}")
        #     return False
    
    def get(self):
        '''return str'''
        if self.get_wav_api():
            return True
        else:
            # if self._get_query():
            #     if self._get_wav():
            #         return True
            # else:
            return False
    
    @staticmethod
    def get_usage():
        url = f"https://api.su-shiki.com/v2/api/?key={API_KEY}"
        headers = {
            "accept": "application/json"
        }
        try:
            req = requests.get(
                url = url,
                headers=headers
            )
        except Exception as e:
            print(f"Error at voicevox: {e}")
            return False
        else:
            r = req.json()
            print(r)
            return r['points'] // 100
    
    @staticmethod
    def _check_surface(surface):
        surface = surface.lower()
        surface = mojimoji.han_to_zen(surface)
        return surface
    
    @staticmethod
    def _check_pronounce(pronounce):
        pronounce = wanakana.to_katakana(pronounce)
        pronounce = mojimoji.han_to_zen(pronounce)
        return pronounce
    
    @staticmethod
    def set_dict(surface, pronounce, accent_type):
        print(f'set dict {surface}[{pronounce}]:{accent_type}')
        surface = Voicevox._check_surface(surface)
        pronounce = Voicevox._check_pronounce(pronounce)
        if accent_type == None:
            accent_type = len(pronounce) - 1
        if uuid := Voicevox._exist_dict(surface):
            return Voicevox._edit_dict(uuid, surface, pronounce, accent_type)
        else:
            return Voicevox._add_dict(surface, pronounce, accent_type)
    
    @staticmethod
    def _add_dict(surface, pronounce, accent_type):
        surface = urllib.parse.quote_plus(surface)
        pronounce = urllib.parse.quote_plus(pronounce)
        url = f"http://localhost:50021/user_dict_word?surface={surface}&pronunciation={pronounce}&accent_type={accent_type}"
        headers = {
            "accept": "application/json"
        }
        try:
            req = requests.post(
                url = url,
                headers=headers
            )
        except Exception as e:
            print(f"Error at voicevox: {e}")
            return False
        else:
            if req.status_code == 200:
                return True
            else:
                print('http error')
                return False
    
    @staticmethod
    def _edit_dict(uuid, surface, pronounce, accent_type):
        surface = urllib.parse.quote_plus(surface)
        pronounce = urllib.parse.quote_plus(pronounce)
        url = f"http://localhost:50021/user_dict_word/{uuid}?surface={surface}&pronunciation={pronounce}&accent_type={accent_type}"
        headers = {
            "accept": "application/json"
        }
        try:
            req = requests.put(
                url = url,
                headers=headers
            )
        except Exception as e:
            print(f"Error at voicevox: {e}")
            return False
        else:
            if req.status_code == 204:
                return True
            else:
                print('http error')
                return False
    
    @staticmethod
    def _get_dict(surface):
        url = "http://localhost:50021/user_dict"
        headers = {
            "accept": "application/json"
        }
        try:
            req = requests.get(
                url = url,
                headers=headers
            )
        except Exception as e:
            print(f"Error at voicevox: {e}")
            return False
        else:
            res = req.json()
            return res
    
    @staticmethod
    def _exist_dict(surface):
        full_dict = Voicevox._get_dict(surface)
        for key, value in full_dict.items():
            if value['surface'] == surface:
                return key
        return None