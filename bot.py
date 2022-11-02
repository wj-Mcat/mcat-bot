"""template of your bot"""
from __future__ import annotations
from argparse import ArgumentParser
import asyncio
from wechaty import Wechaty, WechatyOptions
from wechaty_plugin_contrib.message_controller import message_controller
from wechaty_plugin_contrib.contrib.api_plugin import APIPlugin
from wechaty_plugin_contrib.contrib.ding_dong_plugin import DingDongPlugin
from mcat_bot.plugins.rss import RSSPlugin
from dotenv import load_dotenv


def get_args():
    """get args which only contains port"""
    parser = ArgumentParser()
    parser.add_argument("--port", default=8081, required=False)
    args = parser.parse_args()
    print(args)
    return args
    

async def main():
    args = get_args()
    load_dotenv()
    options = WechatyOptions(
        port=args.port,
    )
    bot = Wechaty(options)
    bot.use([
        APIPlugin(),
        DingDongPlugin(),
        RSSPlugin()
    ])
    message_controller.init_plugins(bot)
    await bot.start()
    

if __name__ == "__main__":
    asyncio.run(main())
