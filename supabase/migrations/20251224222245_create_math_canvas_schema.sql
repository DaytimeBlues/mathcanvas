/*
  # MathCanvas Database Schema

  ## Overview
  Complete database schema for the MathCanvas Year 1 learning app to track
  student progress, problem attempts, drawings, and analytics.

  ## New Tables

  ### 1. `students`
  Student profiles with authentication
  - `id` (uuid, primary key) - Unique student identifier
  - `name` (text) - Student display name
  - `grade_level` (text) - Current grade (defaults to 'year_1')
  - `avatar_emoji` (text) - Student's chosen avatar emoji
  - `created_at` (timestamptz) - Account creation timestamp
  - `last_active` (timestamptz) - Last activity timestamp
  - `total_problems_solved` (integer) - Running total counter
  - `total_unicorns_earned` (integer) - Gamification metric

  ### 2. `learning_sessions`
  Individual learning sessions
  - `id` (uuid, primary key) - Session identifier
  - `student_id` (uuid, foreign key) - Reference to student
  - `started_at` (timestamptz) - Session start time
  - `ended_at` (timestamptz) - Session end time (nullable)
  - `strand_id` (text) - Curriculum strand (number, measurement, space, statistics)
  - `topic_id` (text) - Specific topic within strand
  - `problems_attempted` (integer) - Count of problems tried
  - `problems_correct` (integer) - Count of correct answers
  - `duration_seconds` (integer) - Total session duration

  ### 3. `problem_attempts`
  Individual problem attempt records
  - `id` (uuid, primary key) - Attempt identifier
  - `session_id` (uuid, foreign key) - Reference to session
  - `student_id` (uuid, foreign key) - Reference to student
  - `strand_id` (text) - Curriculum strand
  - `topic_id` (text) - Specific topic
  - `problem_type` (text) - Type of problem (arithmetic, sequence, etc.)
  - `question_text` (text) - The actual question asked
  - `correct_answer` (text) - The correct answer
  - `student_answer` (text) - Student's submitted answer (nullable)
  - `is_correct` (boolean) - Whether answer was correct (nullable)
  - `hint_used` (boolean) - Whether student viewed the hint
  - `time_spent_seconds` (integer) - Time spent on this problem
  - `attempted_at` (timestamptz) - When problem was attempted

  ### 4. `drawings`
  Student drawings with metadata
  - `id` (uuid, primary key) - Drawing identifier
  - `student_id` (uuid, foreign key) - Reference to student
  - `session_id` (uuid, foreign key) - Reference to session (nullable)
  - `problem_attempt_id` (uuid, foreign key) - Associated problem (nullable)
  - `stroke_data` (jsonb) - Serialized stroke data
  - `canvas_background` (text) - Background theme used
  - `thumbnail_emoji` (text) - Visual preview (nullable)
  - `created_at` (timestamptz) - Creation timestamp
  - `updated_at` (timestamptz) - Last modification timestamp

  ### 5. `progress_milestones`
  Achievement tracking
  - `id` (uuid, primary key) - Milestone identifier
  - `student_id` (uuid, foreign key) - Reference to student
  - `milestone_type` (text) - Type (first_problem, 10_correct, strand_complete, etc.)
  - `strand_id` (text) - Related strand (nullable)
  - `topic_id` (text) - Related topic (nullable)
  - `achieved_at` (timestamptz) - Achievement timestamp
  - `metadata` (jsonb) - Additional context (nullable)

  ## Security
  - RLS enabled on all tables
  - Students can only access their own data
  - No anonymous access allowed

  ## Indexes
  - Performance indexes on frequently queried columns
  - Composite indexes for common query patterns
*/

-- ============================================================================
-- STUDENTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS students (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  grade_level text DEFAULT 'year_1',
  avatar_emoji text DEFAULT '🎓',
  created_at timestamptz DEFAULT now(),
  last_active timestamptz DEFAULT now(),
  total_problems_solved integer DEFAULT 0,
  total_unicorns_earned integer DEFAULT 0,
  CONSTRAINT name_length CHECK (char_length(name) >= 1 AND char_length(name) <= 100)
);

ALTER TABLE students ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Students can view own profile"
  ON students FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

CREATE POLICY "Students can update own profile"
  ON students FOR UPDATE
  TO authenticated
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

CREATE POLICY "Anyone can create student profile"
  ON students FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = id);

-- ============================================================================
-- LEARNING SESSIONS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id uuid NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  started_at timestamptz DEFAULT now(),
  ended_at timestamptz,
  strand_id text NOT NULL,
  topic_id text NOT NULL,
  problems_attempted integer DEFAULT 0,
  problems_correct integer DEFAULT 0,
  duration_seconds integer DEFAULT 0,
  CONSTRAINT valid_duration CHECK (duration_seconds >= 0),
  CONSTRAINT valid_problems CHECK (problems_attempted >= 0 AND problems_correct >= 0),
  CONSTRAINT correct_not_exceeds_attempted CHECK (problems_correct <= problems_attempted)
);

