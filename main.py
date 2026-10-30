"""
VERIDECT — AI Media Authentication
Entry point. Run this file to launch the application.
"""

import os
import logging

os.environ.setdefault('KIVY_NO_ENV_CONFIG', '1')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['KIVY_LOG_LEVEL'] = 'warning'

logging.basicConfig(level=logging.WARNING)
logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('kivy').setLevel(logging.WARNING)

from kivy.config import Config

# ── Mobile portrait window ────────────────────────────────────────────────────
Config.set('graphics', 'width',          '420')
Config.set('graphics', 'height',         '820')
Config.set('graphics', 'minimum_width',  '360')
Config.set('graphics', 'minimum_height', '640')
Config.set('graphics', 'resizable',      '1')
Config.set('input', 'mouse', 'mouse,disable_multitouch')

from ui.app import VeriDectApp

if __name__ == '__main__':
    VeriDectApp().run()
