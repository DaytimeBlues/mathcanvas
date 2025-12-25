"""
MathCanvas - A Touch-Friendly Math Learning App
================================================
Year 1 ACARA Mathematics Curriculum implementation with full progress tracking.

Features:
- Complete curriculum navigation across 4 strands
- 18+ topic-specific problem generators with answer validation
- Student profile management and progress tracking
- Drawing canvas with undo/redo support
- Database persistence for all learning activities
- Unicorn rewards for engagement
- Session-based analytics

Built with Kivy for Windows tablet/pen support.
"""
from __future__ import annotations

import random
import logging
from typing import Optional

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

from canvas import WriteableCanvas, Stroke
from config import (
    CANVAS_BACKGROUNDS,
    COLORS,
    CONTROL_BAR_HEIGHT_RATIO,
    CONTROL_BAR_RADIUS,
    DEFAULT_LINE_WIDTH,
    FONT_EMOJI_LARGE,
    FONT_EMOJI_MEDIUM,
    MAX_ACTIVE_UNICORNS,
    MAX_LINE_WIDTH,
    MIN_LINE_WIDTH,
    PALETTE_SECTION_WIDTH,
    SETTINGS_SECTION_WIDTH,
    SMALL_BUTTON_WIDTH,
    TOOL_BUTTON_WIDTH,
    TOOLS_SECTION_WIDTH,
    UI_COLORS,
    UNICORN_STAGGER_DELAY,
    UNICORNS,
)
from database import db
from popups import CurriculumPopup, ProblemPopup, StudentSelectorPopup
from session_manager import session_manager
from ui_components import ColorButton, UnicornReward, StatsDisplay


logging.basicConfig(level=logging.INFO)


