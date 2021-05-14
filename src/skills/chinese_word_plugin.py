from __future__ import annotations

from wechaty import (
    Wechaty,
    Message,
    WechatyPlugin
)
import asyncio
import json, random
from src.utils import SupportSet

class Idiom:
    def __init__(self, file: str = './assets/data/chinese-xinhua/data/idiom.json'):
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.idioms = data
    
    def one(self):
        random_one = random.randint(0, len(self.idioms))
        return self.idioms[random_one]

class XieHouYu:
    def __init__(self, file: str = './assets/data/chinese-xinhua/data/xiehouyu.json'):
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.xiehouyu = data
    
    def one(self):
        random_one = random.randint(0, len(self.xiehouyu))
        return self.xiehouyu[random_one]


class ChineseWordPlugin(WechatyPlugin):
    def __init__(self, options = None):
        super().__init__(options)
        self.support_set = SupportSet.from_file('./assets/data/chinese-xinhua/intents.json')
        self.idiom: Idiom = Idiom()
        self.xiehouyu: XieHouYu = XieHouYu()
    
    async def init_plugin(self, wechaty: Wechaty):
        return await super().init_plugin(wechaty)
    
    async def on_message(self, msg: Message):
        text = msg.text()
        labels = self.support_set.predict_labels(text=text)
        if labels:
            if 'ask_for_idiom' in labels:
                one = self.idiom.one()
                reply_text = one['derivation'] + '。' + one['explanation']
                await msg.say(reply_text)
                await asyncio.sleep(10)
                await msg.say(f"答案是：{one['word']}" )
            
            if 'ask_for_xiehouyu' in labels:
                one = self.xiehouyu.one()
                reply_text = one['riddle']
                await msg.say(reply_text)
                await asyncio.sleep(2)
                await msg.say(f"答案是：{one['answer']}" )