"""
LearnSphere AI - Complete Database & Schema Models
Supports Master Prompt Specifications:
- Adaptive Learning Paths (Foundation, Standard, Challenge)
- Multi-Format Study Library (Simple, Point-wise, Detailed, Exam-Ready, Visual, Flashcards)
- Mistake Detective (Misconception identification)
- Hint Ladder (4 Progressive hint levels)
- Confidence vs Knowledge Tracker (Not Sure, Somewhat Sure, Very Sure)
- Topic Prerequisites & Gap Map
- Smart Revision & Spaced Repetition Flashcards
- Teach-Back Mode (Student explains concept)
- Examination Preparation Centre
- School & College Curricula
- User Roles (Student, Teacher, Administrator)
"""

import sqlite3
import os
import json
from datetime import datetime, date, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "learnsphere.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student', -- 'student', 'teacher', 'admin'
        education_level TEXT DEFAULT 'School', -- 'School' or 'College'
        grade TEXT DEFAULT 'Class 10',
        school TEXT DEFAULT 'Shri Vishnumoorthi Hayavadanaswami High School, Innanje',
        preferred_language TEXT DEFAULT 'en', -- 'en', 'kn', 'hi'
        avatar TEXT DEFAULT '👨‍🎓',
        learning_points INTEGER DEFAULT 350,
        streak_days INTEGER DEFAULT 4,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Subjects Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL DEFAULT 'School', -- 'School' or 'College'
        icon TEXT NOT NULL,
        color TEXT NOT NULL,
        description TEXT NOT NULL
    );
    """)

    # Topics Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        grade_level TEXT NOT NULL,
        difficulty TEXT NOT NULL, -- 'Foundation', 'Standard', 'Challenge'
        summary TEXT NOT NULL,
        simple_explanation TEXT NOT NULL,
        pointwise_notes TEXT,
        detailed_explanation TEXT NOT NULL,
        exam_ready_notes TEXT,
        real_life_example TEXT NOT NULL,
        kannada_explanation TEXT NOT NULL,
        hindi_explanation TEXT NOT NULL,
        formula_box TEXT,
        visual_type TEXT, -- 'linear_graph', 'force_sim', 'photosynthesis', 'c_pointer', 'none'
        prerequisite_text TEXT,
        FOREIGN KEY (subject_id) REFERENCES subjects(id)
    );
    """)

    # Topic Prerequisites Graph Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS topic_prerequisites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER NOT NULL,
        prerequisite_name TEXT NOT NULL,
        mastery_status TEXT NOT NULL DEFAULT 'demonstrated', -- 'demonstrated', 'needs_practice', 'in_progress'
        recommendation TEXT NOT NULL,
        FOREIGN KEY (topic_id) REFERENCES topics(id)
    );
    """)

    # Quizzes Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER NOT NULL,
        difficulty_mode TEXT DEFAULT 'Standard', -- 'Foundation', 'Standard', 'Challenge'
        question TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_option TEXT NOT NULL, -- 'A', 'B', 'C', 'D'
        explanation TEXT NOT NULL,
        FOREIGN KEY (topic_id) REFERENCES topics(id)
    );
    """)

    # Hint Ladder Table (4 progressive assistance levels)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quiz_hints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER NOT NULL,
        level INTEGER NOT NULL, -- 1, 2, 3, 4
        title TEXT NOT NULL,
        hint_text TEXT NOT NULL,
        FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
    );
    """)

    # Mistake Detective Table (Identifies exact misconceptions)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mistake_detective (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER NOT NULL,
        wrong_option TEXT NOT NULL, -- 'A', 'B', 'C', or 'D'
        misconception_name TEXT NOT NULL,
        why_it_happens TEXT NOT NULL,
        how_to_fix TEXT NOT NULL,
        follow_up_practice TEXT,
        FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
    );
    """)

    # Quiz Attempts History
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quiz_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        topic_id INTEGER NOT NULL,
        score INTEGER NOT NULL,
        total_questions INTEGER NOT NULL,
        percentage REAL NOT NULL,
        difficulty_mode TEXT DEFAULT 'Standard',
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (topic_id) REFERENCES topics(id)
    );
    """)

    # Confidence vs Knowledge Tracker
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS confidence_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        quiz_id INTEGER NOT NULL,
        selected_option TEXT NOT NULL,
        is_correct INTEGER NOT NULL,
        confidence_level TEXT NOT NULL, -- 'not_sure', 'somewhat_sure', 'very_sure'
        classification TEXT NOT NULL, -- 'mastery_confirmed', 'misconception_warning', 'retrieval_needed', 'foundation_needed'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
    );
    """)

    # Learning Gaps Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS learning_gaps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        topic_id INTEGER NOT NULL,
        mastery_score REAL NOT NULL,
        status TEXT NOT NULL, -- 'critical_gap', 'needs_revision', 'in_progress', 'mastered'
        recommended_action TEXT NOT NULL,
        last_assessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, topic_id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (topic_id) REFERENCES topics(id)
    );
    """)

    # Smart Revision & Spaced Repetition Flashcards
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS flashcards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER NOT NULL,
        front_prompt TEXT NOT NULL,
        back_answer TEXT NOT NULL,
        interval_day INTEGER DEFAULT 1, -- Day 1, 2, 5, 10, 20
        last_reviewed TIMESTAMP,
        repetition_count INTEGER DEFAULT 0,
        FOREIGN KEY (topic_id) REFERENCES topics(id)
    );
    """)

    # Teach-Back Prompts & Rubrics
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teach_back_prompts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER NOT NULL,
        prompt TEXT NOT NULL,
        required_concepts TEXT NOT NULL, -- JSON list of keywords
        model_answer TEXT NOT NULL,
        rubric_guide TEXT NOT NULL,
        FOREIGN KEY (topic_id) REFERENCES topics(id)
    );
    """)

    # Study Tasks Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS study_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        subject_id INTEGER NOT NULL,
        scheduled_day TEXT NOT NULL,
        time_slot TEXT NOT NULL,
        is_completed INTEGER DEFAULT 0,
        task_type TEXT NOT NULL, -- 'revision', 'quiz', 'video', 'notes', 'teach_back'
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (subject_id) REFERENCES subjects(id)
    );
    """)

    # Career Pathways Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS career_paths (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        match_subjects TEXT NOT NULL,
        description TEXT NOT NULL,
        required_skills TEXT NOT NULL,
        colleges TEXT NOT NULL,
        entrance_exams TEXT NOT NULL,
        salary_range TEXT NOT NULL
    );
    """)

    conn.commit()
    seed_master_data(conn)
    conn.close()

def seed_master_data(conn):
    cursor = conn.cursor()

    # Check if subjects already seeded
    cursor.execute("SELECT COUNT(*) FROM subjects")
    if cursor.fetchone()[0] > 0:
        return

    # Seed Users
    cursor.execute("""
    INSERT INTO users (username, full_name, role, education_level, grade, school, preferred_language, avatar, learning_points, streak_days)
    VALUES 
    ('arjun_student', 'Arjun Rao', 'student', 'School', 'Class 10', 'Shri Vishnumoorthi Hayavadanaswami High School, Innanje', 'en', '👨‍🎓', 420, 5),
    ('ananya_student', 'Ananya Shenoy', 'student', 'School', 'Class 9', 'Shri Vishnumoorthi Hayavadanaswami High School, Innanje', 'kn', '👩‍🎓', 380, 3),
    ('pooja_teacher', 'Mrs. Pooja (Social Science)', 'teacher', 'School', 'Faculty', 'Shri Vishnumoorthi Hayavadanaswami High School, Innanje', 'en', '👩‍🏫', 0, 0),
    ('admin_smvitm', 'Administrator', 'admin', 'College', 'Department Coordinator', 'SMVITM Bantakal', 'en', '🛡️', 0, 0);
    """)

    # Seed Subjects (Both School & College)
    subjects_data = [
        # School
        ('Mathematics', 'MATH', 'School', '📐', '#3b82f6', 'Algebra, Linear Equations, Geometry, and Quadratic Equations.'),
        ('Science', 'SCI', 'School', '🔬', '#10b981', 'Physics (Laws of Motion, Forces) and Biology (Photosynthesis).'),
        ('Social Science', 'SOC', 'School', '🌍', '#f59e0b', 'History (French Revolution), Civics, and Geography.'),
        ('English', 'ENG', 'School', '📖', '#8b5cf6', 'Grammar essentials, Tenses, and Active-Passive Voice.'),
        ('Hindi', 'HIN', 'School', '🇮🇳', '#ec4899', 'Vyakaran (कारक और समास), Shabdkosh, and Sentence Formations.'),
        ('Kannada', 'KAN', 'School', '🌟', '#f97316', 'ಕನ್ನಡ ಸಾಹಿತ್ಯ, ವ್ಯಾಕರಣ ಮತ್ತು ಪ್ರಬಂಧ ರಚನೆ.'),
        # College (Engineering / Computer Science at SMVITM Bantakal)
        ('Programming in C', 'CS-C', 'College', '💻', '#06b6d4', 'Variables, Conditionals, Loops, Pointers, and Memory Allocation.'),
        ('Data Structures', 'CS-DSA', 'College', '🌲', '#8b5cf6', 'Arrays, Stacks, Queues, Linked Lists, Trees, and Graphs.'),
        ('Artificial Intelligence', 'AIDS-AI', 'College', '🤖', '#6366f1', 'Search Algorithms, Knowledge Representation, and Machine Learning.')
    ]
    cursor.executemany("""
    INSERT INTO subjects (name, code, category, icon, color, description)
    VALUES (?, ?, ?, ?, ?, ?)
    """, subjects_data)

    cursor.execute("SELECT id, code FROM subjects")
    sub_map = {row['code']: row['id'] for row in cursor.fetchall()}

    # Seed Topics with multi-format notes
    topics_data = [
        # Mathematics - Linear Equations
        (
            sub_map['MATH'],
            'Linear Equations in One Variable',
            'linear-equations',
            'Class 8-10',
            'Standard',
            'Understanding equations with single variable of power 1 and solving using balancing method.',
            'A linear equation is a balance scale where the highest power of the unknown letter is 1. If you add, subtract, multiply, or divide something on the left, you must do the exact same to the right to keep it balanced!',
            """• Definition: An equation where highest power of variable is 1.
