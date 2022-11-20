import pytest

from asyncio import Event
from wechaty import Wechaty, WechatyOptions, Message
from wechaty.fake_puppet import FakePuppet 
from mcat_bot.plugins.chathistory_plugin import ChatHistoryPlugin


@pytest.mark.asyncio
async def test_message_add(fake_puppet: FakePuppet):
    bot = Wechaty(
        options=WechatyOptions(
            puppet=fake_puppet
        )
    )

    message_event = Event()

    async def on_message(self, msg: Message):
        message_event.set()

    bot.on_message = on_message
    
    fake_puppet
    fake_puppet.emit("message", )

    