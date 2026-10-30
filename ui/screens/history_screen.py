"""
ui/screens/history_screen.py — v6
Redesigned history cards, theme-aware, improved tab bar.
"""

import os
from datetime import datetime

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse, Rectangle
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from ui.theme import ThemeManager as TM

HISTORY_KV = """
#:import TM ui.theme.ThemeManager

<HistoryScreen>:
    name: 'history'

    canvas.before:
        Color:
            rgba: TM.bg
        Rectangle:
            pos: self.pos
            size: self.size

    FloatLayout:

        BoxLayout:
            orientation: 'vertical'
            size: root.size
            pos: root.pos

            # Top bar
            BoxLayout:
                size_hint_y: None
                height: dp(58)
                padding: [dp(14), dp(10), dp(14), dp(10)]
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

                BoxLayout:
                    size_hint_x: None
                    width: dp(38)
                    pos_hint: {'center_y': 0.5}
                    canvas.before:
                        Color:
                            rgba: 0, 0.761, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(9)]
                    MDLabel:
                        text: 'V'
                        bold: True
                        theme_text_color: 'Custom'
                        text_color: 0.020, 0.031, 0.051, 1
                        halign: 'center'
                        valign: 'middle'
                        font_style: 'H6'

                BoxLayout:
                    orientation: 'vertical'
                    size_hint_x: None
                    width: dp(130)
                    spacing: dp(2)
                    MDLabel:
                        text: 'SCAN HISTORY'
                        bold: True
                        theme_text_color: 'Custom'
                        text_color: TM.text
                        font_style: 'Button'
                        size_hint_y: 0.58
                    MDLabel:
                        id: lbl_count
                        text: '—'
                        theme_text_color: 'Custom'
                        text_color: TM.accent
                        font_style: 'Overline'
                        size_hint_y: 0.42

                Widget:

                # Theme toggle
                MDIconButton:
                    icon: 'weather-sunny' if TM.is_dark else 'weather-night'
                    theme_text_color: 'Custom'
                    text_color: TM.text_dim
                    size_hint: None, None
                    size: dp(36), dp(38)
                    user_font_size: dp(18)
                    pos_hint: {'center_y': 0.5}
                    on_release: app.toggle_theme()

                MDIconButton:
                    icon: 'trash-can-outline'
                    theme_text_color: 'Custom'
                    text_color: TM.text_dim
                    size_hint: None, None
                    size: dp(36), dp(38)
                    user_font_size: dp(18)
                    pos_hint: {'center_y': 0.5}
                    on_release: root.clear_all()

            # Stats row
            BoxLayout:
                size_hint_y: None
                height: dp(64)
                padding: [dp(10), dp(8), dp(10), dp(8)]
                spacing: dp(6)
                canvas.before:
                    Color:
                        rgba: TM.bg2
                    Rectangle:
                        pos: self.pos
                        size: self.size

                BoxLayout:
                    orientation: 'vertical'
                    spacing: dp(2)
                    padding: [dp(8), dp(4)]
                    canvas.before:
                        Color:
                            rgba: TM.card
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(10)]
                    MDLabel:
                        id: stat_total
                        text: '0'
                        bold: True
                        halign: 'center'
                        theme_text_color: 'Custom'
                        text_color: TM.text
                        font_style: 'H6'
                        size_hint_y: 0.6
                    MDLabel:
                        text: 'Total'
                        halign: 'center'
                        theme_text_color: 'Custom'
                        text_color: TM.text_dim
                        font_style: 'Caption'
                        size_hint_y: 0.4

                BoxLayout:
                    orientation: 'vertical'
                    spacing: dp(2)
                    padding: [dp(8), dp(4)]
                    canvas.before:
                        Color:
                            rgba: 0.016, 0.10, 0.062, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(10)]
                        Color:
                            rgba: 0, 0.878, 0.612, 0.3
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(10)]
                            width: dp(0.7)
                    MDLabel:
                        id: stat_real
                        text: '0'
                        bold: True
                        halign: 'center'
                        theme_text_color: 'Custom'
                        text_color: 0, 0.878, 0.612, 1
                        font_style: 'H6'
                        size_hint_y: 0.6
                    MDLabel:
                        text: 'Authentic'
                        halign: 'center'
                        theme_text_color: 'Custom'
                        text_color: 0, 0.878, 0.612, 0.7
                        font_style: 'Caption'
                        size_hint_y: 0.4

                BoxLayout:
                    orientation: 'vertical'
                    spacing: dp(2)
                    padding: [dp(8), dp(4)]
                    canvas.before:
                        Color:
                            rgba: 0.14, 0.020, 0.035, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(10)]
                        Color:
                            rgba: 1, 0.231, 0.361, 0.3
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(10)]
                            width: dp(0.7)
                    MDLabel:
                        id: stat_fake
                        text: '0'
                        bold: True
                        halign: 'center'
                        theme_text_color: 'Custom'
                        text_color: 1, 0.231, 0.361, 1
                        font_style: 'H6'
                        size_hint_y: 0.6
                    MDLabel:
                        text: 'AI Fakes'
                        halign: 'center'
                        theme_text_color: 'Custom'
                        text_color: 1, 0.231, 0.361, 0.7
                        font_style: 'Caption'
                        size_hint_y: 0.4

                BoxLayout:
                    orientation: 'vertical'
                    spacing: dp(2)
                    padding: [dp(8), dp(4)]
                    canvas.before:
                        Color:
                            rgba: TM.card
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(10)]
                        Color:
                            rgba: TM.accent
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(10)]
                            width: dp(0.6)
                    MDLabel:
                        id: stat_pct
                        text: '0%'
                        bold: True
                        halign: 'center'
                        theme_text_color: 'Custom'
                        text_color: TM.accent
                        font_style: 'H6'
                        size_hint_y: 0.6
                    MDLabel:
                        text: 'Fake Rate'
                        halign: 'center'
                        theme_text_color: 'Custom'
                        text_color: TM.text_dim
                        font_style: 'Caption'
                        size_hint_y: 0.4

            # Search bar
            BoxLayout:
                size_hint_y: None
                height: dp(48)
                padding: [dp(14), dp(6), dp(14), dp(6)]
                canvas.before:
                    Color:
                        rgba: TM.bg2
                    Rectangle:
                        pos: self.pos
                        size: self.size
                MDTextField:
                    id: search_field
                    hint_text: 'Search filename...'
                    mode: 'rectangle'
                    font_size: dp(12)
                    on_text: root.on_search(self.text)

            # Filter chips
            BoxLayout:
                size_hint_y: None
                height: dp(42)
                padding: [dp(14), dp(6), dp(14), dp(6)]
                spacing: dp(8)
                canvas.before:
                    Color:
                        rgba: TM.bg
                    Rectangle:
                        pos: self.pos
                        size: self.size

                BoxLayout:
                    size_hint_x: None
                    width: dp(46)
                    height: dp(30)
                    pos_hint: {'center_y': 0.5}
                    canvas.before:
                        Color:
                            rgba: 0, 0.761, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(15)]
                    on_touch_down: root.set_filter('') if self.collide_point(*args[1].pos) else None
                    MDLabel:
                        text: 'All'
                        halign: 'center'
                        bold: True
                        theme_text_color: 'Custom'
                        text_color: 0.020, 0.031, 0.051, 1
                        font_style: 'Caption'

                BoxLayout:
                    size_hint_x: None
                    width: dp(80)
                    height: dp(30)
                    pos_hint: {'center_y': 0.5}
                    canvas.before:
                        Color:
                            rgba: 0, 0.878, 0.612, 0.12
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(15)]
                        Color:
                            rgba: 0, 0.878, 0.612, 0.5
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(15)]
                            width: dp(0.7)
                    on_touch_down: root.set_filter('REAL') if self.collide_point(*args[1].pos) else None
                    MDLabel:
                        text: 'Authentic'
                        halign: 'center'
                        bold: True
                        theme_text_color: 'Custom'
                        text_color: 0, 0.878, 0.612, 1
                        font_style: 'Caption'

                BoxLayout:
                    size_hint_x: None
                    width: dp(72)
                    height: dp(30)
                    pos_hint: {'center_y': 0.5}
                    canvas.before:
                        Color:
                            rgba: 1, 0.231, 0.361, 0.12
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(15)]
                        Color:
                            rgba: 1, 0.231, 0.361, 0.5
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(15)]
                            width: dp(0.7)
                    on_touch_down: root.set_filter('AI GENERATED') if self.collide_point(*args[1].pos) else None
                    MDLabel:
                        text: 'AI Fakes'
                        halign: 'center'
                        bold: True
                        theme_text_color: 'Custom'
                        text_color: 1, 0.231, 0.361, 1
                        font_style: 'Caption'

                Widget:

            # Thin divider
            BoxLayout:
                size_hint_y: None
                height: dp(1)
                canvas.before:
                    Color:
                        rgba: TM.border
                    Rectangle:
                        pos: self.pos
                        size: self.size

            # Scroll list
            ScrollView:
                id: scroll
                do_scroll_x: False
                bar_width: dp(3)
                bar_color: 0, 0.761, 1, 0.35
                BoxLayout:
                    id: list_container
                    orientation: 'vertical'
                    spacing: dp(8)
                    padding: [dp(14), dp(12), dp(14), dp(150)]
                    size_hint_y: None
                    height: self.minimum_height

            # Empty state
            BoxLayout:
                id: empty_box
                orientation: 'vertical'
                spacing: dp(10)
                padding: [dp(40), dp(60)]
                opacity: 0
                size_hint_y: None
                height: dp(250)
                MDLabel:
                    text: 'No scans yet'
                    halign: 'center'
                    theme_text_color: 'Custom'
                    text_color: TM.text_dim
                    font_style: 'H6'
                    size_hint_y: None
                    height: dp(32)
                MDLabel:
                    text: 'Analysed files will appear here'
                    halign: 'center'
                    theme_text_color: 'Custom'
                    text_color: TM.text_sub
                    font_style: 'Body2'
                    size_hint_y: None
                    height: dp(24)

        # Floating tab bar — same as analyze screen
        BoxLayout:
            size_hint: None, None
            width: dp(270)
            height: dp(58)
            pos_hint: {'center_x': 0.5}
            y: dp(16)
            spacing: dp(6)
            padding: [dp(6), dp(6), dp(6), dp(6)]
            canvas.before:
                Color:
                    rgba: TM.tab_bg
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(30)]
                Color:
                    rgba: TM.tab_border
                Line:
                    rounded_rectangle: [self.x, self.y, self.width, self.height, dp(30)]
                    width: dp(0.8)

            BoxLayout:
                size_hint_x: 0.5
                spacing: dp(6)
                padding: [dp(12), dp(8), dp(8), dp(8)]
                on_touch_down: app.show_analyze() if self.collide_point(*args[1].pos) else None
                MDIconButton:
                    icon: 'magnify-scan'
                    theme_text_color: 'Custom'
                    text_color: TM.text_dim
                    user_font_size: dp(18)
                    size_hint: None, None
                    size: dp(30), dp(30)
                    pos_hint: {'center_y': 0.5}
                    on_release: app.show_analyze()
                MDLabel:
                    text: 'Scan'
                    theme_text_color: 'Custom'
                    text_color: TM.text_dim
                    font_style: 'Caption'
                    halign: 'left'
                    valign: 'middle'

            BoxLayout:
                size_hint_x: 0.5
                spacing: dp(6)
                padding: [dp(12), dp(8), dp(8), dp(8)]
                canvas.before:
                    Color:
                        rgba: 0, 0.761, 1, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(24)]
                on_touch_down: app.show_history() if self.collide_point(*args[1].pos) else None
                MDIconButton:
                    icon: 'history'
                    theme_text_color: 'Custom'
                    text_color: 0.020, 0.031, 0.051, 1
                    user_font_size: dp(18)
                    size_hint: None, None
                    size: dp(30), dp(30)
                    pos_hint: {'center_y': 0.5}
                    on_release: app.show_history()
                MDLabel:
                    text: 'History'
                    theme_text_color: 'Custom'
                    text_color: 0.020, 0.031, 0.051, 1
                    font_style: 'Caption'
                    bold: True
                    halign: 'left'
                    valign: 'middle'
"""

