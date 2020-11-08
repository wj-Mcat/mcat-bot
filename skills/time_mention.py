from wechaty import WechatyPlugin, Message, Wechaty
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
import argparse
import jieba
from datetime import datetime, timedelta


class TimeMentionPlugin(WechatyPlugin):
    def __init__(self):
        super(TimeMentionPlugin, self).__init__()
        self.scheduler = AsyncIOScheduler()
        self.parser = argparse.ArgumentParser()

    @property
    def name(self) -> str:
        return 'time-mention-plugin'

    async def init_plugin(self, wechaty: Wechaty):
        """init the timeMention plugin"""
        # 1. start the scheduler
        self.scheduler.start()

        # 2. add argument parser
        self.parser.add_argument('-t', help="mention time", required=True)
        self.parser.add_argument('-c', help="content", required=True)

    async def _time_mention(self, content: str, conversation_id: str):
        """only support personal time task"""
        contact = self.bot.Contact.load(conversation_id)
        await contact.say(content)

    async def on_message(self, msg: Message):
        text = msg.text()
        if text.startswith('time '):
            args = text[6:].split()
            try:
                args = self.parser.parse_args(args)

                # 1. get the time info
                time = args.t
                tokens = jieba.lcut(time)
                assert len(tokens) == 3

                # 2. get the mention content
                content = args.c

                # 3. create task job
                talker = msg.talker()
                now = datetime.now()
                if tokens[1] == '分钟':
                    time_delta = timedelta(minutes=int(tokens[0]))
                elif tokens[1] == "秒":
                    time_delta = timedelta(seconds=int(tokens[0]))
                else:
                    raise ValueError('not support time type')
                run_time = now + time_delta
                self.scheduler.add_job(
                    self._time_mention, args=(content, talker.contact_id), next_run_time=run_time,
                    trigger='date'
                )
            except:
                help_msg = self.parser.format_help()
                await msg.say(help_msg)
                pass