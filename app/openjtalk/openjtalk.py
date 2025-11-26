import subprocess
import os
from enum import Enum
from logging import getLogger

if __name__ == '__main__':
    import voicevox
else:
    from openjtalk import voicevox

# ローカル環境用のパス（Docker環境では/app/）
# openjtalk.py から見て、appディレクトリを指す
# app/openjtalk/openjtalk.py -> app/openjtalk -> app
WORK_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '')

class Openjtalk():
    ADDR_BIN = r"open_jtalk"
    ADDR_DIC = os.path.join(WORK_DIR, r"openjtalk/open_jtalk_dic_utf_8-1.10/")
    ADDR_VOICE_DIR = os.path.join(WORK_DIR, r"hts_voice/")
    ADDR_MP3 = os.path.join(WORK_DIR, r"src/")
    class VOICE(Enum):
        MEI_NORMAL = os.path.join(WORK_DIR, r"hts_voice/mei/mei_normal.htsvoice")
        MEI_ANGRY = os.path.join(WORK_DIR, r"hts_voice/mei/mei_angry.htsvoice")
        MEI_HAPPY = os.path.join(WORK_DIR, r"hts_voice/mei/mei_happy.htsvoice")
        MEI_SAD = os.path.join(WORK_DIR, r"hts_voice/mei/mei_sad.htsvoice")
        MEI_BASHFUL = os.path.join(WORK_DIR, r"hts_voice/mei/mei_bashful.htsvoice")
        NITECH = os.path.join(WORK_DIR, r"hts_voice/nitech_jp_atr503_m001.htsvoice")
        TOHOKU_ANGRY = os.path.join(WORK_DIR, r"hts_voice/htsvoice-tohoku-f01-master/tohoku-f01-angry.htsvoice")
        TOHOKU_HAPPY = os.path.join(WORK_DIR, r"hts_voice/htsvoice-tohoku-f01-master/tohoku-f01-happy.htsvoice")
        TOHOKU_NEUTRAL = os.path.join(WORK_DIR, r"hts_voice/htsvoice-tohoku-f01-master/tohoku-f01-neutral.htsvoice")
        TOHOKU_SAD = os.path.join(WORK_DIR, r"hts_voice/htsvoice-tohoku-f01-master/tohoku-f01-sad.htsvoice")
        AK_1 = os.path.join(WORK_DIR, r"hts_voice/akihiro/20代男性01.htsvoice")
        AK_2 = os.path.join(WORK_DIR, r"hts_voice/akihiro/なないろニジ.htsvoice")
        AK_3 = os.path.join(WORK_DIR, r"hts_voice/akihiro/カマ声ギル子.htsvoice")
        AK_4 = os.path.join(WORK_DIR, r"hts_voice/akihiro/グリマルキン_1.0.htsvoice")
        AK_5 = os.path.join(WORK_DIR, r"hts_voice/akihiro/スランキ.htsvoice")
        AK_6 = os.path.join(WORK_DIR, r"hts_voice/akihiro/ワタシ.htsvoice")
        AK_7 = os.path.join(WORK_DIR, r"hts_voice/akihiro/京歌カオル.htsvoice")
        AK_8 = os.path.join(WORK_DIR, r"hts_voice/akihiro/句音コノ。.htsvoice")
        AK_9 = os.path.join(WORK_DIR, r"hts_voice/akihiro/和音シバ.htsvoice")
        AK_10 = os.path.join(WORK_DIR, r"hts_voice/akihiro/唱地ヨエ.htsvoice")
        AK_11 = os.path.join(WORK_DIR, r"hts_voice/akihiro/天月りよん.htsvoice")
        AK_12 = os.path.join(WORK_DIR, r"hts_voice/akihiro/想音いくと.htsvoice")
        AK_13 = os.path.join(WORK_DIR, r"hts_voice/akihiro/想音いくる.htsvoice")
        AK_14 = os.path.join(WORK_DIR, r"hts_voice/akihiro/戯歌ラカン.htsvoice")
        AK_15 = os.path.join(WORK_DIR, r"hts_voice/akihiro/月音ラミ_1.0.htsvoice")
        AK_16 = os.path.join(WORK_DIR, r"hts_voice/akihiro/松尾P.htsvoice")
        AK_17 = os.path.join(WORK_DIR, r"hts_voice/akihiro/桃音モモ.htsvoice")
        AK_18 = os.path.join(WORK_DIR, r"hts_voice/akihiro/沙音ほむ.htsvoice")
        AK_19 = os.path.join(WORK_DIR, r"hts_voice/akihiro/獣音ロウ.htsvoice")
        AK_20 = os.path.join(WORK_DIR, r"hts_voice/akihiro/瑞歌ミズキ_Talk.htsvoice")
        AK_21 = os.path.join(WORK_DIR, r"hts_voice/akihiro/白狐舞.htsvoice")
        AK_22 = os.path.join(WORK_DIR, r"hts_voice/akihiro/空唄カナタ.htsvoice")
        AK_23 = os.path.join(WORK_DIR, r"hts_voice/akihiro/緋惺.htsvoice")
        AK_24 = os.path.join(WORK_DIR, r"hts_voice/akihiro/能民音ソウ.htsvoice")
        AK_25 = os.path.join(WORK_DIR, r"hts_voice/akihiro/蒼歌ネロ.htsvoice")
        AK_26 = os.path.join(WORK_DIR, r"hts_voice/akihiro/薪宮風季.htsvoice")
        AK_27 = os.path.join(WORK_DIR, r"hts_voice/akihiro/誠音コト.htsvoice")
        AK_28 = os.path.join(WORK_DIR, r"hts_voice/akihiro/遊音一莉.htsvoice")
        AK_29 = os.path.join(WORK_DIR, r"hts_voice/akihiro/遠藤愛.htsvoice")
        AK_30 = os.path.join(WORK_DIR, r"hts_voice/akihiro/闇夜 桜_1.0.htsvoice")
        AK_31 = os.path.join(WORK_DIR, r"hts_voice/akihiro/飴音わめあ.htsvoice")
    
    class VOICEVOX(Enum):
        四国めたんノーマル=2
        四国めたんあまあま=0
        四国めたんツンツン=6
        四国めたんセクシー=4
        四国めたんささやき=36
        四国めたんヒソヒソ=37
        ずんだもんノーマル=3
        ずんだもんあまあま=1
        ずんだもんツンツン=7
        ずんだもんセクシー=5
        ずんだもんささやき=22
        ずんだもんヒソヒソ=38
        春日部つむぎノーマル=8
        雨晴はうノーマル=10
        波音リツノーマル=9
        玄野武宏ノーマル=11
        玄野武宏喜び=39
        玄野武宏ツンギレ=40
        玄野武宏悲しみ=41
        白上虎太郎ふつう=12
        白上虎太郎わーい=32
        白上虎太郎びくびく=33
        白上虎太郎おこ=34
        白上虎太郎びえーん=35
        青山龍星ノーマル=13
        冥鳴ひまりノーマル=14
        九州そらノーマル=16
        九州そらあまあま=15
        九州そらツンツン=18
        九州そらセクシー=17
        九州そらささやき=19
        もち子さんノーマル=20
        剣崎雌雄ノーマル=21
        WhiteCULノーマル=23
        WhiteCULたのしい=24
        WhiteCULかなしい=25
        WhiteCULびえーん=26
        後鬼人間ver=27
        後鬼ぬいぐるみver=28
        No7ノーマル=29
        No7アナウンス=30
        No7読み聞かせ=31
        ちび式じいノーマル=42
        櫻歌ミコノーマル=43
        櫻歌ミコ第二形態=44
        櫻歌ミコロリ=45
        小夜SAYOノーマル=46
        ナースロボ＿タイプＴノーマル=47
        ナースロボ＿タイプＴ楽々=48
        ナースロボ＿タイプＴ恐怖=49
        ナースロボ＿タイプＴ内緒話=50
    
    class TYPE(Enum):
        OPENJTALK = 1
        VOICEVOX = 2
    
    @staticmethod
    def add_dictionary(surface, pronounce, accent_type=None):
        return voicevox.Voicevox.set_dict(surface, pronounce, accent_type)
    
    def __init__(self, text, name='sample', overwrite=False):
        self.text = text
        self.name = name
        self.mp3 = os.path.join(Openjtalk.ADDR_MP3, f'{name}.mp3')
        self.over_writable = overwrite
        self.params = {}
        self.type = Openjtalk.TYPE.OPENJTALK
        self.set_voice(Openjtalk.VOICE.NITECH)
        self.speed = 1.0
        self.intonation_scale = 1.0
        self.pitch = 0.0
        self.logger = getLogger(__name__)
    
    def _checktext(self):
        l=0
        m=len(self.text)
        c=0
        while l < m or l < 150:
            if l+1 >= m:
                break
            for x in self.text[l-c:l+1]:
                if x != self.text[l]:
                    c=0
                    break
            c+=1
            if c>5:
                self.text= self.text[0:l] + ',' + self.text[l:]
                c=0
                m+=1
            l+=1

    def set_voice(self, voice, all_pass=0.55, speed=1.0, volume=0.0, pitch=0.0, intonation_scale=1.0):
        if voice in Openjtalk.VOICE:
            self.type = Openjtalk.TYPE.OPENJTALK
            self.voice = voice
            self.set_voice_param('a', all_pass)
            self.set_voice_param('r', speed)
            self.set_voice_param('g', volume)
        elif voice in Openjtalk.VOICEVOX:
            self.type = Openjtalk.TYPE.VOICEVOX
            self.voice = voice
            self.speed = speed
            self.pitch = pitch
            self.intonation_scale = intonation_scale
        else:
            print('set_voice(): voice is out of Enum')
        self._set_mp3_name()
    
    def set_voice_param(self, fix, value):
        if fix in ['s','p','a','b','r','fm','u','jm','jf','g','z']:
            if fix in ['s','p','z']:
                value = int(value)
            if fix in ['a','b','u'] and (float(value) < 0 or 1 < float(value)):
                return False
            if fix in ['r','jm','jf','z'] and float(value) < 0:
                return False
            if fix in ['s','p'] and value < 1:
                return False
            self.params[fix] = str(value)
    
    def _set_mp3_name(self):
        name = f'{self.name}_{self.voice.name}'
        if self.type == Openjtalk.TYPE.OPENJTALK:
            for key in self.params:
                name += f'_{key}_{self.params[key]}'
            self.mp3 = os.path.join(Openjtalk.ADDR_MP3, f'{name}.mp3')
        elif self.type == Openjtalk.TYPE.VOICEVOX:
            name += f'_p_{self.pitch}'
            name += f'_s_{self.speed}'
            name += f'_i_{self.intonation_scale}'
            self.mp3 = os.path.join(Openjtalk.ADDR_MP3, f'{name}.wav')

    def get_mp3(self):
        if self.type == Openjtalk.TYPE.OPENJTALK:
            self._checktext()
            return self.get_mp3_oj()
        elif self.type == Openjtalk.TYPE.VOICEVOX:
            return self.get_mp3_vv()
            
    def get_mp3_oj(self):
        if os.path.exists(self.mp3) and not self.over_writable:
            return os.path.abspath(self.mp3)
        
        source = self.name + '.txt'
        with open(source, mode='w') as f:
            f.write(self.text)
        cmd = [Openjtalk.ADDR_BIN]
        for key in self.params:
            cmd += [f'-{key}', self.params[key]]
        cmd += ["-x", Openjtalk.ADDR_DIC, "-m", self.voice.value, "-ow", self.mp3, source]
        print(cmd)
        subprocess.run(cmd)
        os.remove(source)
        return os.path.abspath(self.mp3)
    
    def get_mp3_vv(self):
        if os.path.exists(self.mp3) and not self.over_writable:
            return os.path.abspath(self.mp3)
        self.logger.info("text:"+str(self.text))
        self.logger.info("speaker:"+str(self.voice.value))
        self.logger.info("file_name:"+str(self.mp3))
        vv = voicevox.Voicevox(text=self.text, speaker=self.voice.value, file_name=self.mp3, pitch=self.pitch, intonation_scale=self.intonation_scale, speed=self.speed)
        if vv.get():
            self.logger.info(os.path.abspath(self.mp3))
            return os.path.abspath(self.mp3)
    
    @staticmethod
    def get_usage_vv():
        return voicevox.Voicevox.get_usage()
        
if __name__ == '__main__':
    # text = str(input())
    oj = Openjtalk("test sentence")
    oj.set_voice(Openjtalk.VOICEVOX(1))
    print(oj.get_mp3_vv())
    p=Openjtalk.VOICEVOX(1)
    print(p.value)
    pass