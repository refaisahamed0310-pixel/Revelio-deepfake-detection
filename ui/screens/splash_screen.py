from kivy.lang import Builder
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse
from kivy.uix.widget import Widget
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel

SPLASH_KV = """
<SplashScreen>:
    name: 'splash'

    canvas.before:
        Color:
            rgba: 0.020, 0.031, 0.051, 1
        Rectangle:
            pos: self.pos
            size: self.size

    #Centre column
    BoxLayout:
        orientation: 'vertical'
        padding: [dp(40), dp(0)]
        spacing: dp(0)

        Widget:
            size_hint_y: 0.28

        # Logo box
        FloatLayout:
            size_hint_y: None
            height: dp(110)
            id: logo_area

            # Outer glow ring 
            SplashRing:
                id: splash_ring
                size: dp(110), dp(110)
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                opacity: 0

            # Logo square + letter
            BoxLayout:
                id: logo_box
                size_hint: None, None
                size: dp(72), dp(72)
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                opacity: 0
                canvas.before:
                    Color:
                        rgba: 0, 0.761, 1, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(18)]

                MDLabel:
                    text: 'R'
                    bold: True
                    theme_text_color: 'Custom'
                    text_color: 0.020, 0.031, 0.051, 1
                    halign: 'center'
                    font_style: 'H4'

        Widget:
            size_hint_y: None
            height: dp(28)

        # App name
        MDLabel:
            id: lbl_name
            text: 'REVELIO'
            halign: 'center'
            bold: True
            theme_text_color: 'Custom'
            text_color: 0.88, 0.93, 1.0, 1
            font_style: 'H4'
            size_hint_y: None
            height: dp(48)
            opacity: 0

        # Subtitle
        MDLabel:
            id: lbl_sub
            text: 'AI  MEDIA  AUTHENTICATION'
            halign: 'center'
            theme_text_color: 'Custom'
            text_color: 0, 0.761, 1, 0.85
            font_style: 'Caption'
            size_hint_y: None
            height: dp(22)
            opacity: 0

        Widget:
            size_hint_y: None
            height: dp(48)

        # Initializing label
        MDLabel:
            id: lbl_init
            text: '●  INITIALIZING SYSTEM'
            halign: 'center'
            theme_text_color: 'Custom'
            text_color: 0.30, 0.42, 0.60, 1
            font_style: 'Caption'
            bold: True
            size_hint_y: None
            height: dp(24)
            opacity: 0

        Widget:
            size_hint_y: 0.30

        # Version footer
        MDLabel:
            text: 'v1.0  ·  DEEPFAKE FORENSICS ENGINE'
            halign: 'center'
            theme_text_color: 'Custom'
            text_color: 0.14, 0.22, 0.36, 1
            font_style: 'Caption'
            size_hint_y: None
            height: dp(28)

        Widget:
            size_hint_y: None
            height: dp(20)
"""

Builder.load_string(SPLASH_KV)


class SplashRing(Widget):
    _sweep = NumericProperty(0.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(_sweep=self._redraw, pos=self._redraw, size=self._redraw)

    def animate(self):
        self._sweep = 0
        Animation(_sweep=360, duration=0.9, t='out_cubic').start(self)

    def _redraw(self, *_):
        self.canvas.clear()
        import math
        cx, cy = self.center_x, self.center_y
        r      = min(self.width, self.height) * 0.46
        stroke = dp(2)

        with self.canvas:
            # Track
            Color(0.08, 0.14, 0.24, 0.5)
            Line(circle=(cx, cy, r), width=stroke)

            # Animated arc
            if self._sweep > 1:
                Color(0.0, 0.761, 1.0, 0.85)
                end_a = 90 - self._sweep
                Line(circle=(cx, cy, r, end_a, 90), width=stroke, cap='round')

            # Small dots at 90° intervals
            for deg in (0, 90, 180, 270):
                rad = math.radians(deg)
                dx = cx + r * math.cos(rad)
                dy = cy + r * math.sin(rad)
                Color(0.0, 0.761, 1.0, 0.4)
                Ellipse(pos=(dx - dp(2), dy - dp(2)), size=(dp(4), dp(4)))


class SplashScreen(MDScreen):

    def on_enter(self, *_):
        Clock.schedule_once(self._run_sequence, 0.1)

    def _run_sequence(self, _dt):
        ids = self.ids

        # Step 1 – logo box fades + scales in
        ids.logo_box.opacity = 0
        a1 = Animation(opacity=1, duration=0.5, t='out_cubic')
        Clock.schedule_once(lambda dt: a1.start(ids.logo_box), 0.2)

        # Step 2 – ring appears and draws
        Clock.schedule_once(lambda dt: self._show_ring(), 0.5)

        # Step 3 – app name slides up
        ids.lbl_name.opacity = 0
        ids.lbl_name.y = ids.lbl_name.y - dp(18)
        Clock.schedule_once(
            lambda dt: Animation(opacity=1, y=ids.lbl_name.y + dp(18),
                                 duration=0.45, t='out_cubic').start(ids.lbl_name),
            1.0,
        )

        # Step 4 – subtitle
        Clock.schedule_once(
            lambda dt: Animation(opacity=1, duration=0.4).start(ids.lbl_sub),
            1.45,
        )

        # Step 5 – initializing text
        Clock.schedule_once(
            lambda dt: Animation(opacity=1, duration=0.4).start(ids.lbl_init),
            1.85,
        )

        # Step 6 – blink initializing then exit
        Clock.schedule_once(self._blink_and_exit, 2.5)

    def _show_ring(self):
        ids = self.ids
        ids.splash_ring.opacity = 1
        ids.splash_ring.animate()

    def _blink_and_exit(self, _dt):
        ids = self.ids
        # Quick blink
        a = (Animation(opacity=0.2, duration=0.15) +
             Animation(opacity=1.0, duration=0.15) +
             Animation(opacity=0.2, duration=0.15) +
             Animation(opacity=1.0, duration=0.15))
        a.bind(on_complete=lambda *_: self._exit())
        a.start(ids.lbl_init)

    def _exit(self):
        # Fade entire screen to black then switch
        a = Animation(opacity=0, duration=0.4)
        a.bind(on_complete=lambda *_: self._go_to_app())
        a.start(self)

    def _go_to_app(self):
        from kivy.app import App
        App.get_running_app().show_analyze()
