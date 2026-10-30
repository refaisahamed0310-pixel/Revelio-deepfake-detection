"""
ui/widgets.py — v6
──────────────────
  LogoBox         Fixed logo square with centred V label
  TitleWave       App title with shimmer/wave colour animation
  ConfidenceRing  360° animated ring gauge
  ScanOverlay     Full-screen scan animation
"""

import math
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import NumericProperty, BooleanProperty, ListProperty
from kivy.graphics import (
    Color, Line, Ellipse, Rectangle, RoundedRectangle,
)
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.animation import Animation

C_ACCENT = (0.0, 0.761, 1.0)
C_REAL   = (0.0, 0.878, 0.612)
C_FAKE   = (1.0, 0.231, 0.361)
C_DIM    = (0.30, 0.42, 0.60)
C_TRACK  = (0.07, 0.13, 0.21)
C_BG     = (0.020, 0.031, 0.051)


# ─────────────────────────────────────────────────────────────────────────────
# LogoBox  — fixed cyan square with V centred inside
# ─────────────────────────────────────────────────────────────────────────────

class LogoBox(BoxLayout):
    """
    Draws a cyan rounded square on canvas.before.
    The single child Label shows 'V' on top of it.
    Use size_hint=None,None and fixed size dp(38),dp(38).
    """
    _glow = NumericProperty(0.3)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._draw, size=self._draw, _glow=self._draw)
        self._pulse()

    def _pulse(self, *_):
        a = (Animation(_glow=0.7, duration=1.0, t='in_out_sine') +
             Animation(_glow=0.2, duration=1.0, t='in_out_sine'))
        a.bind(on_complete=self._pulse)
        a.start(self)

    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            # glow halo
            Color(*C_ACCENT, self._glow * 0.3)
            Ellipse(pos=(self.x - dp(6), self.y - dp(6)),
                    size=(self.width + dp(12), self.height + dp(12)))
            # logo square
            Color(*C_ACCENT, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(9)])


# ─────────────────────────────────────────────────────────────────────────────
# TitleWave  — app title with wave shimmer animation
# ─────────────────────────────────────────────────────────────────────────────

class TitleWave(BoxLayout):

    title_text = 'REVELIO'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spacing   = dp(1)
        self._labels   = []
        self._phase    = 0.0
        self._tick_ev  = None
        Clock.schedule_once(self._build, 0)

    def _build(self, _dt):
        from ui.theme import ThemeManager as TM
        self.clear_widgets()
        self._labels = []
        r, g, b = TM.text[:3]
        for ch in self.title_text:
            lbl = Label(
                text=ch,
                font_size=dp(18),
                bold=True,
                color=(r, g, b, 1),
                size_hint=(None, 1),
                width=dp(14) if ch != ' ' else dp(6),
                halign='center',
                valign='middle',
            )
            self._labels.append(lbl)
            self.add_widget(lbl)
        # Rebuild labels when theme changes
        from ui.theme import ThemeManager as TM2
        TM2.bind(is_dark=self._on_theme)
        self._start_wave()

    def _on_theme(self, *_):
        """Rebuild when theme toggles so letter base colour updates."""
        Clock.schedule_once(self._build, 0)

    def _start_wave(self):
        if self._tick_ev:
            self._tick_ev.cancel()
        self._tick_ev = Clock.schedule_interval(self._wave_tick, 1 / 30)

    def _wave_tick(self, dt):
        from ui.theme import ThemeManager as TM
        self._phase += dt * 2.2
        r, g, b = TM.text[:3]
        for i, lbl in enumerate(self._labels):
            v = 0.55 + 0.45 * math.sin(self._phase + i * 0.72)
            lbl.color = (r, g, b, v)


# ─────────────────────────────────────────────────────────────────────────────
# ConfidenceRing
# ─────────────────────────────────────────────────────────────────────────────

