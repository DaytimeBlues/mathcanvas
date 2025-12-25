"""
MathCanvas - A Touch-Friendly Math Learning App
================================================
Year 1 ACARA Mathematics Curriculum with Gemini AI answer checking.
Features:
- Problem overlay on canvas - write your answer!
- Gemini 2.0 Flash OCR reads handwriting
- Voice feedback with Gemini TTS
- Unicorn rewards for correct answers

Built with Kivy for Windows tablet/pen support.
"""
from __future__ import annotations

import random
import time
import io
from typing import Callable
from threading import Thread

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

# Screenshot capture
try:
    from PIL import Image
    import pyautogui
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False
    print("⚠️ pyautogui not available for screenshots")

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
    FONT_PROBLEM_DISPLAY,
    FONT_UNICORN,
    MAX_ACTIVE_UNICORNS,
    MAX_LINE_WIDTH,
    MAX_UNDO_STACK,
    MIN_LINE_WIDTH,
    PALETTE_SECTION_WIDTH,
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

# Gemini AI
try:
    from gemini_client import check_answer, speak_feedback, is_available as gemini_available
    from gemini_client import CORRECT_MESSAGES, INCORRECT_MESSAGES
    GEMINI_READY = True
except ImportError:
    GEMINI_READY = False
    CORRECT_MESSAGES = ["Correct!"]
    INCORRECT_MESSAGES = ["Try again!"]
    print("⚠️ gemini_client not available")


# ═══════════════════════════════════════════════════════════════════════════
# STROKE DATA CLASS
# ═══════════════════════════════════════════════════════════════════════════

class Stroke:
    """Represents a single drawing stroke with its canvas instruction."""
    __slots__ = ('points', 'color', 'width', 'time', 'instruction')
    
    def __init__(self, points: list, color: list, width: float, instruction: InstructionGroup) -> None:
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
        self._current_stroke_points: list = []
        self._current_instruction: InstructionGroup | None = None
        self.last_draw_time: float = time.time()
        self._unicorn_check_event = None
        self.unicorn_callback = None
        
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
        # Allow touches in top 12% (control bar) and bottom 10% (problem bar)
        if touch.y > self.height * 0.88 or touch.y < self.height * 0.10:
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

        self._current_stroke_points = []
        self._current_instruction = None
        return True

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

    def get_screenshot(self) -> Image.Image | None:
        """Capture the canvas area as a PIL Image."""
        if not SCREENSHOT_AVAILABLE:
            return None
        try:
            # Get window position and canvas bounds
            # Capture area between control bar and problem bar
            x = int(Window.left)
            y = int(Window.top)
            w = int(Window.width)
            h = int(Window.height)
            
            # Exclude top 12% (controls) and bottom 10% (problem bar)
            top_offset = int(h * 0.12)
            bottom_offset = int(h * 0.10)
            
            screenshot = pyautogui.screenshot(region=(
                x, y + top_offset,
                w, h - top_offset - bottom_offset
            ))
            return screenshot
        except Exception as e:
            print(f"Screenshot error: {e}")
            return None


# ═══════════════════════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════

class ColorButton(Button):
    color_value = ListProperty([0, 0, 0, 1])

    def __init__(self, color_value, **kwargs) -> None:
        super().__init__(**kwargs)
        self.color_value = list(color_value)
        self.background_normal = ''
        self.background_color = color_value
        self.size_hint = (None, None)
        self.size = COLOR_BUTTON_SIZE
        self.border = (0, 0, 0, 0)


class UnicornReward(Label):
    def __init__(self, emoji: str = '🦄', **kwargs) -> None:
        super().__init__(**kwargs)
        self.text = emoji
        self.font_size = FONT_UNICORN
        self.opacity = 1
        self.size_hint = (None, None)
        self.size = UNICORN_WIDGET_SIZE

    def animate_in(self, on_complete=None) -> None:
        anim = Animation(y=self.y + UNICORN_FLOAT_DISTANCE, opacity=0,
                        duration=UNICORN_ANIMATION_DURATION, t='out_cubic')
        if on_complete:
            anim.bind(on_complete=lambda *_: on_complete(self))
        anim.start(self)


# ═══════════════════════════════════════════════════════════════════════════
# CURRICULUM NAVIGATION POPUP
# ═══════════════════════════════════════════════════════════════════════════

