"""ui/app.py — v7"""
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivymd.app import MDApp
from ui.theme import ThemeManager as TM
from ui.screens.splash_screen  import SplashScreen   # noqa
from ui.screens.analyze_screen import AnalyzeScreen  # noqa
from ui.screens.history_screen import HistoryScreen  # noqa
from ui.screens.result_screen  import ResultScreen   # noqa


class VeriDectApp(MDApp):

    def build(self):
        self.theme_cls.theme_style     = 'Dark'
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.accent_palette  = 'Cyan'
        self.title = 'VERIDECT  ·  AI Media Authentication'
        sm = ScreenManager(transition=FadeTransition(duration=0.22))
        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(AnalyzeScreen(name='analyze'))
        sm.add_widget(ResultScreen(name='result'))
        sm.add_widget(HistoryScreen(name='history'))
        sm.current = 'splash'
        return sm

    def show_analyze(self):
        self.root.current = 'analyze'

    def show_history(self):
        self.root.current = 'history'

    def toggle_theme(self):
        TM.toggle()
        self.theme_cls.theme_style = 'Light' if not TM.is_dark else 'Dark'
