from typing import Optional
import argparse
from dataclasses import dataclass
from skills.gpt_chitchat import gpt_api
from wechaty_puppet import get_logger

from wechaty import WechatyPlugin, Message, Wechaty, WechatyPluginOptions
from tokenizers import BertWordPieceTokenizer

log = get_logger('GptChitchatPlugin')


class GptChitChatPlugin(WechatyPlugin):
    def __init__(self, options: Optional[WechatyPluginOptions] = None):
        super().__init__(options)
        self.argparse = argparse.ArgumentParser('gpt')

    @property
    def name(self) -> str:
        return 'ChitChatPlugin'

    async def init_plugin(self, wechaty: Wechaty):
        self.argparse.add_argument('-q', required=True, type=str, help='the query feed into gpt2 model')
        self.argparse.add_argument('-l', required=False, type=int, default=30, help='the length of response')

    async def on_message(self, msg: Message):
        """listen message event and chit with users"""
        text = msg.text()
        if text.startswith('gpt '):
            try:

                text = text[4:].split()
                args = self.argparse.parse_args(text)
                length = args.l
                query = args.q
                res_text = gpt_api.get_gpt_response(query, length)
                await msg.say(res_text)
            except Exception as e:
                help_msg = self.argparse.format_help()
                await msg.say(help_msg)
