"""
Database Operations Module
===========================
Handles all Supabase database operations for MathCanvas.
Manages students, sessions, problem attempts, drawings, and milestones.
"""
from __future__ import annotations

import os
import logging
from typing import Any, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    from supabase import create_client, Client
except ImportError:
    logging.warning("Supabase client not installed. Database features disabled.")
    create_client = None
    Client = None


@dataclass
class Student:
    """Student profile data."""
    id: str
    name: str
    grade_level: str
    avatar_emoji: str
    total_problems_solved: int
    total_unicorns_earned: int
    created_at: datetime
    last_active: datetime


@dataclass
class LearningSession:
    """Learning session data."""
    id: str
    student_id: str
    started_at: datetime
    ended_at: Optional[datetime]
    strand_id: str
    topic_id: str
    problems_attempted: int
    problems_correct: int
    duration_seconds: int


@dataclass
class ProblemAttempt:
    """Problem attempt record."""
    id: str
    session_id: str
    student_id: str
    strand_id: str
    topic_id: str
    problem_type: str
    question_text: str
    correct_answer: str
    student_answer: Optional[str]
    is_correct: Optional[bool]
    hint_used: bool
    time_spent_seconds: int
    attempted_at: datetime


class DatabaseManager:
    """Manages all database operations for MathCanvas."""

    def __init__(self) -> None:
        self.client: Optional[Client] = None
        self.enabled = False
        self._init_client()

    def _init_client(self) -> None:
        """Initialize Supabase client from environment variables."""
        if create_client is None:
            logging.warning("Supabase not available. Running in offline mode.")
            return

        try:
            url = os.getenv('VITE_SUPABASE_URL')
            key = os.getenv('VITE_SUPABASE_ANON_KEY')

            if url and key:
                self.client = create_client(url, key)
                self.enabled = True
                logging.info("Database connection established")
            else:
                logging.warning("Database credentials not found. Running in offline mode.")
        except Exception as e:
            logging.error(f"Failed to initialize database: {e}")
            self.enabled = False

    def create_student(self, name: str, avatar_emoji: str = '🎓') -> Optional[dict]:
        """Create a new student profile."""
        if not self.enabled:
            return None

        try:
            response = self.client.table('students').insert({
                'name': name,
                'avatar_emoji': avatar_emoji,
                'grade_level': 'year_1',
            }).execute()

            if response.data:
                logging.info(f"Created student: {name}")
                return response.data[0]
        except Exception as e:
            logging.error(f"Failed to create student: {e}")

        return None

    def get_student(self, student_id: str) -> Optional[dict]:
        """Get student by ID."""
        if not self.enabled:
            return None

        try:
            response = self.client.table('students').select('*').eq('id', student_id).maybeSingle().execute()
            return response.data
        except Exception as e:
            logging.error(f"Failed to get student: {e}")
            return None

    def list_students(self) -> list[dict]:
        """List all students."""
        if not self.enabled:
            return []

        try:
            response = self.client.table('students').select('*').order('last_active', desc=True).execute()
            return response.data or []
        except Exception as e:
            logging.error(f"Failed to list students: {e}")
            return []

    def update_student(self, student_id: str, **kwargs) -> Optional[dict]:
        """Update student profile."""
        if not self.enabled:
            return None

        try:
            response = self.client.table('students').update(kwargs).eq('id', student_id).execute()
            if response.data:
                return response.data[0]
        except Exception as e:
            logging.error(f"Failed to update student: {e}")

        return None

    def start_session(
        self,
        student_id: str,
        strand_id: str,
        topic_id: str
    ) -> Optional[dict]:
        """Start a new learning session."""
        if not self.enabled:
            return None

        try:
            response = self.client.table('learning_sessions').insert({
                'student_id': student_id,
                'strand_id': strand_id,
                'topic_id': topic_id,
                'problems_attempted': 0,
                'problems_correct': 0,
                'duration_seconds': 0,
            }).execute()

            if response.data:
                logging.info(f"Started session for student {student_id}")
                return response.data[0]
        except Exception as e:
            logging.error(f"Failed to start session: {e}")

        return None

    def end_session(
        self,
        session_id: str,
        duration_seconds: int,
        problems_attempted: int,
        problems_correct: int
    ) -> Optional[dict]:
        """End a learning session."""
        if not self.enabled:
            return None

        try:
            response = self.client.table('learning_sessions').update({
                'ended_at': datetime.now().isoformat(),
                'duration_seconds': duration_seconds,
                'problems_attempted': problems_attempted,
                'problems_correct': problems_correct,
            }).eq('id', session_id).execute()

            if response.data:
                return response.data[0]
        except Exception as e:
            logging.error(f"Failed to end session: {e}")

        return None

    def record_problem_attempt(
        self,
        session_id: str,
        student_id: str,
        strand_id: str,
        topic_id: str,
        problem_type: str,
        question_text: str,
        correct_answer: str,
        student_answer: Optional[str] = None,
        is_correct: Optional[bool] = None,
        hint_used: bool = False,
        time_spent_seconds: int = 0
    ) -> Optional[dict]:
        """Record a problem attempt."""
        if not self.enabled:
            return None

        try:
            response = self.client.table('problem_attempts').insert({
                'session_id': session_id,
                'student_id': student_id,
                'strand_id': strand_id,
                'topic_id': topic_id,
                'problem_type': problem_type,
                'question_text': question_text,
                'correct_answer': str(correct_answer),
                'student_answer': str(student_answer) if student_answer is not None else None,
                'is_correct': is_correct,
                'hint_used': hint_used,
                'time_spent_seconds': time_spent_seconds,
            }).execute()

            if response.data:
                if is_correct:
                    self._increment_student_stats(student_id)
                return response.data[0]
        except Exception as e:
            logging.error(f"Failed to record problem attempt: {e}")

        return None

    def _increment_student_stats(self, student_id: str) -> None:
        """Increment student's problem solved counter."""
        if not self.enabled:
            return

        try:
            student = self.get_student(student_id)
            if student:
                self.client.table('students').update({
                    'total_problems_solved': student['total_problems_solved'] + 1
                }).eq('id', student_id).execute()
        except Exception as e:
            logging.error(f"Failed to increment stats: {e}")

    def save_drawing(
        self,
        student_id: str,
        stroke_data: dict,
        session_id: Optional[str] = None,
        problem_attempt_id: Optional[str] = None,
        canvas_background: str = 'cream',
        thumbnail_emoji: Optional[str] = None
    ) -> Optional[dict]:
        """Save a student drawing."""
        if not self.enabled:
            return None

        try:
            response = self.client.table('drawings').insert({
                'student_id': student_id,
                'session_id': session_id,
                'problem_attempt_id': problem_attempt_id,
                'stroke_data': stroke_data,
                'canvas_background': canvas_background,
                'thumbnail_emoji': thumbnail_emoji,
            }).execute()

            if response.data:
                logging.info("Drawing saved successfully")
                return response.data[0]
        except Exception as e:
            logging.error(f"Failed to save drawing: {e}")

        return None

    def get_student_drawings(self, student_id: str, limit: int = 20) -> list[dict]:
        """Get recent drawings for a student."""
        if not self.enabled:
            return []

        try:
            response = self.client.table('drawings').select('*').eq(
                'student_id', student_id
            ).order('created_at', desc=True).limit(limit).execute()

            return response.data or []
        except Exception as e:
            logging.error(f"Failed to get drawings: {e}")
            return []

    def get_student_progress(self, student_id: str) -> dict:
        """Get comprehensive progress data for a student."""
        if not self.enabled:
            return {}

        try:
            sessions = self.client.table('learning_sessions').select('*').eq(
                'student_id', student_id
            ).execute()

            attempts = self.client.table('problem_attempts').select('*').eq(
                'student_id', student_id
            ).execute()

            milestones = self.client.table('progress_milestones').select('*').eq(
                'student_id', student_id
            ).execute()

            return {
                'sessions': sessions.data or [],
                'attempts': attempts.data or [],
                'milestones': milestones.data or [],
            }
        except Exception as e:
            logging.error(f"Failed to get progress: {e}")
            return {}

    def award_milestone(
        self,
        student_id: str,
        milestone_type: str,
        strand_id: Optional[str] = None,
        topic_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Optional[dict]:
        """Award a milestone to a student."""
        if not self.enabled:
            return None

        try:
            response = self.client.table('progress_milestones').insert({
                'student_id': student_id,
                'milestone_type': milestone_type,
                'strand_id': strand_id,
                'topic_id': topic_id,
                'metadata': metadata,
            }).execute()

            if response.data:
                logging.info(f"Awarded milestone: {milestone_type}")
                return response.data[0]
        except Exception as e:
            if 'unique_milestone' in str(e).lower():
                logging.debug(f"Milestone {milestone_type} already awarded")
            else:
                logging.error(f"Failed to award milestone: {e}")

        return None

    def get_topic_stats(self, student_id: str, strand_id: str, topic_id: str) -> dict:
        """Get statistics for a specific topic."""
        if not self.enabled:
            return {'total': 0, 'correct': 0, 'accuracy': 0.0}

        try:
            response = self.client.table('problem_attempts').select('*').eq(
                'student_id', student_id
            ).eq('strand_id', strand_id).eq('topic_id', topic_id).execute()

            attempts = response.data or []
            total = len(attempts)
            correct = sum(1 for a in attempts if a.get('is_correct'))
            accuracy = (correct / total * 100) if total > 0 else 0.0

            return {
                'total': total,
                'correct': correct,
                'accuracy': accuracy,
            }
        except Exception as e:
            logging.error(f"Failed to get topic stats: {e}")
            return {'total': 0, 'correct': 0, 'accuracy': 0.0}


logging.basicConfig(level=logging.INFO)
db = DatabaseManager()
