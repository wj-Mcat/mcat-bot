"""base configuration for mcat-bot"""
from datetime import datetime


def _get_version() -> str:
    """load version from VERSION file"""
    with open('./VERSION', 'r', encoding='utf-8') as f:
        return f.read().strip()


version = _get_version()
_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S %f')

login_welcome_words = f'<MCatBot>version: <{version}>\nI"m alive\ntime: <{_now}>'
logout_welcome_words = f'<MCatBot>version: <{version}>\nI"m gonna logout\ntime: <{_now}>'