• General Form: ax + b = c (where a ≠ 0)
• Golden Rule: Whatever operation is applied to LHS must be applied to RHS.
• Steps to Solve:
  1. Simplify both sides if brackets exist.
  2. Transpose variable terms to one side, constants to the other.
  3. Divide by the coefficient of x.""",
            """A linear equation in one variable is an algebraic equation of the first degree involving a single variable. The algebraic standard form is ax + b = 0 or ax + b = c. The solution of such an equation is the unique real number which, when substituted for the variable, makes the equality valid. Geometrically, on a Cartesian plane, linear relations graph as perfectly straight lines.""",
            """EXAM PREPARATION NOTES:
1. Standard Definition (2 Marks): A polynomial equation of degree 1.
2. Common Exam Trap: Forgetting to multiply the outer bracket into ALL terms inside! Example: 2(x + 3) = 2x + 6, NOT 2x + 3.
3. Word Problems Technique: Always declare 'Let the unknown quantity be x'.
4. Quick Formula: x = (c - b) / a.""",
            'Balance scale in a vegetable market: If a bag of potatoes plus 2 kg equals 5 kg, removing 2 kg leaves the potatoes weighing exactly 3 kg!',
            'ರೇಖೀಯ ಸಮೀಕರಣವು ಅಜ್ಞಾತ ಚರಾಂಶದ ಗರಿಷ್ಠ ಘಾತಾಂಕ 1 ಆಗಿರುವ ಗಣಿತ ಸಮೀಕರಣವಾಗಿದೆ. ax + b = c ರೂಪದಲ್ಲಿರುತ್ತದೆ. ಎರಡೂ ಬದಿ ಸಮತೋಲನಗೊಳಿಸಿ ಸುಲಭವಾಗಿ x ಮೌಲ್ಯ ಕಂಡುಹಿಡಿಯಬಹುದು.',
            'एक चर वाले रैखिक समीकरण में चर की अधिकतम घात 1 होती है। इसे ax + b = c के रूप में लिखा जाता है।',
            'Standard Form: ax + b = c | Solution: x = (c - b) / a\nExample: 2x + 3 = 7 => 2x = 4 => x = 2',
            'linear_graph',
            'Arithmetic operations and integer addition/subtraction.'
        ),
        # Science - Newton's Laws
        (
            sub_map['SCI'],
            "Newton's Laws of Motion & Balanced Forces",
            'newtons-laws-motion',
            'Class 9-10',
            'Standard',
            "Mastering Newton's three laws of motion, inertia, momentum, and action-reaction pairs.",
            "Newton's 1st Law: Things are lazy and keep doing what they are doing until pushed. 2nd Law: F = m × a (heavy objects need more push). 3rd Law: For every action, there is an equal and opposite reaction!",
            """• 1st Law (Inertia): Body remains at rest or uniform motion unless acted upon by net external force.
