import os, threading, logging
from datetime import datetime

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import ListProperty, StringProperty, BooleanProperty, NumericProperty, ColorProperty
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line, Ellipse
from kivy.uix.behaviors import ButtonBehavior

from kivymd.uix.screen import MDScreen
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.snackbar import Snackbar

from kivy.uix.modalview import ModalView
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout

def _show_snack(message: str):
    """KivyMD 1.2.0 compatible snackbar — set text after construction."""
    bar = Snackbar()
    bar.text = message
    bar.open()

from ui.widgets import ConfidenceRing, ScanOverlay, LogoBox, TitleWave  # noqa
from ui.theme import ThemeManager as TM

logger = logging.getLogger(__name__)

ANALYZE_KV = """
#:import dp kivy.metrics.dp
#:import TM ui.theme.ThemeManager

<AnalyzeScreen>:
    name: 'analyze'

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

            # ── HEADER ─────────────────────────────────
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

                # Logo square — fixed size, canvas drawn inside LogoBox
                LogoBox:
                    size_hint: None, None
                    size: dp(38), dp(38)
                    pos_hint: {'center_y': 0.5}
                    padding: 0
                    MDLabel:
                        text: 'R'
                        bold: True
                        theme_text_color: 'Custom'
                        text_color: 0.020, 0.031, 0.051, 1
                        halign: 'center'
                        valign: 'middle'
                        font_style: 'H6'

                # Title wave + subtitle
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_x: None
                    width: dp(118)
                    spacing: dp(2)

                    TitleWave:
                        id: title_wave
                        size_hint_y: None
                        height: dp(26)

                    MDLabel:
                        text: 'AI  FORENSICS'
                        theme_text_color: 'Custom'
                        text_color: TM.text_dim
                        font_style: 'Overline'
                        size_hint_y: None
                        height: dp(14)

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
                    on_release: root.toggle_theme()

                BoxLayout:
                    size_hint_x: None
                    width: dp(2)

                # Status pill
                BoxLayout:
                    id: status_pill
                    size_hint_x: None
                    width: dp(100)
                    spacing: dp(4)
                    padding: [dp(9), dp(7), dp(9), dp(7)]
                    canvas.before:
                        Color:
                            rgba: root.status_bg
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(20)]
                        Color:
                            rgba: root.status_color
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(20)]
                            width: dp(0.7)

                    Widget:
                        size_hint_x: None
                        width: dp(7)
                        canvas:
                            Color:
                                rgba: root.status_color
                            Ellipse:
                                pos: self.x, self.center_y - dp(3.5)
                                size: dp(7), dp(7)

                    MDLabel:
                        text: root.status_text
                        theme_text_color: 'Custom'
                        text_color: root.status_color
                        font_style: 'Caption'
                        bold: True
                        font_size: dp(9)
                        halign: 'left'

            # ── SCROLL ─────────────────────────────────
            ScrollView:
                do_scroll_x: False
                bar_width: 0

                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(14), dp(64), dp(14), dp(150)]
                    spacing: dp(30)

                    # Upload card
                    BoxLayout:
                        id: upload_card
                        size_hint_y: None
                        height: dp(168)
                        canvas.before:
                            Color:
                                rgba: TM.card
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [dp(18)]
                            Color:
                                rgba: root.drop_border_color
                            Line:
                                rounded_rectangle: [self.x+dp(2), self.y+dp(2), self.width-dp(4), self.height-dp(4), dp(18)]
                                width: dp(1.2)
                                dash_length: 9
                                dash_offset: 6

                        BoxLayout:
                            orientation: 'vertical'
                            spacing: dp(10)
                            padding: [dp(20), dp(16), dp(20), dp(14)]

                            MDIconButton:
                                icon: 'cloud-upload-outline'
                                theme_text_color: 'Custom'
                                text_color: TM.accent
                                size_hint: None, None
                                size: dp(48), dp(48)
                                pos_hint: {'center_x': 0.5}
                                user_font_size: dp(32)
                                on_release: root.open_file_chooser()

                            MDLabel:
                                text: '[b]Tap to select media[/b]'
                                markup: True
                                halign: 'center'
                                theme_text_color: 'Custom'
                                text_color: TM.text
                                font_style: 'Body1'
                                size_hint_y: None
                                height: dp(24)

                            MDLabel:
                                text: 'Images: JPG  PNG  BMP      Videos: MP4  AVI  MOV'
                                halign: 'center'
                                theme_text_color: 'Custom'
                                text_color: TM.text_sub
                                font_style: 'Caption'
                                size_hint_y: None
                                height: dp(16)

                            MDRaisedButton:
                                text: 'Browse Files'
                                pos_hint: {'center_x': 0.5}
                                size_hint_x: 0.46
                                size_hint_y: None
                                height: dp(34)
                                font_size: dp(12)
                                bold: True
                                elevation: 0
                                on_release: root.open_file_chooser()
                                canvas.before:
                                    Color:
                                        rgba: 0, 0.761, 1, 0.15
                                    RoundedRectangle:
                                        pos: self.pos
                                        size: self.size
                                        radius: [dp(8)]
                                    Color:
                                        rgba: 0, 0.761, 1, 0.6
                                    Line:
                                        rounded_rectangle: [self.x, self.y, self.width, self.height, dp(8)]
                                        width: dp(0.8)

                    # Preview card
                    BoxLayout:
                        id: preview_card
                        size_hint_y: None
                        height: 0
                        opacity: 0
                        canvas.before:
                            Color:
                                rgba: TM.card
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [dp(16)]
                            Color:
                                rgba: root.preview_border_color
                            Line:
                                rounded_rectangle: [self.x+dp(1), self.y+dp(1), self.width-dp(2), self.height-dp(2), dp(16)]
                                width: dp(0.9)

                        BoxLayout:
                            size_hint_x: None
                            width: dp(80)
                            padding: [dp(10), dp(10), dp(4), dp(10)]
                            canvas.before:
                                Color:
                                    rgba: TM.bg2
                                RoundedRectangle:
                                    pos: self.x + dp(10), self.y + dp(10)
                                    size: dp(60), dp(76)
                                    radius: [dp(10)]
                            Image:
                                id: preview_thumb
                                allow_stretch: True
                                keep_ratio: True

                        BoxLayout:
                            orientation: 'vertical'
                            padding: [dp(10), dp(12), dp(12), dp(12)]
                            spacing: dp(5)

                            MDLabel:
                                id: lbl_filename
                                text: '—'
                                bold: True
                                theme_text_color: 'Custom'
                                text_color: TM.text
                                font_style: 'Body2'
                                size_hint_y: None
                                height: dp(22)
                                shorten: True
                                shorten_from: 'right'

                            BoxLayout:
                                size_hint_y: None
                                height: dp(20)
                                spacing: dp(8)

                                BoxLayout:
                                    size_hint_x: None
                                    width: dp(42)
                                    padding: [dp(4), dp(2), dp(4), dp(2)]
                                    canvas.before:
                                        Color:
                                            rgba: root.badge_bg
                                        RoundedRectangle:
                                            pos: self.pos
                                            size: self.size
                                            radius: [dp(5)]
                                    MDLabel:
                                        id: lbl_badge
                                        text: 'IMG'
                                        theme_text_color: 'Custom'
                                        text_color: root.badge_color
                                        font_style: 'Caption'
                                        bold: True
                                        halign: 'center'

                                MDLabel:
                                    id: lbl_dims
                                    text: ''
                                    theme_text_color: 'Custom'
                                    text_color: TM.text_dim
                                    font_style: 'Caption'

                            MDLabel:
                                id: lbl_meta2
                                text: ''
                                theme_text_color: 'Custom'
                                text_color: TM.text_sub
                                font_style: 'Caption'
                                size_hint_y: None
                                height: dp(16)

                    # Face Detection card — fully contained
                    BoxLayout:
                        size_hint_y: None
                        height: dp(72)
                        padding: [dp(16), dp(8), dp(16), dp(8)]
                        spacing: dp(12)
                        canvas.before:
                            Color:
                                rgba: TM.card
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [dp(16)]
                            Color:
                                rgba: TM.border
                            Line:
                                rounded_rectangle: [self.x+dp(1), self.y+dp(1), self.width-dp(2), self.height-dp(2), dp(16)]
                                width: dp(0.8)

                        MDIconButton:
                            icon: 'face-recognition'
                            theme_text_color: 'Custom'
                            text_color: TM.accent
                            size_hint: None, None
                            size: dp(40), dp(40)
                            pos_hint: {'center_y': 0.5}
                            user_font_size: dp(22)

                        BoxLayout:
                            orientation: 'vertical'
                            spacing: dp(2)
                            size_hint_x: 1
                            pos_hint: {'center_y': 0.5}

                            MDLabel:
                                text: 'Face Detection'
                                theme_text_color: 'Custom'
                                text_color: TM.text
                                font_style: 'Body2'
                                bold: True
                                size_hint_y: None
                                height: dp(22)

                            MDLabel:
                                text: 'Crop & analyse detected faces first'
                                theme_text_color: 'Custom'
                                text_color: TM.text_dim
                                font_style: 'Caption'
                                size_hint_y: None
                                height: dp(16)

                        # Custom Modern Toggle — Perfectly centered and contained
                        AnchorLayout:
                            size_hint_x: None
                            width: dp(80)
                            anchor_x: 'right'
                            anchor_y: 'center'
                            padding: [0, 0, dp(12), 0]

                            ModernToggle:
                                id: face_switch
                                active: True

                    # Scan button
                    BoxLayout:
                        id: scan_btn_box
                        size_hint_y: None
                        height: dp(54)
                        canvas.before:
                            Color:
                                rgba: root.scan_btn_color
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [dp(16)]
                        MDLabel:
                            id: scan_btn_lbl
                            text: 'SCAN FOR DEEPFAKES'
                            halign: 'center'
                            bold: True
                            theme_text_color: 'Custom'
                            text_color: 0.020, 0.031, 0.051, 1
                            font_style: 'Button'
                            font_size: dp(14)
                            on_touch_down:
                                if self.collide_point(*args[1].pos): root.start_analysis()

        # ── FLOATING TAB BAR ────────────────────────
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
                canvas.before:
                    Color:
                        rgba: 0, 0.761, 1, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(24)]
                on_touch_down: app.show_analyze() if self.collide_point(*args[1].pos) else None
                MDIconButton:
                    icon: 'magnify-scan'
                    theme_text_color: 'Custom'
                    text_color: 0.020, 0.031, 0.051, 1
                    user_font_size: dp(18)
                    size_hint: None, None
                    size: dp(30), dp(30)
                    pos_hint: {'center_y': 0.5}
                    on_release: app.show_analyze()
                MDLabel:
                    text: 'Scan'
                    theme_text_color: 'Custom'
                    text_color: 0.020, 0.031, 0.051, 1
                    font_style: 'Caption'
                    bold: True
                    halign: 'left'
                    valign: 'middle'

            BoxLayout:
                size_hint_x: 0.5
                spacing: dp(6)
                padding: [dp(12), dp(8), dp(8), dp(8)]
                on_touch_down: app.show_history() if self.collide_point(*args[1].pos) else None
                MDIconButton:
                    icon: 'history'
                    theme_text_color: 'Custom'
                    text_color: TM.text_dim
                    user_font_size: dp(18)
                    size_hint: None, None
                    size: dp(30), dp(30)
                    pos_hint: {'center_y': 0.5}
                    on_release: app.show_history()
                MDLabel:
                    text: 'History'
                    theme_text_color: 'Custom'
                    text_color: TM.text_dim
                    font_style: 'Caption'
                    halign: 'left'
                    valign: 'middle'

        ScanOverlay:
            id: scan_overlay
            size: root.size
            pos: root.pos
"""

