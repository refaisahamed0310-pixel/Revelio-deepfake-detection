

from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty, ListProperty


class _ThemeManager(EventDispatcher):
    is_dark = BooleanProperty(True)

    # ── Computed colour properties (updated on toggle) ──────────────────────

    # Backgrounds
    bg          = ListProperty([0.020, 0.031, 0.051, 1])
    bg2         = ListProperty([0.031, 0.047, 0.078, 1])
    card        = ListProperty([0.035, 0.051, 0.082, 1])
    card2       = ListProperty([0.047, 0.067, 0.102, 1])
    header_bg   = ListProperty([0.016, 0.027, 0.047, 1])

    # Text
    text        = ListProperty([0.88,  0.93,  1.0,  1])
    text_dim    = ListProperty([0.30,  0.42,  0.60, 1])
    text_sub    = ListProperty([0.22,  0.33,  0.52, 1])

    # Borders / surfaces
    border      = ListProperty([0.10,  0.20,  0.36, 0.55])
    surface_row = ListProperty([0.024, 0.037, 0.062, 1])
    surface_row_bdr = ListProperty([0.08, 0.16, 0.30, 0.6])

    # Accent (stays same in both themes)
    accent      = ListProperty([0.0,   0.761, 1.0,  1])
    real_col    = ListProperty([0.0,   0.878, 0.612, 1])
    fake_col    = ListProperty([1.0,   0.231, 0.361, 1])

    # Tab bar
    tab_bg      = ListProperty([0.024, 0.037, 0.062, 0.97])
    tab_border  = ListProperty([0.12,  0.22,  0.38, 0.85])

    def toggle(self):
        self.is_dark = not self.is_dark
        self._apply()

    def _apply(self):
        d = self.is_dark
        if d:
            self.bg          = [0.020, 0.031, 0.051, 1]
            self.bg2         = [0.031, 0.047, 0.078, 1]
            self.card        = [0.035, 0.051, 0.082, 1]
            self.card2       = [0.047, 0.067, 0.102, 1]
            self.header_bg   = [0.016, 0.027, 0.047, 1]
            self.text        = [0.88,  0.93,  1.0,  1]
            self.text_dim    = [0.30,  0.42,  0.60, 1]
            self.text_sub    = [0.22,  0.33,  0.52, 1]
            self.border      = [0.10,  0.20,  0.36, 0.55]
            self.surface_row = [0.024, 0.037, 0.062, 1]
            self.surface_row_bdr = [0.08, 0.16, 0.30, 0.6]
            self.tab_bg      = [0.024, 0.037, 0.062, 0.97]
            self.tab_border  = [0.12,  0.22,  0.38, 0.85]
        else:
            self.bg          = [0.94,  0.96,  0.99, 1]
            self.bg2         = [0.88,  0.92,  0.97, 1]
            self.card        = [1.0,   1.0,   1.0,  1]
            self.card2       = [0.95,  0.97,  1.0,  1]
            self.header_bg   = [0.96,  0.97,  1.0,  1]
            self.text        = [0.08,  0.10,  0.16, 1]
            self.text_dim    = [0.30,  0.38,  0.52, 1]
            self.text_sub    = [0.50,  0.58,  0.70, 1]
            self.border      = [0.72,  0.80,  0.92, 0.8]
            self.surface_row = [0.92,  0.95,  0.99, 1]
            self.surface_row_bdr = [0.75, 0.83, 0.94, 0.7]
            self.tab_bg      = [0.96,  0.97,  1.0,  0.97]
            self.tab_border  = [0.72,  0.82,  0.94, 0.85]


ThemeManager = _ThemeManager()