class CurriculumPopup(Popup):
    def __init__(self, on_topic_selected, **kwargs) -> None:
        super().__init__(**kwargs)
        self.on_topic_selected = on_topic_selected
        self.title = ''
        self.separator_height = 0
        self.background = ''
        self.background_color = (0.12, 0.14, 0.18, 0.98)
        self.size_hint = (0.9, 0.85)
        self._build_ui()

    def _build_ui(self) -> None:
        main = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        main.add_widget(Label(text='📚 Year 1 Maths', font_size=36, bold=True,
                              color=(1,1,1,1), size_hint_y=0.1))
        main.add_widget(Label(text='Select a topic to practise', font_size=18,
                              color=(0.7,0.7,0.8,1), size_hint_y=0.05))
        
        grid = GridLayout(cols=2, spacing=15, size_hint_y=0.75)
        for strand_id, strand in CURRICULUM.items():
            grid.add_widget(self._build_strand_card(strand_id, strand))
        main.add_widget(grid)
        
        close = Button(text='✕ Close', font_size=20, size_hint_y=0.1,
                      background_normal='', background_color=(0.4,0.4,0.45,1))
        close.bind(on_release=self.dismiss)
        main.add_widget(close)
        self.content = main

    def _build_strand_card(self, strand_id: str, strand: dict) -> BoxLayout:
        card = BoxLayout(orientation='vertical', padding=10, spacing=8)
        with card.canvas.before:
            Color(*get_color_from_hex(strand['color']), 0.3)
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[15])
        card.bind(pos=lambda w,p: setattr(w._bg, 'pos', p))
        card.bind(size=lambda w,s: setattr(w._bg, 'size', s))
        
        card.add_widget(Label(text=f"{strand['icon']} {strand['name']}", font_size=24,
                             bold=True, color=(1,1,1,1), size_hint_y=0.2))
        
        scroll = ScrollView(size_hint_y=0.8)
        topics = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        topics.bind(minimum_height=topics.setter('height'))
        
        for tid, topic in strand['topics'].items():
            btn = Button(text=f"{topic['icon']} {topic['name']}", font_size=16,
                        size_hint_y=None, height=45, background_normal='',
                        background_color=get_color_from_hex(strand['color']))
            btn.bind(on_release=lambda x, s=strand_id, t=tid: self._select(s, t))
            topics.add_widget(btn)
        
        scroll.add_widget(topics)
        card.add_widget(scroll)
        return card

    def _select(self, strand_id: str, topic_id: str) -> None:
        self.dismiss()
        self.on_topic_selected(strand_id, topic_id)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════

