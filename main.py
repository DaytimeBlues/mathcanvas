"""
MathCanvas - A Touch-Friendly Math Learning App
================================================
Year 1 ACARA Mathematics Curriculum implementation.
Features:
- Full curriculum navigation across 4 strands
- 18+ topic-specific problem generators
- Visual math problems with emojis
- Undo/redo drawing support
- Unicorn rewards for engagement

Built with Kivy for Windows tablet/pen support.
"""
from __future__ import annotations

import random
import time
from typing import Callable

from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line, Rectangle, RoundedRectangle, InstructionGroup
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

from config import (
    CANVAS_BACKGROUNDS,
    COLORS,
    CONTROL_BAR_HEIGHT_RATIO,
    CONTROL_BAR_RADIUS,
    CONTROL_BAR_TOUCH_THRESHOLD,
    COLOR_BUTTON_SIZE,
    DEFAULT_BACKGROUND,
    DEFAULT_LINE_WIDTH,
    ERASER_WIDTH_MULTIPLIER,
    FONT_EMOJI_LARGE,
    FONT_EMOJI_MEDIUM,
    FONT_HEADER,
    FONT_HINT,
    FONT_MATH_OPERATOR,
    FONT_PROBLEM_DISPLAY,
    FONT_UNICORN,
    MAX_ACTIVE_UNICORNS,
    MAX_LINE_WIDTH,
    MAX_UNDO_STACK,
    MIN_LINE_WIDTH,
    PALETTE_SECTION_WIDTH,
    POPUP_BUTTON_PADDING,
    POPUP_SIZE_HINT,
    SETTINGS_SECTION_WIDTH,
    SMALL_BUTTON_WIDTH,
    STROKE_RECENT_THRESHOLD,
    TOOL_BUTTON_WIDTH,
    TOOLS_SECTION_WIDTH,
    UI_COLORS,
    UNICORN_ANIMATION_DURATION,
    UNICORN_CHECK_DELAY,
    UNICORN_FLOAT_DISTANCE,
    UNICORN_IDLE_THRESHOLD,
    UNICORN_STAGGER_DELAY,
    UNICORN_WIDGET_SIZE,
    UNICORNS,
)

from curriculum import CURRICULUM, get_problem, Problem


# ═══════════════════════════════════════════════════════════════════════════
# STROKE DATA CLASS
# ═══════════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════════
# DRAWING CANVAS WIDGET
# ═══════════════════════════════════════════════════════════════════════════

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
        self._current_instruction: InstructionGroup | None = None
        self.last_draw_time: float = time.time()
        self._unicorn_check_event: Clock.ClockEvent | None = None
        self.unicorn_callback: Callable[[list[Stroke]], None] | None = None
        
        self._init_background()
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _init_background(self) -> None:
        self.canvas.before.clear()
        with self.canvas.before:
            self._bg_color = Color(*self.background_color)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)

    def _update_bg(self, *args) -> None:
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size

    def on_touch_down(self, touch) -> bool:
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
        self._unicorn_check_event = None
        if time.time() - self.last_draw_time >= UNICORN_IDLE_THRESHOLD and self.unicorn_callback:
            recent = [s for s in self.strokes if time.time() - s.time < STROKE_RECENT_THRESHOLD]
            if recent:
                self.unicorn_callback(recent)

    def undo(self) -> bool:
        if not self.strokes:
            return False
        stroke = self.strokes.pop()
        self._undo_stack.append(stroke)
        self.canvas.remove(stroke.instruction)
        return True

    def redo(self) -> bool:
        if not self._undo_stack:
            return False
        stroke = self._undo_stack.pop()
        self.strokes.append(stroke)
        self.canvas.add(stroke.instruction)
        return True

    def clear_canvas(self) -> None:
        if self._unicorn_check_event:
            self._unicorn_check_event.cancel()
            self._unicorn_check_event = None
        self.canvas.clear()
        self.strokes.clear()
        self._undo_stack.clear()
        self._init_background()

    def set_background(self, color_key: str) -> None:
        if color_key not in CANVAS_BACKGROUNDS:
            return
        self.background_key = color_key
        self.background_color = list(CANVAS_BACKGROUNDS[color_key])
        if hasattr(self, '_bg_color'):
            self._bg_color.rgba = self.background_color


# ═══════════════════════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════

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

    def animate_in(self, on_complete: Callable | None = None) -> None:
        anim = Animation(
            y=self.y + UNICORN_FLOAT_DISTANCE,
            opacity=0,
            duration=UNICORN_ANIMATION_DURATION,
            t='out_cubic'
        )
        if on_complete:
            anim.bind(on_complete=lambda *_: on_complete(self))
        anim.start(self)


