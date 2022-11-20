import os
import tempfile
from wechaty import Wechaty, WechatyOptions
from wechaty_puppet.schemas.puppet import PuppetOptions

from wechaty.fake_puppet import FakePuppet
from mcat_bot.plugins.rss import RSSPlugin
import unittest


class TestRssPlugin(unittest.TestCase):

    def setUp(self) -> None:
        self.bot = Wechaty(
            options=WechatyOptions(
                puppet=FakePuppet(
                    PuppetOptions()
                )
            )
        )
        self.temp_dir = tempfile.TemporaryDirectory()
        os.environ['CACHE_DIR'] = self.temp_dir.name
        self.plugin = RSSPlugin()

    def test_get_message(self):
        
        pass
