# 🦄 MathCanvas - Year 1 ACARA Mathematics Learning App

A beautiful, touch-friendly drawing canvas designed for **Year 1 students** following the **Australian Curriculum (ACARA v9.0)**. Built with Python/Kivy for Windows tablets with pen support.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Kivy](https://img.shields.io/badge/Kivy-2.3+-green.svg)
![ACARA](https://img.shields.io/badge/ACARA-v9.0-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### 📚 Complete Year 1 Curriculum
All four ACARA Mathematics strands with 18+ topics:

| Strand | Topics |
|--------|--------|
| 🔢 **Number** | Counting (to 120), Skip Counting, Odd/Even, Place Value, Addition, Subtraction, Number Bonds, Missing Number, Multiplication, Division, Fractions |
| 📏 **Measurement** | Length, Mass, Capacity, Time |
| 📐 **Space** | 2D Shapes, 3D Shapes, Position |
| 📊 **Statistics** | Tally Marks, Pictographs |

### 🎨 Drawing Canvas
- Smooth pen/touch input
- 8 curated colors
- Adjustable pen thickness
- Eraser tool
- Multiple background themes
- **Undo/Redo** (Ctrl+Z / Ctrl+Y)

### 🦄 Unicorn Rewards
When you pause drawing, unicorn emojis float up as encouragement! 🦄✨🌈

## 🚀 Quick Start

```powershell
# Clone the repository
git clone https://github.com/YOUR_USERNAME/mathcanvas.git
cd mathcanvas

# Create virtual environment (Python 3.10-3.13)
python -m venv venv
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

Press **Escape** to exit fullscreen mode.

## 🎮 Controls

| Control | Action |
|---------|--------|
| 📚 Curriculum | Open curriculum navigator |
| 🎲 | Quick problem from current topic |
| 🎨 Colors | Select drawing color |
| ✏️ Slider | Adjust pen thickness |
| 🧽 | Toggle eraser |
| 🗑️ | Clear canvas |
| 🌙/☀️ | Toggle background theme |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |

## 📁 Project Structure

```
mathcanvas/
├── main.py           # Main Kivy application
├── curriculum.py     # Year 1 ACARA syllabus & problem generators
├── config.py         # Configuration constants
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## 🧠 Curriculum Coverage

Based on **Australian Curriculum v9.0** Content Descriptions:

- **AC9M1N01**: Recognise, represent and order numbers to 120
- **AC9M1N02**: Partition numbers into tens and ones
- **AC9M1N03**: Quantify sets using skip counting
- **AC9M1N04**: Addition and subtraction strategies
- **AC9M1M02**: Measure length with informal units
- **AC9M1SP01**: Recognise 2D and 3D shapes
- **AC9M1ST01**: Acquire and record data

## 🛠️ Tech Stack

- **Python 3.10+** - Core language
- **Kivy 2.3+** - Cross-platform UI framework
- **Pillow** - Image processing (optional OCR support)

## 📝 License

MIT License - Feel free to use and modify!

---

Made with 💖 for curious young learners 🇦🇺
