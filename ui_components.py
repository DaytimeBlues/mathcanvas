"""
UI Components Module
====================
Reusable UI widgets for MathCanvas application.
"""
from __future__ import annotations

from typing import Callable, Optional

from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import ListProperty
from kivy.uix.button import Button
from kivy.uix.label import Label

from config import (
    COLOR_BUTTON_SIZE,
    FONT_UNICORN,
    UNICORN_ANIMATION_DURATION,
    UNICORN_FLOAT_DISTANCE,
    UNICORN_WIDGET_SIZE,
)


class ColorButton(Button):
    """Circular color picker button."""
    color_value = ListProperty([0, 0, 0, 1])

    def __init__(self, color_value: tuple[float, ...], **kwargs) -> None:
        super().__init__(**kwargs)
        self.color_value = list(color_value)
        self.background_normal = ''
        self.background_color = color_value
        self.size_hint = (None, None)
        self.size = COLOR_BUTTON_SIZE
        self.border = (0, 0, 0, 0)


class UnicornReward(Label):
    """Animated emoji that floats up and fades out."""

    def __init__(self, emoji: str = '🦄', **kwargs) -> None:
        super().__init__(**kwargs)
        self.text = emoji
        self.font_size = FONT_UNICORN
        self.opacity = 1
        self.size_hint = (None, None)
        self.size = UNICORN_WIDGET_SIZE

    def animate_in(self, on_complete: Optional[Callable] = None) -> None:
        """Animate the unicorn floating up and fading out."""
        anim = Animation(
            y=self.y + UNICORN_FLOAT_DISTANCE,
            opacity=0,
            duration=UNICORN_ANIMATION_DURATION,
            t='out_cubic'
        )
        if on_complete:
            anim.bind(on_complete=lambda *_: on_complete(self))
        anim.start(self)


class RoundedButton(Button):
    """Button with rounded corners and custom background."""

    def __init__(self, bg_color: tuple[float, ...] = (0.3, 0.4, 0.5, 1), radius: int = 10, **kwargs) -> None:
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)

        with self.canvas.before:
            self._bg_color = Color(*bg_color)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])

        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args) -> None:
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def set_color(self, color: tuple[float, ...]) -> None:
        """Update button background color."""
        self._bg_color.rgba = color


class StatsDisplay(Label):
    """Display for showing statistics and progress."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.font_size = 18
        self.color = (1, 1, 1, 1)
        self.halign = 'center'
        self.valign = 'middle'

    def update_stats(self, attempted: int, correct: int) -> None:
        """Update the stats display."""
        accuracy = (correct / attempted * 100) if attempted > 0 else 0
        self.text = f"✓ {correct}/{attempted} ({accuracy:.0f}%)"


class ProgressBar(Label):
    """Simple visual progress indicator."""

    def __init__(self, max_value: int = 10, **kwargs) -> None:
        super().__init__(**kwargs)
        self.max_value = max_value
        self.current_value = 0
        self.font_size = 24
        self._update_display()

    def set_progress(self, value: int) -> None:
        """Update progress value."""
        self.current_value = min(value, self.max_value)
        self._update_display()

    def _update_display(self) -> None:
        """Update the visual representation."""
        filled = int((self.current_value / self.max_value) * 10)
        empty = 10 - filled
        self.text = '⭐' * filled + '☆' * empty