ALTER TABLE learning_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Students can view own sessions"
  ON learning_sessions FOR SELECT
  TO authenticated
  USING (auth.uid() = student_id);

CREATE POLICY "Students can create own sessions"
  ON learning_sessions FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = student_id);

CREATE POLICY "Students can update own sessions"
  ON learning_sessions FOR UPDATE
  TO authenticated
  USING (auth.uid() = student_id)
  WITH CHECK (auth.uid() = student_id);

-- ============================================================================
-- PROBLEM ATTEMPTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS problem_attempts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id uuid NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
  student_id uuid NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  strand_id text NOT NULL,
  topic_id text NOT NULL,
  problem_type text NOT NULL,
  question_text text NOT NULL,
  correct_answer text NOT NULL,
  student_answer text,
  is_correct boolean,
  hint_used boolean DEFAULT false,
  time_spent_seconds integer DEFAULT 0,
  attempted_at timestamptz DEFAULT now(),
  CONSTRAINT valid_time_spent CHECK (time_spent_seconds >= 0)
);

ALTER TABLE problem_attempts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Students can view own attempts"
  ON problem_attempts FOR SELECT
  TO authenticated
  USING (auth.uid() = student_id);

CREATE POLICY "Students can create own attempts"
  ON problem_attempts FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = student_id);

CREATE POLICY "Students can update own attempts"
  ON problem_attempts FOR UPDATE
  TO authenticated
  USING (auth.uid() = student_id)
  WITH CHECK (auth.uid() = student_id);

-- ============================================================================
-- DRAWINGS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS drawings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id uuid NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  session_id uuid REFERENCES learning_sessions(id) ON DELETE SET NULL,
  problem_attempt_id uuid REFERENCES problem_attempts(id) ON DELETE SET NULL,
  stroke_data jsonb NOT NULL,
  canvas_background text DEFAULT 'cream',
  thumbnail_emoji text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE drawings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Students can view own drawings"
  ON drawings FOR SELECT
  TO authenticated
  USING (auth.uid() = student_id);

CREATE POLICY "Students can create own drawings"
  ON drawings FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = student_id);

CREATE POLICY "Students can update own drawings"
  ON drawings FOR UPDATE
  TO authenticated
  USING (auth.uid() = student_id)
  WITH CHECK (auth.uid() = student_id);

CREATE POLICY "Students can delete own drawings"
  ON drawings FOR DELETE
  TO authenticated
  USING (auth.uid() = student_id);

-- ============================================================================
-- PROGRESS MILESTONES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS progress_milestones (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id uuid NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  milestone_type text NOT NULL,
  strand_id text,
  topic_id text,
  achieved_at timestamptz DEFAULT now(),
  metadata jsonb,
  CONSTRAINT unique_milestone UNIQUE (student_id, milestone_type, strand_id, topic_id)
);

ALTER TABLE progress_milestones ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Students can view own milestones"
  ON progress_milestones FOR SELECT
  TO authenticated
  USING (auth.uid() = student_id);

CREATE POLICY "Students can create own milestones"
  ON progress_milestones FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = student_id);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_sessions_student_id ON learning_sessions(student_id);
CREATE INDEX IF NOT EXISTS idx_sessions_started_at ON learning_sessions(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_strand_topic ON learning_sessions(strand_id, topic_id);

CREATE INDEX IF NOT EXISTS idx_attempts_student_id ON problem_attempts(student_id);
CREATE INDEX IF NOT EXISTS idx_attempts_session_id ON problem_attempts(session_id);
CREATE INDEX IF NOT EXISTS idx_attempts_topic ON problem_attempts(strand_id, topic_id);
CREATE INDEX IF NOT EXISTS idx_attempts_attempted_at ON problem_attempts(attempted_at DESC);

CREATE INDEX IF NOT EXISTS idx_drawings_student_id ON drawings(student_id);
CREATE INDEX IF NOT EXISTS idx_drawings_session_id ON drawings(session_id);
CREATE INDEX IF NOT EXISTS idx_drawings_created_at ON drawings(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_milestones_student_id ON progress_milestones(student_id);
CREATE INDEX IF NOT EXISTS idx_milestones_type ON progress_milestones(milestone_type);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to update student's last_active timestamp
CREATE OR REPLACE FUNCTION update_student_last_active()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE students 
  SET last_active = now()
  WHERE id = NEW.student_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to update last_active on new session
DROP TRIGGER IF EXISTS trigger_update_last_active ON learning_sessions;
CREATE TRIGGER trigger_update_last_active
  AFTER INSERT ON learning_sessions
  FOR EACH ROW
  EXECUTE FUNCTION update_student_last_active();

-- Function to update drawing timestamp
CREATE OR REPLACE FUNCTION update_drawing_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_drawing_timestamp ON drawings;
CREATE TRIGGER trigger_update_drawing_timestamp
  BEFORE UPDATE ON drawings
  FOR EACH ROW
  EXECUTE FUNCTION update_drawing_timestamp();