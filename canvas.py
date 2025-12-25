"""
Canvas Module
=============
Drawing canvas widget with touch/pen input, undo/redo, and stroke tracking.
"""
from __future__ import annotations

import time
from typing import Callable, Optional

from kivy.clock import Clock
from kivy.graphics import Color, Line, Rectangle, InstructionGroup
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    StringProperty,
)
from kivy.uix.widget import Widget

from config import (
    CANVAS_BACKGROUNDS,
    CONTROL_BAR_TOUCH_THRESHOLD,
    DEFAULT_BACKGROUND,
    DEFAULT_LINE_WIDTH,
    ERASER_WIDTH_MULTIPLIER,
    MAX_UNDO_STACK,
    STROKE_RECENT_THRESHOLD,
    UNICORN_CHECK_DELAY,
    UNICORN_IDLE_THRESHOLD,
)


class Stroke:
    """Represents a single drawing stroke with its canvas instruction."""

    __slots__ = ('points', 'color', 'width', 'time', 'instruction')

    def __init__(
        self,
        points: list[tuple[float, float]],
        color: list[float],
        width: float,
        instruction: InstructionGroup
    ) -> None:
        self.points = points
        self.color = color
        self.width = width
        self.time = time.time()
        self.instruction = instruction

    def to_dict(self) -> dict:
        """Serialize stroke data for storage."""
        return {
            'points': self.points,
            'color': self.color,
            'width': self.width,
            'time': self.time,
        }


class WriteableCanvas(Widget):
    """Main drawing surface with touch/pen input and undo/redo support."""

    current_color = ListProperty([0.15, 0.15, 0.18, 1.0])
    line_width = NumericProperty(DEFAULT_LINE_WIDTH)
    is_eraser = BooleanProperty(False)
    background_color = ListProperty(list(CANVAS_BACKGROUNDS[DEFAULT_BACKGROUND]))
    background_key = StringProperty(DEFAULT_BACKGROUND)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.strokes: list[Stroke] = []
        self._undo_stack: list[Stroke] = []
        self._current_stroke_points: list[tuple[float, float]] = []
        self._current_instruction: Optional[InstructionGroup] = None
        self.last_draw_time: float = time.time()
        self._unicorn_check_event: Optional[Clock.ClockEvent] = None
        self.unicorn_callback: Optional[Callable[[list[Stroke]], None]] = None

        self._init_background()
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _init_background(self) -> None:
        """Initialize canvas background."""
        self.canvas.before.clear()
        with self.canvas.before:
            self._bg_color = Color(*self.background_color)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)

    def _update_bg(self, *args) -> None:
        """Update background rectangle on size/position change."""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size

    def on_touch_down(self, touch) -> bool:
        """Handle touch/pen down event."""
        if not self.collide_point(touch.x, touch.y):
            return super().on_touch_down(touch)
        if touch.y > self.height * CONTROL_BAR_TOUCH_THRESHOLD:
            return super().on_touch_down(touch)
        if super().on_touch_down(touch):
            return True

        touch.grab(self)
        self._current_stroke_points = [(touch.x, touch.y)]
        self._current_instruction = InstructionGroup()

        if self.is_eraser:
            self._current_instruction.add(Color(*self.background_color))
            line = Line(points=(touch.x, touch.y), width=self.line_width * ERASER_WIDTH_MULTIPLIER)
        else:
            self._current_instruction.add(Color(*self.current_color))
            line = Line(points=(touch.x, touch.y), width=self.line_width)

        self._current_instruction.add(line)
        touch.ud['line'] = line
        self.canvas.add(self._current_instruction)
        return True

    def on_touch_move(self, touch) -> bool:
        """Handle touch/pen move event."""
        if touch.grab_current is not self:
            return super().on_touch_move(touch)
        if not self.collide_point(touch.x, touch.y):
            return True
        if 'line' in touch.ud:
            touch.ud['line'].points += [touch.x, touch.y]
            self._current_stroke_points.append((touch.x, touch.y))
            self.last_draw_time = time.time()
        return True

    def on_touch_up(self, touch) -> bool:
        """Handle touch/pen up event."""
        if touch.grab_current is not self:
            return super().on_touch_up(touch)
        touch.ungrab(self)

        if self._current_stroke_points and self._current_instruction and not self.is_eraser:
            stroke = Stroke(
                points=self._current_stroke_points.copy(),
                color=self.current_color.copy(),
                width=self.line_width,
                instruction=self._current_instruction
            )
            self.strokes.append(stroke)
            self._undo_stack.clear()

            if len(self.strokes) > MAX_UNDO_STACK:
                self.strokes.pop(0)

            if self._unicorn_check_event:
                self._unicorn_check_event.cancel()
            if self.unicorn_callback:
                self._unicorn_check_event = Clock.schedule_once(
                    self._check_for_number, UNICORN_CHECK_DELAY
                )

        self._current_stroke_points = []
        self._current_instruction = None
        return True

    def _check_for_number(self, dt: float) -> None:
        """Check if user has finished drawing (for unicorn rewards)."""
        self._unicorn_check_event = None
        if time.time() - self.last_draw_time >= UNICORN_IDLE_THRESHOLD and self.unicorn_callback:
            recent = [s for s in self.strokes if time.time() - s.time < STROKE_RECENT_THRESHOLD]
            if recent:
                self.unicorn_callback(recent)

    def undo(self) -> bool:
        """Undo the last stroke."""
        if not self.strokes:
            return False
        stroke = self.strokes.pop()
        self._undo_stack.append(stroke)
        self.canvas.remove(stroke.instruction)
        return True

    def redo(self) -> bool:
        """Redo the last undone stroke."""
        if not self._undo_stack:
            return False
        stroke = self._undo_stack.pop()
        self.strokes.append(stroke)
        self.canvas.add(stroke.instruction)
        return True

    def clear_canvas(self) -> None:
        """Clear all strokes from canvas."""
        if self._unicorn_check_event:
            self._unicorn_check_event.cancel()
            self._unicorn_check_event = None
        self.canvas.clear()
        self.strokes.clear()
        self._undo_stack.clear()
        self._init_background()

    def set_background(self, color_key: str) -> None:
        """Change canvas background color."""
        if color_key not in CANVAS_BACKGROUNDS:
            return
        self.background_key = color_key
        self.background_color = list(CANVAS_BACKGROUNDS[color_key])
        if hasattr(self, '_bg_color'):
            self._bg_color.rgba = self.background_color

    def export_strokes(self) -> dict:
        """Export all strokes as serializable data."""
        return {
            'strokes': [s.to_dict() for s in self.strokes],
            'background': self.background_key,
            'timestamp': time.time(),
        }

    def import_strokes(self, data: dict) -> None:
        """Import strokes from serialized data."""
        self.clear_canvas()

        if 'background' in data:
            self.set_background(data['background'])

        for stroke_data in data.get('strokes', []):
            instruction = InstructionGroup()
            instruction.add(Color(*stroke_data['color']))
            instruction.add(Line(points=stroke_data['points'], width=stroke_data['width']))

            stroke = Stroke(
                points=stroke_data['points'],
                color=stroke_data['color'],
                width=stroke_data['width'],
                instruction=instruction
            )
            self.strokes.append(stroke)
            self.canvas.add(instruction)

    def has_content(self) -> bool:
        """Check if canvas has any strokes."""
        return len(self.strokes) > 0
