# MathCanvas - Year 1 ACARA Mathematics Learning App

A comprehensive, touch-friendly drawing canvas designed for **Year 1 students** following the **Australian Curriculum (ACARA v9.0)**. Built with Python/Kivy for Windows tablets with pen support, featuring full progress tracking and student management.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Kivy](https://img.shields.io/badge/Kivy-2.3+-green.svg)
![Supabase](https://img.shields.io/badge/Supabase-Enabled-success.svg)
![ACARA](https://img.shields.io/badge/ACARA-v9.0-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

### Complete Year 1 Curriculum
All four ACARA Mathematics strands with 18+ topics:

| Strand | Topics |
|--------|--------|
| **Number** | Counting (to 120), Skip Counting, Odd/Even, Place Value, Addition, Subtraction, Number Bonds, Missing Number, Multiplication, Division, Fractions |
| **Measurement** | Length, Mass, Capacity, Time |
| **Space** | 2D Shapes, 3D Shapes, Position |
| **Statistics** | Tally Marks, Pictographs |

### Interactive Problem Solving
- Answer validation with instant feedback
- Multiple choice and text input questions
- Progressive hint system
- Visual math problems with emojis
- Real-time correctness checking

### Student Progress Tracking
- Multi-user student profiles with avatars
- Session-based learning analytics
- Problem attempt history
- Accuracy and performance metrics
- Achievement milestones
- Topic-specific statistics

### Drawing Canvas
- Smooth pen/touch input optimized for tablets
- 8 curated colors
- Adjustable pen thickness
- Eraser tool
- Multiple background themes
- Undo/Redo support (Ctrl+Z / Ctrl+Y)
- Save/export drawings (Ctrl+S)

### Engagement Features
- Unicorn rewards for drawing and correct answers
- Visual feedback and celebrations
- Progress display in control bar
- Session continuity

## Quick Start

```powershell
# Clone the repository
git clone https://github.com/YOUR_USERNAME/mathcanvas.git
cd mathcanvas

# Create virtual environment (Python 3.10-3.13)
python -m venv venv
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (create .env file)
# VITE_SUPABASE_URL=your_supabase_url
# VITE_SUPABASE_ANON_KEY=your_supabase_key

# Run the app
python main.py
```

Press **Escape** to exit fullscreen mode.

## Controls

| Control | Action |
|---------|--------|
| Curriculum | Open full curriculum navigator |
| Practice | Quick problem from current topic |
| Colors | Select drawing color |
| Size Slider | Adjust pen thickness |
| Erase | Toggle eraser mode |
| Clear | Clear entire canvas |
| Theme | Toggle background theme |
| Save | Save current drawing |
| Ctrl+Z | Undo last stroke |
| Ctrl+Shift+Z / Ctrl+Y | Redo stroke |
| Ctrl+S | Save drawing to database |

## Project Structure

```
mathcanvas/
├── main.py              # Main application entry point
├── canvas.py            # Drawing canvas widget
├── curriculum.py        # ACARA syllabus & problem generators
├── config.py            # Configuration constants
├── database.py          # Supabase database operations
├── session_manager.py   # Learning session management
├── ui_components.py     # Reusable UI widgets
├── popups.py            # Dialog windows (curriculum, problems, profiles)
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Database Schema

The app uses Supabase for persistent storage:

- **students** - Student profiles and lifetime statistics
- **learning_sessions** - Individual practice sessions
- **problem_attempts** - Detailed attempt records with correctness
- **drawings** - Saved canvas artwork
- **progress_milestones** - Achievement tracking

All tables have Row Level Security (RLS) enabled for data protection.

## Curriculum Coverage

Based on **Australian Curriculum v9.0** Content Descriptions:

- **AC9M1N01**: Recognise, represent and order numbers to 120
- **AC9M1N02**: Partition numbers into tens and ones
- **AC9M1N03**: Quantify sets using skip counting
- **AC9M1N04**: Addition and subtraction strategies
- **AC9M1M01**: Compare objects using mass and capacity
- **AC9M1M02**: Measure length with informal units
- **AC9M1M03**: Describe duration using months, weeks, days
- **AC9M1SP01**: Recognise 2D and 3D shapes
- **AC9M1SP02**: Give and follow directions using position
- **AC9M1ST01**: Acquire and record data
- **AC9M1ST02**: Represent data with one-to-one displays

## Tech Stack

- **Python 3.10+** - Core language
- **Kivy 2.3+** - Cross-platform UI framework
- **Supabase** - PostgreSQL database with real-time capabilities
- **Pillow** - Image processing support

## Key Improvements

This enhanced version includes:

**Architecture:**
- Modular codebase split into focused modules
- Separation of concerns (UI, logic, data)
- Clean dependency management

**Features:**
- Complete student profile system
- Answer validation and scoring
- Progress tracking and analytics
- Drawing persistence
- Session management
- Milestone achievements

**Code Quality:**
- Comprehensive error handling
- Logging throughout
- Type hints
- Proper documentation
- Security best practices (RLS, data validation)

## Development

To run in offline mode (without database):
- The app automatically detects missing database credentials
- All features work except progress tracking
- Students can still practice problems and draw

## License

MIT License - Feel free to use and modify!

---

Made with care for curious young learners