Builder.load_string(HISTORY_KV)


class HistoryCard(BoxLayout):
    """Redesigned history card with horizontal layout."""

    def __init__(self, entry: dict, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height      = dp(62)          # reduced from 72
        self.padding     = [dp(12), dp(8), dp(12), dp(8)]
        self.spacing     = dp(10)

        is_fake = entry.get('verdict') == 'AI GENERATED'
        C_REAL  = (0.0, 0.878, 0.612)
        C_FAKE  = (1.0, 0.231, 0.361)
        accent  = C_FAKE if is_fake else C_REAL
        icon_bg = (0.14, 0.020, 0.035) if is_fake else (0.016, 0.10, 0.062)

        # Card background — use only 3 channels + explicit alpha
        card_rgb = TM.card[:3]
        with self.canvas.before:
            Color(*card_rgb, 1)                    # fixed: no extra alpha arg
            self._bg  = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
            Color(*accent, 0.30)
            self._bdr = Line(rounded_rectangle=[*self.pos, *self.size, dp(12)], width=dp(0.8))
        self.bind(pos=self._upd, size=self._upd)

        # Left: verdict icon circle
        icon_col = BoxLayout(size_hint_x=None, width=dp(46))
        with icon_col.canvas.before:
            Color(*icon_bg, 1)
            self._icbg = Ellipse(
                pos=(icon_col.x + dp(1), icon_col.center_y - dp(20)),
                size=(dp(40), dp(40)),
            )
            Color(*accent, 0.6)
            self._icbdr = Line(
                circle=[icon_col.x + dp(21), icon_col.center_y, dp(20)],
                width=dp(1.2),
            )
        icon_col.bind(pos=self._upd_icon, size=self._upd_icon, center_y=self._upd_icon)
        self._icon_col_ref = icon_col

        icon_lbl = MDLabel(
            text='X' if is_fake else 'OK',
            theme_text_color='Custom',
            text_color=(*accent, 1),
            font_style='Caption',
            bold=True,
            halign='center',
            valign='middle',
            font_size=dp(11),
        )
        icon_col.add_widget(icon_lbl)
        self.add_widget(icon_col)

        # Centre: filename + meta
        info = BoxLayout(orientation='vertical', spacing=dp(4))
        # Use explicit dark/light colour based on current theme
        txt_color = (*TM.text[:3], 1) if TM.is_dark else (0.08, 0.10, 0.16, 1)
        name_lbl = MDLabel(
            text=entry.get('filename', '—'),
            bold=True,
            theme_text_color='Custom',
            text_color=txt_color,
            font_style='Body2',
            size_hint_y=0.55,
            shorten=True,
            shorten_from='right',
        )

        meta_row = BoxLayout(size_hint_y=0.45, spacing=dp(6))

        # type chip — wide enough to show VIDEO without wrapping
        mtype = entry.get('media_type', 'image').upper()
        chip_w = dp(52) if mtype == 'VIDEO' else dp(46)
        type_chip = BoxLayout(size_hint_x=None, width=chip_w,
                              padding=[dp(4), dp(1), dp(4), dp(1)])
        with type_chip.canvas.before:
            Color(0.0, 0.761, 1.0, 0.14)
            self._tchip = RoundedRectangle(pos=type_chip.pos, size=type_chip.size,
                                           radius=[dp(5)])
        type_chip.bind(
            pos=lambda w, _: setattr(self._tchip, 'pos', w.pos),
            size=lambda w, _: setattr(self._tchip, 'size', w.size),
        )
        type_chip.add_widget(MDLabel(
            text=mtype,
            theme_text_color='Custom',
            text_color=(0.0, 0.761, 1.0, 0.9),
            font_style='Caption', bold=True, halign='center',
        ))
        meta_row.add_widget(type_chip)

        conf = entry.get('confidence', 0)
        dim_color = (*TM.text_dim[:3], 1)
        meta_row.add_widget(MDLabel(
            text=f"Conf {conf * 100:.1f}%",
            theme_text_color='Custom',
            text_color=dim_color,
            font_style='Caption',
            shorten=True,
            shorten_from='right',
        ))

        ts_raw = entry.get('timestamp', '')
        try:
            ts_str = datetime.fromisoformat(ts_raw).strftime('%b %d  %H:%M')
        except Exception:
            ts_str = ts_raw[:16] if ts_raw else '—'

        meta_row.add_widget(MDLabel(
            text=ts_str,
            theme_text_color='Custom',
            text_color=(*TM.text_sub[:3], 1),
            font_style='Caption', halign='right',
        ))

        info.add_widget(name_lbl)
        info.add_widget(meta_row)
        self.add_widget(info)

        # Right: verdict label
        v_box = BoxLayout(size_hint_x=None, width=dp(76),
                          padding=[dp(4), dp(10), dp(4), dp(10)])
        with v_box.canvas.before:
            Color(*accent, 0.15)
            self._vpill = RoundedRectangle(pos=v_box.pos, size=v_box.size, radius=[dp(10)])
            Color(*accent, 0.5)
            self._vpilld = Line(rounded_rectangle=[*v_box.pos, *v_box.size, dp(10)], width=dp(0.7))
        v_box.bind(
            pos=lambda w, _: (setattr(self._vpill, 'pos', w.pos),
                              setattr(self._vpilld, 'rounded_rectangle', [*w.pos, *w.size, dp(10)])),
            size=lambda w, _: (setattr(self._vpill, 'size', w.size),
                               setattr(self._vpilld, 'rounded_rectangle', [*w.pos, *w.size, dp(10)])),
        )
        verdict_text = 'FAKE' if is_fake else 'REAL'
        v_box.add_widget(MDLabel(
            text=verdict_text,
            theme_text_color='Custom',
            text_color=(*accent, 1),
            font_style='Caption', bold=True, halign='center', valign='middle',
        ))
        self.add_widget(v_box)

    def _upd(self, *_):
        self._bg.pos  = self.pos;  self._bg.size  = self.size
        self._bdr.rounded_rectangle = [*self.pos, *self.size, dp(14)]

    def _upd_icon(self, *_):
        ic = self._icon_col_ref
        self._icbg.pos  = (ic.x + dp(2), ic.center_y - dp(22))
        self._icbg.size = (dp(44), dp(44))
        self._icbdr.circle = [ic.x + dp(24), ic.center_y, dp(22)]


class HistoryScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._filter = ''
        self._query  = ''

    def on_pre_enter(self, *_):
        self._populate()
        self._refresh_stats()

    def _refresh_stats(self):
        try:
            from utils.database import get_stats
            s = get_stats()
            self.ids.stat_total.text = str(s['total'])
            self.ids.stat_real.text  = str(s['real_count'])
            self.ids.stat_fake.text  = str(s['fake_count'])
            self.ids.stat_pct.text   = f"{s['fake_pct']}%"
        except Exception:
            pass

    def _populate(self):
        from utils.database import search_scans, get_all_scans, delete_scan

        # Auto-prune: keep only the 10 most recent scans globally
        all_entries = get_all_scans(limit=500)
        if len(all_entries) > 10:
            # all_entries is newest-first; delete from index 10 onwards
            for old in all_entries[10:]:
                delete_scan(old['id'])

        entries   = search_scans(query=self._query, verdict_filter=self._filter)
        # Limit display to 10
        entries   = entries[:10]
        container = self.ids.list_container
        container.clear_widgets()
        count = len(entries)
        self.ids.lbl_count.text = f"{count} RECORD{'S' if count != 1 else ''}"
        if not entries:
            self.ids.empty_box.opacity = 1
            self.ids.empty_box.height  = dp(250)
            self.ids.empty_box.size_hint_y = None
            self.ids.scroll.opacity    = 0
            self.ids.scroll.size_hint_y = 0
            return
        self.ids.empty_box.opacity = 0
        self.ids.empty_box.height  = 0
        self.ids.empty_box.size_hint_y = None
        self.ids.scroll.opacity    = 1
        self.ids.scroll.size_hint_y = 1
        for entry in entries:
            container.add_widget(HistoryCard(entry=entry))

    def on_search(self, text):
        self._query = text.strip()
        self._populate()

    def set_filter(self, verdict):
        self._filter = verdict
        self._populate()

    def clear_all(self):
        from utils.database import clear_all_scans
        clear_all_scans()
        self._populate()
        self._refresh_stats()
