"""
Popups Module
=============
All popup dialogs for MathCanvas with enhanced answer validation and feedback.
"""
from __future__ import annotations

from typing import Callable, Optional

from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex

from config import (
    FONT_HEADER,
    FONT_HINT,
    FONT_PROBLEM_DISPLAY,
    POPUP_BUTTON_PADDING,
    POPUP_SIZE_HINT,
    UI_COLORS,
)
from curriculum import CURRICULUM, get_problem, Problem
from ui_components import StatsDisplay


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
        """Build the curriculum navigation interface."""
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        header = Label(
            text='Year 1 Maths Curriculum',
            font_size=36,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.1
        )
        main_layout.add_widget(header)

        subtitle = Label(
            text='Australian Curriculum v9.0 | Select a topic to practise',
            font_size=18,
            color=(0.7, 0.7, 0.8, 1),
            size_hint_y=0.05
        )
        main_layout.add_widget(subtitle)

        strands_grid = GridLayout(cols=2, spacing=15, size_hint_y=0.75)

        for strand_id, strand_data in CURRICULUM.items():
            strand_box = self._build_strand_card(strand_id, strand_data)
            strands_grid.add_widget(strand_box)

        main_layout.add_widget(strands_grid)

        close_btn = Button(
            text='Close',
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

        with card.canvas.before:
            Color(*get_color_from_hex(strand_data['color']), 0.3)
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[15])
        card.bind(pos=lambda w, p: setattr(w._bg, 'pos', p))
        card.bind(size=lambda w, s: setattr(w._bg, 'size', s))

        header = Label(
            text=f"{strand_data['icon']} {strand_data['name']}",
            font_size=24,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.2
        )
        card.add_widget(header)

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
        """Handle topic selection."""
        self.dismiss()
        self.on_topic_selected(strand_id, topic_id)


class ProblemPopup(Popup):
    """Display a curriculum-based math problem with answer validation."""

    def __init__(
        self,
        strand_id: str,
        topic_id: str,
        on_answer_submit: Optional[Callable[[str, bool], None]] = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.strand_id = strand_id
        self.topic_id = topic_id
        self.on_answer_submit = on_answer_submit
        self.current_problem: Optional[Problem] = None
        self.hint_viewed = False

        self.title = ''
        self.separator_height = 0
        self.background = ''
        self.background_color = (0.12, 0.14, 0.18, 0.95)
        self.size_hint = POPUP_SIZE_HINT
        self.auto_dismiss = True

        self._build_problem()

    def _build_problem(self) -> None:
        """Generate and display a problem with answer input."""
        strand = CURRICULUM.get(self.strand_id, {})
        topic = strand.get('topics', {}).get(self.topic_id, {})
        self.current_problem = get_problem(self.topic_id)

        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)

        header_color = strand.get('color', '#4CAF50')
        header = Label(
            text=f"{topic.get('icon', '')} {topic.get('name', 'Practice')}",
            font_size=FONT_HEADER,
            color=get_color_from_hex(header_color),
            size_hint_y=0.1
        )
        layout.add_widget(header)

        if self.current_problem.visual:
            visual = Label(
                text=self.current_problem.visual,
                font_size=32,
                color=(1, 1, 1, 1),
                size_hint_y=0.12
            )
            layout.add_widget(visual)

        question = Label(
            text=self.current_problem.question,
            font_size=FONT_PROBLEM_DISPLAY if len(self.current_problem.question) < 20 else 60,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.2
        )
        layout.add_widget(question)

        self.hint_label = Label(
            text='',
            font_size=FONT_HINT,
            color=(0.7, 0.7, 0.8, 1),
            size_hint_y=0.1
        )
        layout.add_widget(self.hint_label)

        self.feedback_label = Label(
            text='',
            font_size=24,
            bold=True,
            size_hint_y=0.1
        )
        layout.add_widget(self.feedback_label)

        if self.current_problem.choices:
            self._add_multiple_choice(layout, header_color)
        else:
            self._add_text_input(layout)

        self._add_buttons(layout, header_color)

        self.content = layout

    def _add_multiple_choice(self, layout: BoxLayout, header_color: str) -> None:
        """Add multiple choice buttons."""
        choices_grid = GridLayout(cols=2, size_hint_y=0.2, spacing=10, padding=[20, 0])

        for choice in self.current_problem.choices:
            choice_btn = Button(
                text=str(choice),
                font_size=24,
                background_normal='',
                background_color=get_color_from_hex(header_color) if header_color else (0.3, 0.4, 0.5, 1)
            )
            choice_btn.bind(on_release=lambda btn, c=choice: self._check_answer(str(c)))
            choices_grid.add_widget(choice_btn)

        layout.add_widget(choices_grid)

    def _add_text_input(self, layout: BoxLayout) -> None:
        """Add text input for answer."""
        input_box = BoxLayout(size_hint_y=0.15, padding=[50, 0])

        self.answer_input = TextInput(
            hint_text='Type your answer here...',
            font_size=28,
            multiline=False,
            input_filter='int' if isinstance(self.current_problem.answer, int) else None
        )
        self.answer_input.bind(on_text_validate=lambda _: self._check_answer(self.answer_input.text))

        input_box.add_widget(self.answer_input)
        layout.add_widget(input_box)

        submit_btn = Button(
            text='Submit Answer',
            font_size=FONT_HINT,
            size_hint_y=0.1,
            background_normal='',
            background_color=get_color_from_hex('#4CAF50')
        )
        submit_btn.bind(on_release=lambda _: self._check_answer(self.answer_input.text))
        layout.add_widget(submit_btn)

    def _add_buttons(self, layout: BoxLayout, header_color: str) -> None:
        """Add control buttons."""
        btn_row = BoxLayout(size_hint_y=0.13, spacing=20, padding=POPUP_BUTTON_PADDING)

        hint_btn = Button(
            text='Show Hint',
            font_size=FONT_HINT,
            background_color=(0.8, 0.6, 0.2, 1),
            background_normal=''
        )
        hint_btn.bind(on_release=self._show_hint)

        new_btn = Button(
            text='New Problem',
            font_size=FONT_HINT,
            background_color=get_color_from_hex(header_color) if header_color else (0.3, 0.4, 0.5, 1),
            background_normal=''
        )
        new_btn.bind(on_release=lambda _: self._refresh())

        done_btn = Button(
            text='Done',
            font_size=FONT_HINT,
            background_color=get_color_from_hex(UI_COLORS['done_button']),
            background_normal=''
        )
        done_btn.bind(on_release=self.dismiss)

        btn_row.add_widget(hint_btn)
        btn_row.add_widget(new_btn)
        btn_row.add_widget(done_btn)
        layout.add_widget(btn_row)

    def _show_hint(self, btn: Button) -> None:
        """Show hint for current problem."""
        if self.current_problem:
            self.hint_label.text = f"Hint: {self.current_problem.hint}"
            self.hint_viewed = True
            btn.disabled = True

    def _check_answer(self, student_answer: str) -> None:
        """Check if the answer is correct."""
        if not student_answer.strip():
            return

        correct_answer = str(self.current_problem.answer).strip().lower()
        student_answer = student_answer.strip().lower()
        is_correct = correct_answer == student_answer

        if is_correct:
            self.feedback_label.text = 'Correct! Well done!'
            self.feedback_label.color = (0.2, 0.8, 0.2, 1)
        else:
            self.feedback_label.text = f'Not quite. The answer is {self.current_problem.answer}'
            self.feedback_label.color = (0.9, 0.3, 0.3, 1)

        if self.on_answer_submit:
            self.on_answer_submit(student_answer, is_correct)

    def _refresh(self) -> None:
        """Load a new problem."""
        self.dismiss()
        ProblemPopup(
            strand_id=self.strand_id,
            topic_id=self.topic_id,
            on_answer_submit=self.on_answer_submit
        ).open()


