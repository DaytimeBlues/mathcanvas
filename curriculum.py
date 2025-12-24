"""
Year 1 ACARA Mathematics Curriculum
====================================
Complete syllabus data structure based on Australian Curriculum v9.0.

Content Descriptions covered:
- AC9M1N01: Recognise, represent and order numbers to at least 120
- AC9M1N02: Partition one- and two-digit numbers into tens and ones
- AC9M1N03: Quantify sets using skip counting
- AC9M1N04: Addition and subtraction using counting strategies
- AC9M1M02: Measure length using informal units
- AC9M1ST01: Acquire and record data
- AC9M1ST02: Represent data with one-to-one displays
"""
from __future__ import annotations
from typing import Final
from dataclasses import dataclass
from enum import Enum
import random


class ProblemType(Enum):
    """Types of math problems."""
    ARITHMETIC = 'arithmetic'          # 5 + 3 = ?
    MISSING_OPERAND = 'missing_operand'  # ? + 3 = 8
    SEQUENCE = 'sequence'              # 2, 4, 6, ?
    COMPARISON = 'comparison'          # Which is longer?
    IDENTIFICATION = 'identification'   # Name this shape
    COUNTING = 'counting'              # How many?
    FRACTION = 'fraction'              # Half of 8 = ?


@dataclass
class Problem:
    """Represents a single math problem."""
    question: str
    answer: str | int
    hint: str
    visual: str | None = None  # Emoji or image reference
    choices: list[str] | None = None  # For multiple choice


@dataclass
class Topic:
    """A curriculum topic with problem generators."""
    id: str
    name: str
    description: str
    icon: str
    problem_type: ProblemType
    acara_code: str  # e.g., "AC9M1N01"


# ═══════════════════════════════════════════════════════════════════════════
# CURRICULUM STRUCTURE
# ═══════════════════════════════════════════════════════════════════════════

