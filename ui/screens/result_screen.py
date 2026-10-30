"""
ui/screens/result_screen.py
────────────────────────────
Dedicated full-screen result view. Shown after every successful scan.

Cards (staggered entrance):
  1. Verdict banner  — REAL: breathing glow every 3s  |  FAKE: shake+flash every 3s
  2. Ring gauge      — funny bouncy overshoot animation
  3. Stat rows       — Raw prob / Face detected / Frames / Timestamp

Nav buttons: [Home]  [New File]  [Re-Scan]
"""

import math
from datetime import datetime

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import ListProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse, Rectangle

from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import Snackbar

def _show_snack(message: str):
    bar = Snackbar()
    bar.text = message
    bar.open()

from ui.widgets import ConfidenceRing   # noqa
from ui.theme import ThemeManager as TM

RESULT_KV = """
#:import TM ui.theme.ThemeManager

<ResultScreen>:
    name: 'result'

    canvas.before:
        Color:
            rgba: TM.bg
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'

        # ── Header ───────────────────────────────────
        BoxLayout:
            size_hint_y: None
            height: dp(52)
            padding: [dp(14), dp(8), dp(14), dp(8)]
            spacing: dp(10)
            canvas.before:
                Color:
                    rgba: TM.header_bg
                Rectangle:
                    pos: self.pos
                    size: self.size
                Color:
                    rgba: TM.border
                Rectangle:
                    pos: self.x, self.y
                    size: self.width, dp(1)

            MDIconButton:
                icon: 'home-outline'
                theme_text_color: 'Custom'
                text_color: TM.text_dim
                size_hint: None, None
                size: dp(36), dp(36)
                user_font_size: dp(20)
                pos_hint: {'center_y': 0.5}
                on_release: root.go_home()

            MDLabel:
                text: 'ANALYSIS  RESULT'
                bold: True
                theme_text_color: 'Custom'
                text_color: TM.text
                font_style: 'Button'
                valign: 'middle'

            Widget:

            # Result badge top-right
            BoxLayout:
                id: header_badge
                size_hint_x: None
                width: dp(96)
                padding: [dp(8), dp(6), dp(8), dp(6)]
                canvas.before:
                    Color:
                        rgba: root.result_border_color
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(20)]
                MDLabel:
                    id: lbl_header_badge
                    text: '—'
                    halign: 'center'
                    bold: True
                    theme_text_color: 'Custom'
                    text_color: 0.020, 0.031, 0.051, 1
                    font_style: 'Caption'
                    font_size: dp(10)

        # ── Scrollable body ───────────────────────────
        ScrollView:
            do_scroll_x: False
            bar_width: 0

            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(14), dp(14), dp(14), dp(90)]
                spacing: dp(12)

                # ══════════════════════════════════════
                # CARD 1: Verdict banner
                # ══════════════════════════════════════
                BoxLayout:
                    id: card_verdict
                    size_hint_y: None
                    height: dp(100)
                    opacity: 0
                    padding: [dp(18), dp(14), dp(18), dp(14)]
                    spacing: dp(14)
                    canvas.before:
                        Color:
                            rgba: root.verdict_banner_color
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(20)]
                        Color:
                            rgba: root.result_border_color
                        Line:
                            rounded_rectangle: [self.x+dp(1), self.y+dp(1), self.width-dp(2), self.height-dp(2), dp(20)]
                            width: dp(1.5)

                    # Icon circle
                    BoxLayout:
                        size_hint_x: None
                        width: dp(56)
                        canvas.before:
                            Color:
                                rgba: root.verdict_icon_bg
                            Ellipse:
                                pos: self.x+dp(2), self.center_y-dp(24)
                                size: dp(48), dp(48)
                            Color:
                                rgba: root.result_border_color
                            Line:
                                circle: [self.x+dp(26), self.center_y, dp(24)]
                                width: dp(1.4)
                        MDLabel:
                            id: lbl_verdict_icon
                            text: '?'
                            halign: 'center'
                            bold: True
                            theme_text_color: 'Custom'
                            text_color: root.verdict_color
                            font_style: 'H5'

                    BoxLayout:
                        orientation: 'vertical'
                        spacing: dp(5)
                        MDLabel:
                            text: 'ANALYSIS  COMPLETE'
                            theme_text_color: 'Custom'
                            text_color: root.verdict_dim_color
                            font_style: 'Overline'
                            bold: True
                            size_hint_y: None
                            height: dp(16)
                        MDLabel:
                            id: lbl_verdict
                            text: '—'
                            bold: True
                            theme_text_color: 'Custom'
                            text_color: root.verdict_color
                            font_style: 'H5'
                            size_hint_y: None
                            height: dp(38)
                        MDLabel:
                            id: lbl_verdict_sub
                            text: ''
                            theme_text_color: 'Custom'
                            text_color: root.verdict_dim_color
                            font_style: 'Caption'
                            size_hint_y: None
                            height: dp(14)

                # ══════════════════════════════════════
                # CARD 2: Ring gauge
                # ══════════════════════════════════════
                BoxLayout:
                    id: card_gauge
                    size_hint_y: None
                    height: dp(240)
                    opacity: 0
                    canvas.before:
                        Color:
                            rgba: TM.card
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(20)]
                        Color:
                            rgba: root.result_border_color
                        Line:
                            rounded_rectangle: [self.x+dp(1), self.y+dp(1), self.width-dp(2), self.height-dp(2), dp(20)]
                            width: dp(1)

                    ConfidenceRing:
                        id: conf_ring
                        confidence: 0
                        is_fake: False

                # ══════════════════════════════════════
                # CARD 3: Stat rows + action buttons
                # ══════════════════════════════════════
                BoxLayout:
                    id: card_stats
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(258)
                    opacity: 0
                    padding: [dp(14), dp(12), dp(14), dp(10)]
                    spacing: dp(6)
                    canvas.before:
                        Color:
                            rgba: TM.card
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(20)]
                        Color:
                            rgba: TM.border
                        Line:
                            rounded_rectangle: [self.x+dp(1), self.y+dp(1), self.width-dp(2), self.height-dp(2), dp(20)]
                            width: dp(0.8)

                    # Row 1
                    BoxLayout:
                        size_hint_y: None
                        height: dp(38)
                        padding: [dp(12), 0, dp(12), 0]
                        spacing: dp(10)
                        canvas.before:
                            Color:
                                rgba: TM.surface_row
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [dp(10)]
                            Color:
                                rgba: TM.surface_row_bdr
                            Line:
                                rounded_rectangle: [self.x, self.y, self.width, self.height, dp(10)]
                                width: dp(0.6)
                        MDIconButton:
                            icon: 'chart-bell-curve'
                            theme_text_color: 'Custom'
                            text_color: TM.accent
                            size_hint: None, None
                            size: dp(28), dp(38)
                            user_font_size: dp(14)
                        MDLabel:
                            text: 'Raw Probability'
                            theme_text_color: 'Custom'
                            text_color: TM.text_dim
                            font_style: 'Caption'
                            bold: True
                            valign: 'middle'
                        MDLabel:
                            id: lbl_prob
                            text: '—'
                            theme_text_color: 'Custom'
                            text_color: TM.text
                            font_style: 'Body2'
                            bold: True
                            halign: 'right'
                            valign: 'middle'

                    # Row 2
                    BoxLayout:
                        size_hint_y: None
                        height: dp(38)
                        padding: [dp(12), 0, dp(12), 0]
                        spacing: dp(10)
                        canvas.before:
                            Color:
                                rgba: TM.surface_row
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [dp(10)]
                            Color:
                                rgba: TM.surface_row_bdr
                            Line:
                                rounded_rectangle: [self.x, self.y, self.width, self.height, dp(10)]
                                width: dp(0.6)
                        MDIconButton:
                            icon: 'face-man-outline'
                            theme_text_color: 'Custom'
                            text_color: TM.accent
                            size_hint: None, None
                            size: dp(28), dp(38)
                            user_font_size: dp(14)
                        MDLabel:
                            text: 'Face Detected'
                            theme_text_color: 'Custom'
                            text_color: TM.text_dim
                            font_style: 'Caption'
                            bold: True
                            valign: 'middle'
                        MDLabel:
                            id: lbl_face
                            text: '—'
                            theme_text_color: 'Custom'
                            text_color: TM.text
                            font_style: 'Body2'
                            bold: True
                            halign: 'right'
                            valign: 'middle'

                    # Row 3
                    BoxLayout:
                        size_hint_y: None
                        height: dp(38)
                        padding: [dp(12), 0, dp(12), 0]
                        spacing: dp(10)
                        canvas.before:
                            Color:
                                rgba: TM.surface_row
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [dp(10)]
                            Color:
                                rgba: TM.surface_row_bdr
                            Line:
                                rounded_rectangle: [self.x, self.y, self.width, self.height, dp(10)]
                                width: dp(0.6)
                        MDIconButton:
                            icon: 'filmstrip'
                            theme_text_color: 'Custom'
                            text_color: TM.accent
                            size_hint: None, None
                            size: dp(28), dp(38)
                            user_font_size: dp(14)
                        MDLabel:
                            text: 'Frames Analysed'
                            theme_text_color: 'Custom'
                            text_color: TM.text_dim
                            font_style: 'Caption'
                            bold: True
                            valign: 'middle'
                        MDLabel:
                            id: lbl_frames
                            text: '—'
                            theme_text_color: 'Custom'
                            text_color: TM.text
                            font_style: 'Body2'
                            bold: True
                            halign: 'right'
                            valign: 'middle'

                    # Row 4
                    BoxLayout:
                        size_hint_y: None
                        height: dp(38)
                        padding: [dp(12), 0, dp(12), 0]
                        spacing: dp(10)
                        canvas.before:
                            Color:
                                rgba: TM.surface_row
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [dp(10)]
                            Color:
                                rgba: TM.surface_row_bdr
                            Line:
                                rounded_rectangle: [self.x, self.y, self.width, self.height, dp(10)]
                                width: dp(0.6)
                        MDIconButton:
                            icon: 'clock-outline'
                            theme_text_color: 'Custom'
                            text_color: TM.accent
                            size_hint: None, None
                            size: dp(28), dp(38)
                            user_font_size: dp(14)
                        MDLabel:
                            text: 'Scanned At'
                            theme_text_color: 'Custom'
                            text_color: TM.text_dim
                            font_style: 'Caption'
                            bold: True
                            valign: 'middle'
                        MDLabel:
                            id: lbl_ts
                            text: '—'
                            theme_text_color: 'Custom'
                            text_color: TM.text
                            font_style: 'Body2'
                            bold: True
                            halign: 'right'
                            valign: 'middle'

                    # Spacer
                    BoxLayout:
                        size_hint_y: None
                        height: dp(4)

                    # Action buttons row
                    BoxLayout:
                        size_hint_y: None
                        height: dp(46)
                        spacing: dp(8)

                        # Home
                        BoxLayout:
                            size_hint_x: 0.30
                            spacing: dp(4)
                            padding: [dp(6), dp(0), dp(6), dp(0)]
                            canvas.before:
                                Color:
                                    rgba: TM.surface_row
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [dp(12)]
                                Color:
                                    rgba: TM.border
                                Line:
                                    rounded_rectangle: [self.x, self.y, self.width, self.height, dp(12)]
                                    width: dp(0.8)
                            MDIconButton:
                                icon: 'home-outline'
                                theme_text_color: 'Custom'
                                text_color: TM.text_dim
                                size_hint: None, None
                                size: dp(26), dp(46)
                                user_font_size: dp(16)
                                pos_hint: {'center_y': 0.5}
                                on_release: root.go_home()
                            MDLabel:
                                text: 'Home'
                                theme_text_color: 'Custom'
                                text_color: TM.text_dim
                                font_style: 'Caption'
                                bold: True
                                halign: 'left'
                                valign: 'middle'
                                on_touch_down:
                                    if self.collide_point(*args[1].pos): root.go_home()

                        # New File
                        BoxLayout:
                            size_hint_x: 0.34
                            spacing: dp(4)
                            padding: [dp(6), dp(0), dp(6), dp(0)]
                            canvas.before:
                                Color:
                                    rgba: TM.surface_row
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [dp(12)]
                                Color:
                                    rgba: TM.border
                                Line:
                                    rounded_rectangle: [self.x, self.y, self.width, self.height, dp(12)]
                                    width: dp(0.8)
                            MDIconButton:
                                icon: 'folder-open-outline'
                                theme_text_color: 'Custom'
                                text_color: TM.text_dim
                                size_hint: None, None
                                size: dp(26), dp(46)
                                user_font_size: dp(16)
                                pos_hint: {'center_y': 0.5}
                                on_release: root.new_file()
                            MDLabel:
                                text: 'New File'
                                theme_text_color: 'Custom'
                                text_color: TM.text_dim
                                font_style: 'Caption'
                                bold: True
                                halign: 'left'
                                valign: 'middle'
                                on_touch_down:
                                    if self.collide_point(*args[1].pos): root.new_file()

                        # Re-Scan
                        BoxLayout:
                            size_hint_x: 0.36
                            spacing: dp(4)
                            padding: [dp(6), dp(0), dp(8), dp(0)]
                            canvas.before:
                                Color:
                                    rgba: 0, 0.761, 1, 1
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [dp(12)]
                            MDIconButton:
                                icon: 'refresh'
                                theme_text_color: 'Custom'
                                text_color: 0.020, 0.031, 0.051, 1
                                size_hint: None, None
                                size: dp(26), dp(46)
                                user_font_size: dp(16)
                                pos_hint: {'center_y': 0.5}
                                on_release: root.rescan()
                            MDLabel:
                                text: 'Re-Scan'
                                theme_text_color: 'Custom'
                                text_color: 0.020, 0.031, 0.051, 1
                                font_style: 'Caption'
                                bold: True
                                font_size: dp(13)
                                halign: 'left'
                                valign: 'middle'
                                on_touch_down:
                                    if self.collide_point(*args[1].pos): root.rescan()
"""