Builder.load_string(ANALYZE_KV)


class ModernToggle(ButtonBehavior, BoxLayout):
    active = BooleanProperty(True)
    track_color = ColorProperty([0, 0, 0, 0.2])
    thumb_color = ColorProperty([0, 0.761, 1, 1])
    thumb_pos_x = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(54), dp(28))
        self.thumb_pos_x = dp(28) if self.active else dp(2)
        self.bind(active=self._update_ui, pos=self._update_canvas, size=self._update_canvas, thumb_pos_x=self._update_canvas)

    def _update_ui(self, *args):
        target_x = dp(28) if self.active else dp(2)
        Animation(thumb_pos_x=target_x, d=0.2, t='out_quad').start(self)

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Track
            Color(rgba=(0.3, 0.3, 0.4, 0.2) if not self.active else (0, 0.761, 1, 0.15))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self.height/2])
            # Border
            Color(rgba=(0.5, 0.5, 0.6, 0.3) if not self.active else (0, 0.761, 1, 0.4))
            Line(rounded_rectangle=[self.x, self.y, self.width, self.height, self.height/2], width=dp(1))
            
            # Thumb (Ball)
            thumb_size = self.height - dp(4)
            Color(rgba=(0.7, 0.7, 0.8, 1) if not self.active else (0, 0.761, 1, 1))
            Ellipse(pos=(self.x + self.thumb_pos_x, self.y + dp(2)), size=(thumb_size, thumb_size))

    def on_release(self):
        self.active = not self.active


