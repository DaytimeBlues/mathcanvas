"""
Session Manager Module
======================
Manages learning sessions, progress tracking, and student state.
"""
from __future__ import annotations

import time
import logging
from typing import Optional
from datetime import datetime

from database import db, DatabaseManager


class SessionManager:
    """Manages student learning sessions and progress tracking."""

    def __init__(self, database: DatabaseManager = db) -> None:
        self.db = database
        self.current_student: Optional[dict] = None
        self.current_session: Optional[dict] = None
        self.session_start_time: Optional[float] = None
        self.problems_attempted: int = 0
        self.problems_correct: int = 0
        self.current_problem_start: Optional[float] = None

    def select_student(self, student_id: str) -> bool:
        """Select a student for the current session."""
        student = self.db.get_student(student_id)
        if student:
            self.current_student = student
            logging.info(f"Selected student: {student['name']}")
            return True
        return False

    def create_student(self, name: str, avatar_emoji: str = '🎓') -> Optional[dict]:
        """Create a new student profile."""
        student = self.db.create_student(name, avatar_emoji)
        if student:
            self.current_student = student
            logging.info(f"Created and selected student: {name}")
        return student

    def list_students(self) -> list[dict]:
        """List all available students."""
        return self.db.list_students()

    def start_session(self, strand_id: str, topic_id: str) -> bool:
        """Start a new learning session."""
        if not self.current_student:
            logging.warning("No student selected")
            return False

        session = self.db.start_session(
            self.current_student['id'],
            strand_id,
            topic_id
        )

        if session:
            self.current_session = session
            self.session_start_time = time.time()
            self.problems_attempted = 0
            self.problems_correct = 0
            logging.info(f"Started session: {strand_id}/{topic_id}")
            return True

        return False

    def end_session(self) -> bool:
        """End the current learning session."""
        if not self.current_session or not self.session_start_time:
            return False

        duration = int(time.time() - self.session_start_time)

        result = self.db.end_session(
            self.current_session['id'],
            duration,
            self.problems_attempted,
            self.problems_correct
        )

        if result:
            self._check_session_milestones()
            self.current_session = None
            self.session_start_time = None
            logging.info("Session ended successfully")
            return True

        return False

    def start_problem(self) -> None:
        """Mark the start of a new problem."""
        self.current_problem_start = time.time()

    def submit_answer(
        self,
        strand_id: str,
        topic_id: str,
        problem_type: str,
        question_text: str,
        correct_answer: str,
        student_answer: str,
        hint_used: bool = False
    ) -> bool:
        """Submit a problem answer and record the attempt."""
        if not self.current_student or not self.current_session:
            logging.warning("No active session for answer submission")
            return False

        time_spent = int(time.time() - self.current_problem_start) if self.current_problem_start else 0
        is_correct = self._check_answer(correct_answer, student_answer)

        self.db.record_problem_attempt(
            session_id=self.current_session['id'],
            student_id=self.current_student['id'],
            strand_id=strand_id,
            topic_id=topic_id,
            problem_type=problem_type,
            question_text=question_text,
            correct_answer=correct_answer,
            student_answer=student_answer,
            is_correct=is_correct,
            hint_used=hint_used,
            time_spent_seconds=time_spent
        )

        self.problems_attempted += 1
        if is_correct:
            self.problems_correct += 1
            self._check_problem_milestones()

        self.current_problem_start = None
        return is_correct

    def _check_answer(self, correct: str, student: str) -> bool:
        """Check if student answer is correct."""
        correct_str = str(correct).strip().lower()
        student_str = str(student).strip().lower()
        return correct_str == student_str

    def _check_session_milestones(self) -> None:
        """Check and award session-based milestones."""
        if not self.current_student or not self.current_session:
            return

        student_id = self.current_student['id']
        strand_id = self.current_session['strand_id']
        topic_id = self.current_session['topic_id']

        if self.problems_correct >= 5:
            self.db.award_milestone(
                student_id,
                'topic_5_correct',
                strand_id,
                topic_id,
                {'session_id': self.current_session['id']}
            )

        if self.problems_correct >= 10:
            self.db.award_milestone(
                student_id,
                'topic_10_correct',
                strand_id,
                topic_id,
                {'session_id': self.current_session['id']}
            )

        if self.problems_attempted > 0:
            accuracy = (self.problems_correct / self.problems_attempted) * 100
            if accuracy >= 80 and self.problems_attempted >= 5:
                self.db.award_milestone(
                    student_id,
                    'high_accuracy',
                    strand_id,
                    topic_id,
                    {'accuracy': accuracy}
                )

    def _check_problem_milestones(self) -> None:
        """Check and award problem-based milestones."""
        if not self.current_student:
            return

        student_id = self.current_student['id']
        total_solved = self.current_student['total_problems_solved'] + self.problems_correct

        milestone_thresholds = [1, 10, 25, 50, 100, 250, 500]
        for threshold in milestone_thresholds:
            if total_solved == threshold:
                self.db.award_milestone(
                    student_id,
                    f'problems_solved_{threshold}',
                    metadata={'total': threshold}
                )

    def save_current_drawing(self, stroke_data: dict, background: str = 'cream') -> bool:
        """Save the current canvas drawing."""
        if not self.current_student:
            return False

        result = self.db.save_drawing(
            student_id=self.current_student['id'],
            stroke_data=stroke_data,
            session_id=self.current_session['id'] if self.current_session else None,
            canvas_background=background
        )

        return result is not None

    def get_progress_summary(self) -> dict:
        """Get a summary of current student progress."""
        if not self.current_student:
            return {}

        return {
            'student': self.current_student,
            'session': self.current_session,
            'problems_attempted': self.problems_attempted,
            'problems_correct': self.problems_correct,
            'accuracy': (self.problems_correct / self.problems_attempted * 100)
                       if self.problems_attempted > 0 else 0,
        }

    def get_topic_history(self, strand_id: str, topic_id: str) -> dict:
        """Get historical performance for a topic."""
        if not self.current_student:
            return {}

        return self.db.get_topic_stats(
            self.current_student['id'],
            strand_id,
            topic_id
        )


session_manager = SessionManager()
