"""template of your bot"""
from __future__ import annotations
import asyncio
from wechaty import Wechaty, WechatyOptions
from wechaty_plugin_contrib.message_controller import message_controller
from wechaty_plugin_contrib.contrib.api_plugin import APIPlugin
from wechaty_plugin_contrib.contrib.ding_dong_plugin import DingDongPlugin
from wechaty_plugin_contrib.contrib.rss_plugin import RSSPlugin
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv()
    options = WechatyOptions(
        port=80,
    )
    bot = Wechaty(options)
    bot.use([
        APIPlugin(),
        RSSPlugin()
    ])
    message_controller.init_plugins(bot)
    asyncio.run(bot.start())
