from typing import Optional
import argparse
from src.skills.gpt_chitchat import gpt_api
from wechaty_puppet import get_logger

from wechaty import WechatyPlugin, Message, Wechaty, WechatyPluginOptions

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

    def get_notion(self, text: str):
        if text.startswith('魔镜魔镜'):
            return True, text[4:]
        if text.startswith('小可爱'):
            return True, text[3:]
        return False, None
            

    async def on_message(self, msg: Message):
        """listen message event and chit with users"""
        text = msg.text()
        notion, content = self.get_notion(text)
        text = content or text
        mention_me = await msg.mention_self()
        if notion or mention_me:
            try:
                # args = self.argparse.parse_args(text)
                # length = args.l
                # query = args.q
                res_text = gpt_api.get_gpt_response(text, 20)
                await msg.say(res_text)
            except Exception as e:
                pass
                # help_msg = self.argparse.format_help()
                # await msg.say(help_msg)