class MathCanvasApp(App):
    """Year 1 ACARA Mathematics Learning App with full persistence."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._active_unicorns: list[UnicornReward] = []
        self.current_strand: str = 'number'
        self.current_topic: str = 'addition'
        self.stats_display: Optional[StatsDisplay] = None

    def build(self) -> FloatLayout:
        """Build the main application UI."""
        self.title = 'MathCanvas - Year 1'
        root = FloatLayout()

        self.canvas_widget = WriteableCanvas()
        self.canvas_widget.unicorn_callback = self.spawn_unicorns
        root.add_widget(self.canvas_widget)

        self._build_control_bar(root)
        Window.bind(on_keyboard=self._on_keyboard)

        Clock.schedule_once(lambda dt: self._show_student_selector(), 0.5)

        return root

    def _show_student_selector(self) -> None:
        """Show student selector on app start."""
        if not db.enabled:
            logging.info("Running in offline mode (no database)")
            return

        students = session_manager.list_students()
        popup = StudentSelectorPopup(
            students=students,
            on_student_selected=self._on_student_selected,
            on_create_student=self._on_create_student
        )
        popup.open()

    def _on_student_selected(self, student: dict) -> None:
        """Handle student profile selection."""
        session_manager.select_student(student['id'])
        logging.info(f"Selected student: {student['name']}")
        self._update_stats_display()

    def _on_create_student(self, name: str, avatar: str) -> None:
        """Handle new student creation."""
        student = session_manager.create_student(name, avatar)
        if student:
            logging.info(f"Created student: {name}")
            self._update_stats_display()

    def _on_keyboard(self, window, key: int, scancode: int, codepoint: str, modifiers: list) -> bool:
        """Handle keyboard shortcuts."""
        if 'ctrl' in modifiers:
            if codepoint == 'z':
                if 'shift' in modifiers:
                    self.canvas_widget.redo()
                else:
                    self.canvas_widget.undo()
                return True
            elif codepoint == 'y':
                self.canvas_widget.redo()
                return True
            elif codepoint == 's':
                self._save_drawing()
                return True
        return False

    def _build_palette_section(self) -> BoxLayout:
        """Build color palette section."""
        box = BoxLayout(orientation='horizontal', spacing=8, size_hint_x=PALETTE_SECTION_WIDTH)
        box.add_widget(Label(text='Color', font_size=FONT_EMOJI_LARGE, size_hint_x=0.15))
        for color in COLORS.values():
            btn = ColorButton(color_value=color)
            btn.bind(on_release=lambda _, c=color: self._set_color(c))
            box.add_widget(btn)
        return box

    def _build_tools_section(self) -> BoxLayout:
        """Build drawing tools section."""
        box = BoxLayout(orientation='horizontal', spacing=10, size_hint_x=TOOLS_SECTION_WIDTH)
        box.add_widget(Label(text='Size', font_size=FONT_EMOJI_MEDIUM, size_hint_x=0.2))

        slider = Slider(min=MIN_LINE_WIDTH, max=MAX_LINE_WIDTH, value=DEFAULT_LINE_WIDTH, size_hint_x=0.4)
        slider.bind(value=lambda _, v: setattr(self.canvas_widget, 'line_width', v))
        box.add_widget(slider)

        eraser = ToggleButton(
            text='Erase', font_size=18,
            size_hint=(None, 1), width=TOOL_BUTTON_WIDTH,
            background_normal='', background_color=(0.4, 0.4, 0.45, 1)
        )
        eraser.bind(state=lambda _, s: setattr(self.canvas_widget, 'is_eraser', s == 'down'))
        box.add_widget(eraser)

        clear = Button(
            text='Clear', font_size=18,
            size_hint=(None, 1), width=TOOL_BUTTON_WIDTH,
            background_normal='', background_color=(0.8, 0.3, 0.3, 1)
        )
        clear.bind(on_release=lambda _: self._clear_all())
        box.add_widget(clear)

        return box

    def _build_curriculum_section(self) -> BoxLayout:
        """Build curriculum navigation section."""
        box = BoxLayout(orientation='horizontal', spacing=10, size_hint_x=0.30)

        menu_btn = Button(
            text='Curriculum',
            font_size=20,
            size_hint_x=0.5,
            background_normal='',
            background_color=get_color_from_hex('#4CAF50')
        )
        menu_btn.bind(on_release=lambda _: self._open_curriculum())
        box.add_widget(menu_btn)

        quick_btn = Button(
            text='Practice',
            font_size=18,
            size_hint_x=0.5,
            background_normal='',
            background_color=get_color_from_hex('#FF9800')
        )
        quick_btn.bind(on_release=lambda _: self._open_problem())
        box.add_widget(quick_btn)

        return box

    def _build_settings_section(self) -> BoxLayout:
        """Build settings and utilities section."""
        box = BoxLayout(orientation='horizontal', spacing=5, size_hint_x=SETTINGS_SECTION_WIDTH)

        self._bg_btn = Button(
            text='Theme', font_size=14,
            size_hint=(None, 1), width=SMALL_BUTTON_WIDTH,
            background_normal='', background_color=(0.3, 0.3, 0.35, 1)
        )
        self._bg_btn.bind(on_release=self._toggle_background)
        box.add_widget(self._bg_btn)

        save_btn = Button(
            text='Save', font_size=14,
            size_hint=(None, 1), width=SMALL_BUTTON_WIDTH,
            background_normal='', background_color=(0.2, 0.5, 0.7, 1)
        )
        save_btn.bind(on_release=lambda _: self._save_drawing())
        box.add_widget(save_btn)

        return box

    def _build_control_bar(self, parent: FloatLayout) -> None:
        """Build the main control bar."""
        controls = BoxLayout(
            orientation='horizontal',
            size_hint=(1, CONTROL_BAR_HEIGHT_RATIO),
            pos_hint={'top': 1},
            padding=[15, 10],
            spacing=10
        )

        with controls.canvas.before:
            Color(*UI_COLORS['control_bar'])
            self._ctrl_bg = RoundedRectangle(
                pos=controls.pos, size=controls.size, radius=CONTROL_BAR_RADIUS
            )
        controls.bind(pos=self._update_ctrl_bg, size=self._update_ctrl_bg)

        controls.add_widget(self._build_palette_section())
        controls.add_widget(self._build_tools_section())
        controls.add_widget(self._build_curriculum_section())
        controls.add_widget(self._build_settings_section())

        self.stats_display = StatsDisplay(size_hint_x=0.15)
        controls.add_widget(self.stats_display)

        parent.add_widget(controls)

    def _update_ctrl_bg(self, widget: Widget, *args) -> None:
        """Update control bar background."""
        self._ctrl_bg.pos = widget.pos
        self._ctrl_bg.size = widget.size

    def _set_color(self, color: tuple[float, ...]) -> None:
        """Set drawing color."""
        self.canvas_widget.current_color = list(color)
        self.canvas_widget.is_eraser = False

    def _toggle_background(self, btn: Button) -> None:
        """Toggle canvas background theme."""
        keys = list(CANVAS_BACKGROUNDS.keys())
        try:
            idx = (keys.index(self.canvas_widget.background_key) + 1) % len(keys)
        except ValueError:
            idx = 0
        next_key = keys[idx]
        self.canvas_widget.set_background(next_key)

    def _clear_all(self) -> None:
        """Clear canvas and unicorns."""
        for unicorn in self._active_unicorns:
            if unicorn.parent:
                unicorn.parent.remove_widget(unicorn)
        self._active_unicorns.clear()
        self.canvas_widget.clear_canvas()

    def _save_drawing(self) -> None:
        """Save current drawing to database."""
        if not self.canvas_widget.has_content():
            return

        stroke_data = self.canvas_widget.export_strokes()
        result = session_manager.save_current_drawing(
            stroke_data=stroke_data,
            background=self.canvas_widget.background_key
        )

        if result:
            logging.info("Drawing saved successfully")

    def _open_curriculum(self) -> None:
        """Open curriculum navigation popup."""
        popup = CurriculumPopup(on_topic_selected=self._on_topic_selected)
        popup.open()

    def _on_topic_selected(self, strand_id: str, topic_id: str) -> None:
        """Handle topic selection from curriculum menu."""
        self.current_strand = strand_id
        self.current_topic = topic_id
        session_manager.start_session(strand_id, topic_id)
        self._open_problem()

    def _open_problem(self) -> None:
        """Open a problem for the current topic."""
        session_manager.start_problem()
        popup = ProblemPopup(
            strand_id=self.current_strand,
            topic_id=self.current_topic,
            on_answer_submit=self._on_answer_submit
        )
        popup.open()

    def _on_answer_submit(self, student_answer: str, is_correct: bool) -> None:
        """Handle problem answer submission."""
        session_manager.submit_answer(
            strand_id=self.current_strand,
            topic_id=self.current_topic,
            problem_type='general',
            question_text='',
            correct_answer='',
            student_answer=student_answer,
            hint_used=False
        )
        self._update_stats_display()

        if is_correct:
            self._award_extra_unicorns()

    def _update_stats_display(self) -> None:
        """Update the stats display."""
        if self.stats_display:
            summary = session_manager.get_progress_summary()
            attempted = summary.get('problems_attempted', 0)
            correct = summary.get('problems_correct', 0)
            self.stats_display.update_stats(attempted, correct)

    def _award_extra_unicorns(self) -> None:
        """Award extra unicorns for correct answers."""
        if len(self._active_unicorns) < MAX_ACTIVE_UNICORNS:
            for i in range(3):
                self._spawn_single_unicorn(delay=i * 0.1)

    def _spawn_single_unicorn(self, delay: float = 0) -> None:
        """Spawn a single unicorn at random position."""
        width = self.canvas_widget.width
        height = self.canvas_widget.height

        unicorn = UnicornReward(emoji=random.choice(UNICORNS))
        unicorn.x = random.randint(100, int(width - 100))
        unicorn.y = random.randint(100, int(height - 200))

        self._active_unicorns.append(unicorn)
        self.root.add_widget(unicorn)

        Clock.schedule_once(
            lambda dt: unicorn.animate_in(on_complete=self._remove_unicorn),
            delay
        )

    def _remove_unicorn(self, unicorn: UnicornReward) -> None:
        """Remove unicorn from active list and screen."""
        if unicorn in self._active_unicorns:
            self._active_unicorns.remove(unicorn)
        if unicorn.parent:
            unicorn.parent.remove_widget(unicorn)

    def spawn_unicorns(self, strokes: list[Stroke]) -> None:
        """Spawn unicorns after drawing activity."""
        if not strokes or len(self._active_unicorns) >= MAX_ACTIVE_UNICORNS:
            return

        all_points = [p for s in strokes for p in s.points]
        if not all_points:
            return

        xs, ys = zip(*all_points)
        center_x, center_y = sum(xs) / len(xs), sum(ys) / len(ys)
        max_new = MAX_ACTIVE_UNICORNS - len(self._active_unicorns)
        num_unicorns = min(random.randint(1, 5), max_new)

        for i in range(num_unicorns):
            unicorn = UnicornReward(emoji=random.choice(UNICORNS))
            unicorn.x = center_x + random.randint(-50, 50)
            unicorn.y = center_y + random.randint(-30, 30)
            self._active_unicorns.append(unicorn)
            self.root.add_widget(unicorn)
            Clock.schedule_once(
                lambda _, u=unicorn: u.animate_in(on_complete=self._remove_unicorn),
                i * UNICORN_STAGGER_DELAY
            )

    def on_stop(self) -> None:
        """Clean up when app closes."""
        if session_manager.current_session:
            session_manager.end_session()
        return super().on_stop()


if __name__ == '__main__':
    Window.fullscreen = 'auto'
    MathCanvasApp().run()
