from __future__ import annotations
from ctypes import Union
import os
from ssl import HAS_NEVER_CHECK_COMMON_NAME
import feedparser
from typing import Optional, List
from dataclasses import dataclass
from quart import Quart
from wechaty_plugin_contrib.message_controller  import message_controller
from wechaty_plugin_contrib.utils import success
from wechaty_plugin_contrib.matchers import RoomMatcher, ContactMatcher
from wechaty_plugin_contrib.finders.room_finder import RoomFinder
from wechaty_plugin_contrib.finders.contact_finder import ContactFinder
from wechaty import Contact, Room, WechatyPlugin, Message, Wechaty, WechatyPluginOptions, UrlLink
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


@dataclass
class ConvRSSPluginOptions(WechatyPluginOptions):
    job_id: str = "conv_rss_plugins_id"
    feed_urls: List[str] = None
    room_finder: RoomFinder = None
    contact_finder: ContactFinder = None
    max_news: int = 2
    interval_minutes: int = 60

class ConvRSSPlugin(WechatyPlugin):
    """rss plugins which can push rss news into Contact & Rooms

        examples:
            >>> plugin = RSSPlugin()
            >>> plugin.setting['url'] = 'your-own-feed-url'
            >>> plugin.settings['room_ids'] = ["your-room-ids"]
            >>> bot.use(plugin)

    """
    VIEW_URL = '/api/plugvins/rss/view'

    def __init__(self, options: ConvRSSPluginOptions):
        options = options or ConvRSSPluginOptions()
        super().__init__(options)
        self.options: ConvRSSPluginOptions = options
    
    async def init_plugin(self, wechaty: Wechaty) -> None:
        await self.restart_jobs()
    
    async def restart_jobs(self):
        self.add_interval_job(
            minutes=self.options.interval_minutes,
            job_id=self.options.job_id,
            handler=self.fetch_news
        )

    def update_read_record(self, conv_id: str, new_id) -> bool:
        if conv_id not in self.setting:
            self.setting[conv_id] = {}
        have_read = new_id in self.setting[conv_id]
        self.setting[conv_id][new_id] = True
        return have_read
    
    async def on_ready(self, payload) -> None:
        # return await super().on_ready(payload)
        await self.fetch_news()
    
    async def fetch_news(self) -> None:
        """fetch news based on the feed-url and seed to contact/rooms"""
        self.logger.info("start to fetch news ...")
        latest_news: List[FeedNews] = []
        # 1. get latest news
        for feed_url in self.options.feed_urls:
            latest_news.extend(parse(feed_url))
        
        latest_news = latest_news[: self.options.max_news]
        self.logger.info(f"fetch {len(latest_news)} news to be send")
        
        # 3. get rooms
        rooms = await self.options.room_finder.match(self.bot)
        if len(rooms) == 0:
            self.logger.find("find no rooms")
        else:
            for room in rooms:
                self.logger.info(f"find room to send news: {room}")
                
        for room in rooms:
            for feed_news in latest_news:
                have_read = self.update_read_record(room.room_id, feed_news.id)
                if have_read:
                    continue
                await room.say(feed_news.to_url_link())
                self.logger.info(f"send news<{feed_news}> to room<{room}>")
    