• 2nd Law: Net Force = mass × acceleration (F = ma). SI Unit: Newton (N).
• 3rd Law: Forces always occur in pairs (F_action = -F_reaction) acting on different bodies.
• Balanced Forces: Net Force = 0 N (Zero acceleration).
• Unbalanced Forces: Net Force > 0 N (Causes acceleration).""",
            """Isaac Newton formulated the foundation of classical mechanics in 1687. Force is an interaction that changes or tends to change the state of rest or motion of a body. The three laws governing macroscopic systems are: Law of Inertia, Law of Momentum Rate of Change (dp/dt = F_net), and Law of Reciprocal Interactions.""",
            """EXAM PREPARATION - FREQUENT QUESTIONS:
1. State Newton's Third Law with two examples (3 Marks): Walking on ground & Rocket propulsion.
2. Differentiate Balanced and Unbalanced Forces (2 Marks): Balanced forces do not change state of motion (net F = 0); Unbalanced forces produce acceleration.
3. Numerical Formula: F = m * a where m is in kg, a in m/s^2, F in N.""",
            'Walking: Your foot pushes the ground backward (Action), and the ground pushes your foot forward (Reaction). Rocket: Gas pushes down, rocket shoots up!',
            'ನ್ಯೂಟನ್ ಅವರ ಮೂರನೇ ನಿಯಮ: ಪ್ರತಿ ಕ್ರಿಯೆಗೆ ಸಮಾನವಾದ ಹಾಗೂ ವಿರುದ್ಧ ದಿಕ್ಕಿನಲ್ಲಿ ಒಂದು ಪ್ರತಿಕ್ರಿಯೆ ಇರುತ್ತದೆ (Action and Reaction). ಉದಾಹರಣೆಗೆ: ನಾವು ನೆಲದ ಮೇಲೆ ನಡೆಯುವಾಗ ನೆಲವನ್ನು ಹಿಂದಕ್ಕೆ ತಳ್ಳುತ್ತೇವೆ, ನೆಲವು ನಮ್ಮನ್ನು ಮುಂದಕ್ಕೆ ತಳ್ಳುತ್ತದೆ.',
            'न्यूटन का तीसरा नियम: प्रत्येक क्रिया की समान और विपरीत प्रतिक्रिया होती है। जैसे: बंदूक से गोली चलने पर झटका लगना।',
            'Newton 2nd Law: F = m × a | Newton 3rd Law: F₁₂ = -F₂₁ | Momentum: p = m × v',
            'force_sim',
            'Basic concepts of speed, velocity, and push/pull forces.'
        ),
        # Science - Photosynthesis
        (
            sub_map['SCI'],
            'Photosynthesis & Plant Nutrition',
            'photosynthesis',
            'Class 8-10',
            'Foundation',
            'How green plants synthesize glucose using sunlight, chlorophyll, water, and carbon dioxide.',
            'Photosynthesis is the cooking process of plants! Leaves use solar energy, water from roots, and carbon dioxide from the air to make delicious sugar food and release oxygen for us.',
            """• Site: Chloroplasts containing green chlorophyll pigment.