class AnalyzeScreen(MDScreen):

    status_text          = StringProperty('INITIALIZING')
    status_color         = ListProperty([0.5, 0.5, 0.6, 1])
    status_bg            = ListProperty([0.5, 0.5, 0.6, 0.10])
    drop_border_color    = ListProperty([0.10, 0.22, 0.42, 0.55])
    preview_border_color = ListProperty([0.10, 0.20, 0.35, 0.4])
    badge_bg             = ListProperty([0.0,  0.761, 1.0,  0.15])
    badge_color          = ListProperty([0.0,  0.761, 1.0,  1.0])
    verdict_color        = ListProperty([0.30, 0.42, 0.60, 1])
    verdict_dim_color    = ListProperty([0.30, 0.42, 0.60, 0.7])
    verdict_banner_color = ListProperty([0.028, 0.043, 0.068, 1])
    verdict_icon_bg      = ListProperty([0.30, 0.42, 0.60, 0.15])
    result_border_color  = ListProperty([0.10, 0.20, 0.35, 0.5])
    scan_btn_color       = ListProperty([0.0,  0.761, 1.0,  1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_file = ''
        self._media_type   = ''
        self._file_manager = None
        self._scanning     = False
        Clock.schedule_once(lambda dt:
            __import__('utils.database', fromlist=['init_db']).init_db(), 0.2)
        Clock.schedule_once(self._preload_model, 0.9)

    def toggle_theme(self):
        TM.toggle()

    def on_face_toggle(self, is_active):
        """Called when Face Detection is toggled."""
        logger.info(f"Face Detection: {is_active}")

    # ── Model ──────────────────────────────────────────────────────────────

    def _preload_model(self, _dt):
        def _load():
            from core.model_loader import load_model, get_model_status
            load_model()
            Clock.schedule_once(
                lambda dt: self._on_model_ready(get_model_status()), 0)
        threading.Thread(target=_load, daemon=True).start()

    def _on_model_ready(self, status):
        cfg = {
            'both':   ([0.0, 0.88, 0.60, 1], [0.0, 0.88, 0.60, 0.10], 'ENSEMBLE READY'),
            'model1': ([0.0, 0.88, 0.60, 1], [0.0, 0.88, 0.60, 0.10], 'MODEL 1 READY'),
            'model2': ([0.0, 0.88, 0.60, 1], [0.0, 0.88, 0.60, 0.10], 'MODEL 2 READY'),
            'demo':   ([1.0, 0.70, 0.0,  1], [1.0, 0.70, 0.0,  0.10], 'DEMO MODE'),
            'failed': ([1.0, 0.23, 0.36, 1], [1.0, 0.23, 0.36, 0.10], 'ERROR'),
        }
        c, bg, txt = cfg.get(status, ([0.5, 0.5, 0.6, 1], [0.5, 0.5, 0.6, 0.10], 'UNKNOWN'))
        self.status_color = c
        self.status_bg    = bg
        self.status_text  = txt

    # ── File chooser ───────────────────────────────────────────────────────

    def open_file_chooser(self):
        if self._file_manager is None:
            self._file_manager = MDFileManager(
                exit_manager=lambda *_: self._file_manager.close(),
                select_path=self._on_file_selected,
                preview=False, selector='file')
        self._file_manager.show(os.path.expanduser('~'))

    def _on_file_selected(self, path):
        self._file_manager.close()
        self._load_media(path)

    # ── Media ──────────────────────────────────────────────────────────────

    def _load_media(self, path):
        from utils.helpers import (get_file_type, get_file_metadata,
                                   is_supported_file, format_duration)
        if not os.path.isfile(path):
            _show_snack("File not found"); return
        if not is_supported_file(path):
            _show_snack("Unsupported format"); return

        self._current_file = path
        self._media_type   = get_file_type(path)
        meta               = get_file_metadata(path)
        ids                = self.ids

        ids.lbl_filename.text = meta['filename']
        ids.lbl_badge.text    = meta['extension']
        ids.lbl_dims.text     = (f"{meta['width']} x {meta['height']}"
                                 if meta['width'] else '')
        ids.lbl_meta2.text    = (
            meta['size_str'] +
            (f"  ·  {format_duration(meta['duration'])}"
             if self._media_type == 'video' and meta['duration'] else '')
        )

        if self._media_type == 'image':
            self.badge_bg = [0.0, 0.878, 0.612, 0.15]
            self.badge_color = [0.0, 0.878, 0.612, 1.0]
            self.preview_border_color = [0.0, 0.878, 0.612, 0.45]
        else:
            self.badge_bg = [0.0, 0.761, 1.0, 0.15]
            self.badge_color = [0.0, 0.761, 1.0, 1.0]
            self.preview_border_color = [0.0, 0.761, 1.0, 0.45]

        threading.Thread(target=self._load_thumb, args=(path,), daemon=True).start()

        if ids.preview_card.opacity == 0:
            Animation(opacity=1, height=dp(96), duration=0.45, t='out_cubic').start(ids.preview_card)

        self.drop_border_color = [0.0, 0.761, 1.0, 1.0]
        Clock.schedule_once(
            lambda dt: setattr(self, 'drop_border_color', [0.10, 0.22, 0.42, 0.55]), 0.9)

    def _load_thumb(self, path):
        try:
            import cv2, io
            from PIL import Image as PILImage
            from kivy.core.image import Image as CoreImage

            if self._media_type == 'image':
                from utils.helpers import load_image
                frame = load_image(path)
            else:
                cap   = cv2.VideoCapture(path)
                total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                cap.set(cv2.CAP_PROP_POS_FRAMES, max(1, int(total * 0.10)))
                ok, frame = cap.read(); cap.release()
                if not ok: return

            if frame is None: return
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = PILImage.fromarray(rgb)
            img.thumbnail((240, 240), PILImage.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            core = CoreImage(buf, ext='png')
            Clock.schedule_once(
                lambda dt: setattr(self.ids.preview_thumb, 'texture', core.texture), 0)
        except Exception as e:
            logger.warning(f"Thumb: {e}")

    # ── Analysis ───────────────────────────────────────────────────────────

    def _show_upload_popup(self):
        """Show a modern styled popup asking user to upload media first."""
        from kivymd.uix.label import MDLabel
        from kivy.uix.widget import Widget

        modal = ModalView(
            size_hint=(0.82, None), height=dp(260),
            background='', background_color=(0, 0, 0, 0),
            overlay_color=(0, 0, 0, 0.65),
            auto_dismiss=True,
        )

        # Main card container
        card = BoxLayout(orientation='vertical', padding=[dp(24), dp(22), dp(24), dp(18)],
                         spacing=dp(10))
        with card.canvas.before:
            # Outer glow
            Color(0, 0.761, 1, 0.06)
            self._popup_glow = RoundedRectangle(
                pos=(card.x - dp(4), card.y - dp(4)),
                size=(card.width + dp(8), card.height + dp(8)),
                radius=[dp(24)])
            # Card bg
            Color(0.028, 0.043, 0.072, 0.97)
            self._popup_bg = RoundedRectangle(pos=card.pos, size=card.size,
                                               radius=[dp(20)])
            # Border
            Color(0, 0.761, 1, 0.25)
            self._popup_bdr = Line(
                rounded_rectangle=[*card.pos, *card.size, dp(20)],
                width=dp(1))

        def _upd_card(*_):
            self._popup_bg.pos = card.pos
            self._popup_bg.size = card.size
            self._popup_glow.pos = (card.x - dp(4), card.y - dp(4))
            self._popup_glow.size = (card.width + dp(8), card.height + dp(8))
            self._popup_bdr.rounded_rectangle = [*card.pos, *card.size, dp(20)]
        card.bind(pos=_upd_card, size=_upd_card)

        # ── Warning icon circle ──
        icon_anchor = AnchorLayout(size_hint_y=None, height=dp(52))
        icon_box = BoxLayout(size_hint=(None, None), size=(dp(48), dp(48)))
        with icon_box.canvas.before:
            Color(1, 0.70, 0, 0.15)
            self._ic_bg = Ellipse(pos=icon_box.pos, size=icon_box.size)
            Color(1, 0.70, 0, 0.6)
            self._ic_ring = Line(circle=[icon_box.center_x, icon_box.center_y, dp(24)],
                                 width=dp(1.5))
        def _upd_ic(*_):
            self._ic_bg.pos = icon_box.pos
            self._ic_bg.size = icon_box.size
            self._ic_ring.circle = [icon_box.center_x, icon_box.center_y, dp(24)]
        icon_box.bind(pos=_upd_ic, size=_upd_ic)
        icon_box.add_widget(MDLabel(
            text='!', bold=True, halign='center', valign='middle',
            theme_text_color='Custom', text_color=(1, 0.75, 0, 1),
            font_style='H5',
        ))
        icon_anchor.add_widget(icon_box)
        card.add_widget(icon_anchor)

        # ── Title ──
        card.add_widget(MDLabel(
            text='No Media Selected', bold=True, halign='center',
            theme_text_color='Custom', text_color=(0.92, 0.95, 1, 1),
            font_style='Subtitle1', size_hint_y=None, height=dp(28),
        ))

        # ── Message ──
        card.add_widget(MDLabel(
            text='Please upload an image or video\nbefore scanning for deepfakes.',
            halign='center', theme_text_color='Custom',
            text_color=(0.45, 0.55, 0.72, 1),
            font_style='Body2', size_hint_y=None, height=dp(42),
        ))

        card.add_widget(Widget(size_hint_y=None, height=dp(6)))

        # ── OK button ──
        btn_anchor = AnchorLayout(size_hint_y=None, height=dp(42))
        btn = BoxLayout(size_hint=(None, None), size=(dp(140), dp(40)))
        with btn.canvas.before:
            Color(0, 0.761, 1, 1)
            self._btn_bg = RoundedRectangle(pos=btn.pos, size=btn.size,
                                             radius=[dp(12)])
        def _upd_btn(*_):
            self._btn_bg.pos = btn.pos
            self._btn_bg.size = btn.size
        btn.bind(pos=_upd_btn, size=_upd_btn)
        btn_lbl = MDLabel(
            text='GOT IT', bold=True, halign='center', valign='middle',
            theme_text_color='Custom', text_color=(0.02, 0.03, 0.05, 1),
            font_style='Button',
        )
        btn.add_widget(btn_lbl)
        btn.bind(on_touch_down=lambda w, t: modal.dismiss() if w.collide_point(*t.pos) else None)
        btn_anchor.add_widget(btn)
        card.add_widget(btn_anchor)

        modal.add_widget(card)
        modal.open()

    def start_analysis(self):
        if self._scanning: return
        if not self._current_file:
            self._show_upload_popup(); return
        self._scanning = True
        self._set_scanning_ui(True)
        threading.Thread(target=self._run_detection, daemon=True).start()

    def _set_scanning_ui(self, active):
        ids = self.ids
        if active:
            ids.scan_btn_lbl.text = 'SCANNING...'
            self.scan_btn_color   = [0.0, 0.55, 0.80, 1]
            ids.scan_overlay.show('Analysing media...')
        else:
            ids.scan_btn_lbl.text = 'SCAN FOR DEEPFAKES'
            self.scan_btn_color   = [0.0, 0.761, 1.0, 1]
            ids.scan_overlay.hide()

    def _run_detection(self):
        try:
            from core.model_loader import load_model
            model = load_model()

            def _prog(prog, status):
                Clock.schedule_once(lambda dt:
                    self.ids.scan_overlay.update_status(
                        status, f"{int(prog * 100)}% complete"), 0)

            if self._media_type == 'image':
                from core.image_detector import detect_image
                result = detect_image(self._current_file,
                    use_face_detection=self.ids.face_switch.active, model=model)
                result.setdefault('frames_analyzed', 1)
            else:
                from core.video_detector import detect_video
                result = detect_video(self._current_file, frame_interval=10,
                    use_face_detection=self.ids.face_switch.active,
                    progress_callback=_prog, model=model)

            Clock.schedule_once(lambda dt: self._show_result(result), 0)
        except Exception as e:
            logger.exception(e)
            msg = str(e)
            Clock.schedule_once(lambda dt: self._on_error(msg), 0)

    def _reveal_card(self, card, duration=0.45, callback=None):
        card.opacity = 0
        orig_y = card.y
        card.y = orig_y - dp(28)
        a = Animation(opacity=1, y=orig_y, duration=duration, t='out_cubic')
        if callback:
            a.bind(on_complete=lambda *_: callback())
        a.start(card)

    @property
    def _last_confidence(self):
        """Helper to retrieve confidence stored after detection."""
        return getattr(self, '_stored_confidence', 0.0)

    def _show_result(self, result):
        self._scanning = False
        self._set_scanning_ui(False)

        if result.get('error'):
            _show_snack(f"Error: {result['error']}"); return

        # Persist to DB
        try:
            from utils.database import insert_scan
            from utils.helpers import get_file_metadata
            insert_scan(self._current_file, result, self._media_type,
                        get_file_metadata(self._current_file))
        except Exception as e:
            logger.warning(f"DB: {e}")

        # Hand off to ResultScreen and navigate
        from kivy.app import App
        app = App.get_running_app()
        result_screen = app.root.get_screen('result')
        result_screen.load_result(result, self._media_type)
        app.root.current = 'result'

    def reset_to_home(self):
        """Reset all state — called when Home button pressed from ResultScreen."""
        self._current_file = ''
        self._media_type   = ''
        self._scanning     = False
        ids = self.ids
        ids.preview_card.opacity  = 0
        ids.preview_card.height   = 0
        ids.preview_thumb.texture = None
        ids.preview_thumb.source  = ''
        ids.lbl_filename.text     = '—'
        ids.lbl_badge.text        = 'IMG'
        ids.lbl_dims.text         = ''
        ids.lbl_meta2.text        = ''
        ids.scan_btn_lbl.text     = 'SCAN FOR DEEPFAKES'
        self.scan_btn_color       = [0.0, 0.761, 1.0, 1]
        self.drop_border_color    = [0.10, 0.22, 0.42, 0.55]
        self.badge_bg             = [0.0, 0.761, 1.0, 0.15]
        self.badge_color          = [0.0, 0.761, 1.0, 1.0]

    def _on_error(self, msg):
        self._scanning = False
        self._set_scanning_ui(False)
        _show_snack(f"Error: {msg}")
