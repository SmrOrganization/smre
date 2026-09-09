from ..graphics.color import Color
from ..mathlib import Vec2


class SMRStyle:
    def __init__(self):
        self.window_bg = Color.from_hex("#000000")
        self.window_bg_alpha = 0.98
        self.window_border = Color.from_hex("#2b2b2b")
        self.title_bg = Color.from_hex("#000000")
        self.title_bg_active = Color.from_hex("#0a0a0a")
        self.title_text = Color.from_hex("#ffffff")

        self.text = Color.from_hex("#f2f2f2")
        self.text_disabled = Color.from_hex("#6b6b6b")

        self.button = Color.from_hex("#141414")
        self.button_hovered = Color.from_hex("#232323")
        self.button_active = Color.from_hex("#ffffff")
        self.button_active_text = Color.from_hex("#000000")

        self.frame_bg = Color.from_hex("#0d0d0d")
        self.frame_bg_hovered = Color.from_hex("#1a1a1a")
        self.frame_bg_active = Color.from_hex("#262626")

        self.header = Color.from_hex("#161616")
        self.header_hovered = Color.from_hex("#232323")
        self.header_active = Color.from_hex("#ffffff")
        self.header_active_text = Color.from_hex("#000000")

        self.checkmark = Color.from_hex("#ffffff")
        self.slider_grab = Color.from_hex("#ffffff")
        self.slider_grab_active = Color.from_hex("#cfcfcf")

        self.separator = Color.from_hex("#2b2b2b")

        self.scrollbar_bg = Color.from_hex("#050505")
        self.scrollbar_grab = Color.from_hex("#333333")
        self.scrollbar_grab_hovered = Color.from_hex("#4a4a4a")
        self.scrollbar_grab_active = Color.from_hex("#ffffff")

        self.badge_bg = Color.from_hex("#1a1a1a")
        self.badge_text = Color.from_hex("#f2f2f2")
        self.success = Color.from_hex("#4ade80")
        self.danger = Color.from_hex("#ff6b6b")

        self.toast_bg = Color.from_hex("#161616")
        self.toast_text = Color.from_hex("#f2f2f2")
        self.toast_border = Color.from_hex("#2b2b2b")

        self.border_size = 1.0
        self.window_rounding = 10.0
        self.frame_rounding = 6.0
        self.scrollbar_size = 12.0

        self.window_padding = Vec2(12.0, 12.0)
        self.item_spacing = Vec2(8.0, 8.0)
        self.frame_padding = Vec2(7.0, 5.0)
        self.indent_spacing = 18.0
        self.title_bar_height = 26.0

        self.hover_transition_seconds = 0.15
        self.disabled_alpha = 0.4

    def window_bg_with_alpha(self):
        return self.window_bg.with_alpha(self.window_bg_alpha)

    def apply_accent(self, color, text_on_accent=None):
        text = text_on_accent if text_on_accent is not None else Color(0.07, 0.07, 0.07, 1.0)
        self.button_active = color
        self.button_active_text = text
        self.header_active = color
        self.header_active_text = text
        self.checkmark = color
        self.slider_grab = color
        self.slider_grab_active = color.lerp(Color(1.0, 1.0, 1.0, 1.0), 0.2)
        self.scrollbar_grab_active = color


DEFAULT_STYLE = SMRStyle()