• Raw Materials: Carbon Dioxide (CO₂), Water (H₂O), Sunlight.
• Byproducts: Glucose (C₆H₁₂O₆) and Oxygen (O₂ gas).
• Light Reactions: Splitting of water (photolysis) in grana.
• Dark Reactions (Calvin Cycle): Fixation of CO₂ in stroma.""",
            """Photosynthesis is an anabolic, endergonic biochemical process by which photoautotrophic organisms convert light energy into chemical energy stored in glucose. The overall balanced chemical equation is 6CO₂ + 6H₂O + radiant light → C₆H₁₂O₆ + 6O₂.""",
            """EXAM TIPS & LAB EXPERIMENTS:
1. Balanced chemical equation (Mandatory 2 Marks).
2. Starch Test on leaves using Iodine solution (Blue-black color indicates starch presence).
3. Role of Stomata: Microscopic pores guarded by guard cells for gas exchange.""",
            'A leaf is a solar kitchen! The sun provides stove heat, roots bring tap water, and air brings carbon dioxide to bake glucose bread.',
            'ದ್ಯುತಿಸಂಶ್ಲೇಷಣೆ: ಸಸ್ಯಗಳು ಸೂರ್ಯನ ಬೆಳಕು, ಕ್ಲೋರೊಫಿಲ್, ನೀರು ಮತ್ತು CO₂ ಬಳಸಿ ಆಹಾರ (ಗ್ಲೂಕೋಸ್) ತಯಾರಿಸುವ ಕ್ರಿಯೆ.',
            'प्रकाश संश्लेषण: हरे पौधे सूर्य के प्रकाश और पर्णहरिम की सहायता से भोजन बनाते हैं।',
            'Chemical Equation:\n6CO₂ + 6H₂O + Sunlight + Chlorophyll → C₆H₁₂O₆ + 6O₂',
            'photosynthesis',
            'Plant parts (roots, leaves, stem) and basic cellular structures.'
        ),
        # College - Programming in C
        (
            sub_map['CS-C'],
            'Pointers & Dynamic Memory in C',
            'c-pointers-memory',
            '1st/2nd Sem B.Tech',
            'Challenge',
            'Understanding memory addresses, pointer arithmetic, dereferencing, and malloc/free.',
            'A pointer is simply a variable that stores the house address of another variable in computer RAM! Instead of carrying the heavy furniture, you give someone the map address.',
            """• Declaration: int *ptr;