class MathCanvasApp(App):
    """Year 1 ACARA Mathematics with AI answer checking."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._active_unicorns: list = []
        self.current_strand = 'number'
        self.current_topic = 'addition'
        self.current_problem: Problem | None = None
        self._checking = False

    def build(self) -> FloatLayout:
        self.title = 'MathCanvas 📚 Year 1'
        root = FloatLayout()

        # Canvas (middle area)
        self.canvas_widget = WriteableCanvas()
        root.add_widget(self.canvas_widget)

        # Control bar (top)
        self._build_control_bar(root)
        
        # Problem bar (bottom)
        self._build_problem_bar(root)
        
        # Load first problem
        Clock.schedule_once(lambda dt: self._new_problem(), 0.5)
        
        Window.bind(on_keyboard=self._on_keyboard)
        return root

    def _on_keyboard(self, window, key, scancode, codepoint, modifiers) -> bool:
        if 'ctrl' in modifiers:
            if codepoint == 'z':
                self.canvas_widget.redo() if 'shift' in modifiers else self.canvas_widget.undo()
                return True
            elif codepoint == 'y':
                self.canvas_widget.redo()
                return True
        return False

    # ─── Control Bar ───

    def _build_control_bar(self, parent: FloatLayout) -> None:
        controls = BoxLayout(
            orientation='horizontal',
            size_hint=(1, CONTROL_BAR_HEIGHT_RATIO),
            pos_hint={'top': 1},
            padding=[15, 10], spacing=10
        )
        with controls.canvas.before:
            Color(*UI_COLORS['control_bar'])
            self._ctrl_bg = RoundedRectangle(pos=controls.pos, size=controls.size,
                                             radius=CONTROL_BAR_RADIUS)
        controls.bind(pos=lambda w,p: setattr(self._ctrl_bg, 'pos', p))
        controls.bind(size=lambda w,s: setattr(self._ctrl_bg, 'size', s))

        # Colors
        colors = BoxLayout(spacing=8, size_hint_x=PALETTE_SECTION_WIDTH)
        colors.add_widget(Label(text='🎨', font_size=FONT_EMOJI_LARGE, size_hint_x=0.15))
        for c in COLORS.values():
            btn = ColorButton(color_value=c)
            btn.bind(on_release=lambda x, col=c: self._set_color(col))
            colors.add_widget(btn)
        controls.add_widget(colors)

        # Tools
        tools = BoxLayout(spacing=10, size_hint_x=TOOLS_SECTION_WIDTH)
        tools.add_widget(Label(text='✏️', font_size=FONT_EMOJI_MEDIUM, size_hint_x=0.2))
        slider = Slider(min=MIN_LINE_WIDTH, max=MAX_LINE_WIDTH, value=DEFAULT_LINE_WIDTH, size_hint_x=0.4)
        slider.bind(value=lambda s,v: setattr(self.canvas_widget, 'line_width', v))
        tools.add_widget(slider)
        eraser = ToggleButton(text='🧽', font_size=FONT_EMOJI_LARGE, size_hint=(None,1),
                             width=TOOL_BUTTON_WIDTH, background_normal='',
                             background_color=(0.4,0.4,0.45,1))
        eraser.bind(state=lambda b,s: setattr(self.canvas_widget, 'is_eraser', s=='down'))
        tools.add_widget(eraser)
        clear = Button(text='🗑️', font_size=FONT_EMOJI_LARGE, size_hint=(None,1),
                      width=TOOL_BUTTON_WIDTH, background_normal='',
                      background_color=(0.8,0.3,0.3,1))
        clear.bind(on_release=lambda x: self._clear_canvas())
        tools.add_widget(clear)
        controls.add_widget(tools)

        # Curriculum
        curr = BoxLayout(spacing=10, size_hint_x=0.25)
        menu = Button(text='📚 Topics', font_size=18, background_normal='',
                     background_color=get_color_from_hex('#4CAF50'))
        menu.bind(on_release=lambda x: CurriculumPopup(self._on_topic_selected).open())
        curr.add_widget(menu)
        controls.add_widget(curr)

        # Settings
        settings = BoxLayout(spacing=5, size_hint_x=SETTINGS_SECTION_WIDTH)
        self._bg_btn = Button(text='🌙', font_size=FONT_EMOJI_MEDIUM, size_hint=(None,1),
                             width=SMALL_BUTTON_WIDTH, background_normal='',
                             background_color=(0.3,0.3,0.35,1))
        self._bg_btn.bind(on_release=self._toggle_background)
        settings.add_widget(self._bg_btn)
        controls.add_widget(settings)

        parent.add_widget(controls)

    # ─── Problem Bar (Bottom) ───

    def _build_problem_bar(self, parent: FloatLayout) -> None:
        bar = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.10),
            pos_hint={'y': 0},
            padding=[20, 8], spacing=15
        )
        with bar.canvas.before:
            Color(0.15, 0.17, 0.22, 0.95)
            self._prob_bg = RoundedRectangle(pos=bar.pos, size=bar.size, radius=[20, 20, 0, 0])
        bar.bind(pos=lambda w,p: setattr(self._prob_bg, 'pos', p))
        bar.bind(size=lambda w,s: setattr(self._prob_bg, 'size', s))

        # Problem text
        self._problem_label = Label(
            text='Loading...',
            font_size=36,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_x=0.45,
            halign='left'
        )
        bar.add_widget(self._problem_label)

        # Feedback label
        self._feedback_label = Label(
            text='',
            font_size=20,
            color=(0.7, 0.8, 0.9, 1),
            size_hint_x=0.20
        )
        bar.add_widget(self._feedback_label)

        # Buttons
        btns = BoxLayout(spacing=10, size_hint_x=0.35)
        
        self._check_btn = Button(
            text='✓ Check',
            font_size=20,
            background_normal='',
            background_color=get_color_from_hex('#4CAF50')
        )
        self._check_btn.bind(on_release=lambda x: self._check_answer())
        btns.add_widget(self._check_btn)

        new_btn = Button(
            text='🎲 New',
            font_size=20,
            background_normal='',
            background_color=get_color_from_hex('#FF9800')
        )
        new_btn.bind(on_release=lambda x: self._new_problem())
        btns.add_widget(new_btn)

        skip_btn = Button(
            text='⏭️',
            font_size=24,
            size_hint_x=0.3,
            background_normal='',
            background_color=(0.4, 0.4, 0.5, 1)
        )
        skip_btn.bind(on_release=lambda x: self._new_problem())
        btns.add_widget(skip_btn)

        bar.add_widget(btns)
        parent.add_widget(bar)

    # ─── Event Handlers ───

    def _set_color(self, color) -> None:
        self.canvas_widget.current_color = list(color)
        self.canvas_widget.is_eraser = False

    def _toggle_background(self, btn) -> None:
        keys = list(CANVAS_BACKGROUNDS.keys())
        idx = (keys.index(self.canvas_widget.background_key) + 1) % len(keys)
        self.canvas_widget.set_background(keys[idx])
        btn.text = '☀️' if keys[idx] == 'slate' else '🌙'

    def _clear_canvas(self) -> None:
        for u in self._active_unicorns:
            if u.parent:
                u.parent.remove_widget(u)
        self._active_unicorns.clear()
        self.canvas_widget.clear_canvas()
        self._feedback_label.text = ''

    def _on_topic_selected(self, strand_id: str, topic_id: str) -> None:
        self.current_strand = strand_id
        self.current_topic = topic_id
        self._new_problem()

    def _new_problem(self) -> None:
        """Generate a new problem for the current topic."""
        self.current_problem = get_problem(self.current_topic)
        self._problem_label.text = f"📝 {self.current_problem.question}"
        self._feedback_label.text = ''
        self._clear_canvas()

    def _check_answer(self) -> None:
        """Capture canvas and check answer with Gemini AI."""
        if self._checking or not self.current_problem:
            return
        
        self._checking = True
        self._check_btn.text = '⏳...'
        self._feedback_label.text = 'Checking...'
        
        # Run AI check in background thread
        def do_check():
            result_correct = False
            feedback = "Let me see..."
            
            if GEMINI_READY and gemini_available():
                # Get screenshot
                img = self.canvas_widget.get_screenshot()
                if img:
                    from gemini_client import check_answer
                    result = check_answer(
                        img,
                        self.current_problem.question,
                        self.current_problem.answer
                    )
                    result_correct = result.is_correct
                    feedback = result.feedback
                else:
                    feedback = "Couldn't capture your answer"
            else:
                # Fallback: random result for demo
                result_correct = random.choice([True, True, False])
                feedback = random.choice(CORRECT_MESSAGES if result_correct else INCORRECT_MESSAGES)
            
            # Update UI on main thread
            Clock.schedule_once(lambda dt: self._show_result(result_correct, feedback), 0)
        
        Thread(target=do_check, daemon=True).start()

    def _show_result(self, correct: bool, feedback: str) -> None:
        """Display result and play feedback."""
        self._checking = False
        self._check_btn.text = '✓ Check'
        self._feedback_label.text = feedback
        
        if correct:
            self._feedback_label.color = (0.3, 0.9, 0.3, 1)  # Green
            self._spawn_unicorns()
            # Auto next problem after delay
            Clock.schedule_once(lambda dt: self._new_problem(), 3.0)
        else:
            self._feedback_label.color = (0.9, 0.6, 0.3, 1)  # Orange
        
        # TTS feedback (in background)
        if GEMINI_READY:
            Thread(target=lambda: speak_feedback(feedback), daemon=True).start()

    def _spawn_unicorns(self) -> None:
        """Spawn celebratory unicorns!"""
        if len(self._active_unicorns) >= MAX_ACTIVE_UNICORNS:
            return
        
        center_x = Window.width / 2
        center_y = Window.height / 2
        
        for i in range(5):
            unicorn = UnicornReward(emoji=random.choice(UNICORNS))
            unicorn.x = center_x + random.randint(-100, 100)
            unicorn.y = center_y + random.randint(-50, 50)
            self._active_unicorns.append(unicorn)
            self.root.add_widget(unicorn)
            Clock.schedule_once(
                lambda dt, u=unicorn: u.animate_in(on_complete=self._remove_unicorn),
                i * 0.1
            )

    def _remove_unicorn(self, unicorn) -> None:
        if unicorn in self._active_unicorns:
            self._active_unicorns.remove(unicorn)
        if unicorn.parent:
            unicorn.parent.remove_widget(unicorn)


# ═══════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    Window.fullscreen = 'auto'
    MathCanvasApp().run()