# ═══════════════════════════════════════════════════════════════════════════
# CURRICULUM NAVIGATION POPUP
# ═══════════════════════════════════════════════════════════════════════════

class CurriculumPopup(Popup):
    """Navigate the Year 1 ACARA Mathematics curriculum."""

    def __init__(self, on_topic_selected: Callable[[str, str], None], **kwargs) -> None:
        super().__init__(**kwargs)
        self.on_topic_selected = on_topic_selected
        
        self.title = ''
        self.separator_height = 0
        self.background = ''
        self.background_color = (0.12, 0.14, 0.18, 0.98)
        self.size_hint = (0.9, 0.85)
        self.auto_dismiss = True
        
        self._build_ui()

    def _build_ui(self) -> None:
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        header = Label(
            text='📚 Year 1 Maths Curriculum',
            font_size=36,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.1
        )
        main_layout.add_widget(header)
        
        # Subtitle
        subtitle = Label(
            text='Australian Curriculum v9.0 • Select a topic to practise',
            font_size=18,
            color=(0.7, 0.7, 0.8, 1),
            size_hint_y=0.05
        )
        main_layout.add_widget(subtitle)
        
        # Strands grid (2x2)
        strands_grid = GridLayout(cols=2, spacing=15, size_hint_y=0.75)
        
        for strand_id, strand_data in CURRICULUM.items():
            strand_box = self._build_strand_card(strand_id, strand_data)
            strands_grid.add_widget(strand_box)
        
        main_layout.add_widget(strands_grid)
        
        # Close button
        close_btn = Button(
            text='✕ Close',
            font_size=20,
            size_hint_y=0.1,
            background_normal='',
            background_color=(0.4, 0.4, 0.45, 1)
        )
        close_btn.bind(on_release=self.dismiss)
        main_layout.add_widget(close_btn)
        
        self.content = main_layout

    def _build_strand_card(self, strand_id: str, strand_data: dict) -> BoxLayout:
        """Build a card for a curriculum strand."""
        card = BoxLayout(orientation='vertical', padding=10, spacing=8)
        
        # Card background
        with card.canvas.before:
            Color(*get_color_from_hex(strand_data['color']), 0.3)
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[15])
        card.bind(pos=lambda w, p: setattr(w._bg, 'pos', p))
        card.bind(size=lambda w, s: setattr(w._bg, 'size', s))
        
        # Strand header
        header = Label(
            text=f"{strand_data['icon']} {strand_data['name']}",
            font_size=24,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.2
        )
        card.add_widget(header)
        
        # Topics scroll
        scroll = ScrollView(size_hint_y=0.8)
        topics_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        topics_layout.bind(minimum_height=topics_layout.setter('height'))
        
        for topic_id, topic_data in strand_data['topics'].items():
            btn = Button(
                text=f"{topic_data['icon']} {topic_data['name']}",
                font_size=16,
                size_hint_y=None,
                height=45,
                background_normal='',
                background_color=get_color_from_hex(strand_data['color'])
            )
            btn.bind(on_release=lambda x, sid=strand_id, tid=topic_id: self._select_topic(sid, tid))
            topics_layout.add_widget(btn)
        
        scroll.add_widget(topics_layout)
        card.add_widget(scroll)
        
        return card

    def _select_topic(self, strand_id: str, topic_id: str) -> None:
        self.dismiss()
        self.on_topic_selected(strand_id, topic_id)


# ═══════════════════════════════════════════════════════════════════════════
# PROBLEM POPUP (Curriculum-Aware)
# ═══════════════════════════════════════════════════════════════════════════