class StudentSelectorPopup(Popup):
    """Select or create student profiles."""

    def __init__(
        self,
        students: list[dict],
        on_student_selected: Callable[[dict], None],
        on_create_student: Callable[[str, str], None],
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.students = students
        self.on_student_selected = on_student_selected
        self.on_create_student = on_create_student

        self.title = ''
        self.separator_height = 0
        self.background = ''
        self.background_color = (0.12, 0.14, 0.18, 0.98)
        self.size_hint = (0.7, 0.75)
        self.auto_dismiss = False

        self._build_ui()

    def _build_ui(self) -> None:
        """Build student selector interface."""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        header = Label(
            text='Select Your Profile',
            font_size=32,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.12
        )
        layout.add_widget(header)

        if self.students:
            scroll = ScrollView(size_hint_y=0.6)
            students_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
            students_layout.bind(minimum_height=students_layout.setter('height'))

            for student in self.students:
                btn = Button(
                    text=f"{student.get('avatar_emoji', '🎓')} {student['name']} | {student.get('total_problems_solved', 0)} problems solved",
                    font_size=22,
                    size_hint_y=None,
                    height=60,
                    background_normal='',
                    background_color=(0.25, 0.35, 0.45, 1)
                )
                btn.bind(on_release=lambda _, s=student: self._select_student(s))
                students_layout.add_widget(btn)

            scroll.add_widget(students_layout)
            layout.add_widget(scroll)
        else:
            info = Label(
                text='No profiles yet. Create one to get started!',
                font_size=18,
                color=(0.7, 0.7, 0.8, 1),
                size_hint_y=0.15
            )
            layout.add_widget(info)

        create_section = BoxLayout(orientation='vertical', size_hint_y=0.28, spacing=10)

        create_label = Label(
            text='Create New Profile:',
            font_size=20,
            color=(1, 1, 1, 1),
            size_hint_y=0.3
        )
        create_section.add_widget(create_label)

        self.name_input = TextInput(
            hint_text='Enter your name...',
            font_size=20,
            multiline=False,
            size_hint_y=0.35
        )
        create_section.add_widget(self.name_input)

        create_btn = Button(
            text='Create Profile',
            font_size=20,
            background_normal='',
            background_color=(0.2, 0.6, 0.3, 1),
            size_hint_y=0.35
        )
        create_btn.bind(on_release=self._create_new)
        create_section.add_widget(create_btn)

        layout.add_widget(create_section)

        self.content = layout

    def _select_student(self, student: dict) -> None:
        """Handle student selection."""
        self.dismiss()
        self.on_student_selected(student)

    def _create_new(self, btn: Button) -> None:
        """Handle new student creation."""
        name = self.name_input.text.strip()
        if name:
            self.dismiss()
            self.on_create_student(name, '🎓')
