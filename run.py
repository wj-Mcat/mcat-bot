"""run the bot"""
import asyncio

import asyncio
import logging

from wechaty_plugin_contrib import (
    DingDongPlugin
)

from src.skills.gpt_chitchat import GptChitChatPlugin
from src.skills.time_mention import TimeMentionPlugin

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
from src.bot import MyBot


async def main():
    """doc"""
    # pylint: disable=W0603
    global bot
    import os
    os.environ['WECHATY_PUPPET_HOSTIE_TOKEN'] = 'your-token'
    bot = MyBot()

    # skills
    time_mention_skill = TimeMentionPlugin()
    gpt_chitchat_skill = GptChitChatPlugin()
    ding_dong_plugin = DingDongPlugin()
    bot.use(time_mention_skill).use(gpt_chitchat_skill).use(ding_dong_plugin)
    await bot.start()


asyncio.run(main())