class ConfidenceRing(Widget):
    confidence = NumericProperty(0.0)
    is_fake    = BooleanProperty(False)
    _draw_val  = NumericProperty(0.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(
            confidence=self._animate, is_fake=self._redraw,
            size=self._redraw, pos=self._redraw, _draw_val=self._redraw,
        )

    def _animate(self, *_):
        Animation.cancel_all(self, '_draw_val')
        Animation(_draw_val=self.confidence, duration=1.2, t='out_cubic').start(self)

    def reset(self):
        Animation.cancel_all(self, '_draw_val')
        self._draw_val = 0.0

    def _redraw(self, *_):
        self.canvas.clear()
        self._draw()

    def _draw(self):
        mg   = dp(14)
        side = min(self.width, self.height) - mg * 2
        cx, cy = self.center_x, self.center_y
        r    = side * 0.37
        sw   = max(side * 0.082, dp(10))
        col  = C_FAKE if self.is_fake else C_REAL

        with self.canvas:
            # halos
            Color(*col, 0.055)
            h1 = r + sw * 2.0
            Ellipse(pos=(cx - h1, cy - h1), size=(h1 * 2, h1 * 2))
            Color(*col, 0.025)
            h2 = r + sw * 3.8
            Ellipse(pos=(cx - h2, cy - h2), size=(h2 * 2, h2 * 2))

            # track
            Color(*C_TRACK, 1)
            Line(circle=(cx, cy, r), width=sw, cap='none')

            # tick marks
            for deg in (0, 90, 180, 270):
                rad = math.radians(deg)
                ox = cx + (r + sw * 0.35) * math.cos(rad)
                oy = cy + (r + sw * 0.35) * math.sin(rad)
                ix = cx + (r - sw * 0.35) * math.cos(rad)
                iy = cy + (r - sw * 0.35) * math.sin(rad)
                Color(*C_DIM, 0.45)
                Line(points=[ix, iy, ox, oy], width=dp(1))

            # arc
            if self._draw_val > 0.005:
                sweep     = self._draw_val * 360
                angle_end = 90 - sweep
                Color(*col, 1)
                Line(circle=(cx, cy, r, angle_end, 90), width=sw, cap='round')

                # tip dot
                tr = math.radians(angle_end)
                tx, ty = cx + r * math.cos(tr), cy + r * math.sin(tr)
                dr = sw * 0.78
                Color(*col, 0.9)
                Ellipse(pos=(tx - dr, ty - dr), size=(dr * 2, dr * 2))
                Color(*col, 0.28)
                Ellipse(pos=(tx - dr * 2.1, ty - dr * 2.1),
                        size=(dr * 4.2, dr * 4.2))
                # top start cap
                Color(*col, 0.45)
                sc = sw * 0.38
                Ellipse(pos=(cx - sc, cy + r - sc), size=(sc * 2, sc * 2))

        self._update_labels(col)

    def _update_labels(self, col):
        if not hasattr(self, '_lbl_pct'):
            self._lbl_pct = Label(bold=True, halign='center', valign='middle',
                                  font_size=dp(36))
            self._lbl_sub = Label(halign='center', valign='middle',
                                  font_size=dp(10), color=(*C_DIM, 1))
            self._lbl_tag = Label(halign='center', valign='middle',
                                  font_size=dp(10.5), bold=True)
            self.add_widget(self._lbl_pct)
            self.add_widget(self._lbl_sub)
            self.add_widget(self._lbl_tag)
            self.bind(pos=self._pos_labels, size=self._pos_labels)

        self._lbl_pct.text  = f"{self._draw_val * 100:.1f}%"
        self._lbl_pct.color = (*col, 1)
        if self.is_fake:
            self._lbl_sub.text  = "PROBABILITY"
            self._lbl_tag.text  = "AI  GENERATED"
            self._lbl_tag.color = (*C_FAKE, 1)
        else:
            self._lbl_sub.text  = "CONFIDENCE"
            self._lbl_tag.text  = "AUTHENTIC"
            self._lbl_tag.color = (*C_REAL, 1)
        self._pos_labels()

    def _pos_labels(self, *_):
        if not hasattr(self, '_lbl_pct'):
            return
        cx, cy, w = self.center_x, self.center_y, self.width
        self._lbl_pct.center_x = cx; self._lbl_pct.center_y = cy + dp(12)
        self._lbl_pct.size     = (w * 0.72, dp(50))
        self._lbl_sub.center_x = cx; self._lbl_sub.center_y = cy - dp(16)
        self._lbl_sub.size     = (w * 0.85, dp(20))
        self._lbl_tag.center_x = cx; self._lbl_tag.center_y = cy - dp(32)
        self._lbl_tag.size     = (w * 0.85, dp(20))


# ─────────────────────────────────────────────────────────────────────────────
# ScanOverlay
# ─────────────────────────────────────────────────────────────────────────────

class ScanOverlay(FloatLayout):
    _ring_angle  = NumericProperty(0.0)
    _ring2_angle = NumericProperty(0.0)
    _scan_y      = NumericProperty(0.5)
    _pulse_a     = NumericProperty(0.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opacity = 0
        self._active = False
        self._lbl = Label(text='Analysing...', font_size=dp(14), bold=True,
                          color=(*C_ACCENT, 1), halign='center', valign='middle')
        self._sub = Label(text='Please wait', font_size=dp(11),
                          color=(*C_DIM, 1), halign='center', valign='middle')
        self.add_widget(self._lbl)
        self.add_widget(self._sub)
        self.bind(
            _ring_angle=self._redraw, _ring2_angle=self._redraw,
            _scan_y=self._redraw, _pulse_a=self._redraw,
        )
        self.bind(pos=self._on_ps, size=self._on_ps)

    def _on_ps(self, *_):
        self._redraw()
        self._pos_labels()

    def show(self, status='Analysing...'):
        self._active = True
        self._lbl.text = status
        self._sub.text = 'Please wait...'
        Animation(opacity=1, duration=0.3).start(self)
        self._start_anim()

    def hide(self):
        self._active = False
        Animation(opacity=0, duration=0.4).start(self)
        Animation.cancel_all(self, '_ring_angle', '_ring2_angle',
                             '_scan_y', '_pulse_a')

    def update_status(self, status, sub=''):
        self._lbl.text = status
        if sub:
            self._sub.text = sub

    def _start_anim(self):
        def _r1(*_):
            if not self._active: return
            a = Animation(_ring_angle=self._ring_angle + 360,
                          duration=2.5, t='linear')
            a.bind(on_complete=_r1); a.start(self)

        def _r2(*_):
            if not self._active: return
            a = Animation(_ring2_angle=self._ring2_angle - 360,
                          duration=1.8, t='linear')
            a.bind(on_complete=_r2); a.start(self)

        def _sc(*_):
            if not self._active: return
            a = (Animation(_scan_y=0.05, duration=1.3, t='in_out_cubic') +
                 Animation(_scan_y=0.95, duration=1.3, t='in_out_cubic'))
            a.bind(on_complete=_sc); a.start(self)

        def _pu(*_):
            if not self._active: return
            a = (Animation(_pulse_a=0.6, duration=0.65) +
                 Animation(_pulse_a=0.0, duration=0.65))
            a.bind(on_complete=_pu); a.start(self)

        _r1(); _r2(); _sc(); _pu()

    def _redraw(self, *_):
        self.canvas.clear()
        if not self._active and self.opacity < 0.05:
            return
        cx, cy = self.center_x, self.center_y
        w, h   = self.width, self.height

        with self.canvas:
            Color(*C_BG, 0.94)
            Rectangle(pos=self.pos, size=self.size)

            scan_cy = self.y + self._scan_y * h
            Color(*C_ACCENT, 0.07)
            Rectangle(pos=(self.x, scan_cy - dp(28)), size=(w, dp(56)))
            Color(*C_ACCENT, 0.52)
            Line(points=[self.x, scan_cy, self.x + w, scan_cy], width=dp(1.3))

            ro = min(w, h) * 0.25
            for i in range(0, 360, 40):
                a1 = i + self._ring_angle
                Color(*C_ACCENT, 0.40)
                Line(circle=(cx, cy, ro, a1, a1 + 18), width=dp(2), cap='round')

            ri = ro * 0.62
            for i in range(0, 360, 60):
                a1 = i + self._ring2_angle
                Color(*C_ACCENT, 0.24)
                Line(circle=(cx, cy, ri, a1, a1 + 28), width=dp(1.3), cap='round')

            Color(*C_ACCENT, self._pulse_a * 0.18)
            rc = ri * 0.45
            Ellipse(pos=(cx - rc, cy - rc), size=(rc * 2, rc * 2))
            Color(*C_ACCENT, 0.7 + self._pulse_a * 0.3)
            Line(circle=(cx, cy, dp(5)), width=dp(2.5))

            sz, t = dp(22), dp(2)
            for bx, by, sx, sy in [
                (cx - ro, cy - ro,  1,  1), (cx + ro, cy - ro, -1,  1),
                (cx - ro, cy + ro,  1, -1), (cx + ro, cy + ro, -1, -1),
            ]:
                Color(*C_ACCENT, 0.65)
                Line(points=[bx, by, bx + sx * sz, by], width=t)
                Line(points=[bx, by, bx, by + sy * sz], width=t)

        self._pos_labels()

    def _pos_labels(self, *_):
        cx, cy = self.center_x, self.center_y
        ro = min(self.width, self.height) * 0.25
        self._lbl.center_x = cx; self._lbl.center_y = cy - ro - dp(26)
        self._lbl.size     = (self.width * 0.8, dp(28))
        self._sub.center_x = cx; self._sub.center_y = cy - ro - dp(50)
        self._sub.size     = (self.width * 0.8, dp(22))
