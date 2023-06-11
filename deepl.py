import json

import requests

AUTH_CODE = '171c6662-3831-30c7-3a02-83b7aff377c2:fx'

class Deepl():
    @staticmethod
    def usage():
        try:
            req = requests.get(
                url='https://api-free.deepl.com/v2/usage',
                params={"auth_key": AUTH_CODE}
            )
        except Exception as e:
            print(e)
            return False
        else:
            return req.json()
    
    def __init__(self, sentence: str, source_lang = "", target_lang = "JA", formality = "default"):
        self.sentence = sentence
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.formality = formality
    
    def _get(self):
        params = {
            "auth_key": AUTH_CODE,
            "text": self.sentence,
            "source_lang": self.source_lang,
            "target_lang": self.target_lang,
            "formality": self.formality
        }
        try:
            req = requests.post(
                url="https://api-free.deepl.com/v2/translate",
                data=params
            )
        except Exception as e:
            print(f"Error at deepl: {e}")
            return False
        else:
            data = req.json()
            if __name__ == '__main__':
                print(data)
            self.datas = data["translations"]
            return True
    
    def get_generator(self):
        '''return generator'''
        if self._get():
            for data in self.datas:
                yield data["text"]
        else:
            return False
    
    def get(self):
        '''return str'''
        if self._get():
            return str(self.datas[0]["text"])
        else:
            return False
    
    def get_list(self):
        '''return list'''
        if self._get():
            ls = []
            for data in self.datas:
                ls.append(data["text"])
            return ls
        else:
            return False

# print(Deepl("weblio translation is outstanding").get())
# print(next(Deepl("なんだこりゃ", target_lang="EN").get_generator()))
# print(Deepl("なんだこりゃ", target_lang="FR").get_list())

print(Deepl.usage())