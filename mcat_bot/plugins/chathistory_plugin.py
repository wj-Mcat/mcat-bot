"""Chat history plugin"""
import os
from typing import Optional, List, Any
from dataclasses import dataclass, field, asdict
from quart import Quart
from wechaty_puppet import MessageType, FileBox
from wechaty import Wechaty, Message, get_logger, Room, Contact, UrlLink
from wechaty.plugin import WechatyPlugin, WechatyPluginOptions
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import (
    Column,
    Integer,
    VARCHAR,
    Text,
    Boolean
)

logger = get_logger('ChatHistoryPlugin')

SUPPORTED_MESSAGE_FILE_TYPES: List[MessageType] = [
    MessageType.MESSAGE_TYPE_ATTACHMENT,
    MessageType.MESSAGE_TYPE_IMAGE,
    MessageType.MESSAGE_TYPE_EMOTICON,
    MessageType.MESSAGE_TYPE_VIDEO,
    MessageType.MESSAGE_TYPE_AUDIO
]

Base: Any = declarative_base()


class RoomInfo(Base):
    __tablename__ = 'Room'
    room_id = Column(Text, primary_key=True)
    payload = Column(Text)

class RoomMessage(Base):
    __tablename__ = 'RoomMessage'
    msg_id = Column(Integer, primary_key=True, autoincrement=True)
    payload = Column(Text, default=None)
    mention_self = Column(Boolean, default=False)
    msg_type = Column(Integer, default=None)
    msg_type_string = Column(Text, default=None)

class ContactInfo(Base):
    __tablename__ = 'ContactInfo'
    contact_id = Column(Text, primary_key=True)
    payload = Column(Text)

class ContactMessage(Base):
    __tablename__ = 'ContactMessage'
    msg_id = Column(Integer, primary_key=True, autoincrement=True)
    payload = Column(Text, default=None)
    msg_type = Column(Integer, default=None)
    msg_type_string = Column(Text, default=None)


@dataclass
class ChatHistoryPluginOptions(WechatyPluginOptions):
    """
    chat history plugin options
    """
    chat_history_path: str = field(default_factory=str)
    chat_history_database: str = field(default_factory=str)


class ChatHistoryPlugin(WechatyPlugin):
    """chat history plugin"""
    VIEW_URL = 'plugins/chathistory'

    def __init__(self, options: Optional[ChatHistoryPluginOptions] = None):
        options = options or ChatHistoryPluginOptions()

        super().__init__(options)
        
        self.chat_history_path = self.cache_dir
        self.chat_history_database = options.chat_history_database or os.path.join(self.cache_dir, 'sqlite+aiosqlite:///chathistory.db')

    async def init_plugin(self, wechaty: Wechaty) -> None:
        """init plugin"""
        async_engine: AsyncEngine = create_async_engine(self.chat_history_database)
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
    async def get_msg_payload(self, msg: Message):
        if msg.type() in SUPPORTED_MESSAGE_FILE_TYPES:
            file_box: FileBox = await msg.to_file_box()
            
            if msg.room():
                cache_dir = os.path.join(self.cache_dir, "room")
            else:
                cache_dir = os.path.join(self.cache_dir, "contact")
            
            cache_file = os.path.join(cache_dir, file_box.name)
            file_box.to_file(
                cache_file 
            )

            payload = cache_file
        
        elif msg.type() == MessageType.MESSAGE_TYPE_URL:
            url_link: UrlLink = await msg.to_url_link()
            payload = str(asdict(url_link.payload))
        
        elif msg.type() == MessageType.MESSAGE_TYPE_TEXT:
            payload = msg.text()
        
        else:
            self.logger.warning("can not saved message type")
            self.logger.warning(msg)
        
        return payload


    async def on_message(self, msg: Message) -> None:
        """listen message event"""
        async_engine = create_async_engine(self.chat_history_database)
        async_session = sessionmaker(async_engine,
                                     expire_on_commit=False,
                                     class_=AsyncSession)

        async with async_session() as session:
            async with session.begin():
                
                # 1. save room message
                msg_type = msg.type().value
                msg_type_string = str(msg.type())
                payload = await self.get_msg_payload(msg)

                if msg.room():
                    room: Room = msg.room()
                    await room.ready()
                    mention_self = await msg.mention_self()
                    
                    session.add(
                        RoomMessage(
                            msg_id=msg.message_id,
                            mention_self=mention_self,
                            payload=payload,
                            msg_type=msg_type,
                            msg_type_string=msg_type_string,
                        )
                    )
                else:
                    session.add(
                        ContactMessage(
                            msg_id=msg.message_id,
                            payload=payload,
                            msg_type=msg_type,
                            msg_type_string=msg_type_string,
                        )
                    )
                    
            await session.commit()
        await async_engine.dispose()
