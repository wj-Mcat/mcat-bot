from typing import Union
from wechaty import (
    Message,
    Contact,
    Room
)


def conversation_object(message: Message) -> Union[Contact, Room]:
    """get conversation object"""
    room = message.room()
    if room:
        return room
    return message.talker()
