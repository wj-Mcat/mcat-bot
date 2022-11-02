from __future__ import annotations
import os
import feedparser
from typing import Optional, List
from dataclasses import dataclass
from quart import Quart
from wechaty_plugin_contrib.message_controller  import message_controller
from wechaty_plugin_contrib.utils import success
from wechaty import WechatyPlugin, Message, Wechaty, WechatyPluginOptions, UrlLink
from wechaty.user.url_link import UrlLinkPayload
from wechaty import WechatyPlugin


def is_room(conv_id: str) -> bool:
    return conv_id.endswith("@chatroom")


@dataclass
class FeedNews:
    """FeedNews instance"""
    id: str
    title: str
    url: str
    description: str

    def to_url_link(self) -> UrlLink:
        """transform url-link instance"""
        # thumbnailUrl: Optional[str] = None
        return UrlLink(
            payload=UrlLinkPayload(
                url=self.url,
                title=self.title,
                description=self.description,
            )
        )


def parse(url) -> List[FeedNews]:
    result = feedparser.parse(url)
    news = []
    for entry in result.get("entries", []):
        news.append(FeedNews(
            id=entry['id'],
            url=entry['link'],
            title=entry['title'],
            description=entry['summary']
        ))
    return news


class RSSPlugin(WechatyPlugin):
    """rss plugins which can push rss news into Contact & Rooms

        examples:
            >>> plugin = RSSPlugin()
            >>> plugin.setting['url'] = 'your-own-feed-url'
            >>> plugin.settings['room_ids'] = ["your-room-ids"]
            >>> bot.use(plugin)

    """
    VIEW_URL = '/api/plugvins/rss/view'

    def __init__(self, options: Optional[WechatyPluginOptions] = None):
        """_summary_

        Args:
            options (Optional[WechatyPluginOptions], optional): _description_. Defaults to None.
        """
        super().__init__(options)
        self._init_default_setting()
        self.rss_job_id = "rss_plugin_job"
        self.fetch_feed_command = "bot rss"
    
    def _init_default_setting(self):
        """init default setting for setting"""
        default_setting = {
            # 每天早上九点钟推送消息
            "feeds": [
                "https://www.ruanyifeng.com/blog/atom.xml",
                "https://openai.com/blog/rss/"
            ],
            "read": {},
            "max_news": 5
        }
        default_setting.update(self.setting)
        self.setting = default_setting
    
    async def blueprint(self, app: Quart) -> None:

        @app.route(self.VIEW_URL)
        async def rss_view():
            basedir = os.path.dirname(__file__)
            with open(os.path.join(basedir, 'rss.html'), 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        
        @app.route(self.VIEW_URL + "/restart", methods=['GET'])
        async def restart_rss_jobs():
            await self.restart_jobs()
            return success("ok")
    
    async def restart_jobs(self):
        skip_fields = ['feeds', 'read', 'max_news']
        setting = self.setting.read_setting()
        for key, sub_setting in setting.items():
            if key in skip_fields or not isinstance(sub_setting, dict):
                continue
            
            self.add_daily_job(
                hour=sub_setting.get("hour", 9),
                handler=self.fetch_news,
                job_id=key,
                args=(key, )
            )
            
    async def push_news(self, new: FeedNews, conv_id: str) -> None:
        """push feed news to contact/rooms"""
        if is_room(conv_id):
            room = self.bot.Room.load(conv_id)
            await room.say(new.to_url_link())
        else:
            contact = self.bot.Contact.load(conv_id)  
            await contact.say(new.to_url_link())
    
    async def fetch_news(self, conv_id: str) -> None:
        """fetch news based on the feed-url and seed to contact/rooms"""
        setting = self.setting.read_setting()
        feed_urls = setting[conv_id].get("feeds")
        if isinstance(feed_urls, str):
            feed_urls = [feed_urls]
        
        for feed_url in feed_urls:
            news:List[FeedNews] = parse(feed_url)
            for new in news:
                if new.id in setting['read']:
                    continue

                setting["read"][new.id] = True
                await self.push_news(new, conv_id)
        self.setting = setting
    
    @message_controller.may_disable_message
    async def on_message(self, msg: Message) -> None:
        """if get fetch-news command, it will send message to different bot
        """
        text = msg.text()
        if text == self.fetch_feed_command:
            if msg.room():
                conv_id = msg.room().room_id
            else:
                conv_id = msg.talker().contact_id
            
            if conv_id in self.setting and self.setting[conv_id].get("feeds", []):
                await self.fetch_news(conv_id)

            message_controller.disable_all_plugins(msg)
