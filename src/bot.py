"""doc"""
# pylint: disable=R0801
import asyncio
import logging
import os
from typing import Optional, Union

from wechaty_puppet import ContactQueryFilter, EventErrorPayload  # type: ignore
from wechaty_plugin_contrib import (
    DingDongPlugin
)

from wechaty import Wechaty, Contact, Friendship
from wechaty.user import Message, Room

from src.config import login_welcome_words, logout_welcome_words
from src.skills.time_mention import TimeMentionPlugin
from src.skills.gpt_chitchat import GptChitChatPlugin
from src.utils import conversation_object

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class MyBot(Wechaty):
    """
    listen wechaty event with inherited functions, which is more friendly for
    oop developer
    """
    def __init__(self):
        super().__init__()

        # lazy load cat account
        self._message_center: Optional[Union[Contact, Room]] = None

    @property
    def message_center(self) -> Union[Contact, Room]:
        """lazy mode: load cat contact"""
        if not self._message_center:
            raise ValueError('can"t get cat attribute before it has been initialized.')
        return self._message_center

    async def on_message(self, msg: Message):
        """
        listen for message event
        """
        pass

    async def on_login(self, contact: Contact):
        """login event which is important for user to test bot"""
        log.info(f'contact<{contact}> has login')

        # 1. load cat account
        contact = await self.Contact.find(ContactQueryFilter(weixin='pure-_--love'))
        if not contact:
            raise ValueError('contact<pure-_--love> not found')
        self._message_center = contact
        await self.message_center.say(login_welcome_words)

    async def on_friendship(self, friendship: Friendship):
        """accept friends"""
        log.info(f'receive friendship<{friendship}>')
        await friendship.accept()

        # tell the message center that I have received on friendship
        friendship_message = str(friendship)
        await self.message_center.say(friendship_message)

    async def on_error(self, payload: EventErrorPayload):
        """send error message to message center"""
        await self._message_center.say('Mcat-bot has Occured an error')
        await self._message_center.say(str(payload))

    async def on_logout(self, contact: Contact):
        """logout event which is dangerous for user to test bot"""

        # 1. tell the message center: I will logout
        await self.message_center.say(logout_welcome_words)


bot: Optional[MyBot] = None


def validate_env():
    token = os.environ['WECHATY_PUPPET_HOSTIE_TOKEN']
    log.info(f"receive the token: <{token}>")
    if 'rock' not in token:
        os.environ['WECHATY_PUPPET_HOSTIE_ENDPOINT'] = ''
    else:
        endpoint = os.environ['WECHATY_PUPPET_HOSTIE_ENDPOINT']
        log.info(f"receive the endpoint: <{endpoint}>")



