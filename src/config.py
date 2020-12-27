"""base configuration for mcat-bot"""
from datetime import datetime


def _get_version() -> str:
    """load version from VERSION file"""
    with open('./VERSION', 'r', encoding='utf-8') as f:
        return f.read().strip()


version = _get_version()
_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

login_welcome_words = f'[Mcat-Bot]\nversion: <{version}>\ntime: <{_now}>\nI"m alive'
logout_welcome_words = f'[Mcat-Bot]\nversion: <{version}>\ntime: <{_now}>\nI"m gonna logout'
