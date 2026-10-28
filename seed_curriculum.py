"""
LearnSphere AI - Curriculum & Textbook-Aligned Content Seeder
Seeds comprehensive Karnataka State Board / DSERT syllabus topics,
notes, quizzes, hint ladders, and mistake detectives directly aligned
with the 86 official textbooks in `text books/`.
"""

import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "learnsphere.db")

def seed():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Ensure topics table has textbook_ref and textbook_id columns
    cursor.execute("PRAGMA table_info(topics)")
    cols = [col["name"] for col in cursor.fetchall()]
    if "textbook_ref" not in cols:
        cursor.execute("ALTER TABLE topics ADD COLUMN textbook_ref TEXT")
    if "textbook_id" not in cols:
        cursor.execute("ALTER TABLE topics ADD COLUMN textbook_id INTEGER")

    # 2. Verify or seed Subjects
    subjects_seed = [
        ('Mathematics', 'MATH', 'School', '📐', '#3b82f6', 'Algebra, Linear Equations, Geometry, Trigonometry, and Arithmetic Progressions.'),
        ('Science', 'SCI', 'School', '🔬', '#10b981', 'Physics (Laws of Motion, Light, Electricity) and Biology (Life Processes, Nutrition).'),
        ('Social Science', 'SOC', 'School', '🌍', '#f59e0b', 'History (Advent of Europeans), Civics (Indian Constitution), and Geography.'),
        ('English', 'ENG', 'School', '📖', '#8b5cf6', 'English Language, Active/Passive Voice, Reported Speech, and Grammar.'),
        ('Kannada', 'KAN', 'School', '🌟', '#f97316', 'ಕನ್ನಡ ಸಾಹಿತ್ಯ, ವ್ಯಾಕರಣ (ಸಂಧಿಗಳು, ಸಮಾಸಗಳು) ಮತ್ತು ಭಾಷಾಭ್ಯಾಸ.'),
        ('Hindi', 'HIN', 'School', '🇮🇳', '#ec4899', 'हिन्दी भाषा, व्याकरण (कारक, समास, मुहावरे) और वाक्य रचना।'),
        ('Programming in C', 'CS-C', 'College', '💻', '#06b6d4', 'C Language, Variables, Pointers, and Dynamic Memory Allocation.'),
        ('Data Structures', 'CS-DSA', 'College', '🌲', '#a855f7', 'Stacks, Queues, Linked Lists, Trees, and Sorting Algorithms.'),
        ('Artificial Intelligence', 'AIDS-AI', 'College', '🤖', '#6366f1', 'Search Algorithms, Knowledge Representation, and Machine Learning.')
    ]

    for name, code, cat, icon, color, desc in subjects_seed:
        cursor.execute("SELECT id FROM subjects WHERE code = ?", (code,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("""
            INSERT INTO subjects (name, code, category, icon, color, description)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (name, code, cat, icon, color, desc))

    cursor.execute("SELECT id, code FROM subjects")
    sub_map = {row['code']: row['id'] for row in cursor.fetchall()}

    # Helper to find textbook ID by class and subject snippet
    def find_tb(class_num, subject, medium_contains="english", title_snippet=""):
        q = "SELECT id, title FROM textbooks WHERE class_num = ? AND subject LIKE ?"
        params = [class_num, f"%{subject}%"]
        if medium_contains:
            q += " AND medium LIKE ?"
            params.append(f"%{medium_contains}%")
        if title_snippet:
            q += " AND title LIKE ?"
            params.append(f"%{title_snippet}%")
        cursor.execute(q, params)
        r = cursor.fetchone()
        return r[0] if r else None

    tb_math_p1 = find_tb(10, "Maths", "english", "PART-1") or 64
    tb_math_p2 = find_tb(10, "Maths", "english", "PART-2") or 63
    tb_sci_p1 = find_tb(10, "Science", "english", "PART-1") or 65
    tb_sci_p2 = find_tb(10, "Science", "english", "PART-2") or 66
    tb_kan_p1 = find_tb(10, "Kannada", "kannada", "FIRST LANGUAGE PART-1") or 75
    tb_eng_p1 = find_tb(10, "English", "english", "FIRST LANGUAGE PART-1") or 55
    tb_hin_p1 = find_tb(10, "Hindi", "hindi", "FIRST LANGUAGE PART-1") or 67

    # 3. Seed Comprehensive Topics
    topics_list = [
        # Mathematics - Linear Equations
        {
            "subject_id": sub_map['MATH'],
            "name": "Pair of Linear Equations in Two Variables",
            "slug": "linear-equations",
            "grade_level": "Class 10 (Karnataka SSLC)",
            "difficulty": "Standard",
            "summary": "Mastering algebraic elimination, substitution, and graphical solutions for systems of two linear equations.",
            "simple_explanation": "Imagine two weighing scales balance at the same time. A pair of linear equations has two unknown quantities (like the price of an apple and a mango). By comparing the two scales, you can find the exact value of both fruits!",
            "pointwise_notes": """• Standard Form: a₁x + b₁y + c₁ = 0 and a₂x + b₂y + c₂ = 0
• Consistency Conditions:
  1. Unique Solution (Intersecting lines): a₁/a₂ ≠ b₁/b₂
  2. Infinitely Many Solutions (Coincident lines): a₁/a₂ = b₁/b₂ = c₁/c₂
  3. No Solution (Parallel lines): a₁/a₂ = b₁/b₂ ≠ c₁/c₂
• Solution Methods: Elimination, Substitution, and Graphical Drawing.""",
            "detailed_explanation": """A system of two linear equations in two variables represents two straight lines in a 2D Cartesian plane. The solutions of the system correspond to the geometric intersection points of these lines. When lines intersect at a single point, the system is consistent with a unique solution. When lines coincide completely, they share an infinite number of common solutions. When lines are strictly parallel, the system has zero solutions and is inconsistent.""",
            "exam_ready_notes": """SSLC BOARD EXAM BLUEPRINT:
1. Consistency check (1 Mark): Verify ratios a₁/a₂, b₁/b₂, c₁/c₂.
2. Algebraic Elimination (3 Marks): Multiply equations to match coefficients of x or y, then add/subtract.
3. Mandatory Graphical Question (4 Marks): Plot points for each table and mark intersection coordinates (x, y).""",
            "real_life_example": "Market shopping: 2 pens and 3 notebooks cost ₹55; 4 pens and 1 notebook cost ₹45. Using linear equations reveals 1 pen = ₹8 and 1 notebook = ₹13.",
            "kannada_explanation": "ಎರಡು ಚರಾಕ್ಷರಗಳಿರುವ ರೇಖೀಯ ಸಮೀಕರಣಗಳ ಜೋಡಿ: a₁x + b₁y + c₁ = 0 ಮತ್ತು a₂x + b₂y + c₂ = 0. ಗ್ರಾಫ್‌ನಲ್ಲಿ ಎರಡು ಸರಳ ರೇಖೆಗಳು ಒಂದೇ ಬಿಂದುವಿನಲ್ಲಿ ಛೇದಿಸಿದರೆ ನಿರ್ದಿಷ್ಟ ಪರಿಹಾರವಿರುತ್ತದೆ.",
            "hindi_explanation": "दो चरों वाले रैखिक समीकरण युग्म का व्यापक रूप a₁x + b₁y + c₁ = 0 तथा a₂x + b₂y + c₂ = 0 होता है।",
            "formula_box": "General: a₁x + b₁y + c₁ = 0, a₂x + b₂y + c₂ = 0\nUnique: a₁/a₂ ≠ b₁/b₂ | Coincident: a₁/a₂ = b₁/b₂ = c₁/c₂ | Parallel: a₁/a₂ = b₁/b₂ ≠ c₁/c₂",
            "visual_type": "linear_graph",
            "prerequisite_text": "One-variable algebraic equations and coordinate graph plotting.",
            "textbook_ref": "Karnataka Class 10 Mathematics Part 1 • Chapter 3 (Pages 38-75)",
            "textbook_id": tb_math_p1
        },
        # Mathematics - Quadratic Equations
        {
            "subject_id": sub_map['MATH'],
            "name": "Quadratic Equations",
            "slug": "quadratic-equations",
            "grade_level": "Class 10 (Karnataka SSLC)",
            "difficulty": "Standard",
            "summary": "Standard form ax² + bx + c = 0, factorisation method, quadratic formula, and discriminant nature of roots.",
            "simple_explanation": "A quadratic equation is like calculating the area of a square garden where the side is stretched. The variable has power 2 (x²), which produces beautiful parabolic curves and two possible roots.",
            "pointwise_notes": """• Standard Form: ax² + bx + c = 0 (where a ≠ 0)
• Quadratic Formula: x = [-b ± √(b² - 4ac)] / (2a)
• Discriminant D = b² - 4ac:
  - If D > 0: Two distinct real roots
  - If D = 0: Two equal real roots (x = -b / 2a)
  - If D < 0: No real roots""",
            "detailed_explanation": """A second-degree polynomial equation in a single variable is termed a quadratic equation. The discriminant D = b² - 4ac determines the geometric nature of the roots by indicating whether the corresponding parabola intersects the x-axis twice, touches it tangentially at a single vertex point, or hovers entirely above/below the axis without real intercepts.""",
            "exam_ready_notes": """BOARD EXAM HIGH-YIELD POINTS:
1. Finding Discriminant D = b² - 4ac (1-2 Marks).
2. Solving by Quadratic Formula (2-3 Marks): State a, b, c clearly before substituting.
3. Word Problems (3-4 Marks): Speed/distance, age calculations, or geometric dimensions.""",
            "real_life_example": "Trajectory of a cricket ball hit for a six: The height follow h(t) = -5t² + 20t + 2, reaching the ground when h(t) = 0.",
            "kannada_explanation": "ವರ್ಗ ಸಮೀಕರಣಗಳು: ax² + bx + c = 0 ರೂಪದಲ್ಲಿರುತ್ತವೆ. ಶೋಧಕ D = b² - 4ac ಮೌಲ್ಯವು ಮೂಲಗಳ ಸ್ವಭಾವವನ್ನು ನಿರ್ಧರಿಸುತ್ತದೆ. D > 0 ಆದರೆ ಭಿನ್ನ ವಾಸ್ತವ ಮೂಲಗಳು, D = 0 ಆದರೆ ಸಮಾನ ವಾಸ್ತವ ಮೂಲಗಳು.",
            "hindi_explanation": "द्विघात समीकरण का मानक रूप ax² + bx + c = 0 होता है। विविक्तकर D = b² - 4ac मूलों की प्रकृति तय करता है।",
            "formula_box": "Standard: ax² + bx + c = 0\nFormula: x = [-b ± √(b² - 4ac)] / (2a)\nDiscriminant: D = b² - 4ac",
            "visual_type": "linear_graph",
            "prerequisite_text": "Polynomial factoring and square roots.",
            "textbook_ref": "Karnataka Class 10 Mathematics Part 1 • Chapter 4 (Pages 70-98)",
            "textbook_id": tb_math_p1
        },
        # Mathematics - Arithmetic Progressions
        {
            "subject_id": sub_map['MATH'],
            "name": "Arithmetic Progressions (A.P.)",
            "slug": "arithmetic-progressions",
            "grade_level": "Class 10 (Karnataka SSLC)",
            "difficulty": "Standard",
            "summary": "Sequences with constant common difference d, finding nth term a_n, and calculating sum of n terms S_n.",
            "simple_explanation": "An Arithmetic Progression is like climbing a staircase where every single step is the exact same height! If step 1 is 10 cm and each step is 5 cm, step 10 is guaranteed to be 10 + 9 × 5 = 55 cm.",
            "pointwise_notes": """• First term: a | Common difference: d = aₙ - aₙ₋₁
• General term: aₙ = a + (n - 1)d
• Sum of first n terms: Sₙ = (n/2)[2a + (n - 1)d]
• Sum when last term (l) is known: Sₙ = (n/2)(a + l)
• Sum of first n positive integers: Sₙ = n(n + 1) / 2""",
            "detailed_explanation": """An arithmetic progression is a sequence of numbers such that the difference of any two successive members is a constant called the common difference 'd'. It models linear discrete growth in economics, compound simple interest, acoustics, and physics.""",
            "exam_ready_notes": """FREQUENT BOARD EXAM QUESTIONS:
1. Find 10th or 20th term (2 Marks): Use aₙ = a + (n - 1)d.
2. Sum of n terms word problem (3 Marks).
3. If aₙ is given as an algebraic expression (e.g. 3n + 1), find common difference by computing a₁ and a₂.""",
            "real_life_example": "Savings piggy bank: Arjun saves ₹100 in January, and increases savings by ₹50 every subsequent month (₹100, ₹150, ₹200...).",
            "kannada_explanation": "ಸಮಾಂತರ ಶ್ರೇಢಿಗಳು (A.P.): ಯಾವುದೇ ಪದ ಮತ್ತು ಹಿಂದಿನ ಪದಗಳ ನಡುವಿನ ವ್ಯತ್ಯಾಸ ಸ್ಥಿರವಾಗಿರುವ ಶ್ರೇಢಿ. n ನೇ ಪದ aₙ = a + (n - 1)d, ಮೊತ್ತ Sₙ = n/2[2a + (n - 1)d].",
            "hindi_explanation": "समांतर श्रेढ़ी (A.P.): जिसमें क्रमागत पदों का अंतर समान (d) रहता है। n वां पद aₙ = a + (n - 1)d होता है।",
            "formula_box": "aₙ = a + (n - 1)d\nSₙ = (n/2)[2a + (n - 1)d] = (n/2)(a + l)\nSum of first n naturals = n(n + 1) / 2",
            "visual_type": "linear_graph",
            "prerequisite_text": "Sequences, pattern identification, and algebraic substitution.",
            "textbook_ref": "Karnataka Class 10 Mathematics Part 1 • Chapter 1 (Pages 1-36)",
            "textbook_id": tb_math_p1
        },
        # Mathematics - Trigonometry
        {
            "subject_id": sub_map['MATH'],
            "name": "Introduction to Trigonometry & Identities",
            "slug": "trigonometry",
            "grade_level": "Class 10 (Karnataka SSLC)",
            "difficulty": "Challenge",
            "summary": "Trigonometric ratios of acute angles, standard angle values, and fundamental trigonometric identities.",
            "simple_explanation": "Trigonometry connects the angles of a right triangle with the lengths of its sides! Using simple ratios like sin, cos, and tan, you can measure the height of a giant coconut tree without ever climbing it.",
            "pointwise_notes": """• Ratios in Right Triangle:
  - sin θ = Opposite / Hypotenuse
  - cos θ = Adjacent / Hypotenuse
  - tan θ = Opposite / Adjacent = sin θ / cos θ
• Reciprocals: csc θ = 1/sin θ, sec θ = 1/cos θ, cot θ = 1/tan θ
• Core Identities:
  1. sin²θ + cos²θ = 1
  2. 1 + tan²θ = sec²θ
  3. 1 + cot²θ = csc²θ""",
            "detailed_explanation": """Trigonometry originated from astronomical angle computations and triangulation. For acute angles in right triangles, the six trigonometric functions form invariant dimensionless ratios independent of the triangle size. Standard reference values at 0°, 30°, 45°, 60°, and 90° serve as calculation anchors.""",
            "exam_ready_notes": """PROVING IDENTITIES TIPS:
1. Always convert tan θ, sec θ, csc θ, cot θ into sin θ and cos θ terms.
2. Look for algebraic identities: (a + b)², a² - b² = (a - b)(a + b).
3. Value Evaluation (2 Marks): Remember sin 30° = 1/2, cos 60° = 1/2, tan 45° = 1.""",
            "real_life_example": "Shadow of a building: If a 10 m tower casts a 10 m shadow on the ground, the angle of the sun is tan θ = 10/10 = 1, so θ = 45°.",
            "kannada_explanation": "ತ್ರಿಕೋನಮಿತಿ: ಲಂಬಕೋನ ತ್ರಿಭುಜದ ಕೋನಗಳು ಮತ್ತು ಬಾಹುಗಳ ಸಂಬಂಧ. sin²θ + cos²θ = 1, 1 + tan²θ = sec²θ.",
            "hindi_explanation": "त्रिकोणमिति का परिचय: समकोण त्रिभुज में भुजाओं और कोणों का अनुपात। sin²θ + cos²θ = 1।",
            "formula_box": "sin²θ + cos²θ = 1 | 1 + tan²θ = sec²θ | 1 + cot²θ = csc²θ\nsin 30° = 1/2, cos 60° = 1/2, tan 45° = 1, sin 90° = 1",
            "visual_type": "linear_graph",
            "prerequisite_text": "Pythagoras theorem and right-angled triangle properties.",
            "textbook_ref": "Karnataka Class 10 Mathematics Part 2 • Chapter 8 (Pages 173-205)",
            "textbook_id": tb_math_p2
        },

        # Science - Force and Laws of Motion
        {
            "subject_id": sub_map['SCI'],
            "name": "Force and Laws of Motion",
            "slug": "newtons-laws-motion",
            "grade_level": "Class 9-10 (Karnataka Board)",
            "difficulty": "Standard",
            "summary": "Newton's three laws of motion, inertia, balanced forces, momentum, and action-reaction pairs.",
            "simple_explanation": "1st Law: Things are lazy and keep moving or resting until pushed. 2nd Law: F = m × a (heavier objects need bigger pushes). 3rd Law: For every action push, there is an equal and opposite reaction push!",
            "pointwise_notes": """• 1st Law (Inertia): Bodies maintain rest or uniform motion unless acted on by external unbalanced force.
• 2nd Law: Rate of change of momentum is proportional to applied force (F = ma). SI Unit: Newton (N).
• 3rd Law: Forces always occur in pairs; Action and Reaction are equal in magnitude and opposite in direction.
• Balanced Forces: Net force = 0 N (No acceleration).
• Unbalanced Forces: Net force > 0 N (Produces acceleration).""",
            "detailed_explanation": """Newtonian classical mechanics establishes force as the fundamental vector interaction governing macroscopic bodies. Inertia is quantified by mass. Newton's second law F = dp/dt simplifies to F = ma for constant mass systems.""",
            "exam_ready_notes": """FREQUENT SSLC EXAM QUESTIONS:
1. State Newton's 3rd Law with 2 examples (3 Marks): Walking on ground & Rocket propulsion.
2. Why passengers fall forward when bus brakes (2 Marks): Inertia of motion.
3. Numerical on F = ma (2 Marks).""",
            "real_life_example": "Rowing a boat: Oars push water backward (action), and the water pushes the boat forward (reaction).",
            "kannada_explanation": "ನ್ಯೂಟನ್ ಚಲನೆಯ ನಿಯಮಗಳು: 1ನೇ ನಿಯಮ ಜಡತ್ವ, 2ನೇ ನಿಯಮ F = ma, 3ನೇ ನಿಯಮ ಪ್ರತಿಯೊಂದು ಕ್ರಿಯೆಗೂ ಸಮಾನ ಹಾಗೂ ವಿರುದ್ಧ ಪ್ರತಿಕ್ರಿಯೆ ಇರುತ್ತದೆ.",
            "hindi_explanation": "न्यूटन के गति नियम: प्रथम नियम जड़त्व, द्वितीय नियम F = ma, तृतीय नियम क्रिया-प्रतिक्रिया का नियम।",
            "formula_box": "F = m × a | Momentum: p = m × v | Impulse: J = F × Δt | F₁₂ = -F₂₁",
            "visual_type": "force_sim",
            "prerequisite_text": "Speed, velocity, acceleration, and vector direction.",
            "textbook_ref": "Karnataka Class 9/10 Science Part 1 • Laws of Motion (Pages 110-135)",
            "textbook_id": tb_sci_p1
        },
        # Science - Photosynthesis & Nutrition
        {
            "subject_id": sub_map['SCI'],
            "name": "Life Processes: Nutrition & Photosynthesis",
            "slug": "photosynthesis",
            "grade_level": "Class 10 (Karnataka SSLC)",
            "difficulty": "Foundation",
            "summary": "Autotrophic nutrition in green plants, chlorophyll, stomatal gas exchange, and chemical reactions of photosynthesis.",
            "simple_explanation": "Leaves are natural solar kitchens! Green leaves catch sunlight using chlorophyll, absorb water from roots, and drink carbon dioxide from air to bake glucose food and give off oxygen for us to breathe.",
            "pointwise_notes": """• Equation: 6CO₂ + 6H₂O + Sunlight + Chlorophyll → C₆H₁₂O₆ + 6O₂
• Site: Chloroplasts containing green chlorophyll pigment.
• Main Events:
  1. Absorption of light energy by chlorophyll.
  2. Conversion of light energy to chemical energy & splitting of water molecules (photolysis).
  3. Reduction of carbon dioxide to carbohydrates (glucose).
• Stomata: Microscopic pores on leaf epidermis for gas exchange and transpiration.""",
            "detailed_explanation": """Photosynthesis is an anabolic, endergonic biochemical process by which photoautotrophic organisms synthesize organic hexose sugars from inorganic precursors. The photolytic cleavage of water in thylakoid membranes liberates molecular oxygen and protons for ATP and NADPH synthesis.""",
            "exam_ready_notes": """LAB EXPERIMENTS & 4-MARK DIAGRAMS:
1. Balanced chemical equation (Mandatory 2 Marks).
2. Starch test using Iodine solution (Turns blue-black if starch is present).
3. Diagram of Stomatal pore showing guard cells and chloroplasts.""",
            "real_life_example": "Houseplants placed near a sunny window grow lush and green, while plants kept in dark closets turn pale yellow and wither.",
            "kannada_explanation": "ದ್ಯುತಿಸಂಶ್ಲೇಷಣೆ: ಹಸಿರು ಸಸ್ಯಗಳು ಸೂರ್ಯನ ಬೆಳಕು, ಕ್ಲೋರೊಫಿಲ್, ನೀರು ಮತ್ತು ಇಂಗಾಲದ ಡೈಆಕ್ಸೈಡ್ ಬಳಸಿ ಗ್ಲೂಕೋಸ್ ಆಹಾರ ತಯಾರಿಸಿ ಆಮ್ಲಜನಕವನ್ನು ಬಿಡುಗಡೆ ಮಾಡುವ ಕ್ರಿಯೆ.",
            "hindi_explanation": "प्रकाश संश्लेषण: हरे पौधे सूर्य के प्रकाश और क्लोरोफिल की उपस्थिति में जल और CO₂ से भोजन (ग्लूकोज) बनाते हैं।",
            "formula_box": "6CO₂ + 6H₂O + Sunlight (Chlorophyll) → C₆H₁₂O₆ + 6O₂",
            "visual_type": "photosynthesis",
            "prerequisite_text": "Plant parts, cell structures, and basic chemical formulas.",
            "textbook_ref": "Karnataka Class 10 Science Part 1 • Chapter 6: Life Processes (Pages 93-112)",
            "textbook_id": tb_sci_p1
        },
        # Science - Electricity & Circuits
        {
            "subject_id": sub_map['SCI'],
            "name": "Electricity, Resistance & Circuits",
            "slug": "electricity-circuits",
            "grade_level": "Class 10 (Karnataka SSLC)",
            "difficulty": "Standard",
            "summary": "Ohm's law, electric potential, resistivity, series and parallel circuits, Joule's law of heating, and electric power.",
            "simple_explanation": "Electricity is like water flowing through pipes! Voltage is the water pump pressure, current is the flow rate of water, and resistance is the narrowness of the pipe that resists flow.",
            "pointwise_notes": """• Ohm's Law: V = I × R (Potential Difference = Current × Resistance)
• Factors affecting Resistance: R = ρ(l / A)
  - Directly proportional to length (l)
  - Inversely proportional to area of cross-section (A)
• Series Combination: Rₛ = R₁ + R₂ + R₃ (Current remains constant)
• Parallel Combination: 1/Rₚ = 1/R₁ + 1/R₂ + 1/R₃ (Voltage remains constant)
• Joule's Heating: H = I²Rt | Electric Power: P = VI = I²R = V²/R""",
            "detailed_explanation": """Electric current is defined as the rate of flow of net electric charge across a cross-section of a conductor. Georg Simon Ohm established that under constant physical temperature conditions, current is linearly proportional to voltage. Resistance measures the microscopic collisions between drifting electrons and lattice ions.""",
            "exam_ready_notes": """SSLC BOARD FREQUENT NUMERICALS:
1. Equivalent resistance of mixed circuits (3 Marks).
2. Cost of electric energy calculation (Units in kWh): Energy = Power (kW) × Hours.
3. Why domestic appliances are connected in parallel, NOT series (2 Marks): Independent switches and full 220 V across all devices.""",
            "real_life_example": "Diwali fairy lights: Old serial lights stop working if one bulb blows. Modern household wiring is parallel, so turning off the bedroom fan does not turn off the television!",
            "kannada_explanation": "ವಿದ್ಯುಚ್ಛಕ್ತಿ ಮತ್ತು ಮಂಡಲಗಳು: ಓಮ್‌ನ ನಿಯಮ V = IR. ಸರಣಿ ಜೋಡಣೆ Rₛ = R₁ + R₂, ಸಮಾಂತರ ಜೋಡಣೆ 1/Rₚ = 1/R₁ + 1/R₂. ಜೌಲನ ಶಾಖೋತ್ಪನ್ನ ನಿಯಮ H = I²Rt.",
            "hindi_explanation": "विद्युत: ओम का नियम V = IR। श्रेणीक्रम संयोजन Rₛ = R₁ + R₂, समांतर क्रम संयोजन 1/Rₚ = 1/R₁ + 1/R₂। जूल का तापन नियम H = I²Rt।",
            "formula_box": "V = I × R | R = ρ(l / A) | Series: Rₛ = ΣRᵢ | Parallel: 1/Rₚ = Σ(1/Rᵢ)\nH = I²Rt | P = VI = I²R = V²/R",
            "visual_type": "force_sim",
            "prerequisite_text": "Basic atomic structure, electrons, and battery potentials.",
            "textbook_ref": "Karnataka Class 10 Science Part 2 • Chapter 12: Electricity (Pages 199-225)",
            "textbook_id": tb_sci_p2
        },
        # Science - Light Reflection and Refraction
        {
            "subject_id": sub_map['SCI'],
            "name": "Light: Reflection & Refraction",
            "slug": "light-reflection-refraction",
            "grade_level": "Class 10 (Karnataka SSLC)",
            "difficulty": "Standard",
            "summary": "Laws of reflection, spherical mirrors (concave/convex), mirror formula, Snell's law, lens formula, and power of lenses.",
            "simple_explanation": "Reflection is light bouncing off shiny surfaces like a ball off a wall. Refraction is light bending when entering water or glass because it changes speed, making a pencil in water look bent!",
            "pointwise_notes": """• Mirror Formula: 1/f = 1/v + 1/u | Magnification: m = -v/u = h'/h
• Lens Formula: 1/f = 1/v - 1/u | Magnification: m = v/u = h'/h
• Snell's Law of Refraction: sin i / sin r = constant (n₂₁)
• Power of a Lens: P = 1 / f (in metres), SI Unit: Dioptre (D)
  - Convex lens: Focal length is positive (+)
  - Concave lens: Focal length is negative (-)""",
            "detailed_explanation": """Geometrical optics models light propagation as rectilinear rays. Concave spherical mirrors produce real, inverted images for object positions beyond the focus, and magnified virtual images when placed within the focal length. Convex mirrors provide broad virtual fields of view for rear-view navigation.""",
            "exam_ready_notes": """MANDATORY 4-MARK RAY DIAGRAMS:
1. Object placed between C and F of a concave mirror.
2. Refraction of light through a rectangular glass slab.
3. Convex lens object at 2F₁ (Image formed at 2F₂, real, inverted, same size).""",
            "real_life_example": "A swimming pool looks shallower than its actual depth due to the refraction of light rays bending away from normal upon exiting water.",
            "kannada_explanation": "ಬೆಳಕು - ಪ್ರತಿಫಲನ ಮತ್ತು ವಕ್ರೀಭವನ: ದರ್ಪಣ ಸೂತ್ರ 1/f = 1/v + 1/u, ಮಸೂರ ಸೂತ್ರ 1/f = 1/v - 1/u. ಮಸೂರದ ಸಾಮರ್ಥ್ಯ P = 1/f (ಡಯಾಪ್ಟರ್).",
            "hindi_explanation": "प्रकाश - परावर्तन तथा अपवर्तन: दर्पण सूत्र 1/f = 1/v + 1/u, लेंस सूत्र 1/f = 1/v - 1/u। लेंस की क्षमता P = 1/f (डायोप्टर)।",
            "formula_box": "Mirror: 1/f = 1/v + 1/u | Lens: 1/f = 1/v - 1/u | Snell: sin i / sin r = n\nPower: P = 1 / f (metres) [Dioptres, D]",
            "visual_type": "linear_graph",
            "prerequisite_text": "Straight line propagation of light, shadows, and angle measurement.",
            "textbook_ref": "Karnataka Class 10 Science Part 2 • Chapter 10: Light (Pages 160-198)",
            "textbook_id": tb_sci_p2
        },

        # Kannada - Sandhigalu
        {
            "subject_id": sub_map['KAN'],
            "name": "ಕನ್ನಡ ಸಂಧಿಗಳು (ಲೋಪ, ಆಗಮ, ಆದೇಶ ಸಂಧಿಗಳು)",
            "slug": "kannada-sandhigalu",
            "grade_level": "Class 10 (Karnataka SSLC)",
            "difficulty": "Standard",
            "summary": "ಕನ್ನಡ ವ್ಯಾಕರಣದ ಪ್ರಮುಖ ಸಂಧಿಗಳು: ಲೋಪ ಸಂಧಿ, ಆಗಮ ಸಂಧಿ (ಯಕಾರಾಗಮ, ವಕಾರಾಗಮ) ಮತ್ತು ಆದೇಶ ಸಂಧಿ ನಿಯಮಗಳು.",
            "simple_explanation": "ಎರಡು ಪದಗಳು ಸೇರಿ ಒಂದಾಗುವಾಗ ಅಕ್ಷರಗಳಲ್ಲಿ ಆಗುವ ಬದಲಾವಣೆಯೇ ಸಂಧಿ. ಒಂದು ಸ್ವರ ಬಿಟ್ಟು ಹೋದರೆ 'ಲೋಪ', ಹೊಸ ಅಕ್ಷರ ಬಂದರೆ 'ಆಗಮ', ಬೇರೆ ಅಕ್ಷರ ಬಂದು ಕುಳಿತರೆ 'ಆದೇಶ' ಸಂಧಿ!",
            "pointwise_notes": """• ಲೋಪ ಸಂಧಿ: ಸ್ವರದ ಮುಂದೆ ಸ್ವರ ಬಂದು ಅರ್ಥ ಕೆಡದಿದ್ದಾಗ ಹಿಂದಿನ ಸ್ವರ ಬಿಟ್ಟುಹೋಗುವುದು (ಉದಾ: ಮಾತು + ಇಲ್ಲ = ಮಾತಿಲ್ಲ, ಊರು + ಊರು = ಊರೂರು).
• ಆಗಮ ಸಂಧಿ: ಸ್ವರದ ಮುಂದೆ ಸ್ವರ ಬಂದಾಗ ಅರ್ಥ ಕೆಡದಂತೆ 'ಯ್' ಅಥವಾ 'ವ್' ವ್ಯಂಜನ ಹೊಸದಾಗಿ ಸೇರುವುದು:
  - ಯಕಾರಾಗಮ: ಮನೆ + ಅನ್ನು = ಮನೆಯನ್ನು, ಕೈ + ಅನ್ನು = ಕೈಯನ್ನು.
  - ವಕಾರಾಗಮ: ಗುರು + ಅನ್ನು = ಗುರುವನ್ನು, ಮರ + ಅನ್ನು = ಮರವನ್ನು.
• ಆದೇಶ ಸಂಧಿ: ಉತ್ತರಪದದ ಆದಿಯಲ್ಲಿರುವ ಕ, ತ, ಪ ವ್ಯಂಜನಗಳಿಗೆ ಕ್ರಮವಾಗಿ ಗ, ದ, ಬ ವ್ಯಂಜನಗಳು ಬರುವುದು (ಉದಾ: ಮಳೆ + ಕಾಲ = ಮಳೆಗಾಲ, ಕಣ್ + ಪನಿ = ಕಂಬನಿ).""",
            "detailed_explanation": """ಕನ್ನಡ ಭಾಷೆಯಲ್ಲಿ ಎರಡು ಶಬ್ದಗಳು ಪರಸ್ಪರ ಸೇರಿ ಒಂದಾಗುವಾಗ ಕಾಲವಿಳಂಬವಿಲ್ಲದೆ ಉಚ್ಚರಿಸಲ್ಪಡುವ ಪ್ರಕ್ರಿಯೆಗೆ ಸಂಧಿ ಎನ್ನಲಾಗುತ್ತದೆ. ಕನ್ನಡ ಸಂಧಿಗಳು ಕನ್ನಡ ಶಬ್ದಗಳ ನಡುವೆ ಮಾತ್ರ ನಡೆಯುತ್ತವೆ. ಸಂಸ್ಕೃತ ಸಂಧಿಗಳು ಕನ್ನಡದಲ್ಲಿ ತತ್ಸಮ ರೂಪಗಳಲ್ಲಿ ಕಂಡುಬರುತ್ತವೆ.""",
            "exam_ready_notes": """ಎಸ್.ಎಸ್.ಎಲ್.ಸಿ ಪರೀಕ್ಷಾ ಪ್ರಮುಖ ಪ್ರಶ್ನೆಗಳು:
1. ಸಂಧಿ ಬಿಡಿಸಿ ಹೆಸರಿಸಿ (2 ಅಂಕ): ಮಳೆಗಾಲ = ಮಳೆ + ಕಾಲ (ಆದೇಶ ಸಂಧಿ), ಮಾತಿಲ್ಲ = ಮಾತು + ಇಲ್ಲ (ಲೋಪ ಸಂಧಿ).
2. ಯಕಾರಾಗಮ ಮತ್ತು ವಕಾರಾಗಮ ವ್ಯತ್ಯಾಸ (2 ಅಂಕ).
3. ಕ, ತ, ಪ ಗಳಿಗೆ ಗ, ದ, ಬ ಗಳು ಆದೇಶವಾಗುವ ನಿಯಮ.""",
            "real_life_example": "ನಾವು ದಿನನಿತ್ಯ ಮಾತನಾಡುವಾಗ 'ಮಾತು ಇಲ್ಲ' ಎಂದು ಬೇರೆಬೇರೆ ಹೇಳುವುದಿಲ್ಲ, ವೇಗವಾಗಿ 'ಮಾತಿಲ್ಲ' ಎಂದು ಸಂಧಿಯ ರೂಪದಲ್ಲಿ ಮಾತನಾಡುತ್ತೇವೆ.",
            "kannada_explanation": "ಕನ್ನಡ ಸಂಧಿಗಳು: ಲೋಪ, ಆಗಮ ಮತ್ತು ಆದೇಶ ಸಂಧಿಗಳು ಕನ್ನಡದ ಮೂರು ಪ್ರಮುಖ ಸಂಧಿಗಳಾಗಿವೆ.",
            "hindi_explanation": "कन्नड़ व्याकरण में संधि: लोप संधि (स्वर का लुप्त होना), आगम संधि (नये वर्ण का आना) तथा आदेश संधि (वर्ण परिवर्तन)।",
            "formula_box": "ಲೋಪ: ಸ್ವರ + ಸ್ವರ = ಪೂರ್ವಸ್ವರ ಲೋಪ (ಮಾತು + ಇಲ್ಲ = ಮಾತಿಲ್ಲ)\nಆಗಮ: ಸ್ವರ + ಸ್ವರ = 'ಯ್'/'ವ್' ಆಗಮ (ಮನೆ + ಅನ್ನು = ಮನೆಯನ್ನು)\nಆದೇಶ: ಕ/ತ/ಪ → ಗ/ದ/ಬ (ಮಳೆ + ಕಾಲ = ಮಳೆಗಾಲ)",
            "visual_type": "none",
            "prerequisite_text": "ಕನ್ನಡ ವರ್ಣಮಾಲೆ, ಸ್ವರಗಳು, ವ್ಯಂಜನಗಳು ಮತ್ತು ಗುಣಿತಾಕ್ಷರಗಳು.",
            "textbook_ref": "Karnataka Class 10 Kannada First Language • ವ್ಯಾಕರಣ ವಿಭಾಗ (Pages 210-228)",
            "textbook_id": tb_kan_p1
        },
        # Kannada - Samasagalu
        {
            "subject_id": sub_map['KAN'],
            "name": "ಕನ್ನಡ ಸಮಾಸಗಳು (ತತ್ಪುರುಷ, ಕರ್ಮಧಾರಯ, ದ್ವಿಗು, ದ್ವಂದ್ವ)",
            "slug": "kannada-samasagalu",
            "grade_level": "Class 10 (Karnataka SSLC)",
            "difficulty": "Standard",
            "summary": "ತತ್ಪುರುಷ, ಕರ್ಮಧಾರಯ, ದ್ವಿಗು, ದ್ವಂದ್ವ ಮತ್ತು ಬಹುವ್ರೀಹಿ ಸಮಾಸಗಳ ಲಕ್ಷಣಗಳು, ವಿಗ್ರಹವಾಕ್ಯ ರಚನೆ ಮತ್ತು ಉದಾಹರಣೆಗಳು.",
            "simple_explanation": "ಬೇರೆ ಬೇರೆ ಅರ್ಥವುಳ್ಳ ಎರಡು ಪದಗಳು ಸೇರಿ ಒಂದೇ ಅರ್ಥವನ್ನು ಕೊಡುವ ಹೊಸ ಶಬ್ದವಾಗುವುದೇ ಸಮಾಸ. ಉದಾಹರಣೆಗೆ: 'ಹಿರಿದಾದ ಮರ' ಎನ್ನುವ ಬದಲು 'ಹೆಮ್ಮರ' ಎಂದು ಸಂಕ್ಷಿಪ್ತಗೊಳಿಸುವುದು.",
            "pointwise_notes": """• ತತ್ಪುರುಷ ಸಮಾಸ: ಉತ್ತರ ಪದದ ಅರ್ಥ ಪ್ರಧಾನವಾಗಿರುವ ಸಮಾಸ (ಉದಾ: ಮರದ + ಕಾಲು = ಮರಗಾಲು, ಅರಸನ + ಮನೆ = ಅರಮನೆ).
• ಕರ್ಮಧಾರಯ ಸಮಾಸ: ಪೂರ್ವಪದ ವಿಶೇಷಣ, ಉತ್ತರಪದ ವಿಶೇಷ್ಯವಾಗಿರುವ ಸಮಾಸ (ಉದಾ: ಹಿರಿದಾದ + ಮರ = ಹೆಮ್ಮರ, ಇಂಪಾದ + ನುಡಿ = ಇನ್ನುಡಿ).
• ದ್ವಿಗು ಸಮಾಸ: ಪೂರ್ವಪದ ಸಂಖ್ಯಾವಾಚಕವಾಗಿರುವ ಸಮಾಸ (ಉದಾ: ಮೂರು + ಲೋಕ = ಮೂರುಲೋಕ/ತ್ರಿಲೋಕ, ಎರಡು + ಮಡಿ = ಇಮ್ಮಡಿ).
• ದ್ವಂದ್ವ ಸಮಾಸ: ಪೂರ್ವ ಮತ್ತು ಉತ್ತರ ಎರಡೂ ಪದಗಳ ಅರ್ಥ ಸಮಾನ ಪ್ರಧಾನವಾಗಿರುವುದು (ಉದಾ: ಗಿಡವೂ + ಮರವೂ + ಬಳ್ಳಿಯೂ = ಗಿಡಮರಬಳ್ಳಿಗಳು).""",
            "detailed_explanation": """ಸಮಾಸವೆಂದರೆ ಸಂಕ್ಷಿಪ್ತಗೊಳಿಸುವುದು. ವಿಭಕ್ತಿ ಪ್ರತ್ಯಯಗಳ ಸಹಾಯದಿಂದ ಬಿಡಿಸಿ ಬರೆದ ವಾಕ್ಯವನ್ನು 'ವಿಗ್ರಹವಾಕ್ಯ' ಎನ್ನುತ್ತಾರೆ. ಜೋಡಿಸಿದ ಹೊಸ ಪದವನ್ನು 'ಸಮಸ್ತಪದ' ಎನ್ನುತ್ತಾರೆ. ಕನ್ನಡದಲ್ಲಿ ಪೂರ್ವಪದ ಮತ್ತು ಉತ್ತರಪದಗಳ ಪ್ರಾಧಾನ್ಯತೆಯ ಆಧಾರದಲ್ಲಿ ಸಮಾಸಗಳನ್ನು ವರ್ಗೀಕರಿಸಲಾಗಿದೆ.""",
            "exam_ready_notes": """ಪರೀಕ್ಷಾ ಪ್ರಮುಖ ವಿಗ್ರಹವಾಕ್ಯ ರಚನೆ:
1. ಹೆಮ್ಮರ = ಹಿರಿದಾದ ಮರ (ಕರ್ಮಧಾರಯ ಸಮಾಸ)
2. ಅರಮನೆ = ಅರಸನ ಮನೆ (ತತ್ಪುರುಷ ಸಮಾಸ)
3. ಪಂಚೇಂದ್ರಿಯಗಳು = ಐದು ಇಂದ್ರಿಯಗಳು (ದ್ವಿಗು ಸಮಾಸ)
4. ತಂದೆತಾಯಿಗಳು = ತಂದೆಯೂ ತಾಯಿಯೂ (ದ್ವಂದ್ವ ಸಮಾಸ)""",
            "real_life_example": "ದಿನಪತ್ರಿಕೆ ಅಥವಾ ಕವನಗಳಲ್ಲಿ ಭಾಷಾ ಸೌಂದರ್ಯ ಮತ್ತು ಸಂಕ್ಷಿಪ್ತತೆಗಾಗಿ ಸಮಾಸಗಳನ್ನು ಹೇರಳವಾಗಿ ಬಳಸಲಾಗುತ್ತದೆ.",
            "kannada_explanation": "ಸಮಾಸ: ಎರಡು ಅಥವಾ ಹೆಚ್ಚು ಪದಗಳು ಅರ್ಥಕ್ಕನುಗುಣವಾಗಿ ಸೇರಿ ಒಂದು ಪದವಾಗುವುದು ಸಮಾಸ.",
            "hindi_explanation": "कन्नड़ समास: तत्पुरुष, कर्मधारय, द्विगु और द्वंद्व समास।",
            "formula_box": "ತತ್ಪುರುಷ: ಉತ್ತರಪದ ಪ್ರಧಾನ | ಕರ್ಮಧಾರಯ: ವಿಶೇಷಣ + ವಿಶೇಷ್ಯ\nದ್ವಿಗು: ಸಂಖ್ಯಾವಾಚಕ ಪೂರ್ವಪದ | ದ್ವಂದ್ವ: ಸರ್ವಪದ ಪ್ರಧಾನ",
            "visual_type": "none",
            "prerequisite_text": "ನಾಮಪದಗಳು, ವಿಭಕ್ತಿ ಪ್ರತ್ಯಯಗಳು ಮತ್ತು ವಿಶೇಷಣಗಳು.",
            "textbook_ref": "Karnataka Class 10 Kannada First Language • ವ್ಯಾಕರಣ ವಿಭಾಗ (Pages 229-245)",
            "textbook_id": tb_kan_p1
        },

        # English - Active and Passive Voice
        {
            "subject_id": sub_map['ENG'],
            "name": "Active and Passive Voice",
            "slug": "active-passive-voice",
            "grade_level": "Class 10 (Karnataka SSLC)",
            "difficulty": "Standard",
            "summary": "Rules for converting active sentences to passive, tense auxiliary modifications, past participles, and by-agent usage.",
            "simple_explanation": "In Active Voice, the subject DOES the action (e.g. 'The cat chased the mouse'). In Passive Voice, the subject RECEIVES the action (e.g. 'The mouse was chased by the cat'). It shifts the spotlight!",
            "pointwise_notes": """• Core Transformation Rule: Object becomes Subject, Subject becomes Object with 'by'.
• Verb Formula: Auxiliary 'be' (am/is/are/was/were/being/been) + Past Participle (V3).
• Tense Table:
  - Simple Present: is/are + V3 (He writes a letter → A letter is written by him)
  - Simple Past: was/were + V3 (She helped me → I was helped by her)
  - Present Continuous: is/are being + V3 (They are playing cricket → Cricket is being played by them)
  - Present Perfect: has/have been + V3 (She has solved it → It has been solved by her)""",
            "detailed_explanation": """Voice indicates whether the grammatical subject performs or undergoes the verbal action. Passive constructions are vital in formal report writing, laboratory experiment procedures, and news journalism where the action or result matters more than the actor.""",
            "exam_ready_notes": """SSLC GRAMMAR RULES (2 MARKS):
1. Pronoun Changes: I → me, he → him, she → her, they → them, we → us.
2. Never change the tense! Present stays present, past stays past.
3. Continuous tenses always require 'being' before the V3 form.""",
            "real_life_example": "News headline: 'A new metro line was inaugurated yesterday' (Passive) sounds more formal and news-worthy than 'The Minister inaugurated a new metro line'.",
            "kannada_explanation": "ಕರ್ತರಿ ಮತ್ತು ಕರ್ಮಣಿ ಪ್ರಯೋಗಗಳು: Active Voice ಕರ್ತೃ ಪ್ರಧಾನವಾಗಿದ್ದರೆ, Passive Voice ಕರ್ಮ ಪದಕ್ಕೆ ಪ್ರಾಮುಖ್ಯತೆ ನೀಡುತ್ತದೆ.",
            "hindi_explanation": "वाच्य (Active & Passive Voice): कर्तृवाच्य में कर्ता की प्रधानता होती है, कर्मवाच्य में कर्म की प्रधानता होती है।",
            "formula_box": "Active: Subject + Verb + Object\nPassive: Object + Auxiliary (be) + V3 (Past Participle) + by + Subject",
            "visual_type": "none",
            "prerequisite_text": "Subjects, direct objects, verbs, and 3 forms of verbs (V1, V2, V3).",
            "textbook_ref": "Karnataka Class 10 English First Language • Grammar Section (Pages 140-158)",
            "textbook_id": tb_eng_p1
        },
        # English - Reported Speech
        {
            "subject_id": sub_map['ENG'],
            "name": "Direct and Indirect / Reported Speech",
            "slug": "reported-speech",
            "grade_level": "Class 10 (Karnataka SSLC)",
            "difficulty": "Challenge",
            "summary": "Rules for converting direct quotations into reported speech, tense backshifting, pronoun changes, and time expressions.",
            "simple_explanation": "Direct speech quotes the exact words inside quotation marks (\"I am happy\"). Reported speech narrates what someone said to another person without quotes ('He said that he was happy').",
            "pointwise_notes": """• Tense Backshifting (when reporting verb is past, e.g. 'said'):
  - Present Simple → Past Simple (writes → wrote)
  - Present Continuous → Past Continuous (is writing → was writing)
  - Present Perfect → Past Perfect (has written → had written)
  - Simple Past → Past Perfect (wrote → had written)
• Time & Place Changes:
  - now → then | today → that day | tomorrow → the next day / following day
  - yesterday → the previous day | here → there | this → that
• Sentence Types: Statements ('said that'), Questions ('asked if/whether' or 'wh-word'), Orders/Advice ('ordered/advised to + V1').""",
            "detailed_explanation": """Reported speech transfers discourse between conversational frames. In assertive sentences, inverted commas are dropped and replaced with the conjunction 'that'. In interrogative sentences, the question inversion is undone to form a standard subject-verb declarative clause.""",
            "exam_ready_notes": """EXAM PITFALLS TO AVOID (2 MARKS):
1. In questions, do NOT write 'asked that'! Example: He asked where I lived, NOT He asked that where I lived.
2. Inverted verb order disappears: 'where do you live?' becomes 'where I lived', NOT 'where did I live'.
3. Universal truths do NOT backshift: 'The teacher said that the Earth revolves around the Sun.'""",
            "real_life_example": "Telling a parent what the principal said at school: 'The principal told us that the annual day celebration is scheduled for Friday.'",
            "kannada_explanation": "ಪ್ರತ್ಯಕ್ಷ ಮತ್ತು ಪರೋಕ್ಷ ನಿರೂಪಣೆ: ಬೇರೆಯವರು ಹೇಳಿದ ಮಾತನ್ನು ಅವರದ್ದೇ ಪದಗಳಲ್ಲಿ ಹೇಳುವುದು Direct Speech; ಆ ಮಾತನ್ನು ನಮ್ಮ ಶಬ್ದಗಳಲ್ಲಿ ವಿವರಿಸುವುದು Indirect Speech.",
            "hindi_explanation": "प्रत्यक्ष और अप्रत्यक्ष कथन (Direct & Indirect Speech): किसी के कहे शब्दों को ज्यों का त्यों कहना या अपने शब्दों में व्यक्त करना।",
            "formula_box": "Statements: said to → told + that + backshifted clause\nQuestions: asked + (if / wh-word) + assertive word order (Subject + Verb)",
            "visual_type": "none",
            "prerequisite_text": "Tenses, pronouns, and punctuation marks.",
            "textbook_ref": "Karnataka Class 10 English First Language • Grammar Section (Pages 160-176)",
            "textbook_id": tb_eng_p1
        },

        # Hindi - Karak
        {
            "subject_id": sub_map['HIN'],
            "name": "कारक और उनके विभक्ति चिह्न (Karak & Vibhakti)",
            "slug": "hindi-karak",
            "grade_level": "Class 10 (Karnataka Board)",
            "difficulty": "Standard",
            "summary": "हिन्दी के आठ कारक (कर्ता, कर्म, करण, संप्रदान, अपादान, संबंध, अधिकरण, संबोधन) और उनके प्रसर्ग।",
            "simple_explanation": "संज्ञा या सर्वनाम का वाक्य की क्रिया से क्या रिश्ता है, यह बताने वाले चिह्नों को 'कारक' कहते हैं। जैसे: 'राम ने रावण को बाण से मारा' में 'ने', 'को', 'से' कारक चिह्न हैं।",
            "pointwise_notes": """• आठ कारक और उनके विभक्ति चिह्न (प्रसर्ग):
  1. कर्ता कारक: ने (काम करने वाला - राम ने पढ़ा)
  2. कर्म कारक: को (जिस पर क्रिया का फल पड़े - पुस्तक को देखो)
  3. करण कारक: से / के द्वारा (साधन - कलम से लिखा)
  4. संप्रदान कारक: को / के लिए (जिसके लिए क्रिया हो - बालक के लिए दूध लाओ)
  5. अपादान कारक: से (अलग होने के अर्थ में - पेड़ से पत्ता गिरा)
  6. संबंध कारक: का / के / की, रा / रे / री (संबंध दर्शाना - राजा का महल)
  7. अधिकरण कारक: में / पर (क्रिया का आधार - मेज पर पुस्तक है)
  8. संबोधन कारक: हे! / अरे! (संबोधित करना - हे ईश्वर!)""",
            "detailed_explanation": """कारक संज्ञा या सर्वनाम के उस रूप को कहते हैं जिससे उसका संबंध वाक्य की क्रिया तथा अन्य शब्दों के साथ जाना जाता है। इन संबंधों को व्यक्त करने वाले प्रत्ययों को विभक्ति या परसर्ग कहा जाता है। 'करण' और 'अपादान' दोनों में 'से' का प्रयोग होता है, किंतु करण साधन हेतु और अपादान अलगाव हेतु प्रयुक्त होता है।""",
            "exam_ready_notes": """बोर्ड परीक्षा मुख्य बिंदु (2 अंक):
1. करण और अपादान में अंतर: 'कलम से' (करण - साधन) बनाम 'पेड़ से' (अपादान - अलगाव)।
2. रिक्त स्थान में सही कारक चिह्न भरना।
3. रेखांकित शब्द का कारक पहचानना।""",
            "real_life_example": "'पेड़ से सेब गिरा' - सेब पेड़ से अलग हो रहा है, इसलिए यह अपादान कारक का प्रत्यक्ष उदाहरण है।",
            "kannada_explanation": "ಹಿಂದಿ ಕಾರಕಗಳು: ಕನ್ನಡದ ವಿಭಕ್ತಿ ಪ್ರತ್ಯಯಗಳಂತೆ (ಪ್ರಥಮಾ 'ನೇ', ದ್ವಿತೀಯಾ 'ಕೋ', ತೃತೀಯಾ 'ಸೇ'...) ಕ್ರಿಯಾಪದದ ಸಂಬಂಧವನ್ನು ಸೂಚಿಸುತ್ತವೆ.",
            "hindi_explanation": "कारक: संज्ञा या सर्वनाम के जिस रूप से क्रिया से संबंध जाना जाए, उसे कारक कहते हैं। कुल 8 भेद होते हैं।",
            "formula_box": "कर्ता ने | कर्म को | करण से/के द्वारा | संप्रदान के लिए\nअपादान से (अलग) | संबंध का/के/की | अधिकरण में/पर | संबोधन हे/अरे",
            "visual_type": "none",
            "prerequisite_text": "संज्ञा, सर्वनाम और क्रिया की बुनियादी पहचान।",
            "textbook_ref": "Karnataka Class 10 Hindi First Language • व्याकरण भाग (Pages 180-195)",
            "textbook_id": tb_hin_p1
        },
        # Hindi - Samas
        {
            "subject_id": sub_map['HIN'],
            "name": "समास और उनके भेद (Samas)",
            "slug": "hindi-samas",
            "grade_level": "Class 10 (Karnataka Board)",
            "difficulty": "Standard",
            "summary": "तत्पुरुष, कर्मधारय, द्विगु, द्वंद्व, अव्ययीभाव और बहुव्रीहि समास के नियम और विग्रह।",
            "simple_explanation": "दो या दो से अधिक शब्दों के मेल से संक्षिप्त नया सार्थक शब्द बनाने की क्रिया को समास कहते हैं। जैसे: 'राजा का पुत्र' कहने के बजाय 'राजपुत्र' कहना।",
            "pointwise_notes": """• समास के 6 प्रमुख भेद:
  1. अव्ययीभाव समास: पहला पद अव्यय और प्रधान (यथाशक्ति = शक्ति के अनुसार, प्रतिदिन = प्रत्येक दिन)
  2. तत्पुरुष समास: उत्तर पद प्रधान और कारक चिह्नों का लोप (राजमहल = राजा का महल)
  3. कर्मधारय समास: विशेषण-विशेष्य का संबंध (नीलकमल = नीला है जो कमल)
  4. द्विगु समास: पहला पद संख्यावाचक (त्रिलोक = तीन लोकों का समूह, चौराहा = चार राहों का समूह)
  5. द्वंद्व समास: दोनों पद समान रूप से प्रधान (माता-पिता = माता और पिता)
  6. बहुव्रीहि समास: दोनों पद गौण, तीसरा पद प्रधान (दशानन = दस हैं आनन जिसके अर्थात् रावण)""",
            "detailed_explanation": """समास का शाब्दिक अर्थ 'संक्षेप' है। परस्पर संबंध रखने वाले दो या दो से अधिक शब्दों के बीच की विभक्तियों का लोप करके एक नया शब्द बनाना समास कहलाता है। समस्त पद को अलग-अलग करके दिखाने की प्रक्रिया को 'समास विग्रह' कहते हैं।""",
            "exam_ready_notes": """बोर्ड परीक्षा टिप्स (2 अंक):
1. कर्मधारय बनाम बहुव्रीहि: 'नीलकंठ' = नीला कंठ (कर्मधारय), 'नीलकंठ' = नीला है कंठ जिसका अर्थात् शिव (बहुव्रीहि)।
2. द्विगु समास में संख्यावाचक पद की पहचान (चौराहा, पंचवटी)।
3. द्वंद्व समास में योजक चिह्न (-) और विग्रह में 'और' लगाना।""",
            "real_life_example": "हम वार्तालाप में 'रसोई के लिए घर' नहीं बोलते, बल्कि संक्षेप में 'रसोईघर' (तत्पुरुष समास) कहते हैं।",
            "kannada_explanation": "ಹಿಂದಿ ಸಮಾಸಗಳು: ತತ್ಪುರುಷ, ಕರ್ಮಧಾರಯ, ದ್ವಿಗು, ದ್ವಂದ್ವ, ಅವ್ಯಯೀಭಾವ ಮತ್ತು ಬಹುವ್ರೀಹಿ ಸಮಾಸಗಳು.",
            "hindi_explanation": "समास: दो या अधिक पदों का मेल। अव्ययीभाव, तत्पुरुष, कर्मधारय, द्विगु, द्वंद्व, बहुव्रीहि।",
            "formula_box": "अव्ययीभाव: अव्यय पद | तत्पुरुष: कारक लोप | कर्मधारय: विशेषण+विशेष्य\nद्विगु: संख्यावाचक | द्वंद्व: दोनों प्रधान | बहुव्रीहि: अन्य अर्थ प्रधान",
            "visual_type": "none",
            "prerequisite_text": "संधि, उपसर्ग, प्रत्यय और कारक चिह्न।",
            "textbook_ref": "Karnataka Class 10 Hindi First Language • व्याकरण भाग (Pages 196-212)",
            "textbook_id": tb_hin_p1
        },

        # Social Science - Advent of Europeans
        {
            "subject_id": sub_map['SOC'],
            "name": "The Advent of Europeans to India",
            "slug": "advent-europeans-india",
            "grade_level": "Class 10 (Karnataka SSLC)",
            "difficulty": "Standard",
            "summary": "Fall of Constantinople (1453), sea routes, trade rivalry between Portuguese, Dutch, French, English, and Battle of Plassey.",
            "simple_explanation": "When land spice trade routes were blocked by the Turks in 1453, brave sailors like Vasco da Gama discovered ocean routes to India. What began as peaceful spice trade quickly turned into military rivalry and colonial rule!",
            "pointwise_notes": """• 1453 Catalyst: Ottoman Turks captured Constantinople, closing the land transit route to Europe.
• 1498 Breakthrough: Portuguese sailor Vasco da Gama reached Kappad near Calicut (Kerala).
• Sequence of European Arrivals:
  1. Portuguese (Alfonso de Albuquerque captured Goa in 1510)
  2. Dutch (United East India Company, 1602)
  3. English (British East India Company chartered by Queen Elizabeth I, 1600)
  4. French (French East India Company, 1664)
• Decisive Turning Points:
  - Carnatic Wars established British supremacy over the French.
  - Battle of Plassey (1757): Robert Clive defeated Siraj-ud-Daulah.
  - Battle of Buxar (1764): Conferred Diwani (revenue collecting) rights of Bengal, Bihar, and Orissa to the British.""",
            "detailed_explanation": """The Portuguese were the pioneers of oceanic exploration to India, inaugurating the colonial spice monopoly. However, superior maritime power, corporate capital structure, and strategic diplomacy allowed the British East India Company to dismantle Dutch, Portuguese, and French commercial competition. The military victories at Plassey and Buxar transformed the British from a trading corporation into sovereign rulers of the Indian subcontinent.""",
            "exam_ready_notes": """FREQUENT SSLC BOARD QUESTIONS:
1. What led to the discovery of a new sea route to India? (2 Marks): Fall of Constantinople to Ottoman Turks in 1453.
2. Dual Government introduced by Robert Clive (2 Marks): British collected taxes (Diwani), while Nawab maintained administration without funds.
3. Outcome of the Battle of Buxar (3 Marks): British secured Diwani rights over Bengal, Bihar, and Orissa.""",
            "real_life_example": "Pepper and cardamom were called 'Black Gold' in Europe because they preserved meat during harsh European winters without refrigeration.",
            "kannada_explanation": "ಭಾರತಕ್ಕೆ ಯುರೋಪಿಯನ್ನರ ಆಗಮನ: 1453 ರಲ್ಲಿ ಕಾನ್‌ಸ್ಟಾಂಟಿನೋಪಲ್ ಪತನವಾದ ನಂತರ ವಾಸ್ಕೊಡಗಾಮ 1498 ರಲ್ಲಿ ಭಾರತಕ್ಕೆ ಜಲಮಾರ್ಗ ಕಂಡುಹಿಡಿದನು. ಪ್ಲಾಸಿ ಕದನ (1757) ಮತ್ತು ಬಕ್ಸಾರ್ ಕದನ (1764) ಬ್ರಿಟಿಷ್ ಸಾಮ್ರಾಜ್ಯಶಾಹಿಗೆ ನಾಂದಿ ಹಾಡಿದವು.",
            "hindi_explanation": "भारत में यूरोपीय लोगों का आगमन: 1453 में कुस्तुंतुनिया पर तुर्कों का अधिकार, 1498 में वास्को डि गामा का आगमन और 1757 का प्लासी युद्ध।",
            "formula_box": "1453: Fall of Constantinople → 1498: Vasco da Gama (Calicut) → 1757: Battle of Plassey → 1764: Battle of Buxar",
            "visual_type": "none",
            "prerequisite_text": "World geography, trade routes, and Mughal empire background.",
            "textbook_ref": "Karnataka Class 10 Social Science Part 1 • History Chapter 1 (Pages 1-18)",
            "textbook_id": 65
        },
        # Social Science - Indian Constitution
        {
            "subject_id": sub_map['SOC'],
            "name": "The Indian Constitution & Fundamental Rights",
            "slug": "indian-constitution",
            "grade_level": "Class 10 (Karnataka SSLC)",
            "difficulty": "Standard",
            "summary": "Preamble, Constituent Assembly, Drafting Committee under Dr. B. R. Ambedkar, and 6 Fundamental Rights under Part III.",
            "simple_explanation": "The Constitution is the supreme rulebook of our nation! It protects every citizen from injustice, guarantees freedom of speech, education, and equality, and ensures that everyone follows the same law.",
            "pointwise_notes": """• Framing History:
  - Constituent Assembly President: Dr. Rajendra Prasad
  - Drafting Committee Chairman: Dr. B. R. Ambedkar (Father of Indian Constitution)
  - Adopted on: 26 November 1949 | Enacted on: 26 January 1950 (Republic Day)
• Preamble: Declares India as a 'Sovereign, Socialist, Secular, Democratic Republic'.
• 6 Fundamental Rights (Part III, Articles 12-35):
  1. Right to Equality (Articles 14-18)
  2. Right to Freedom (Articles 19-22)
  3. Right against Exploitation (Articles 23-24)
  4. Right to Freedom of Religion (Articles 25-28)
  5. Cultural and Educational Rights (Articles 29-30)
  6. Right to Constitutional Remedies (Article 32 - called 'Heart and Soul' by Dr. Ambedkar)""",
            "detailed_explanation": """The Constitution of India is the longest written constitution of any sovereign state in the world. It establishes a federal structure with unitary bias. Fundamental Rights are justiciable, meaning citizens can directly petition the High Courts (Article 226) or Supreme Court (Article 32) through prerogative writs to protect against state infringement.""",
            "exam_ready_notes": """SSLC FREQUENT BOARD QUESTIONS:
1. Explain Article 32 as 'Heart and Soul' of the Constitution (3 Marks): Enables direct Supreme Court intervention through writs (Habeas Corpus, Mandamus, Prohibition, Quo-Warranto, Certiorari).
2. Four key values in Preamble (2 Marks): Justice, Liberty, Equality, Fraternity.
3. Abolition of Untouchability (1 Mark): Guaranteed under Article 17.""",
            "real_life_example": "If a government school refuses admission to a student based on caste or gender, the student can enforce their Right to Equality and Right to Education under the Constitution.",
            "kannada_explanation": "ಭಾರತದ ಸಂವಿಧಾನ ಮತ್ತು ಮೂಲಭೂತ ಹಕ್ಕುಗಳು: ಡಾ. ಬಿ.ಆರ್. ಅಂಬೇಡ್ಕರ್ ಅವರ ಅಧ್ಯಕ್ಷತೆಯಲ್ಲಿ ರಚಿತವಾದ ಸಂವಿಧಾನವು ಸಮಾನತೆ, ಸ್ವಾತಂತ್ರ್ಯ ಮತ್ತು ಸಂವಿಧಾನಾತ್ಮಕ ಪರಿಹಾರಗಳ ಹಕ್ಕನ್ನು ಖಾತರಿಪಡಿಸುತ್ತದೆ.",
            "hindi_explanation": "भारतीय संविधान तथा मौलिक अधिकार: डॉ. बी.आर. आंबेडकर द्वारा प्रारूपित। 6 मौलिक अधिकार संविधान के भाग 3 में वर्णित हैं।",
            "formula_box": "Adopted: 26 Nov 1949 | Enacted: 26 Jan 1950 | 6 Fundamental Rights | Article 32: Heart and Soul",
            "visual_type": "none",
            "prerequisite_text": "Indian freedom struggle and democratic values.",
            "textbook_ref": "Karnataka Class 10 Social Science Part 1 • Political Science Chapter 1 (Pages 65-82)",
            "textbook_id": 65
        },

        # College - C Pointers
        {
            "subject_id": sub_map['CS-C'],
            "name": "Pointers & Dynamic Memory in C",
            "slug": "c-pointers-memory",
            "grade_level": "1st/2nd Sem B.Tech (SMVITM Bantakal)",
            "difficulty": "Challenge",
            "summary": "Memory addresses, pointer arithmetic, dereferencing, call-by-reference, and dynamic allocation via malloc and free.",
            "simple_explanation": "A pointer is a variable that stores the memory address of another variable in RAM! Instead of duplicating a heavy data structure, you pass the GPS address of where it lives.",
            "pointwise_notes": """• Pointer Declaration: int *ptr;
• Address-of Operator (&): Retrieves the memory address (&x).
• Dereference Operator (*): Accesses the value stored at the referenced address (*ptr).
• Dynamic Memory Allocation in Heap:
  - malloc(n * sizeof(int)): Allocates uninitialized bytes.
  - calloc(n, sizeof(int)): Allocates and zeros memory.
  - free(ptr): Deallocates heap memory to prevent memory leaks.""",
            "detailed_explanation": """In C, memory is segmented into Code, Data, Stack, and Heap. Pointers enable direct byte-level manipulation of hardware addresses. Passing pointers to functions allows call-by-reference mutation and prevents stack frame bloat for large structures.""",
            "exam_ready_notes": """ENGINEERING EXAM CODING TRAPS:
1. Swapping two numbers using pointers (call by reference).
2. Dangling pointer: Using a pointer after calling free(ptr).
3. Memory leak: Forgetting free(ptr) in long-running loops.""",
            "real_life_example": "A website bookmark link: The bookmark does not duplicate the website contents; it points directly to the server URL address.",
            "kannada_explanation": "ಸಿ ಪ್ರೋಗ್ರಾಮಿಂಗ್‌ನಲ್ಲಿ ಪಾಯಿಂಟರ್‌ಗಳು: ಇನ್ನೊಂದು ವೇರಿಯೇಬಲ್‌ನ ಮೆಮೊರಿ ವಿಳಾಸವನ್ನು ಸಂಗ್ರಹಿಸುವ ವಿಶೇಷ ವೇರಿಯೇಬಲ್.",
            "hindi_explanation": "सी में पॉइंटर्स: किसी अन्य वेरिएबल का मेमोरी एड्रेस स्टोर करने वाला विशेष वेरिएबल।",
            "formula_box": "int x = 10; int *p = &x;\n*p = 20; // x becomes 20\nptr = (int*)malloc(n * sizeof(int));\nfree(ptr);",
            "visual_type": "c_pointer",
            "prerequisite_text": "C variables, data types, functions, and array indexing.",
            "textbook_ref": "VTU / SMVITM 1st Year Engineering • Programming in C (Module 4: Pointers)",
            "textbook_id": 55
        },
        # College - Data Structures Stack and Queue
        {
            "subject_id": sub_map['CS-DSA'],
            "name": "Stacks, Queues & Linear Data Structures",
            "slug": "data-structures-stack-queue",
            "grade_level": "3rd Sem B.Tech (SMVITM Bantakal)",
            "difficulty": "Challenge",
            "summary": "LIFO stack operations, FIFO queue operations, overflow/underflow checks, and infix-to-postfix conversions.",
            "simple_explanation": "A Stack is like a stack of cafeteria plates: the last plate placed on top is the first plate taken (LIFO). A Queue is like waiting in a movie ticket line: the first person to arrive is the first person served (FIFO)!",
            "pointwise_notes": """• Stack Operations (LIFO):
  - push(val): Adds item to top (Check Stack Overflow: top == MAX - 1)
  - pop(): Removes and returns item from top (Check Stack Underflow: top == -1)
  - peek(): Inspects top without removal
• Queue Operations (FIFO):
  - enqueue(val): Inserts at rear
  - dequeue(): Removes from front
• Applications: Undo/Redo in editors, browser back history, printer spoolers, and infix-to-postfix expressions.""",
            "detailed_explanation": """Stacks and Queues are fundamental linear abstract data types (ADTs) with constrained insertion and deletion endpoints. Stacks provide the runtime mechanism for nested function call frames, recursion trees, and syntax validation in compiler parsers.""",
            "exam_ready_notes": """DSA EXAM ALGORITHMS:
1. Push and Pop array implementation with boundary checks.
2. Infix to Postfix conversion using operator precedence stack.
3. Circular Queue to solve standard array queue memory waste.""",
            "real_life_example": "The 'Undo' (Ctrl+Z) feature in Google Docs: Every edit is pushed onto an undo stack. When you hit undo, the most recent action is popped off.",
            "kannada_explanation": "ಡೇಟಾ ಸ್ಟ್ರಕ್ಚರ್ಸ್: ಸ್ಟಾಕ್ (LIFO - Last In First Out) ಮತ್ತು ಕ್ಯೂ (FIFO - First In First Out) ರೇಖೀಯ ದತ್ತಾಂಶ ರಚನೆಗಳು.",
            "hindi_explanation": "डेटा संरचनाएँ: स्टैक (LIFO सिद्धांत) तथा क्यू (FIFO सिद्धांत)।",
            "formula_box": "Stack: LIFO (top = top + 1) | Queue: FIFO (front, rear)\nInfix to Postfix: Shunting-Yard Algorithm",
            "visual_type": "none",
            "prerequisite_text": "Arrays, struct in C, and pointer manipulations.",
            "textbook_ref": "VTU / SMVITM 3rd Sem Computer Science • Data Structures (Module 2: Stacks & Queues)",
            "textbook_id": 64
        }
    ]

    for t in topics_list:
        cursor.execute("SELECT id FROM topics WHERE slug = ?", (t["slug"],))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("""
            UPDATE topics SET
                subject_id = ?, name = ?, grade_level = ?, difficulty = ?, summary = ?,
                simple_explanation = ?, pointwise_notes = ?, detailed_explanation = ?,
                exam_ready_notes = ?, real_life_example = ?, kannada_explanation = ?,
                hindi_explanation = ?, formula_box = ?, visual_type = ?,
                prerequisite_text = ?, textbook_ref = ?, textbook_id = ?
            WHERE id = ?
            """, (
                t["subject_id"], t["name"], t["grade_level"], t["difficulty"], t["summary"],
                t["simple_explanation"], t["pointwise_notes"], t["detailed_explanation"],
                t["exam_ready_notes"], t["real_life_example"], t["kannada_explanation"],
                t["hindi_explanation"], t["formula_box"], t["visual_type"],
                t["prerequisite_text"], t["textbook_ref"], t["textbook_id"], existing["id"]
            ))
        else:
            cursor.execute("""
            INSERT INTO topics (
                subject_id, name, slug, grade_level, difficulty, summary,
                simple_explanation, pointwise_notes, detailed_explanation, exam_ready_notes,
                real_life_example, kannada_explanation, hindi_explanation,
                formula_box, visual_type, prerequisite_text, textbook_ref, textbook_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                t["subject_id"], t["name"], t["slug"], t["grade_level"], t["difficulty"], t["summary"],
                t["simple_explanation"], t["pointwise_notes"], t["detailed_explanation"],
                t["exam_ready_notes"], t["real_life_example"], t["kannada_explanation"],
                t["hindi_explanation"], t["formula_box"], t["visual_type"],
                t["prerequisite_text"], t["textbook_ref"], t["textbook_id"]
            ))

    cursor.execute("SELECT id, slug FROM topics")
    topic_map = {row['slug']: row['id'] for row in cursor.fetchall()}

    # 4. Clean and reseed Quizzes with high syllabus alignment
    # Remove old quizzes and insert the full textbook set
    cursor.execute("DELETE FROM quizzes")
    cursor.execute("DELETE FROM quiz_hints")
    cursor.execute("DELETE FROM mistake_detective")

    quiz_records = [
        # 1. Linear Equations (Maths)
        (
            topic_map["linear-equations"], "Standard",
            "For what condition do two linear equations a₁x + b₁y + c₁ = 0 and a₂x + b₂y + c₂ = 0 represent coincident lines with infinitely many solutions?",
            "a₁/a₂ ≠ b₁/b₂",
            "a₁/a₂ = b₁/b₂ = c₁/c₂",
            "a₁/a₂ = b₁/b₂ ≠ c₁/c₂",
            "a₁/a₂ + b₁/b₂ = 1",
            "B",
            "Two lines are coincident (overlapping everywhere) when the ratios of their coefficients and constants are strictly identical: a₁/a₂ = b₁/b₂ = c₁/c₂."
        ),
        (
            topic_map["linear-equations"], "Standard",
            "Solve the system of equations: x + y = 14 and x - y = 4. What are the values of x and y?",
            "x = 10, y = 4",
            "x = 9, y = 5",
            "x = 8, y = 6",
            "x = 11, y = 3",
            "B",
            "Adding the two equations: 2x = 18 => x = 9. Substituting x = 9 into x + y = 14 gives y = 5."
        ),
        (
            topic_map["linear-equations"], "Challenge",
            "If 2x + 3y = 11 and 2x - 4y = -24, what is the value of m for which y = mx + 3?",
            "m = 1",
            "m = -1",
            "m = 2",
            "m = -2",
            "B",
            "Subtracting the equations gives 7y = 35 => y = 5. Then 2x + 15 = 11 => 2x = -4 => x = -2. Substituting into y = mx + 3 gives 5 = m(-2) + 3 => 2 = -2m => m = -1."
        ),
        (
            topic_map["linear-equations"], "Foundation",
            "Solve the linear equation: 2(x + 3) = 14. What is the value of x?",
            "x = 5.5",
            "x = 4",
            "x = 11",
            "x = 8",
            "B",
            "Expanding the parentheses: 2x + 6 = 14 => 2x = 8 => x = 4."
        ),

        # 2. Quadratic Equations (Maths)
        (
            topic_map["quadratic-equations"], "Standard",
            "What is the nature of the roots of a quadratic equation ax² + bx + c = 0 if the discriminant b² - 4ac > 0?",
            "No real roots",
            "Two equal real roots",
            "Two distinct real roots",
            "Imaginary roots only",
            "C",
            "When the discriminant D > 0, the quadratic formula yields two distinct real numbers: (-b ± √D) / 2a."
        ),
        (
            topic_map["quadratic-equations"], "Standard",
            "Find the roots of the quadratic equation: x² - 5x + 6 = 0.",
            "x = 2 and x = 3",
            "x = -2 and x = -3",
            "x = 1 and x = 6",
            "x = -1 and x = -6",
            "A",
            "Factorising the quadratic: (x - 2)(x - 3) = 0. Therefore, the roots are x = 2 and x = 3."
        ),
        (
            topic_map["quadratic-equations"], "Standard",
            "What is the discriminant of the quadratic equation 2x² - 4x + 3 = 0?",
            "8",
            "-8",
            "16",
            "0",
            "B",
            "Discriminant D = b² - 4ac = (-4)² - 4(2)(3) = 16 - 24 = -8. Since D < 0, it has no real roots."
        ),
        (
            topic_map["quadratic-equations"], "Challenge",
            "If one root of the quadratic equation 2x² + kx - 6 = 0 is 2, what is the value of k?",
            "k = 1",
            "k = -1",
            "k = 2",
            "k = -2",
            "B",
            "Substitute x = 2: 2(2)² + k(2) - 6 = 0 => 8 + 2k - 6 = 0 => 2k = -2 => k = -1."
        ),

        # 3. Arithmetic Progressions (Maths)
        (
            topic_map["arithmetic-progressions"], "Standard",
            "In an Arithmetic Progression, if first term a = 7 and common difference d = 3, what is the 10th term (a₁₀)?",
            "31",
            "34",
            "37",
            "30",
            "B",
            "Formula aₙ = a + (n - 1)d => a₁₀ = 7 + (10 - 1)(3) = 7 + 27 = 34."
        ),
        (
            topic_map["arithmetic-progressions"], "Standard",
            "What is the formula for the sum of the first n terms of an A.P. with first term a and last term l?",
            "Sₙ = n(a + l)",
            "Sₙ = (n/2)(a + l)",
            "Sₙ = (n/2)(2a + l)",
            "Sₙ = n(a - l)",
            "B",
            "The sum of n terms with known first term 'a' and last term 'l' is Sₙ = (n/2)(a + l)."
        ),
        (
            topic_map["arithmetic-progressions"], "Standard",
            "Which term of the A.P. 21, 18, 15, ... is zero?",
            "7th term",
            "8th term",
            "9th term",
            "10th term",
            "B",
            "Here a = 21, d = 18 - 21 = -3. Setting aₙ = 0 => 21 + (n - 1)(-3) = 0 => -3(n - 1) = -21 => n - 1 = 7 => n = 8."
        ),
        (
            topic_map["arithmetic-progressions"], "Foundation",
            "Find the sum of the first 20 positive integers (1 + 2 + 3 + ... + 20).",
            "200",
            "210",
            "220",
            "190",
            "B",
            "Using formula Sₙ = n(n + 1) / 2 => S₂₀ = 20 × 21 / 2 = 210."
        ),

        # 4. Trigonometry (Maths)
        (
            topic_map["trigonometry"], "Standard",
            "In a right-angled triangle, if sin θ = 3/5, what is the value of cos θ?",
            "4/5",
            "5/4",
            "3/4",
            "5/3",
            "A",
            "Using the fundamental identity sin²θ + cos²θ = 1 => cos θ = √(1 - 9/25) = √(16/25) = 4/5."
        ),
        (
            topic_map["trigonometry"], "Foundation",
            "What is the exact numerical value of sin 30° + cos 60°?",
            "0",
            "1/2",
            "1",
            "√3",
            "C",
            "sin 30° = 1/2 and cos 60° = 1/2. Their sum is 1/2 + 1/2 = 1."
        ),
        (
            topic_map["trigonometry"], "Standard",
            "Simplify the trigonometric expression: (1 + tan²θ) / (1 + cot²θ).",
            "sin²θ",
            "tan²θ",
            "cot²θ",
            "sec²θ",
            "B",
            "1 + tan²θ = sec²θ and 1 + cot²θ = csc²θ. sec²θ / csc²θ = (1/cos²θ) / (1/sin²θ) = sin²θ / cos²θ = tan²θ."
        ),
        (
            topic_map["trigonometry"], "Standard",
            "Evaluate: 9 sec²A - 9 tan²A.",
            "1",
            "9",
            "8",
            "0",
            "B",
            "Factoring out 9: 9(sec²A - tan²A). Since sec²A - tan²A = 1, the result is 9 × 1 = 9."
        ),

        # 5. Force and Laws of Motion (Science)
        (
            topic_map["newtons-laws-motion"], "Standard",
            "Which of the following is an example of a balanced force?",
            "A moving car accelerating on a highway",
            "A book kept stationary on a table",
            "A kicked football flying through the air",
            "A freely falling apple towards Earth",
            "B",
            "A stationary book on a table has downward gravity balanced by upward normal contact force of the table, producing zero net force and zero acceleration."
        ),
        (
            topic_map["newtons-laws-motion"], "Standard",
            "A 10 kg box is pushed with 30 N force to the right while 30 N friction acts to the left. What is the acceleration?",
            "3 m/s²",
            "0 m/s²",
            "1 m/s²",
            "6 m/s²",
            "B",
            "Net Force = 30 N - 30 N = 0 N. By F = ma, a = 0 / 10 = 0 m/s²."
        ),
        (
            topic_map["newtons-laws-motion"], "Standard",
            "Why does a passenger fall forward when a moving bus suddenly applies brakes?",
            "Inertia of rest",
            "Inertia of motion",
            "Gravitational pull increases",
            "Action-reaction cancellation",
            "B",
            "Due to inertia of motion, the upper body continues moving forward while the feet come to rest with the bus."
        ),
        (
            topic_map["newtons-laws-motion"], "Standard",
            "When a bullet is fired from a gun, the gun recoils backward. This is a direct consequence of which law?",
            "Newton's First Law",
            "Newton's Second Law",
            "Newton's Third Law",
            "Universal Law of Gravitation",
            "C",
            "Newton's Third Law states every action has an equal and opposite reaction. The bullet shoots forward, recoil pushes backward."
        ),

        # 6. Photosynthesis (Science)
        (
            topic_map["photosynthesis"], "Foundation",
            "What are the primary raw materials required by green plants for photosynthesis?",
            "Glucose, Oxygen, and Soil",
            "Carbon Dioxide, Water, and Sunlight",
            "Nitrogen, Oxygen, and Hydrogen",
            "Starch, Protein, and Chlorophyll",
            "B",
            "Photosynthesis converts carbon dioxide and water into glucose and oxygen in the presence of sunlight and chlorophyll."
        ),
        (
            topic_map["photosynthesis"], "Standard",
            "During the starch test of a green leaf, what color does the leaf turn when treated with iodine solution?",
            "Bright Red",
            "Blue-black",
            "Pale Yellow",
            "Colorless",
            "B",
            "Iodine interacts chemically with starch stored in leaves to form a blue-black compound."
        ),
        (
            topic_map["photosynthesis"], "Standard",
            "In which cellular organelle does photosynthesis take place inside plant cells?",
            "Mitochondria",
            "Chloroplast",
            "Ribosome",
            "Endoplasmic Reticulum",
            "B",
            "Chloroplasts contain green chlorophyll pigments and are the dedicated sites of photosynthesis."
        ),
        (
            topic_map["photosynthesis"], "Challenge",
            "The oxygen gas (O₂) released into the atmosphere during photosynthesis originates from which reactant?",
            "Carbon Dioxide (CO₂)",
            "Water (H₂O)",
            "Glucose (C₆H₁₂O₆)",
            "Atmospheric Nitrogen",
            "B",
            "During light-dependent reactions, photolysis splits water (H₂O) into protons, electrons, and oxygen gas (O₂)."
        ),

        # 7. Electricity & Circuits (Science)
        (
            topic_map["electricity-circuits"], "Standard",
            "According to Ohm's Law, what is the mathematical relationship between Potential Difference (V), Current (I), and Resistance (R)?",
            "V = I / R",
            "V = I × R",
            "I = V × R",
            "R = V × I",
            "B",
            "Ohm's Law states that current through a conductor is directly proportional to voltage across its ends: V = IR."
        ),
        (
            topic_map["electricity-circuits"], "Standard",
            "Two resistors of 4 Ω and 6 Ω are connected in series across a 10 V battery. What is the total equivalent resistance?",
            "2.4 Ω",
            "10 Ω",
            "24 Ω",
            "5 Ω",
            "B",
            "In series connection, equivalent resistance is the arithmetic sum: Rₛ = R₁ + R₂ = 4 Ω + 6 Ω = 10 Ω."
        ),
        (
            topic_map["electricity-circuits"], "Standard",
            "What is the SI unit of electric resistivity (ρ)?",
            "Ohm (Ω)",
            "Ohm-metre (Ω·m)",
            "Ampere per metre (A/m)",
            "Watt (W)",
            "B",
            "From R = ρ(l / A), resistivity ρ = R × A / l = Ω × m² / m = Ω·m."
        ),
        (
            topic_map["electricity-circuits"], "Challenge",
            "An electric iron consumes 1 kW electric power when operated at 220 V. How much heat is produced in 1 second?",
            "1000 Joules",
            "220 Joules",
            "4400 Joules",
            "50 Joules",
            "A",
            "Heat produced H = Power × Time = 1000 W × 1 s = 1000 Joules."
        ),

        # 8. Light: Reflection & Refraction (Science)
        (
            topic_map["light-reflection-refraction"], "Standard",
            "What is the focal length of a spherical mirror whose radius of curvature is 30 cm?",
            "60 cm",
            "15 cm",
            "30 cm",
            "10 cm",
            "B",
            "Focal length is half of the radius of curvature: f = R / 2 = 30 / 2 = 15 cm."
        ),
        (
            topic_map["light-reflection-refraction"], "Standard",
            "Which type of mirror is universally used as a rear-view mirror in vehicles to provide a wide field of view?",
            "Concave mirror",
            "Convex mirror",
            "Plane mirror",
            "Cylindrical mirror",
            "B",
            "Convex mirrors always form erect, diminished virtual images with a wide outward field of view."
        ),
        (
            topic_map["light-reflection-refraction"], "Standard",
            "The refractive index of glass with respect to air is 1.5. What is the speed of light in glass? (Speed of light in air = 3 × 10⁸ m/s)",
            "1.5 × 10⁸ m/s",
            "2 × 10⁸ m/s",
            "3 × 10⁸ m/s",
            "4.5 × 10⁸ m/s",
            "B",
            "v = c / n = (3 × 10⁸) / 1.5 = 2 × 10⁸ m/s."
        ),
        (
            topic_map["light-reflection-refraction"], "Challenge",
            "A convex lens has a focal length of +25 cm (+0.25 m). What is the optical power of this lens?",
            "+2.5 D",
            "+4 D",
            "-4 D",
            "+0.25 D",
            "B",
            "Power P = 1 / f(in metres) = 1 / 0.25 = +4 Dioptres (D)."
        ),

        # 9. Kannada Sandhigalu (Kannada)
        (
            topic_map["kannada-sandhigalu"], "Standard",
            "'ಮಾತು + ಇಲ್ಲ = ಮಾತಿಲ್ಲ' - ಇದು ಯಾವ ಸಂಧಿಗೆ ಉದಾಹರಣೆಯಾಗಿದೆ?",
            "ಆಗಮ ಸಂಧಿ",
            "ಲೋಪ ಸಂಧಿ",
            "ಆದೇಶ ಸಂಧಿ",
            "ಗುಣ ಸಂಧಿ",
            "B",
            "'ಮಾತು' ಪದದ ಕೊನೆಯ 'ಉ' ಸ್ವರವು 'ಇಲ್ಲ' ಪದದ 'ಇ' ಸ್ವರದ ಮುಂದೆ ಬಂದು ಲೋಪವಾಗುವುದರಿಂದ ಇದು ಸ್ವರ ಲೋಪ ಸಂಧಿಯಾಗಿದೆ."
        ),
        (
            topic_map["kannada-sandhigalu"], "Standard",
            "'ಮನೆ + ಅನ್ನು = ಮನೆಯನ್ನು' - ಇಲ್ಲಿ ಯಾವ ಅಕ್ಷರ ಹೊಸದಾಗಿ ಆಗಮವಾಗಿದೆ?",
            "ವ್ ಕಾರ",
            "ಯ್ ಕಾರ",
            "ಗ್ ಕಾರ",
            "ರ್ ಕಾರ",
            "B",
            "ಅ, ಆ, ಎ, ಏ, ಐ ಸ್ವರಗಳ ಮುಂದೆ ಸ್ವರ ಬಂದಾಗ 'ಯ್' ಕಾರವು ಹೊಸದಾಗಿ ಆಗಮವಾಗುವುದರಿಂದ ಇದು ಯಕಾರಾಗಮ ಸಂಧಿಯಾಗಿದೆ."
        ),
        (
            topic_map["kannada-sandhigalu"], "Standard",
            "'ಮಳೆ + ಕಾಲ = ಮಳೆಗಾಲ' - ಇಲ್ಲಿ 'ಕ' ಕಾರಕ್ಕೆ 'ಗ' ಕಾರ ಬಂದಿರುವುದು ಯಾವ ಸಂಧಿಯಾಗಿದೆ?",
            "ಆದೇಶ ಸಂಧಿ",
            "ಲೋಪ ಸಂಧಿ",
            "ಆಗಮ ಸಂಧಿ",
            "ವೃದ್ಧಿ ಸಂಧಿ",
            "A",
            "ಉತ್ತರ ಪದದ ಆದಿಯಲ್ಲಿರುವ ಕ, ತ, ಪ ವ್ಯಂಜನಗಳಿಗೆ ಕ್ರಮವಾಗಿ ಗ, ದ, ಬ ಗಳು ಆದೇಶವಾಗಿ ಬರುವುದನ್ನು ಆದೇಶ ಸಂಧಿ ಎನ್ನುತ್ತಾರೆ."
        ),
        (
            topic_map["kannada-sandhigalu"], "Standard",
            "'ಗುರು + ಅನ್ನು = ಗುರುವನ್ನು' - ಇದು ಯಾವ ಆಗಮ ಸಂಧಿಗೆ ಉದಾಹರಣೆಯಾಗಿದೆ?",
            "ಯಕಾರಾಗಮ ಸಂಧಿ",
            "ವಕಾರಾಗಮ ಸಂಧಿ",
            "ಲೋಪ ಸಂಧಿ",
            "ಆದೇಶ ಸಂಧಿ",
            "B",
            "ಉ, ಊ, ಋ, ಒ, ಓ ಸ್ವರಗಳ ಮುಂದೆ ಸ್ವರ ಬಂದರೆ 'ವ್' ಕಾರ ಹೊಸದಾಗಿ ಆಗಮವಾಗುತ್ತದೆ (ವಕಾರಾಗಮ ಸಂಧಿ)."
        ),

        # 10. Kannada Samasagalu (Kannada)
        (
            topic_map["kannada-samasagalu"], "Standard",
            "'ಹೆಮ್ಮರ' (ಹಿರಿದಾದ + ಮರ) ಎಂಬುದು ಯಾವ ಸಮಾಸಕ್ಕೆ ಸೂಕ್ತ ಉದಾಹರಣೆಯಾಗಿದೆ?",
            "ತತ್ಪುರುಷ ಸಮಾಸ",
            "ಕರ್ಮಧಾರಯ ಸಮಾಸ",
            "ದ್ವಿಗು ಸಮಾಸ",
            "ಬಹುವ್ರೀಹಿ ಸಮಾಸ",
            "B",
            "ಪೂರ್ವಪದವು ವಿಶೇಷಣವಾಗಿಯೂ, ಉತ್ತರಪದವು ವಿಶೇಷ್ಯವಾಗಿಯೂ ಇರುವ ಸಮಾಸವನ್ನು ಕರ್ಮಧಾರಯ ಸಮಾಸ ಎನ್ನುತ್ತಾರೆ."
        ),
        (
            topic_map["kannada-samasagalu"], "Standard",
            "ಪೂರ್ವಪದವು ಸಂಖ್ಯಾವಾಚಕವಾಗಿದ್ದು, ಉತ್ತರಪದದೊಂದಿಗೆ ಸೇರಿ ಆಗುವ ಸಮಾಸ ಯಾವುದು? (ಉದಾ: ಮೂರುಲೋಕ)",
            "ದ್ವಿಗು ಸಮಾಸ",
            "ದ್ವಂದ್ವ ಸಮಾಸ",
            "ತತ್ಪುರುಷ ಸಮಾಸ",
            "ಅಂಶಿ ಸಮಾಸ",
            "A",
            "ಪೂರ್ವಪದವು ಸಂಖ್ಯಾವಾಚಕವಾಗಿದ್ದರೆ ಅದು ದ್ವಿಗು ಸಮಾಸವಾಗುತ್ತದೆ (ಮೂರು + ಲೋಕ = ಮೂರುಲೋಕ)."
        ),
        (
            topic_map["kannada-samasagalu"], "Standard",
            "'ಗಿಡಮರಬಳ್ಳಿಗಳು' (ಗಿಡವೂ + ಮರವೂ + ಬಳ್ಳಿಯೂ) ಎಂಬಲ್ಲಿ ಎಲ್ಲಾ ಪದಗಳ ಅರ್ಥವೂ ಪ್ರಧಾನವಾಗಿರುವ ಸಮಾಸ ಯಾವುದು?",
            "ದ್ವಂದ್ವ ಸಮಾಸ",
            "ಕರ್ಮಧಾರಯ ಸಮಾಸ",
            "ದ್ವಿಗು ಸಮಾಸ",
            "ತತ್ಪುರುಷ ಸಮಾಸ",
            "A",
            "ಸಮಾನ ಪ್ರಾಧಾನ್ಯತೆಯುಳ್ಳ ನಾಮಪದಗಳು ಕೂಡಿ ಆಗುವ ಸಮಾಸವನ್ನು ದ್ವಂದ್ವ ಸಮಾಸ ಎನ್ನುತ್ತಾರೆ."
        ),
        (
            topic_map["kannada-samasagalu"], "Standard",
            "'ಮರಗಾಲು' (ಮರದ + ಕಾಲು) - ಇದರಲ್ಲಿ ಉತ್ತರ ಪದದ ಅರ್ಥವೇ ಪ್ರಧಾನವಾಗಿರುವುದರಿಂದ ಇದು ಯಾವ ಸಮಾಸ?",
            "ತತ್ಪುರುಷ ಸಮಾಸ",
            "ಬಹುವ್ರೀಹಿ ಸಮಾಸ",
            "ಕ್ರಿಯಾ ಸಮಾಸ",
            "ಗಮಕ ಸಮಾಸ",
            "A",
            "ವಿಭಕ್ತಿ ಪ್ರತ್ಯಯದಿಂದ ಕೂಡಿದ ಪೂರ್ವಪದದೊಂದಿಗೆ ಉತ್ತರಪದವು ಸೇರಿ ಉತ್ತರಪದದ ಅರ್ಥವೇ ಪ್ರಧಾನವಾಗಿರುವುದು ತತ್ಪುರುಷ ಸಮಾಸ."
        ),

        # 11. Active and Passive Voice (English)
        (
            topic_map["active-passive-voice"], "Standard",
            "Change into Passive Voice: 'The teacher explained the lesson.'",
            "The lesson is explained by the teacher.",
            "The lesson was explained by the teacher.",
            "The lesson had explained by the teacher.",
            "The teacher was explained by the lesson.",
            "B",
            "Past active 'explained' changes to 'was/were + past participle' ('was explained') in passive voice."
        ),
        (
            topic_map["active-passive-voice"], "Standard",
            "Change into Passive Voice: 'They are building a new bridge.'",
            "A new bridge was built by them.",
            "A new bridge is being built by them.",
            "A new bridge has been built by them.",
            "A new bridge is built by them.",
            "B",
            "Present continuous 'are building' becomes 'is/are being + V3' ('is being built')."
        ),
        (
            topic_map["active-passive-voice"], "Standard",
            "Identify the voice: 'The letter was written by Shakespeare in 1605.'",
            "Active Voice",
            "Passive Voice",
            "Imperative Voice",
            "Subjunctive Voice",
            "B",
            "The subject 'The letter' receives the action, indicated by auxiliary 'was' + V3 'written' + agent 'by'."
        ),
        (
            topic_map["active-passive-voice"], "Standard",
            "Change into Active Voice: 'The mouse was caught by the cat.'",
            "The cat catches the mouse.",
            "The cat caught the mouse.",
            "The cat was catching the mouse.",
            "The cat had caught the mouse.",
            "B",
            "'was caught' in passive reverts to simple past active 'caught' with 'The cat' as active subject."
        ),

        # 12. Reported Speech (English)
        (
            topic_map["reported-speech"], "Standard",
            "Change into Indirect Speech: Ramesh said, 'I am studying for the exam.'",
            "Ramesh said that he is studying for the exam.",
            "Ramesh said that he was studying for the exam.",
            "Ramesh said that I was studying for the exam.",
            "Ramesh told that he has been studying for the exam.",
            "B",
            "Present continuous 'am studying' backshifts to past continuous 'was studying', and 'I' becomes 'he'."
        ),
        (
            topic_map["reported-speech"], "Standard",
            "Change into Indirect Speech: She said to me, 'Where do you live?'",
            "She asked me where I lived.",
            "She asked me where did I live.",
            "She told me where do I live.",
            "She asked me where you lived.",
            "A",
            "In reported wh-questions, the verb is 'asked', no 'that' is used, and the clause becomes assertive ('where I lived')."
        ),
        (
            topic_map["reported-speech"], "Standard",
            "How does the time word 'tomorrow' transform in indirect speech?",
            "Yesterday",
            "The following day / the next day",
            "That day",
            "Today",
            "B",
            "'Tomorrow' shifts to 'the next day' or 'the following day' in reported speech."
        ),
        (
            topic_map["reported-speech"], "Standard",
            "Change into Indirect Speech: The doctor said to the patient, 'Take these medicines regularly.'",
            "The doctor said to take medicines regularly.",
            "The doctor advised the patient to take those medicines regularly.",
            "The doctor told that take those medicines regularly.",
            "The doctor warned the patient that takes these medicines.",
            "B",
            "For medical advice, reporting verb becomes 'advised', 'these' becomes 'those', using infinitive 'to take'."
        ),

        # 13. Hindi Karak (Hindi)
        (
            topic_map["hindi-karak"], "Standard",
            "'राम ने रावण को बाण से मारा' - इस वाक्य में 'बाण से' में कौन-सा कारक है?",
            "अपादान कारक",
            "करण कारक",
            "कर्म कारक",
            "संप्रदान कारक",
            "B",
            "जिस साधन या माध्यम से क्रिया की जाती है, उसे करण कारक कहते हैं (विभक्ति: 'से' / 'के द्वारा')।"
        ),
        (
            topic_map["hindi-karak"], "Standard",
            "'पेड़ से पत्ता गिरा' - इस वाक्य में 'पेड़ से' में कौन-सा कारक है?",
            "करण कारक",
            "अपादान कारक",
            "कर्ता कारक",
            "अधिकरण कारक",
            "B",
            "जब किसी वस्तु का किसी स्थान से अलग होने (अलगाव) का भाव हो, तो अपादान कारक होता है (विभक्ति: 'से')।"
        ),
        (
            topic_map["hindi-karak"], "Foundation",
            "कर्ता कारक का विभक्ति चिह्न (प्रसर्ग) क्या है?",
            "को",
            "ने",
            "से",
            "में",
            "B",
            "कर्ता कारक का प्रसर्ग 'ने' होता है (जैसे: बालक ने पुस्तक पढ़ी)।"
        ),
        (
            topic_map["hindi-karak"], "Standard",
            "'मेज पर किताब रखी है' - यहाँ 'मेज पर' में कौन-सा कारक है?",
            "अधिकरण कारक",
            "संबंध कारक",
            "संप्रदान कारक",
            "कर्म कारक",
            "A",
            "क्रिया के आधार या स्थान का बोध कराने वाले कारक को अधिकरण कारक कहते हैं (विभक्ति: 'में', 'पर')।"
        ),

        # 14. Hindi Samas (Hindi)
        (
            topic_map["hindi-samas"], "Standard",
            "'चौराहा' (चार राहों का समूह) में कौन-सा समास है?",
            "तत्पुरुष समास",
            "द्विगु समास",
            "द्वंद्व समास",
            "कर्मधारय समास",
            "B",
            "जिस समास का पहला पद संख्यावाचक विशेषण हो और वह समूह का बोध कराए, उसे द्विगु समास कहते हैं।"
        ),
        (
            topic_map["hindi-samas"], "Standard",
            "'माता-पिता' (माता और पिता) में दोनों पद प्रधान होने के कारण कौन-सा समास है?",
            "द्वंद्व समास",
            "द्विगु समास",
            "बहुव्रीहि समास",
            "अव्ययीभाव समास",
            "A",
            "जिस समास में दोनों पद समान रूप से प्रधान हों और विग्रह करने पर 'और' आए, उसे द्वंद्व समास कहते हैं।"
        ),
        (
            topic_map["hindi-samas"], "Standard",
            "'नीलकंठ' (नीला है कंठ जिसका अर्थात् शिव) - इसमें कौन-सा समास है?",
            "कर्मधारय समास",
            "बहुव्रीहि समास",
            "तत्पुरुष समास",
            "अव्ययीभाव समास",
            "B",
            "जब दोनों पद मिलकर किसी तीसरे अन्य अर्थ (शिव) की ओर संकेत करते हैं, तो बहुव्रीहि समास होता है।"
        ),
        (
            topic_map["hindi-samas"], "Standard",
            "'राजपुत्र' (राजा का पुत्र) में कौन-सा समास है?",
            "तत्पुरुष समास",
            "अव्ययीभाव समास",
            "द्विगु समास",
            "कर्मधारय समास",
            "A",
            "जिस समास में उत्तर पद प्रधान हो तथा कारक चिह्न (का) का लोप हो, उसे तत्पुरुष समास कहते हैं।"
        ),

        # 15. Advent of Europeans (Social Science)
        (
            topic_map["advent-europeans-india"], "Standard",
            "Which historic event in 1453 forced European nations to discover a new maritime sea route to India?",
            "Battle of Plassey",
            "Capture of Constantinople by Ottoman Turks",
            "Discovery of America",
            "Battle of Buxar",
            "B",
            "In 1453, the Ottoman Turks captured Constantinople, closing land spice trade routes to Europe."
        ),
        (
            topic_map["advent-europeans-india"], "Standard",
            "In which year did the Portuguese navigator Vasco da Gama arrive at Kappad near Calicut in India?",
            "1492",
            "1498",
            "1600",
            "1757",
            "B",
            "Vasco da Gama sailed around Africa's Cape of Good Hope and reached Calicut in 1498."
        ),
        (
            topic_map["advent-europeans-india"], "Standard",
            "The decisive Battle of Plassey (1757) was fought between Robert Clive and which Nawab of Bengal?",
            "Mir Jafar",
            "Siraj-ud-Daulah",
            "Mir Qasim",
            "Alivardi Khan",
            "B",
            "Robert Clive defeated Nawab Siraj-ud-Daulah at Plassey on 23 June 1757, initiating British territorial rule."
        ),
        (
            topic_map["advent-europeans-india"], "Standard",
            "Which Portuguese Governor was considered the real founder of the Portuguese Empire in the East and captured Goa in 1510?",
            "Francisco de Almeida",
            "Alfonso de Albuquerque",
            "Vasco da Gama",
            "Dupleix",
            "B",
            "Alfonso de Albuquerque captured Goa from Bijapur in 1510, making it the capital of Portuguese trade."
        ),

        # 16. Indian Constitution (Social Science)
        (
            topic_map["indian-constitution"], "Standard",
            "Who served as the Chairman of the Drafting Committee of the Indian Constitution?",
            "Dr. Rajendra Prasad",
            "Dr. B. R. Ambedkar",
            "Jawaharlal Nehru",
            "Sardar Vallabhbhai Patel",
            "B",
            "Dr. B. R. Ambedkar was the Chairman of the Drafting Committee and is known as the Father of the Indian Constitution."
        ),
        (
            topic_map["indian-constitution"], "Standard",
            "How many Fundamental Rights are currently guaranteed to Indian citizens under Part III of the Constitution?",
            "7",
            "6",
            "8",
            "10",
            "B",
            "Currently, 6 Fundamental Rights are guaranteed to citizens under Articles 12 to 35."
        ),
        (
            topic_map["indian-constitution"], "Standard",
            "Why did Dr. B. R. Ambedkar describe Article 32 (Right to Constitutional Remedies) as the 'Heart and Soul' of the Constitution?",
            "It allows citizens to amend the Constitution directly",
            "It empowers citizens to move the Supreme Court via writs to protect Fundamental Rights",
            "It abolishes untouchability in India",
            "It grants free primary school education",
            "B",
            "Article 32 allows citizens to appeal directly to the Supreme Court through writs to enforce their Fundamental Rights."
        ),
        (
            topic_map["indian-constitution"], "Foundation",
            "On which date did the Constitution of India formally come into full legal effect across the nation?",
            "15 August 1947",
            "26 November 1949",
            "26 January 1950",
            "2 October 1950",
            "C",
            "The Constitution was enacted on 26 January 1950, commemorated annually as Republic Day."
        ),

        # 17. College C Pointers
        (
            topic_map["c-pointers-memory"], "Challenge",
            "If int x = 20; int *ptr = &x; what will printf(\"%d\", *ptr); output?",
            "Memory address of x",
            "20",
            "Garbage value",
            "Compiler syntax error",
            "B",
            "The dereference operator (*) accesses the value stored at the referenced memory address, which is 20."
        ),
        (
            topic_map["c-pointers-memory"], "Challenge",
            "Which standard C library function in <stdlib.h> is used to allocate raw heap memory bytes without initializing them to zero?",
            "calloc()",
            "malloc()",
            "realloc()",
            "free()",
            "B",
            "malloc(size) allocates uninitialized bytes in heap memory. calloc() clears them to zero."
        ),
        (
            topic_map["c-pointers-memory"], "Challenge",
            "What critical issue occurs if dynamically allocated memory using malloc() is never deallocated with free()?",
            "Segmentation fault immediately",
            "Memory leak",
            "Compile-time syntax error",
            "Stack overflow",
            "B",
            "Unreleased memory remains allocated in RAM, resulting in memory leaks that degrade performance."
        ),
        (
            topic_map["c-pointers-memory"], "Challenge",
            "In C pointer arithmetic, if int *p = 1000 (assuming 4-byte integers), what is the value of p + 1?",
            "1001",
            "1004",
            "1002",
            "1008",
            "B",
            "Pointer arithmetic scales by sizeof(type): 1000 + 1 × 4 = 1004."
        ),

        # 18. College Stacks and Queues
        (
            topic_map["data-structures-stack-queue"], "Challenge",
            "Which data structure operates strictly on the Last-In, First-Out (LIFO) operational principle?",
            "Queue",
            "Stack",
            "Linked List",
            "Binary Tree",
            "B",
            "A Stack operates on LIFO (Last-In, First-Out): the most recently pushed item is the first one popped."
        ),
        (
            topic_map["data-structures-stack-queue"], "Challenge",
            "What condition occurs when attempting to push a new element into a stack that is already completely full?",
            "Stack Underflow",
            "Stack Overflow",
            "Deadlock",
            "Memory Thrashing",
            "B",
            "Attempting to add to a full stack triggers a Stack Overflow error."
        ),
        (
            topic_map["data-structures-stack-queue"], "Challenge",
            "Which linear data structure operates on the First-In, First-Out (FIFO) principle?",
            "Stack",
            "Queue",
            "Binary Search Tree",
            "Priority Heap",
            "B",
            "A Queue inserts at the rear and removes from the front (FIFO)."
        ),
        (
            topic_map["data-structures-stack-queue"], "Challenge",
            "Which data structure is primarily used by compilers to convert an Infix expression into a Postfix expression?",
            "Queue",
            "Stack",
            "Graph",
            "Hash Table",
            "B",
            "Stacks are used in the Shunting-Yard algorithm to evaluate operator precedence and convert infix to postfix."
        )
    ]

    for q in quiz_records:
        cursor.execute("""
        INSERT INTO quizzes (topic_id, difficulty_mode, question, option_a, option_b, option_c, option_d, correct_option, explanation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, q)

    cursor.execute("SELECT id, question FROM quizzes")
    quiz_id_map = {row['question']: row['id'] for row in cursor.fetchall()}

    # 5. Seed Hint Ladders for key questions
    # E.g. Linear equations question
    q_lin = quiz_id_map.get("Solve the linear equation: 2(x + 3) = 14. What is the value of x?")
    if q_lin:
        cursor.executemany("""
        INSERT INTO quiz_hints (quiz_id, level, title, hint_text)
        VALUES (?, ?, ?, ?)
        """, [
            (q_lin, 1, "Recall Core Concept", "Look at the parentheses: 2(x + 3). The multiplier 2 applies to everything inside."),
            (q_lin, 2, "Suggest Next Step", "Either expand the bracket (2x + 6 = 14) or divide both sides by 2 first."),
            (q_lin, 3, "Partial Solution", "If 2x + 6 = 14, subtracting 6 gives 2x = 8."),
            (q_lin, 4, "Final Step", "Divide 8 by 2 to get x = 4.")
        ])

    # Newton balanced forces question
    q_newt = quiz_id_map.get("Which of the following is an example of a balanced force?")
    if q_newt:
        cursor.executemany("""
        INSERT INTO quiz_hints (quiz_id, level, title, hint_text)
        VALUES (?, ?, ?, ?)
        """, [
            (q_newt, 1, "Recall Core Concept", "Balanced forces mean Net Force = 0 N, so acceleration must be zero."),
            (q_newt, 2, "Check State of Motion", "Look for an object that is completely stationary or in uniform motion."),
            (q_newt, 3, "Analyze Forces", "A book at rest on a desk has gravity pulling down and the desk pushing up with equal force."),
            (q_newt, 4, "Final Answer", "The stationary book has Net Force = 0 N, so Option B is correct.")
        ])

    # 6. Seed Mistake Detective records
    if q_lin:
        cursor.executemany("""
        INSERT INTO mistake_detective (quiz_id, wrong_option, misconception_name, why_it_happens, how_to_fix, follow_up_practice)
        VALUES (?, ?, ?, ?, ?, ?)
        """, [
            (q_lin, "C", "Bracket Expansion Error", "You multiplied 2 by x but forgot to multiply 2 by 3 (writing 2x + 3 = 14).", "Always draw arrows: 2*(x) + 2*(3) = 2x + 6.", "Try solving: 3(x + 4) = 24."),
            (q_lin, "A", "Premature Division / Order of Operations", "You subtracted 3 before dividing or expanding.", "Use BODMAS: clear brackets first.", "Try solving: 4(y - 2) = 16.")
        ])

    # 7. Flashcards across all topics
    cursor.execute("DELETE FROM flashcards")
    fc_data = [
        (topic_map["linear-equations"], "What is the condition for coincident lines in linear equations?", "a₁/a₂ = b₁/b₂ = c₁/c₂ (Infinitely many solutions)", 1),
        (topic_map["quadratic-equations"], "State the quadratic formula for ax² + bx + c = 0.", "x = [-b ± √(b² - 4ac)] / (2a)", 1),
        (topic_map["quadratic-equations"], "What does D = b² - 4ac = 0 indicate about the roots?", "Two equal real roots (x = -b / 2a)", 2),
        (topic_map["arithmetic-progressions"], "What is the formula for the nth term of an A.P.?", "aₙ = a + (n - 1)d", 1),
        (topic_map["arithmetic-progressions"], "What is the sum of the first n positive integers?", "Sₙ = n(n + 1) / 2", 2),
        (topic_map["trigonometry"], "What is the fundamental Pythagorean identity in trigonometry?", "sin²θ + cos²θ = 1", 1),
        (topic_map["trigonometry"], "What is the value of tan 45°?", "tan 45° = 1", 1),
        (topic_map["newtons-laws-motion"], "Write the mathematical formula for Newton's 2nd Law.", "F = m × a (Force = mass × acceleration)", 1),
        (topic_map["newtons-laws-motion"], "Do Newton's 3rd law action-reaction forces cancel out?", "No, because they act on TWO DIFFERENT bodies.", 3),
        (topic_map["photosynthesis"], "Write the overall balanced chemical equation for photosynthesis.", "6CO₂ + 6H₂O + Sunlight + Chlorophyll → C₆H₁₂O₆ + 6O₂", 1),
        (topic_map["electricity-circuits"], "State Ohm's Law formula.", "V = I × R (Potential Difference = Current × Resistance)", 1),
        (topic_map["electricity-circuits"], "What is the formula for resistors connected in parallel?", "1/Rₚ = 1/R₁ + 1/R₂ + 1/R₃", 2),
        (topic_map["light-reflection-refraction"], "State the spherical mirror formula.", "1/f = 1/v + 1/u", 1),
        (topic_map["kannada-sandhigalu"], "ಲೋಪ ಸಂಧಿಯ ಪ್ರಮುಖ ಲಕ್ಷಣವೇನು?", "ಸ್ವರದ ಮುಂದೆ ಸ್ವರ ಬಂದು ಅರ್ಥ ಕೆಡದಿದ್ದಾಗ ಹಿಂದಿನ ಸ್ವರ ಬಿಟ್ಟುಹೋಗುವುದು (ಮಾತು + ಇಲ್ಲ = ಮಾತಿಲ್ಲ).", 1),
        (topic_map["kannada-sandhigalu"], "ಆದೇಶ ಸಂಧಿಯಲ್ಲಿ ಕ, ತ, ಪ ವ್ಯಂಜನಗಳಿಗೆ ಯಾವ ವ್ಯಂಜನಗಳು ಬರುತ್ತವೆ?", "ಕ್ರಮವಾಗಿ ಗ, ದ, ಬ ವ್ಯಂಜನಗಳು ಬರುತ್ತವೆ (ಮಳೆ + ಕಾಲ = ಮಳೆಗಾಲ).", 2),
        (topic_map["kannada-samasagalu"], "ದ್ವಿಗು ಸಮಾಸದ ಪೂರ್ವಪದ ಹೇಗಿರುತ್ತದೆ?", "ಪೂರ್ವಪದವು ಯಾವಾಗಲೂ ಸಂಖ್ಯಾವಾಚಕವಾಗಿರುತ್ತದೆ (ಮೂರು + ಲೋಕ = ಮೂರುಲೋಕ).", 1),
        (topic_map["active-passive-voice"], "What auxiliary verb is required for continuous passive sentences?", "The auxiliary 'being' (e.g. 'is being built', 'was being written').", 1),
        (topic_map["hindi-karak"], "अपादान कारक और करण कारक में क्या मुख्य अंतर है?", "करण साधन के लिए प्रयुक्त होता है (कलम से), जबकि अपादान अलग होने के लिए (पेड़ से)।", 1),
        (topic_map["indian-constitution"], "Who chaired the Drafting Committee of the Indian Constitution?", "Dr. B. R. Ambedkar (Father of the Indian Constitution).", 1),
        (topic_map["c-pointers-memory"], "What is the function of the '&' operator in C?", "Address-of operator: It returns the memory address of the variable.", 1)
    ]
    cursor.executemany("""
    INSERT INTO flashcards (topic_id, front_prompt, back_answer, interval_day)
    VALUES (?, ?, ?, ?)
    """, fc_data)

    conn.commit()
    conn.close()
    print("Curriculum and textbook seeding complete!")

if __name__ == "__main__":
    seed()
