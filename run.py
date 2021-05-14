"""run the bot"""
import asyncio

import asyncio
import logging

from src.bot import MyBot
from src.skills.gpt_chitchat import GptChitChatPlugin
from src.skills.time_mention import TimeMentionPlugin
from src.skills.chinese_word_plugin import ChineseWordPlugin

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


async def main():
    """doc"""
    # pylint: disable=W0603
    global bot
    bot = MyBot()

    # skills
    time_mention_skill = TimeMentionPlugin()
    gpt_chitchat_skill = GptChitChatPlugin()
    chinese_word_skill = ChineseWordPlugin()
    bot.use(time_mention_skill).use(gpt_chitchat_skill).use(chinese_word_skill)
    await bot.start()


asyncio.run(main())