CURRICULUM: Final[dict] = {
    'number': {
        'name': 'Number',
        'icon': '🔢',
        'color': '#4CAF50',
        'topics': {
            'counting': {
                'name': 'Counting to 120',
                'icon': '🔢',
                'description': 'Count forwards and backwards',
                'acara_code': 'AC9M1N01',
            },
            'skip_counting': {
                'name': 'Skip Counting',
                'icon': '🦘',
                'description': 'Count by 2s, 5s, and 10s',
                'acara_code': 'AC9M1N03',
            },
            'odd_even': {
                'name': 'Odd & Even',
                'icon': '🎲',
                'description': 'Recognise odd and even numbers',
                'acara_code': 'AC9M1N01',
            },
            'place_value': {
                'name': 'Tens & Ones',
                'icon': '🧱',
                'description': 'Partition numbers into tens and ones',
                'acara_code': 'AC9M1N02',
            },
            'addition': {
                'name': 'Addition',
                'icon': '➕',
                'description': 'Add numbers up to 20',
                'acara_code': 'AC9M1N04',
            },
            'subtraction': {
                'name': 'Subtraction',
                'icon': '➖',
                'description': 'Subtract numbers up to 20',
                'acara_code': 'AC9M1N04',
            },
            'number_bonds': {
                'name': 'Number Bonds',
                'icon': '🔗',
                'description': 'Find pairs that make 10 or 20',
                'acara_code': 'AC9M1N04',
            },
            'missing_number': {
                'name': 'Missing Number',
                'icon': '❓',
                'description': 'Find the missing number in equations',
                'acara_code': 'AC9M1N04',
            },
            'multiplication': {
                'name': 'Equal Groups',
                'icon': '✖️',
                'description': 'Multiply using repeated addition',
                'acara_code': 'AC9M1N04',
            },
            'division': {
                'name': 'Sharing Equally',
                'icon': '➗',
                'description': 'Divide by sharing into equal groups',
                'acara_code': 'AC9M1N04',
            },
            'fractions': {
                'name': 'Halves & Quarters',
                'icon': '🥧',
                'description': 'Find halves and quarters',
                'acara_code': 'AC9M1N04',
            },
        }
    },
    'measurement': {
        'name': 'Measurement',
        'icon': '📏',
        'color': '#2196F3',
        'topics': {
            'length': {
                'name': 'Length',
                'icon': '📏',
                'description': 'Compare and measure lengths',
                'acara_code': 'AC9M1M02',
            },
            'mass': {
                'name': 'Mass',
                'icon': '⚖️',
                'description': 'Compare heavier and lighter',
                'acara_code': 'AC9M1M01',
            },
            'capacity': {
                'name': 'Capacity',
                'icon': '🥛',
                'description': 'Compare holds more and holds less',
                'acara_code': 'AC9M1M01',
            },
            'time': {
                'name': 'Time',
                'icon': '🕐',
                'description': 'Days of the week and duration',
                'acara_code': 'AC9M1M03',
            },
        }
    },
    'space': {
        'name': 'Space',
        'icon': '📐',
        'color': '#9B59B6',
        'topics': {
            'shapes_2d': {
                'name': '2D Shapes',
                'icon': '🔷',
                'description': 'Recognise circles, squares, triangles',
                'acara_code': 'AC9M1SP01',
            },
            'shapes_3d': {
                'name': '3D Shapes',
                'icon': '📦',
                'description': 'Recognise cubes, spheres, cylinders',
                'acara_code': 'AC9M1SP01',
            },
            'position': {
                'name': 'Position',
                'icon': '📍',
                'description': 'Above, below, beside, between',
                'acara_code': 'AC9M1SP02',
            },
        }
    },
    'statistics': {
        'name': 'Statistics',
        'icon': '📊',
        'color': '#FF9800',
        'topics': {
            'tally': {
                'name': 'Tally Marks',
                'icon': '📝',
                'description': 'Count and record using tallies',
                'acara_code': 'AC9M1ST01',
            },
            'pictograph': {
                'name': 'Pictographs',
                'icon': '📊',
                'description': 'Read simple picture graphs',
                'acara_code': 'AC9M1ST02',
            },
        }
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# PROBLEM GENERATORS
# ═══════════════════════════════════════════════════════════════════════════

# Visual emojis for counting problems
COUNTING_OBJECTS = ['🍎', '⭐', '🌸', '🐱', '🚗', '🎈', '🐠', '🌻']
SHAPE_2D = ['⬛', '⬜', '🔴', '🔵', '🟢', '🟡', '🟣', '🔶', '🔷', '🔺', '🔻']
DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


def generate_counting_problem(direction: str = 'forward') -> Problem:
    """Generate a counting problem (what comes next/before)."""
    start = random.randint(1, 115)
    
    if direction == 'forward':
        question = f"What comes after {start}?"
        answer = start + 1
        hint = f"Count: {start}, ..."
    else:
        start = random.randint(2, 120)
        question = f"What comes before {start}?"
        answer = start - 1
        hint = f"Count backwards to find what's before {start}"
    
    return Problem(question=question, answer=answer, hint=hint)


def generate_skip_counting_problem(skip: int = 2) -> Problem:
    """Generate a skip counting sequence problem."""
    start = random.randint(0, 10) * skip
    sequence = [start + (i * skip) for i in range(4)]
    
    # Hide the last number
    question = f"Count by {skip}s: {sequence[0]}, {sequence[1]}, {sequence[2]}, ?"
    answer = sequence[3]
    hint = f"Add {skip} to find the next number"
    
    return Problem(question=question, answer=answer, hint=hint)


def generate_odd_even_problem() -> Problem:
    """Generate an odd/even identification problem."""
    num = random.randint(1, 20)
    is_even = num % 2 == 0
    
    question = f"Is {num} odd or even?"
    answer = "Even" if is_even else "Odd"
    hint = "Even numbers end in 0, 2, 4, 6, 8"
    choices = ["Odd", "Even"]
    
    return Problem(question=question, answer=answer, hint=hint, choices=choices)


def generate_place_value_problem() -> Problem:
    """Generate a tens and ones problem."""
    tens = random.randint(1, 9)
    ones = random.randint(0, 9)
    number = tens * 10 + ones
    
    problem_type = random.choice(['identify', 'build'])
    
    if problem_type == 'identify':
        question = f"How many tens in {number}?"
        answer = tens
        hint = f"{number} = ___ tens and {ones} ones"
    else:
        question = f"{tens} tens and {ones} ones = ?"
        answer = number
        hint = f"Tens are worth 10 each"
    
    return Problem(question=question, answer=answer, hint=hint)


def generate_addition_problem(max_sum: int = 20) -> Problem:
    """Generate an addition problem with visual."""
    num1 = random.randint(1, max_sum // 2)
    num2 = random.randint(1, max_sum - num1)
    answer = num1 + num2
    
    emoji = random.choice(COUNTING_OBJECTS)
    visual = emoji * num1 + " + " + emoji * num2
    
    question = f"{num1} + {num2} = ?"
    hint = f"Count: {visual}"
    
    return Problem(question=question, answer=answer, hint=hint, visual=visual)


def generate_subtraction_problem(max_num: int = 20) -> Problem:
    """Generate a subtraction problem."""
    num1 = random.randint(2, max_num)
    num2 = random.randint(1, num1)
    answer = num1 - num2
    
    question = f"{num1} − {num2} = ?"
    hint = f"Start at {num1} and count back {num2}"
    
    return Problem(question=question, answer=answer, hint=hint)


def generate_number_bonds_problem(target: int = 10) -> Problem:
    """Generate a number bonds problem."""
    num1 = random.randint(1, target - 1)
    num2 = target - num1
    
    question = f"{num1} + ? = {target}"
    answer = num2
    hint = f"What do you add to {num1} to make {target}?"
    
    return Problem(question=question, answer=answer, hint=hint)


def generate_missing_number_problem() -> Problem:
    """Generate a missing addend/subtrahend problem."""
    operation = random.choice(['add', 'subtract'])
    
    if operation == 'add':
        answer = random.randint(1, 10)
        num2 = random.randint(1, 10)
        result = answer + num2
        question = f"? + {num2} = {result}"
        hint = f"What plus {num2} equals {result}?"
    else:
        num1 = random.randint(5, 15)
        answer = random.randint(1, num1 - 1)
        result = num1 - answer
        question = f"{num1} − ? = {result}"
        hint = f"{num1} minus what equals {result}?"
    
    return Problem(question=question, answer=answer, hint=hint)


def generate_multiplication_problem(max_factor: int = 5) -> Problem:
    """Generate a multiplication as repeated addition problem."""
    groups = random.randint(2, max_factor)
    items = random.randint(2, max_factor)
    answer = groups * items
    
    emoji = random.choice(COUNTING_OBJECTS)
    visual = " ".join([emoji * items for _ in range(groups)])
    
    question = f"{groups} groups of {items} = ?"
    hint = f"Add {items} + {items}... ({groups} times)"
    
    return Problem(question=question, answer=answer, hint=hint, visual=visual)


def generate_division_problem(max_total: int = 20) -> Problem:
    """Generate a sharing/division problem."""
    groups = random.randint(2, 5)
    per_group = random.randint(2, 4)
    total = groups * per_group
    
    emoji = random.choice(COUNTING_OBJECTS)
    
    question = f"Share {total} {emoji} between {groups} friends. How many each?"
    answer = per_group
    hint = f"Divide {total} into {groups} equal groups"
    
    return Problem(question=question, answer=answer, hint=hint)


def generate_fraction_problem() -> Problem:
    """Generate a halves/quarters problem."""
    fraction_type = random.choice(['half', 'quarter'])
    
    if fraction_type == 'half':
        whole = random.choice([2, 4, 6, 8, 10, 12])
        answer = whole // 2
        question = f"Half of {whole} = ?"
        hint = "Split into 2 equal parts"
        visual = "🍕" * whole + " → " + "🍕" * answer + " | " + "🍕" * answer
    else:
        whole = random.choice([4, 8, 12])
        answer = whole // 4
        question = f"Quarter of {whole} = ?"
        hint = "Split into 4 equal parts"
        visual = "🍕" * whole
    
    return Problem(question=question, answer=answer, hint=hint, visual=visual)


def generate_length_comparison_problem() -> Problem:
    """Generate a length comparison problem."""
    objects = [
        ('🐍 Snake', 'long'), ('🐛 Caterpillar', 'short'),
        ('🚂 Train', 'long'), ('🚗 Car', 'short'),
        ('🦒 Giraffe', 'tall'), ('🐁 Mouse', 'short'),
        ('✏️ Pencil', 'medium'), ('🖍️ Crayon', 'short'),
    ]
    
    obj1, obj2 = random.sample(objects, 2)
    
    question = f"Which is longer: {obj1[0]} or {obj2[0]}?"
    if obj1[1] in ['long', 'tall'] and obj2[1] == 'short':
        answer = obj1[0].split()[1]
    elif obj2[1] in ['long', 'tall'] and obj1[1] == 'short':
        answer = obj2[0].split()[1]
    else:
        answer = random.choice([obj1[0].split()[1], obj2[0].split()[1]])
    
    hint = "Think about which one would stretch further"
    choices = [obj1[0].split()[1], obj2[0].split()[1]]
    
    return Problem(question=question, answer=answer, hint=hint, choices=choices)


def generate_time_problem() -> Problem:
    """Generate a days of the week problem."""
    day_idx = random.randint(0, 5)
    day = DAYS_OF_WEEK[day_idx]
    next_day = DAYS_OF_WEEK[day_idx + 1]
    
    question = f"What day comes after {day}?"
    answer = next_day
    hint = "Think about the order of days"
    
    return Problem(question=question, answer=answer, hint=hint)


def generate_shapes_2d_problem() -> Problem:
    """Generate a 2D shape recognition problem."""
    shapes = [
        ('⬜', 'Square', '4 equal sides'),
        ('🔴', 'Circle', 'No corners, round'),
        ('🔺', 'Triangle', '3 sides'),
        ('▬', 'Rectangle', '4 sides, 2 pairs equal'),
    ]
    
    shape = random.choice(shapes)
    question = f"What shape is this? {shape[0]}"
    answer = shape[1]
    hint = shape[2]
    choices = ['Circle', 'Square', 'Triangle', 'Rectangle']
    
    return Problem(question=question, answer=answer, hint=hint, choices=choices)


def generate_position_problem() -> Problem:
    """Generate a position/location problem."""
    positions = [
        ('🐱', '📦', 'on', 'The cat is ON the box'),
        ('🐱', '📦', 'under', 'The cat is UNDER the box'),
        ('🐱', '📦', 'beside', 'The cat is BESIDE the box'),
        ('🐱', '🌳', 'behind', 'The cat is BEHIND the tree'),
    ]
    
    scenario = random.choice(positions)
    visual = f"{scenario[0]} {scenario[2]} {scenario[1]}"
    question = f"Where is the {scenario[0]}? (on/under/beside)"
    answer = scenario[2]
    hint = scenario[3]
    choices = ['on', 'under', 'beside', 'behind']
    
    return Problem(question=question, answer=answer, hint=hint, choices=choices, visual=visual)


def generate_tally_problem() -> Problem:
    """Generate a tally marks problem."""
    count = random.randint(1, 10)
    
    # Create tally representation
    full_groups = count // 5
    remainder = count % 5
    tally = "𝍸 " * full_groups + "|" * remainder
    
    problem_type = random.choice(['read', 'write'])
    
    if problem_type == 'read':
        question = f"How many does this tally show? {tally}"
        answer = count
        hint = "Each 𝍸 is 5, each | is 1"
    else:
        question = f"How many tally marks for {count}?"
        answer = tally.strip()
        hint = "Group by 5s with a cross-through"
    
    return Problem(question=question, answer=answer, hint=hint)


# ═══════════════════════════════════════════════════════════════════════════
# PROBLEM GENERATOR MAPPING
# ═══════════════════════════════════════════════════════════════════════════

PROBLEM_GENERATORS: Final[dict[str, callable]] = {
    'counting': lambda: generate_counting_problem(random.choice(['forward', 'backward'])),
    'skip_counting': lambda: generate_skip_counting_problem(random.choice([2, 5, 10])),
    'odd_even': generate_odd_even_problem,
    'place_value': generate_place_value_problem,
    'addition': generate_addition_problem,
    'subtraction': generate_subtraction_problem,
    'number_bonds': lambda: generate_number_bonds_problem(random.choice([10, 20])),
    'missing_number': generate_missing_number_problem,
    'multiplication': generate_multiplication_problem,
    'division': generate_division_problem,
    'fractions': generate_fraction_problem,
    'length': generate_length_comparison_problem,
    'mass': generate_length_comparison_problem,  # Similar format
    'capacity': generate_length_comparison_problem,  # Similar format
    'time': generate_time_problem,
    'shapes_2d': generate_shapes_2d_problem,
    'shapes_3d': generate_shapes_2d_problem,  # TODO: Add 3D shapes
    'position': generate_position_problem,
    'tally': generate_tally_problem,
    'pictograph': generate_tally_problem,  # Similar format
}


def get_problem(topic_id: str) -> Problem:
    """Get a random problem for the given topic."""
    generator = PROBLEM_GENERATORS.get(topic_id)
    if generator:
        return generator()
    # Fallback to counting
    return generate_counting_problem()


def get_all_topic_ids() -> list[str]:
    """Get all topic IDs across all strands."""
    topics = []
    for strand in CURRICULUM.values():
        topics.extend(strand['topics'].keys())
    return topics