class ProblemPopup(Popup):
    """Display a curriculum-based math problem."""

    def __init__(
        self,
        strand_id: str,
        topic_id: str,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.strand_id = strand_id
        self.topic_id = topic_id
        
        self.title = ''
        self.separator_height = 0
        self.background = ''
        self.background_color = (0.12, 0.14, 0.18, 0.95)
        self.size_hint = POPUP_SIZE_HINT
        self.auto_dismiss = True
        
        self._build_problem()

    def _build_problem(self) -> None:
        """Generate and display a problem."""
        strand = CURRICULUM.get(self.strand_id, {})
        topic = strand.get('topics', {}).get(self.topic_id, {})
        problem = get_problem(self.topic_id)
        
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        
        # Header with topic name
        header_color = strand.get('color', '#4CAF50')
        header = Label(
            text=f"{topic.get('icon', '📝')} {topic.get('name', 'Practice')}",
            font_size=FONT_HEADER,
            color=get_color_from_hex(header_color),
            size_hint_y=0.12
        )
        layout.add_widget(header)
        
        # Visual (if present)
        if problem.visual:
            visual = Label(
                text=problem.visual,
                font_size=32,
                color=(1, 1, 1, 1),
                size_hint_y=0.15
            )
            layout.add_widget(visual)
        
        # Question
        question = Label(
            text=problem.question,
            font_size=FONT_PROBLEM_DISPLAY if len(problem.question) < 20 else 60,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.3
        )
        layout.add_widget(question)
        
        # Hint
        hint = Label(
            text=f"💡 {problem.hint}",
            font_size=FONT_HINT,
            color=(0.7, 0.7, 0.8, 1),
            size_hint_y=0.12
        )
        layout.add_widget(hint)
        
        # Multiple choice (if available)
        if problem.choices:
            choices_row = BoxLayout(size_hint_y=0.15, spacing=10, padding=[20, 0])
            for choice in problem.choices:
                choice_btn = Button(
                    text=str(choice),
                    font_size=24,
                    background_normal='',
                    background_color=(0.3, 0.4, 0.5, 1)
                )
                choices_row.add_widget(choice_btn)
            layout.add_widget(choices_row)
        
        # Buttons row
        btn_row = BoxLayout(size_hint_y=0.16, spacing=20, padding=POPUP_BUTTON_PADDING)
        
        new_btn = Button(
            text='🎲 New Problem',
            font_size=FONT_HINT,
            background_color=get_color_from_hex(header_color),
            background_normal=''
        )
        new_btn.bind(on_release=lambda _: self._refresh())
        
        menu_btn = Button(
            text='📚 Menu',
            font_size=FONT_HINT,
            background_color=(0.4, 0.5, 0.6, 1),
            background_normal=''
        )
        menu_btn.bind(on_release=lambda _: self._back_to_menu())
        
        done_btn = Button(
            text='✓ Done',
            font_size=FONT_HINT,
            background_color=get_color_from_hex(UI_COLORS['done_button']),
            background_normal=''
        )
        done_btn.bind(on_release=self.dismiss)
        
        btn_row.add_widget(new_btn)
        btn_row.add_widget(menu_btn)
        btn_row.add_widget(done_btn)
        layout.add_widget(btn_row)
        
        self.content = layout

    def _refresh(self) -> None:
        self.dismiss()
        ProblemPopup(strand_id=self.strand_id, topic_id=self.topic_id).open()

    def _back_to_menu(self) -> None:
        self.dismiss()
        # This will be handled by the app


# ═══════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════

class MathCanvasApp(App):
    """Year 1 ACARA Mathematics Learning App."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._active_unicorns: list[UnicornReward] = []
        self.current_strand: str = 'number'
        self.current_topic: str = 'addition'

    def build(self) -> FloatLayout:
        self.title = 'MathCanvas 📚 Year 1'
        root = FloatLayout()

        self.canvas_widget = WriteableCanvas()
        self.canvas_widget.unicorn_callback = self.spawn_unicorns
        root.add_widget(self.canvas_widget)

        self._build_control_bar(root)
        Window.bind(on_keyboard=self._on_keyboard)
        
        return root

    def _on_keyboard(self, window, key: int, scancode: int, codepoint: str, modifiers: list) -> bool:
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
        return False

    def _build_palette_section(self) -> BoxLayout:
        box = BoxLayout(orientation='horizontal', spacing=8, size_hint_x=PALETTE_SECTION_WIDTH)
        box.add_widget(Label(text='🎨', font_size=FONT_EMOJI_LARGE, size_hint_x=0.15))
        for color in COLORS.values():
            btn = ColorButton(color_value=color)
            btn.bind(on_release=lambda _, c=color: self._set_color(c))
            box.add_widget(btn)
        return box

    def _build_tools_section(self) -> BoxLayout:
        box = BoxLayout(orientation='horizontal', spacing=10, size_hint_x=TOOLS_SECTION_WIDTH)
        box.add_widget(Label(text='✏️', font_size=FONT_EMOJI_MEDIUM, size_hint_x=0.2))

        slider = Slider(min=MIN_LINE_WIDTH, max=MAX_LINE_WIDTH, value=DEFAULT_LINE_WIDTH, size_hint_x=0.4)
        slider.bind(value=lambda _, v: setattr(self.canvas_widget, 'line_width', v))
        box.add_widget(slider)

        eraser = ToggleButton(
            text='🧽', font_size=FONT_EMOJI_LARGE,
            size_hint=(None, 1), width=TOOL_BUTTON_WIDTH,
            background_normal='', background_color=(0.4, 0.4, 0.45, 1)
        )
        eraser.bind(state=lambda _, s: setattr(self.canvas_widget, 'is_eraser', s == 'down'))
        box.add_widget(eraser)

        clear = Button(
            text='🗑️', font_size=FONT_EMOJI_LARGE,
            size_hint=(None, 1), width=TOOL_BUTTON_WIDTH,
            background_normal='', background_color=(0.8, 0.3, 0.3, 1)
        )
        clear.bind(on_release=lambda _: self._clear_all())
        box.add_widget(clear)

        return box

    def _build_curriculum_section(self) -> BoxLayout:
        """Build the curriculum navigation section."""
        box = BoxLayout(orientation='horizontal', spacing=10, size_hint_x=0.30)
        
        # Curriculum menu button
        menu_btn = Button(
            text='📚 Curriculum',
            font_size=20,
            size_hint_x=0.6,
            background_normal='',
            background_color=get_color_from_hex('#4CAF50')
        )
        menu_btn.bind(on_release=lambda _: self._open_curriculum())
        box.add_widget(menu_btn)
        
        # Quick problem button
        quick_btn = Button(
            text='🎲',
            font_size=28,
            size_hint=(None, 1),
            width=TOOL_BUTTON_WIDTH,
            background_normal='',
            background_color=get_color_from_hex('#FF9800')
        )
        quick_btn.bind(on_release=lambda _: self._open_problem())
        box.add_widget(quick_btn)
        
        return box

    def _build_settings_section(self) -> BoxLayout:
        box = BoxLayout(orientation='horizontal', spacing=5, size_hint_x=SETTINGS_SECTION_WIDTH)
        self._bg_btn = Button(
            text='🌙', font_size=FONT_EMOJI_MEDIUM,
            size_hint=(None, 1), width=SMALL_BUTTON_WIDTH,
            background_normal='', background_color=(0.3, 0.3, 0.35, 1)
        )
        self._bg_btn.bind(on_release=self._toggle_background)
        box.add_widget(self._bg_btn)
        return box

    def _build_control_bar(self, parent: FloatLayout) -> None:
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

        parent.add_widget(controls)

    def _update_ctrl_bg(self, widget: Widget, *args) -> None:
        self._ctrl_bg.pos = widget.pos
        self._ctrl_bg.size = widget.size

    def _set_color(self, color: tuple[float, ...]) -> None:
        self.canvas_widget.current_color = list(color)
        self.canvas_widget.is_eraser = False

    def _toggle_background(self, btn: Button) -> None:
        keys = list(CANVAS_BACKGROUNDS.keys())
        try:
            idx = (keys.index(self.canvas_widget.background_key) + 1) % len(keys)
        except ValueError:
            idx = 0
        next_key = keys[idx]
        self.canvas_widget.set_background(next_key)
        btn.text = '☀️' if next_key == 'slate' else '🌙'

    def _clear_all(self) -> None:
        for unicorn in self._active_unicorns:
            if unicorn.parent:
                unicorn.parent.remove_widget(unicorn)
        self._active_unicorns.clear()
        self.canvas_widget.clear_canvas()

    def _open_curriculum(self) -> None:
        """Open the curriculum navigation popup."""
        popup = CurriculumPopup(on_topic_selected=self._on_topic_selected)
        popup.open()

    def _on_topic_selected(self, strand_id: str, topic_id: str) -> None:
        """Handle topic selection from curriculum menu."""
        self.current_strand = strand_id
        self.current_topic = topic_id
        self._open_problem()

    def _open_problem(self) -> None:
        """Open a problem for the current topic."""
        popup = ProblemPopup(
            strand_id=self.current_strand,
            topic_id=self.current_topic
        )
        popup.open()

    def _remove_unicorn(self, unicorn: UnicornReward) -> None:
        if unicorn in self._active_unicorns:
            self._active_unicorns.remove(unicorn)
        if unicorn.parent:
            unicorn.parent.remove_widget(unicorn)

    def spawn_unicorns(self, strokes: list[Stroke]) -> None:
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


# ═══════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    Window.fullscreen = 'auto'
    MathCanvasApp().run()