• Address-of operator (&): Gets memory address (&x).
• Dereference operator (*): Accesses the value stored at the address (*ptr).
• Memory Allocation: malloc(size) allocates bytes in Heap memory; free(ptr) releases it to prevent memory leaks.""",
            """Pointers allow direct hardware memory manipulation, efficient array passing, and dynamic data structure construction. A pointer variable stores the hexadecimal virtual address of another variable. Improper usage leads to segmentation faults, dangling pointers, and memory leaks.""",
            """EXAM CODING QUESTIONS:
1. Swap two integers using pointers (call by reference).
2. Dynamic array allocation using malloc() and free().
3. Difference between *ptr++ and (*ptr)++.""",
            'A web URL link on the internet: The link is a pointer that points to the actual webpage on a server!',
            'ಸಿ ಪ್ರೋಗ್ರಾಮಿಂಗ್‌ನಲ್ಲಿ ಪಾಯಿಂಟರ್ (Pointer) ಇನ್ನೊಂದು ವೇರಿಯೇಬಲ್‌ನ ಮೆಮೊರಿ ವಿಳಾಸವನ್ನು (Memory Address) ಸಂಗ್ರಹಿಸುವ ವಿಶೇಷ ವೇರಿಯೇಬಲ್ ಆಗಿದೆ.',
            'सी में पॉइंटर एक वेरिएबल है जो दूसरे वेरिएबल का मेमोरी एड्रेस स्टोर करता है।',
            'Syntax:\nint x = 10;\nint *ptr = &x; // stores address of x\nprintf("%d", *ptr); // prints 10',
            'c_pointer',
            'Basic C variables, data types, and functions.'
        )
    ]

    cursor.executemany("""
    INSERT INTO topics (
        subject_id, name, slug, grade_level, difficulty, summary,
        simple_explanation, pointwise_notes, detailed_explanation, exam_ready_notes,
        real_life_example, kannada_explanation, hindi_explanation,
        formula_box, visual_type, prerequisite_text
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, topics_data)

    cursor.execute("SELECT id, slug FROM topics")
    topic_map = {row['slug']: row['id'] for row in cursor.fetchall()}

    # Seed Prerequisites Graph
    prereqs_data = [
        (topic_map['linear-equations'], 'Fractions & Ratios', 'demonstrated', 'Mastered foundational arithmetic operations.'),
        (topic_map['linear-equations'], 'Algebraic Variables & Terms', 'demonstrated', 'Understands combining like terms.'),
        (topic_map['newtons-laws-motion'], 'Speed, Velocity & Acceleration', 'demonstrated', 'Calculates rate of change of position.'),
        (topic_map['newtons-laws-motion'], 'Vector Direction vs Scalar', 'needs_practice', 'Prerequisite recommended: Review force vector addition.'),
        (topic_map['c-pointers-memory'], 'C Variables & Data Types', 'demonstrated', 'Understands integer sizes and memory.'),
        (topic_map['c-pointers-memory'], 'Functions & Call Stack', 'needs_practice', 'Review pass-by-value vs pass-by-reference.')
    ]
    cursor.executemany("""
    INSERT INTO topic_prerequisites (topic_id, prerequisite_name, mastery_status, recommendation)
    VALUES (?, ?, ?, ?)
    """, prereqs_data)

    # Seed Quizzes with Hint Ladders & Mistake Detective
    quiz_inserts = [
        # Science - Balanced Force Question
        (
            topic_map['newtons-laws-motion'],
            'Standard',
            'Which of the following is an example of a balanced force?',
            'A moving car accelerating on a highway',
            'A book kept stationary on a table',
            'A kicked football flying through the air',
            'A freely falling apple towards Earth',
            'B',
            'A book kept at rest on a table has balanced forces: gravity pulls it downward while the normal contact force of the table pushes upward with equal magnitude, resulting in zero net force and zero acceleration.'
        ),
        (
            topic_map['newtons-laws-motion'],
            'Standard',
            'A 10 kg box is pushed with 30 N force to the right while 30 N friction acts to the left. What is the acceleration?',
            '3 m/s²',
            '0 m/s²',
            '1 m/s²',
            '6 m/s²',
            'B',
            'Net Force = 30 N - 30 N = 0 N. Since F_net = m * a, 0 = 10 * a => a = 0 m/s² (Forces are perfectly balanced).'
        ),
        # Math - Linear Equations
        (
            topic_map['linear-equations'],
            'Standard',
            'Solve the equation: 2(x + 3) = 14. What is the value of x?',
            'x = 5.5',
            'x = 4',
            'x = 11',
            'x = 8',
            'B',
            'Expand the bracket: 2*x + 2*3 = 14 => 2x + 6 = 14. Subtract 6: 2x = 8. Divide by 2: x = 4.'
        ),
        # College C Pointers
        (
            topic_map['c-pointers-memory'],
            'Challenge',
            'If int x = 20; int *ptr = &x; what will printf("%d", *ptr) output?',
            'Memory address of x',
            '20',
            'Garbage value',
            'Compiler syntax error',
            'B',
            'The dereference operator (*) accesses the value stored at the pointed address, which is 20.'
        )
    ]

    for q in quiz_inserts:
        cursor.execute("""
        INSERT INTO quizzes (topic_id, difficulty_mode, question, option_a, option_b, option_c, option_d, correct_option, explanation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, q)

    cursor.execute("SELECT id, question FROM quizzes")
    quiz_map = {row['question']: row['id'] for row in cursor.fetchall()}

    # Seed Hint Ladder (4 progressive levels) for Quiz 1 (Balanced Force)
    q1_id = quiz_map['Which of the following is an example of a balanced force?']
    hints_q1 = [
        (q1_id, 1, 'Recall the Core Concept', 'What does "balanced" mean? Think of a tug-of-war where both teams pull with the exact same strength so nobody moves.'),
        (q1_id, 2, 'Suggest Next Step', 'Check which scenario has an object with ZERO acceleration (either stationary or constant velocity).'),
        (q1_id, 3, 'Partial Solution', 'Look at the forces: Downward gravity and upward normal force on a resting surface cancel each other out.'),
        (q1_id, 4, 'Full Worked Explanation', 'A stationary book on a table has Net Force = 0 N because Table Normal Force (Up) = Gravity (Down). Therefore it is balanced.')
    ]
    cursor.executemany("""
    INSERT INTO quiz_hints (quiz_id, level, title, hint_text)
    VALUES (?, ?, ?, ?)
    """, hints_q1)

    # Seed Mistake Detective for Quiz 3 (2(x + 3) = 14)
    q3_id = quiz_map['Solve the equation: 2(x + 3) = 14. What is the value of x?']
    mistakes_q3 = [
        (
            q3_id,
            'C',
            'Distributive Property Error (Forgot to multiply inner term)',
            'You wrote 2x + 3 = 14 instead of 2x + 6 = 14. The outer multiplier (2) must be multiplied into BOTH x and 3.',
            'Always draw multiplication arrows: 2*(x) + 2*(3) = 2x + 6.',
            'Try solving: 3(x + 2) = 15. Expand carefully!'
        ),
        (
            q3_id,
            'A',
            'Premature Division / Order of Operations Confusion',
            'You subtracted 3 first without accounting for the bracket multiplier.',
            'Remember BODMAS: Clear parentheses first or divide the whole other side by 2 first: (x + 3) = 14/2 = 7.',
            'Try solving: 4(y - 1) = 12.'
        )
    ]
    cursor.executemany("""
    INSERT INTO mistake_detective (quiz_id, wrong_option, misconception_name, why_it_happens, how_to_fix, follow_up_practice)
    VALUES (?, ?, ?, ?, ?, ?)
    """, mistakes_q3)

    # Seed Spaced Repetition Flashcards
    flashcards_data = [
        (topic_map['newtons-laws-motion'], "What is Newton's First Law also known as?", "The Law of Inertia: An object at rest stays at rest unless acted upon by a net external force.", 1),
        (topic_map['newtons-laws-motion'], "Write the formula for Newton's Second Law.", "F = m × a (Force = mass × acceleration, measured in Newtons).", 2),
        (topic_map['newtons-laws-motion'], "Do action-reaction forces cancel each other out?", "No! They never cancel each other because they act on TWO DIFFERENT bodies.", 5),
        (topic_map['linear-equations'], "What is the degree of a linear equation?", "Degree is 1 (the variable's highest exponent is 1).", 1),
        (topic_map['photosynthesis'], "Where do the light-dependent reactions take place?", "In the thylakoid membranes / grana of the chloroplast.", 2),
        (topic_map['c-pointers-memory'], "What does the '&' operator do in C?", "Address-of operator: It returns the memory address where the variable is stored.", 1)
    ]
    cursor.executemany("""
    INSERT INTO flashcards (topic_id, front_prompt, back_answer, interval_day)
    VALUES (?, ?, ?, ?)
    """, flashcards_data)

    # Seed Teach-Back Prompts
    teach_back_data = [
        (
            topic_map['photosynthesis'],
            'Explain how photosynthesis works as if you were teaching it to a classmate in Class 8.',
            json.dumps(['sunlight', 'chlorophyll', 'water', 'carbon dioxide', 'glucose', 'oxygen']),
            'Green plants use sunlight absorbed by chlorophyll in leaves, water absorbed from roots, and carbon dioxide from the air. Through chemical reactions in chloroplasts, they produce glucose for energy and release oxygen gas into the atmosphere.',
            'Score 1 pt for mentioning sunlight/chlorophyll, 1 pt for raw materials (CO2 + water), 1 pt for products (glucose + O2).'
        ),
        (
            topic_map['newtons-laws-motion'],
            'Explain Newton\'s Third Law using a real-world example like swimming or rocket launch.',
            json.dumps(['action', 'reaction', 'equal', 'opposite', 'different bodies']),
            'Newton\'s Third Law states that whenever one object exerts a force on a second object, the second exerts an equal and opposite force on the first. In swimming, the swimmer pushes water backward (action), and the water pushes the swimmer forward (reaction).',
            'Must state equal and opposite direction, and specify that forces act on two different entities.'
        )
    ]
    cursor.executemany("""
    INSERT INTO teach_back_prompts (topic_id, prompt, required_concepts, model_answer, rubric_guide)
    VALUES (?, ?, ?, ?, ?)
    """, teach_back_data)

    # Seed Study Tasks
    cursor.execute("""
    INSERT INTO study_tasks (user_id, title, subject_id, scheduled_day, time_slot, is_completed, task_type)
    VALUES 
    (1, 'Foundation: Revise Balance Scales in Linear Equations', ?, 'Today', '10:00 AM - 10:45 AM', 1, 'revision'),
    (1, 'Mistake Review: Newton Forces Vector Diagnostic', ?, 'Today', '04:00 PM - 04:30 PM', 0, 'quiz'),
    (1, 'Teach-Back Challenge: Explain Photosynthesis to a Friend', ?, 'Tomorrow', '09:00 AM - 09:30 AM', 0, 'teach_back'),
    (1, 'Spaced Repetition: 5 Review Flashcards (Day 2 Interval)', ?, 'Tomorrow', '05:00 PM - 05:20 PM', 0, 'notes'),
    (1, 'Exam Prep: Mock Paper on Balanced Forces (45 mins)', ?, 'This Week', '06:00 PM - 06:45 PM', 0, 'quiz')
    """, (sub_map['MATH'], sub_map['SCI'], sub_map['SCI'], sub_map['MATH'], sub_map['SCI']))

    # Seed Learning Gaps
    cursor.execute("""
    INSERT INTO learning_gaps (user_id, topic_id, mastery_score, status, recommended_action)
    VALUES 
    (1, ?, 33.3, 'critical_gap', 'Critical Gap (33%): Focus on balanced vs unbalanced forces. Use Hint Ladder and Visual Simulation.'),
    (1, ?, 100.0, 'mastered', 'Mastered (100%): Ready for Challenge Mode multi-step equations.')
    """, (topic_map['newtons-laws-motion'], topic_map['linear-equations']))

    # Seed Confidence Record sample
    cursor.execute("""
    INSERT INTO confidence_records (user_id, quiz_id, selected_option, is_correct, confidence_level, classification)
    VALUES 
    (1, ?, 'C', 0, 'very_sure', 'misconception_warning')
    """, (q3_id,))

    # Seed Career Paths
    careers_data = [
        ('Artificial Intelligence & Data Engineering', 'Engineering', 'Mathematics, Computer Science, Statistics',
         'Design scalable machine learning models and intelligent data systems.', 'Python, Linear Algebra, Algorithms', 'SMVITM Bantakal, IISc, NITK', 'KCET, JEE Main', '₹7 - ₹28 LPA'),
        ('Medicine & Healthcare (MBBS / BDS)', 'Medicine', 'Biology, Chemistry, Physics',
         'Patient treatment, diagnostics, clinical healthcare advancement.', 'Anatomy, Clinical Diagnostics, Empathy', 'KMC Manipal, BMCRI, AIIMS', 'NEET UG', '₹8 - ₹35 LPA'),
        ('Software Systems & Cloud Architecture', 'Engineering', 'Computer Science, C/Python, Data Structures',
         'Build distributed systems, enterprise software, and cloud applications.', 'C, Java, System Design, Data Structures', 'SMVITM Bantakal, RVCE, PES', 'KCET, COMEDK', '₹6 - ₹24 LPA')
    ]
    cursor.executemany("""
    INSERT INTO career_paths (title, category, match_subjects, description, required_skills, colleges, entrance_exams, salary_range)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, careers_data)

    conn.commit()

if __name__ == "__main__":
    init_db()
    print("LearnSphere Master Database Initialized successfully.")