Builder.load_string(RESULT_KV)


class ResultScreen(MDScreen):

    verdict_color        = ListProperty([0.30, 0.42, 0.60, 1])
    verdict_dim_color    = ListProperty([0.30, 0.42, 0.60, 0.7])
    verdict_banner_color = ListProperty([0.028, 0.043, 0.068, 1])
    verdict_icon_bg      = ListProperty([0.30, 0.42, 0.60, 0.15])
    result_border_color  = ListProperty([0.10, 0.20, 0.35, 0.5])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._is_fake        = False
        self._confidence     = 0.0
        self._loop_event     = None     # repeating animation event

    # ── Public API ─────────────────────────────────────────────────────────

    def load_result(self, result: dict, media_type: str):
        """
        Called from AnalyzeScreen after detection completes.
        Populates all fields then starts entrance + loop animations.
        """
        # Cancel any previous loop
        self._stop_loop()

        verdict    = result.get('verdict', 'UNKNOWN')
        prob       = result.get('probability', 0.0)
        confidence = result.get('confidence', 0.0)
        self._is_fake    = verdict == 'AI GENERATED'
        self._confidence = confidence

        # Colour scheme
        if self._is_fake:
            vcol = [1.0, 0.231, 0.361, 1];  vdim = [1.0, 0.231, 0.361, 0.65]
            vbg  = [0.16, 0.024, 0.045, 1];  vibg = [1.0, 0.231, 0.361, 0.18]
            rbdr = [1.0, 0.231, 0.361, 0.65]; vicon = 'X'
        else:
            vcol = [0.0, 0.878, 0.612, 1];   vdim = [0.0, 0.878, 0.612, 0.65]
            vbg  = [0.016, 0.115, 0.070, 1]; vibg = [0.0, 0.878, 0.612, 0.18]
            rbdr = [0.0, 0.878, 0.612, 0.65]; vicon = 'OK'

        self.verdict_color        = vcol
        self.verdict_dim_color    = vdim
        self.verdict_banner_color = vbg
        self.verdict_icon_bg      = vibg
        self.result_border_color  = rbdr

        ids = self.ids
        ids.lbl_header_badge.text  = 'FAKE' if self._is_fake else 'REAL'
        ids.lbl_verdict_icon.text  = vicon
        ids.lbl_verdict.text       = verdict
        ids.lbl_verdict_sub.text   = (f"Confidence  {confidence*100:.1f}%  |  "
                                      f"Prob  {prob:.4f}")
        ids.lbl_prob.text    = f"{prob:.4f}"
        ids.lbl_face.text    = 'YES' if result.get('face_detected') else 'NO'
        ids.lbl_frames.text  = str(result.get('frames_analyzed', 1))
        ids.lbl_ts.text      = datetime.now().strftime('%d %b %Y  %H:%M:%S')

        # Reset ring
        ids.conf_ring.is_fake    = self._is_fake
        ids.conf_ring.confidence = 0

        # Reset card visibility
        for cid in ('card_verdict', 'card_gauge', 'card_stats'):
            ids[cid].opacity = 0

    def on_enter(self, *_):
        """Start entrance animations when screen becomes active."""
        if self._is_fake:
            self._entrance_fake()
        else:
            self._entrance_real()

    def on_leave(self, *_):
        self._stop_loop()

    # ── Navigation ─────────────────────────────────────────────────────────

    def go_home(self):
        """Navigate back to analyze screen and do a full reset."""
        self._stop_loop()
        from kivy.app import App
        app = App.get_running_app()
        analyze = app.root.get_screen('analyze')
        analyze.reset_to_home()
        app.root.current = 'analyze'

    def new_file(self):
        """Go to analyze screen and open file chooser directly."""
        self._stop_loop()
        from kivy.app import App
        app = App.get_running_app()
        analyze = app.root.get_screen('analyze')
        analyze.reset_to_home()
        app.root.current = 'analyze'
        Clock.schedule_once(lambda dt: analyze.open_file_chooser(), 0.3)

    def rescan(self):
        """Go back to analyze screen and trigger scan on the same file."""
        self._stop_loop()
        from kivy.app import App
        app = App.get_running_app()
        app.root.current = 'analyze'
        Clock.schedule_once(lambda dt: app.root.get_screen('analyze').start_analysis(), 0.3)

    # ── Entrance animations ─────────────────────────────────────────────────

    def _reveal_card(self, card, duration=0.45, t='out_cubic', callback=None):
        card.opacity = 0
        orig_y = card.y
        card.y = orig_y - dp(32)
        a = Animation(opacity=1, y=orig_y, duration=duration, t=t)
        if callback:
            a.bind(on_complete=lambda *_: callback())
        a.start(card)

    def _entrance_real(self):
        """Smooth green slide-in sequence."""
        ids = self.ids
        # Card 1
        self._reveal_card(ids.card_verdict, 0.5, 'out_cubic')
        # Card 2 after 0.35s → then ring
        Clock.schedule_once(lambda dt: self._reveal_card(
            ids.card_gauge, 0.45, 'out_cubic',
            callback=self._start_gauge_bounce), 0.35)
        # Card 3 after 0.7s
        Clock.schedule_once(lambda dt: self._reveal_card(
            ids.card_stats, 0.45, 'out_cubic'), 0.70)
        # Start continuous loop after 1.2s
        Clock.schedule_once(lambda dt: self._start_loop(), 1.2)

    def _entrance_fake(self):
        """Hard flash + shake entrance."""
        ids = self.ids
        # Card 1 instant flash
        ids.card_verdict.opacity = 0
        Animation(opacity=1, duration=0.18).start(ids.card_verdict)
        Clock.schedule_once(lambda dt: self._shake(ids.card_verdict), 0.2)
        self._pulse_border(4)

        # Card 2
        Clock.schedule_once(lambda dt: self._reveal_card(
            ids.card_gauge, 0.38, 'out_expo',
            callback=self._start_gauge_bounce), 0.45)
        # Card 3
        Clock.schedule_once(lambda dt: self._reveal_card(
            ids.card_stats, 0.38, 'out_cubic'), 0.75)
        # Start continuous loop after 1.0s
        Clock.schedule_once(lambda dt: self._start_loop(), 1.0)

    # ── Continuous loop animations ──────────────────────────────────────────

    def _start_loop(self):
        """Start the repeating 3-second animation loop."""
        if self._is_fake:
            self._loop_event = Clock.schedule_interval(
                lambda dt: self._loop_fake_tick(), 3.0)
        else:
            self._loop_event = Clock.schedule_interval(
                lambda dt: self._loop_real_tick(), 3.0)

    def _stop_loop(self):
        if self._loop_event:
            self._loop_event.cancel()
            self._loop_event = None
        Animation.cancel_all(self)

    def _loop_real_tick(self):
        """REAL: soft breathing glow pulse on the verdict banner border."""
        orig = list(self.result_border_color)
        bright = [0.0, 1.0, 0.72, 1.0]
        a = (Animation(result_border_color=bright, duration=0.4, t='in_out_sine') +
             Animation(result_border_color=orig,   duration=0.55, t='in_out_sine'))
        a.start(self)
        # Also do a gentle scale breathe on card_verdict via opacity pulse
        ids = self.ids
        ba = (Animation(opacity=0.75, duration=0.35, t='in_out_sine') +
              Animation(opacity=1.0,  duration=0.45, t='in_out_sine'))
        ba.start(ids.card_verdict)

    def _loop_fake_tick(self):
        """FAKE: rapid shake + red flash every 3 seconds."""
        self._shake(self.ids.card_verdict)
        self._pulse_border(3)

    # ── Gauge bounce (funny) ────────────────────────────────────────────────

    def _start_gauge_bounce(self):
        """
        Funny bouncy fill:
          - Overshoots to 110% of target → snaps back to exact value
          - Then does a little 3-step jiggle
          - Card does a tiny vertical bounce
        """
        ids    = self.ids
        target = self._confidence

        # Step 1: animate to overshoot (min 1.0 = full circle, max target+0.12)
        overshoot = min(1.0, target + 0.14)
        ids.conf_ring.confidence = 0

        a1 = Animation(confidence=overshoot, duration=0.7, t='out_cubic')

        def _step2(*_):
            # Step 2: snap back hard
            a2 = Animation(confidence=target * 0.88, duration=0.18, t='in_cubic')
            def _step3(*_):
                # Step 3: final settle with tiny overshoot
                a3 = (Animation(confidence=min(1.0, target + 0.05), duration=0.14) +
                      Animation(confidence=target,                    duration=0.20,
                                t='out_cubic'))
                a3.start(ids.conf_ring)
            a2.bind(on_complete=_step3)
            a2.start(ids.conf_ring)

        a1.bind(on_complete=_step2)
        a1.start(ids.conf_ring)

        # Card vertical bounce — 3 tiny hops
        orig_y = ids.card_gauge.y
        bounce = (
            Animation(y=orig_y + dp(6), duration=0.14, t='out_cubic') +
            Animation(y=orig_y - dp(3), duration=0.10, t='in_cubic') +
            Animation(y=orig_y + dp(2), duration=0.09) +
            Animation(y=orig_y,         duration=0.09)
        )
        Clock.schedule_once(lambda dt: bounce.start(ids.card_gauge), 0.65)

    # ── Shake + pulse helpers ───────────────────────────────────────────────

    def _shake(self, widget):
        orig_x = widget.x
        (Animation(x=orig_x + dp(9), duration=0.055) +
         Animation(x=orig_x - dp(9), duration=0.055) +
         Animation(x=orig_x + dp(6), duration=0.055) +
         Animation(x=orig_x - dp(6), duration=0.055) +
         Animation(x=orig_x + dp(3), duration=0.055) +
         Animation(x=orig_x,         duration=0.055)).start(widget)

    def _pulse_border(self, count=3):
        if count <= 0:
            return
        orig   = list(self.result_border_color)
        bright = [1.0, 0.5, 0.6, 1.0]
        a = (Animation(result_border_color=bright, duration=0.10) +
             Animation(result_border_color=orig,   duration=0.10))
        a.bind(on_complete=lambda *_: self._pulse_border(count - 1))
        a.start(self)
