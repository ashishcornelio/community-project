"""
LearnSphere AI - Personalized Learning Support System
Main Flask Application Server
Karnataka DSERT School Curriculum | Classes 8, 9 and 10
"""

import functools
import hashlib
import hmac
import os
import secrets
from flask import Flask, request, jsonify, render_template, send_from_directory, send_file, session, redirect, url_for
from database import get_db, init_db
from ai_engine import ai_engine
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.environ.get("LEARNSPHERE_SECRET_KEY") or secrets.token_hex(32)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

TEXTBOOKS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "text books")

# Ensure DB is created on startup
init_db()

PUBLIC_ENDPOINTS = {"login", "register", "static"}


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(stored_hash: str, password: str) -> bool:
    if not stored_hash:
        return False
    if stored_hash.startswith(("pbkdf2:", "scrypt:")):
        return check_password_hash(stored_hash, password)
    return hmac.compare_digest(stored_hash, hashlib.sha256(password.encode("utf-8")).hexdigest())


def current_user_id():
    return session["user_id"]


def get_session_user():
    if not session.get("user_id"):
        return None
    return {
        "id": session.get("user_id"),
        "username": session.get("username"),
        "full_name": session.get("full_name"),
        "role": session.get("role", "student"),
        "grade": session.get("grade", "Class 10"),
        "school": session.get("school", ""),
        "avatar": session.get("avatar", "👨‍🎓"),
        "streak_days": session.get("streak_days", 0),
    }


def start_user_session(user_row):
    session.clear()
    session["user_id"] = user_row["id"]
    session["username"] = user_row["username"]
    session["full_name"] = user_row["full_name"]
    session["role"] = user_row["role"]
    session["grade"] = user_row["grade"]
    session["school"] = user_row["school"]
    session["avatar"] = user_row["avatar"]
    session["streak_days"] = user_row["streak_days"]


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            if request.path.startswith("/api/"):
                return jsonify({"success": False, "error": "Authentication required"}), 401
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def roles_required(*roles):
    def decorate(view):
        @functools.wraps(view)
        def wrapped(*args, **kwargs):
            if session.get("role") not in roles:
                return jsonify({"success": False, "error": "Insufficient permissions"}), 403
            return view(*args, **kwargs)
        return wrapped
    return decorate


@app.before_request
def protect_all_routes():
    """Require a signed-in user for every route except login, register and static files."""
    if request.endpoint in PUBLIC_ENDPOINTS or request.endpoint is None:
        return None
    if not session.get("user_id"):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": "Authentication required"}), 401
        return redirect(url_for("login", next=request.path))
    return None


# ==========================================
# AUTHENTICATION
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():
    """Sign in an existing student, teacher or administrator."""
    if session.get("user_id"):
        return redirect(url_for("index"))

    next_url = request.args.get("next") or request.form.get("next") or "/"
    if not next_url.startswith("/") or next_url.startswith("//"):
        next_url = "/"

    if request.method == "POST":
        identifier = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (identifier, identifier),
        )
        user = cursor.fetchone()
        conn.close()

        if user and verify_password(user["password_hash"], password):
            if not user["password_hash"].startswith(("pbkdf2:", "scrypt:")):
                upgraded_hash = hash_password(password)
                conn = get_db()
                conn.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (upgraded_hash, user["id"]),
                )
                conn.commit()
                conn.close()
                user = dict(user)
                user["password_hash"] = upgraded_hash
            start_user_session(user)
            return redirect(next_url)

        return render_template(
            "login.html", mode="login", error="Invalid username or password.",
            username=identifier, next_url=next_url,
        )

    return render_template("login.html", mode="login", next_url=next_url)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Create a new student account."""
    if session.get("user_id"):
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        full_name = request.form.get("full_name", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        grade = request.form.get("grade", "Class 10")

        if grade not in ("Class 8", "Class 9", "Class 10"):
            grade = "Class 10"

        error = None
        if not username or not email or not full_name or not password:
            error = "All fields are required."
        elif len(password) < 6:
            error = "Password must be at least 6 characters long."
        elif password != confirm:
            error = "Passwords do not match."

        if not error:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE username = ? OR email = ?",
                (username, email),
            )
            if cursor.fetchone():
                error = "That username or email is already registered."
            else:
                cursor.execute("""
                INSERT INTO users (
                    username, email, password_hash, full_name, role, education_level,
                    grade, school, preferred_language, avatar, learning_points, streak_days
                ) VALUES (?, ?, ?, ?, 'student', 'School', ?, ?, 'en', '👨‍🎓', 0, 0)
                """, (
                    username, email, hash_password(password), full_name, grade,
                    "Shri Vishnumoorthi Hayavadanaswami High School, Innanje",
                ))
                conn.commit()
                cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
                user = cursor.fetchone()
                conn.close()
                start_user_session(user)
                return redirect("/")

            conn.close()

        return render_template(
            "login.html", mode="register", error=error,
            username=username, email=email, full_name=full_name, grade=grade,
        )

    return render_template("login.html", mode="register")


@app.route("/logout")
def logout():
    """Clear the session and return to the login screen."""
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    """Serves the main single-page application prototype."""
    return render_template("index.html", current_user=get_session_user())

# ==========================================
# REST API ENDPOINTS
# ==========================================

@app.route("/api/users", methods=["GET"])
def get_users():
    """Returns only the currently signed-in user's safe profile."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, full_name, role, grade, school, preferred_language, avatar "
        "FROM users WHERE id = ?",
        (current_user_id(),),
    )
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"success": True, "users": users})

@app.route("/api/subjects", methods=["GET"])
def get_subjects():
    """Returns all available subjects with topic count and color codes."""
    grade = request.args.get("grade", "").strip()
    grade_num = "".join(ch for ch in grade if ch.isdigit())
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT s.id, s.name, s.code, s.icon, s.color, s.description,
           COUNT(CASE WHEN ? = '' OR t.grade_level LIKE ? THEN t.id END) as topic_count
    FROM subjects s
    LEFT JOIN topics t ON s.id = t.subject_id
    WHERE s.category = 'School'
    GROUP BY s.id
    ORDER BY s.id
    """, (grade_num, f"%{grade_num}%"))
    subjects = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"success": True, "subjects": subjects})

@app.route("/api/topics", methods=["GET"])
def get_topics():
    """Returns school topics with optional subject and class filtering."""
    subject_id = request.args.get("subject_id")
    grade = request.args.get("grade")

    query = """
    SELECT t.id, t.subject_id, t.name, t.slug, t.grade_level, t.difficulty,
           t.summary, t.visual_type, t.textbook_ref, t.textbook_id,
           s.name as subject_name, s.color as subject_color, s.icon as subject_icon
    FROM topics t
    JOIN subjects s ON t.subject_id = s.id
    WHERE s.category = 'School'
    """
    params = []
    if subject_id:
        query += " AND t.subject_id = ?"
        params.append(subject_id)
    grade_num = "".join(ch for ch in str(grade or session.get("grade", "")) if ch.isdigit())
    if grade_num in ("8", "9", "10"):
        query += " AND t.grade_level LIKE ?"
        params.append(f"%{grade_num}%")
    query += " ORDER BY t.subject_id ASC, t.id ASC"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    topics = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"success": True, "topics": topics})

@app.route("/api/topics/<slug>", methods=["GET"])
def get_topic_detail(slug):
    """Returns complete topic details including multilingual content and formulas."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT t.*, s.name as subject_name, s.color as subject_color, s.icon as subject_icon
    FROM topics t
    JOIN subjects s ON t.subject_id = s.id
    WHERE t.slug = ? AND s.category = 'School'
    """, (slug,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return jsonify({"success": False, "error": "Topic not found"}), 404
    return jsonify({"success": True, "topic": dict(row)})

@app.route("/api/quizzes/<int:topic_id>", methods=["GET"])
def get_quiz_by_topic(topic_id):
    """Returns interactive practice quiz questions for a topic."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT q.id, q.topic_id, q.difficulty_mode, q.question, q.option_a, q.option_b, q.option_c, q.option_d, q.correct_option, q.explanation
    FROM quizzes q
    JOIN topics t ON q.topic_id = t.id
    JOIN subjects s ON t.subject_id = s.id
    WHERE q.topic_id = ? AND s.category = 'School'
    ORDER BY q.id
    """, (topic_id,))
    quizzes = [dict(row) for row in cursor.fetchall()]

    # Fetch topic details including textbook reference and subject
    cursor.execute("""
    SELECT t.id, t.name, t.slug, t.grade_level, t.difficulty, t.textbook_ref, t.textbook_id,
           s.id as subject_id, s.name as subject_name, s.color as subject_color, s.icon as subject_icon
    FROM topics t
    JOIN subjects s ON t.subject_id = s.id
    WHERE t.id = ? AND s.category = 'School'
    """, (topic_id,))
    topic_row = cursor.fetchone()
    topic_meta = dict(topic_row) if topic_row else {}
    conn.close()
    return jsonify({"success": True, "quizzes": quizzes, "topic": topic_meta})

@app.route("/api/quiz-attempts", methods=["POST"])
def submit_quiz_attempt():
    """
    Submits quiz score, updates learning gap detector,
    and auto-creates personalized revision tasks if score is low.
    """
    data = request.get_json() or {}
    user_id = current_user_id()
    topic_id = data.get("topic_id")
    score = data.get("score", 0)
    total_questions = data.get("total_questions", 1)

    if (
        not topic_id
        or not isinstance(score, int)
        or not isinstance(total_questions, int)
        or total_questions <= 0
        or score < 0
        or score > total_questions
    ):
        return jsonify({"success": False, "error": "A valid topic_id, score, and total_questions are required"}), 400

    percentage = round((score / total_questions) * 100.0, 1) if total_questions > 0 else 0.0

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT t.id FROM topics t
    JOIN subjects s ON t.subject_id = s.id
    WHERE t.id = ? AND s.category = 'School'
    """, (topic_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"success": False, "error": "School topic not found"}), 404

    # Record attempt
    cursor.execute("""
    INSERT INTO quiz_attempts (user_id, topic_id, score, total_questions, percentage)
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, topic_id, score, total_questions, percentage))

    # Evaluate Learning Gap
    if percentage < 50.0:
        gap_status = "critical_gap"
        action = f"Critical Gap ({percentage}%): Re-read the simple explanation, review the formula card, and try guided practice."
    elif percentage < 70.0:
        gap_status = "needs_revision"
        action = f"Needs Revision ({percentage}%): Review mistakes and attempt another practice quiz."
    else:
        gap_status = "mastered"
        action = f"Mastered ({percentage}%): Well done! Try a new school-syllabus topic."

    cursor.execute("""
    INSERT INTO learning_gaps (user_id, topic_id, mastery_score, status, recommended_action, last_assessed)
    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(user_id, topic_id) DO UPDATE SET
        mastery_score = excluded.mastery_score,
        status = excluded.status,
        recommended_action = excluded.recommended_action,
        last_assessed = CURRENT_TIMESTAMP
    """, (user_id, topic_id, percentage, gap_status, action))

    # If gap detected or needs revision, automatically suggest revision in study tasks
    if percentage < 70.0:
        cursor.execute("SELECT name, subject_id FROM topics WHERE id = ?", (topic_id,))
        topic_info = cursor.fetchone()
        if topic_info:
            task_title = f"AI Revision: {topic_info['name']}"
            cursor.execute("""
            SELECT id FROM study_tasks 
            WHERE user_id = ? AND title = ? AND is_completed = 0
            """, (user_id, task_title))
            if not cursor.fetchone():
                cursor.execute("""
                INSERT INTO study_tasks (user_id, title, subject_id, scheduled_day, time_slot, is_completed, task_type)
                VALUES (?, ?, ?, 'Tomorrow', '04:30 PM - 05:00 PM', 0, 'revision')
                """, (user_id, task_title, topic_info['subject_id']))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "score": score,
        "total_questions": total_questions,
        "percentage": percentage,
        "gap_status": gap_status,
        "recommendation": action
    })

@app.route("/api/doubt-solver", methods=["POST"])
def solve_doubt():
    """
    AI Doubt Solver API (Slide 25 Mockup 5).

    Answers are grounded in the official PDF textbooks: the response includes
    the exact book, chapter, page number and a link to open that PDF page.
    """
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    subject = data.get("subject", "General")
    language = data.get("language", "en")
    grade = data.get("grade")
    textbook_id = data.get("textbook_id")

    if not query:
        return jsonify({"success": False, "error": "Query cannot be empty"}), 400

    try:
        textbook_id = int(textbook_id) if textbook_id else None
    except (TypeError, ValueError):
        textbook_id = None

    result = ai_engine.solve_doubt(
        query, subject, language, grade=grade, textbook_id=textbook_id
    )
    return jsonify(result)


@app.route("/api/textbook-index/stats", methods=["GET"])
def get_textbook_index_stats():
    """Returns how many textbook PDFs/pages are searchable by the doubt solver."""
    from textbook_search import textbook_search_engine
    return jsonify({"success": True, "stats": textbook_search_engine.stats()})

@app.route("/api/generate-notes", methods=["POST"])
def generate_notes():
    """Generates Short Notes, Bullet Points, or Mind Map (Slide 25 Mockup 7)."""
    data = request.get_json() or {}
    topic_slug = data.get("topic_slug", "linear-equations")
    format_type = data.get("format_type", "short_notes")
    language = data.get("language", "en")

    conn = get_db()
    topic = conn.execute("""
    SELECT t.id FROM topics t
    JOIN subjects s ON t.subject_id = s.id
    WHERE t.slug = ? AND s.category = 'School'
    """, (topic_slug,)).fetchone()
    conn.close()
    if not topic:
        return jsonify({"success": False, "error": "School topic not found"}), 404

    result = ai_engine.generate_notes(topic_slug, format_type, language)
    return jsonify(result)

@app.route("/api/prerequisites/<int:topic_id>", methods=["GET"])
def get_topic_prerequisites(topic_id):
    """Returns prerequisite topic relationships and current mastery status (Section 10)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, topic_id, prerequisite_name, mastery_status, recommendation
    FROM topic_prerequisites
    WHERE topic_id = ? AND topic_id IN (
        SELECT t.id FROM topics t
        JOIN subjects s ON t.subject_id = s.id
        WHERE s.category = 'School'
    )
    """, (topic_id,))
    prereqs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"success": True, "prerequisites": prereqs})

@app.route("/api/hints/<int:quiz_id>", methods=["GET"])
def get_quiz_hints(quiz_id):
    """Returns 4 progressive hint levels for Hint Ladder (Section 8)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT h.level, h.title, h.hint_text
    FROM quiz_hints h
    JOIN quizzes q ON h.quiz_id = q.id
    JOIN topics t ON q.topic_id = t.id
    JOIN subjects s ON t.subject_id = s.id
    WHERE h.quiz_id = ? AND s.category = 'School'
    ORDER BY level ASC
    """, (quiz_id,))
    hints = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"success": True, "hints": hints})

@app.route("/api/mistake-detective/<int:quiz_id>/<wrong_option>", methods=["GET"])
def get_mistake_detective(quiz_id, wrong_option):
    """Returns diagnosed misconception and recovery guidance (Section 7)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT md.misconception_name, md.why_it_happens, md.how_to_fix, md.follow_up_practice
    FROM mistake_detective md
    JOIN quizzes q ON md.quiz_id = q.id
    JOIN topics t ON q.topic_id = t.id
    JOIN subjects s ON t.subject_id = s.id
    WHERE md.quiz_id = ? AND md.wrong_option = ? AND s.category = 'School'
    """, (quiz_id, wrong_option.upper()))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({"success": True, "has_misconception": True, "detective": dict(row)})
    return jsonify({
        "success": True,
        "has_misconception": False,
        "detective": {
            "misconception_name": "General Conceptual Slip",
            "why_it_happens": "This answer does not align with the standard formula or definition.",
            "how_to_fix": "Review the core definition and test with simple numbers.",
            "follow_up_practice": "Try checking the Hint Ladder or reviewing the worked example."
        }
    })

@app.route("/api/confidence-record", methods=["POST"])
def record_confidence():
    """Records student confidence rating and evaluates calibration (Section 9)."""
    data = request.get_json() or {}
    user_id = current_user_id()
    quiz_id = data.get("quiz_id")
    selected_option = data.get("selected_option", "")
    is_correct = bool(data.get("is_correct", False))
    confidence_level = data.get("confidence_level", "somewhat_sure")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT q.id FROM quizzes q
    JOIN topics t ON q.topic_id = t.id
    JOIN subjects s ON t.subject_id = s.id
    WHERE q.id = ? AND s.category = 'School'
    """, (quiz_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"success": False, "error": "School quiz not found"}), 404

    evaluation = ai_engine.classify_confidence(is_correct, confidence_level)
    cursor.execute("""
    INSERT INTO confidence_records (user_id, quiz_id, selected_option, is_correct, confidence_level, classification)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, quiz_id, selected_option, 1 if is_correct else 0, confidence_level, evaluation["classification"]))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "evaluation": evaluation})

@app.route("/api/flashcards/<int:topic_id>", methods=["GET"])
def get_flashcards(topic_id):
    """Returns smart revision & spaced repetition flashcards (Section 11)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT f.id, f.topic_id, f.front_prompt, f.back_answer, f.interval_day, f.repetition_count
    FROM flashcards f
    JOIN topics t ON f.topic_id = t.id
    JOIN subjects s ON t.subject_id = s.id
    WHERE f.topic_id = ? AND s.category = 'School'
    ORDER BY f.id ASC
    """, (topic_id,))
    cards = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"success": True, "flashcards": cards})

@app.route("/api/teach-back", methods=["POST"])
def evaluate_teach_back():
    """Evaluates student's self-explanation in Teach-Back Mode (Section 12)."""
    data = request.get_json() or {}
    topic_slug = data.get("topic_slug", "photosynthesis")
    explanation = data.get("explanation", "").strip()
    user_id = current_user_id()

    if not explanation:
        return jsonify({"success": False, "error": "Explanation cannot be empty"}), 400

    conn = get_db()
    topic = conn.execute("""
    SELECT t.id FROM topics t
    JOIN subjects s ON t.subject_id = s.id
    WHERE t.slug = ? AND s.category = 'School'
    """, (topic_slug,)).fetchone()
    if not topic:
        conn.close()
        return jsonify({"success": False, "error": "School topic not found"}), 404

    result = ai_engine.evaluate_teach_back(topic_slug, explanation)

    # Award learning points
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET learning_points = learning_points + 25 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    return jsonify(result)

@app.route("/api/admin-stats", methods=["GET"])
@roles_required("admin")
def get_admin_stats():
    """Administrator dashboard metrics (Section 17)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM subjects WHERE category = 'School'")
    total_subjects = cursor.fetchone()[0]
    cursor.execute("""
    SELECT COUNT(*) FROM topics t
    JOIN subjects s ON t.subject_id = s.id
    WHERE s.category = 'School'
    """)
    total_topics = cursor.fetchone()[0]
    cursor.execute("""
    SELECT COUNT(*) FROM quiz_attempts qa
    JOIN topics t ON qa.topic_id = t.id
    JOIN subjects s ON t.subject_id = s.id
    WHERE s.category = 'School'
    """)
    total_attempts = cursor.fetchone()[0]
    cursor.execute("""
    SELECT COUNT(*) FROM confidence_records cr
    JOIN quizzes q ON cr.quiz_id = q.id
    JOIN topics t ON q.topic_id = t.id
    JOIN subjects s ON t.subject_id = s.id
    WHERE s.category = 'School'
    """)
    total_confidence = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM textbooks WHERE class_num BETWEEN 8 AND 10")
    total_textbooks = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM exam_materials WHERE grade_level IN ('Class 8', 'Class 9', 'Class 10')")
    total_exam_materials = cursor.fetchone()[0]
    conn.close()
    return jsonify({
        "success": True,
        "total_users": total_users,
        "total_subjects": total_subjects,
        "total_topics": total_topics,
        "total_attempts": total_attempts,
        "total_confidence_evaluations": total_confidence,
        "total_textbooks": total_textbooks,
        "total_exam_materials": total_exam_materials,
        "database_health": "Healthy (SQLite Persistent WAL)",
        "offline_ready": True
    })

# ==========================================
# OFFICIAL KARNATAKA TEXTBOOKS LIBRARY (SECTION 5 & 21)
# ==========================================

@app.route("/api/textbooks", methods=["GET"])
def get_textbooks():
    """Returns official textbooks with optional class, subject, medium, and search filters."""
    class_num = request.args.get("class")
    subject = request.args.get("subject")
    medium = request.args.get("medium")
    search = request.args.get("search")

    query = "SELECT * FROM textbooks WHERE class_num BETWEEN 8 AND 10"
    params = []

    if class_num:
        try:
            class_num = int(class_num)
        except ValueError:
            return jsonify({"success": False, "error": "Class must be 8, 9, or 10"}), 400
        if class_num not in (8, 9, 10):
            return jsonify({"success": False, "error": "Class must be 8, 9, or 10"}), 400
        query += " AND class_num = ?"
        params.append(class_num)
    if subject and subject != "All":
        query += " AND subject = ?"
        params.append(subject)
    if medium and medium != "All":
        query += " AND medium = ?"
        params.append(medium)
    if search:
        query += " AND (title LIKE ? OR subject LIKE ?)"
        params.append(f"%{search}%")
        params.append(f"%{search}%")

    query += " ORDER BY class_num DESC, subject ASC, title ASC"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    books = [dict(row) for row in cursor.fetchall()]

    # Collect metadata for filters
    cursor.execute("SELECT DISTINCT class_num FROM textbooks WHERE class_num BETWEEN 8 AND 10 ORDER BY class_num ASC")
    classes = [r[0] for r in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT subject FROM textbooks WHERE class_num BETWEEN 8 AND 10 ORDER BY subject ASC")
    subjects = [r[0] for r in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT medium FROM textbooks WHERE class_num BETWEEN 8 AND 10 ORDER BY medium ASC")
    mediums = [r[0] for r in cursor.fetchall()]

    cursor.execute("SELECT COUNT(*), SUM(file_size_mb) FROM textbooks WHERE file_exists = 1 AND class_num BETWEEN 8 AND 10")
    stats_row = cursor.fetchone()
    total_count = stats_row[0] or 0
    total_size_mb = round(stats_row[1] or 0.0, 1)

    conn.close()

    # Enrich with download and read URLs
    for b in books:
        b["read_url"] = f"/api/textbooks/read/{b['id']}"
        b["download_url"] = f"/api/textbooks/download/{b['id']}"

    return jsonify({
        "success": True,
        "total": len(books),
        "total_available_books": total_count,
        "total_size_mb": total_size_mb,
        "classes": classes,
        "subjects": subjects,
        "mediums": mediums,
        "textbooks": books
    })

@app.route("/api/textbooks/<int:book_id>", methods=["GET"])
def get_textbook_detail(book_id):
    """Returns single textbook metadata."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM textbooks WHERE id = ? AND class_num BETWEEN 8 AND 10", (book_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return jsonify({"success": False, "error": "Textbook not found"}), 404

    book = dict(row)
    book["read_url"] = f"/api/textbooks/read/{book['id']}"
    book["download_url"] = f"/api/textbooks/download/{book['id']}"
    return jsonify({"success": True, "textbook": book})

@app.route("/api/textbooks/read/<int:book_id>", methods=["GET"])
def read_textbook(book_id):
    """Serves the PDF for inline browser viewing in iframe or tab."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT filename, title FROM textbooks WHERE id = ? AND class_num BETWEEN 8 AND 10", (book_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return "Textbook record not found in database", 404

    filename = row["filename"]
    full_path = os.path.join(TEXTBOOKS_DIR, filename)
    if not os.path.exists(full_path):
        return f"Textbook file not found on server disk: {filename}", 404

    return send_file(full_path, mimetype="application/pdf", as_attachment=False, download_name=os.path.basename(filename))

@app.route("/api/textbooks/download/<int:book_id>", methods=["GET"])
def download_textbook(book_id):
    """Serves the PDF as an attachment download for offline learning."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT filename, title FROM textbooks WHERE id = ? AND class_num BETWEEN 8 AND 10", (book_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return "Textbook record not found in database", 404

    filename = row["filename"]
    full_path = os.path.join(TEXTBOOKS_DIR, filename)
    if not os.path.exists(full_path):
        return f"Textbook file not found on server disk: {filename}", 404

    clean_title = row["title"].replace(" ", "_")[:60] + ".pdf"
    return send_file(full_path, mimetype="application/pdf", as_attachment=True, download_name=clean_title)

@app.route("/api/textbooks/related/<topic_slug>", methods=["GET"])
def get_related_textbooks(topic_slug):
    """Returns official textbook references for a topic."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT t.id, t.name, t.slug, t.textbook_ref, t.textbook_id, s.name as subject_name
    FROM topics t
    JOIN subjects s ON t.subject_id = s.id
    WHERE t.slug = ? AND s.category = 'School'
    """, (topic_slug,))
    topic_row = cursor.fetchone()

    prescribed_book = None
    if topic_row and topic_row["textbook_id"]:
        cursor.execute("SELECT * FROM textbooks WHERE id = ?", (topic_row["textbook_id"],))
        p_row = cursor.fetchone()
        if p_row:
            prescribed_book = dict(p_row)
            prescribed_book["read_url"] = f"/api/textbooks/read/{prescribed_book['id']}"
            prescribed_book["download_url"] = f"/api/textbooks/download/{prescribed_book['id']}"

    # Determine subject for additional class 10/9 textbooks
    sub_key = "Maths"
    if topic_row:
        s_name = topic_row["subject_name"].lower()
        if "math" in s_name: sub_key = "Maths"
        elif "sci" in s_name: sub_key = "Science"
        elif "kan" in s_name: sub_key = "Kannada"
        elif "eng" in s_name: sub_key = "English"
        elif "hin" in s_name: sub_key = "Hindi"
        elif "soc" in s_name: sub_key = "Social Science"

    class_num = request.args.get("class", session.get("grade", "Class 10"))
    class_num = "".join(ch for ch in str(class_num) if ch.isdigit())
    if class_num not in ("8", "9", "10"):
        class_num = "10"
    cursor.execute("""
    SELECT * FROM textbooks
    WHERE class_num = ? AND subject = ?
    ORDER BY medium ASC, title ASC
    """, (int(class_num), sub_key))
    books = [dict(row) for row in cursor.fetchall()]
    conn.close()

    for b in books:
        b["read_url"] = f"/api/textbooks/read/{b['id']}"
        b["download_url"] = f"/api/textbooks/download/{b['id']}"

    return jsonify({
        "success": True,
        "topic_slug": topic_slug,
        "prescribed_book": prescribed_book,
        "textbook_ref": topic_row["textbook_ref"] if topic_row else "Karnataka State Board DSERT",
        "related_books": books
    })

# ==========================================
# EXAMINATION PREPARATION CENTRE (SECTION 14)
# ==========================================

@app.route("/api/exam-materials", methods=["GET"])
def get_exam_materials():
    """Returns examination blueprints, formula sheets, mock papers, and definitions."""
    material_type = request.args.get("type")
    grade = request.args.get("grade") or session.get("grade", "Class 10")
    grade_num = "".join(ch for ch in str(grade) if ch.isdigit())
    if grade_num not in ("8", "9", "10"):
        grade_num = "10"
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM exam_materials WHERE grade_level = ?"
    params = [f"Class {grade_num}"]
    if material_type and material_type != "All":
        query += " AND material_type = ?"
        params.append(material_type)
    query += " ORDER BY id ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    materials = []
    import json
    for r in rows:
        m = dict(r)
        try:
            m["content"] = json.loads(m["content_json"])
        except Exception:
            m["content"] = {}
        del m["content_json"]
        materials.append(m)

    return jsonify({
        "success": True,
        "materials": materials,
        "exam_countdowns": [
            {"title": "Karnataka SSLC Board Examination 2026", "target_date": "2026-03-25", "tag": "Class 10 State Board"},
            {"title": "Class 9 Summative Assessment (SA-2)", "target_date": "2026-03-12", "tag": "Class 9 Annual"},
            {"title": "Class 8 Summative Assessment (SA-2)", "target_date": "2026-03-10", "tag": "Class 8 Annual"}
        ]
    })

# ==========================================
# BOOKMARKS & SAVED NOTES (SECTION 19)
# ==========================================

@app.route("/api/bookmarks", defaults={"user_id": None}, methods=["GET"])
@app.route("/api/bookmarks/<int:user_id>", methods=["GET"])
def get_bookmarks(user_id):
    """Returns saved notes, textbooks, and formulas for the user."""
    user_id = current_user_id()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookmarks WHERE user_id = ? ORDER BY id DESC", (user_id,))
    bookmarks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"success": True, "bookmarks": bookmarks})

@app.route("/api/bookmarks/toggle", methods=["POST"])
def toggle_bookmark():
    """Adds or removes a bookmark."""
    data = request.get_json() or {}
    user_id = current_user_id()
    item_type = data.get("item_type", "topic")
    item_id = str(data.get("item_id", ""))
    title = data.get("title", "Saved Item")

    if not item_id:
        return jsonify({"success": False, "error": "item_id is required"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM bookmarks WHERE user_id = ? AND item_type = ? AND item_id = ?", (user_id, item_type, item_id))
    row = cursor.fetchone()

    if row:
        cursor.execute("DELETE FROM bookmarks WHERE id = ?", (row["id"],))
        bookmarked = False
    else:
        cursor.execute("INSERT INTO bookmarks (user_id, item_type, item_id, title) VALUES (?, ?, ?, ?)",
                       (user_id, item_type, item_id, title))
        bookmarked = True

    conn.commit()
    conn.close()
    return jsonify({"success": True, "bookmarked": bookmarked})


@app.route("/api/progress", defaults={"user_id": None}, methods=["GET"])
@app.route("/api/progress/<int:user_id>", methods=["GET"])
def get_user_progress(user_id):

    """Returns analytics, overall completion %, topic breakdown, and detected gaps (Slide 25 Mockup 8)."""
    user_id = current_user_id()
    grade_num = "".join(ch for ch in str(request.args.get("grade") or session.get("grade", "Class 10")) if ch.isdigit())
    if grade_num not in ("8", "9", "10"):
        grade_num = "10"
    conn = get_db()
    gaps = ai_engine.detect_learning_gaps(user_id, conn, grade_num)

    # Calculate overall stats
    total_topics = len(gaps)
    completed = sum(1 for g in gaps if g["status"] == "mastered")
    in_progress = sum(1 for g in gaps if g["status"] in ["needs_revision", "in_progress"])
    critical = sum(1 for g in gaps if g["status"] == "critical_gap")
    not_started = sum(1 for g in gaps if g["status"] == "not_started")

    scores = [g["score"] for g in gaps if g["attempts"] > 0]
    overall_mastery = round(sum(scores) / len(scores), 1) if scores else 0.0

    # Subject-wise average
    subject_map = {}
    for g in gaps:
        sub = g["subject_name"]
        if sub not in subject_map:
            subject_map[sub] = {"scores": [], "color": g["subject_color"]}
        if g["attempts"] > 0:
            subject_map[sub]["scores"].append(g["score"])

    subject_breakdown = []
    for sub, val in subject_map.items():
        avg = round(sum(val["scores"]) / len(val["scores"]), 1) if val["scores"] else 0.0
        subject_breakdown.append({
            "subject": sub,
            "average": avg,
            "color": val["color"]
        })

    conn.close()
    return jsonify({
        "success": True,
        "overall_mastery": overall_mastery,
        "total_topics": total_topics,
        "completed": completed,
        "in_progress": in_progress,
        "critical_gaps": critical,
        "not_started": not_started,
        "subject_breakdown": subject_breakdown,
        "topics_gaps": gaps
    })

@app.route("/api/study-plan", defaults={"user_id": None}, methods=["GET"])
@app.route("/api/study-plan/<int:user_id>", methods=["GET"])
def get_study_plan(user_id):
    """Returns study plan schedule grouped by day (Slide 25 Mockup 9)."""
    user_id = current_user_id()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT st.id, st.user_id, st.title, st.scheduled_day, st.time_slot, st.is_completed, st.task_type,
           s.name as subject_name, s.color as subject_color, s.icon as subject_icon
    FROM study_tasks st
    JOIN subjects s ON st.subject_id = s.id
    WHERE st.user_id = ?
    ORDER BY st.is_completed ASC, st.id ASC
    """, (user_id,))
    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"success": True, "tasks": tasks})

@app.route("/api/study-tasks/toggle", methods=["POST"])
def toggle_study_task():
    """Toggles task completion status."""
    data = request.get_json() or {}
    task_id = data.get("task_id")
    if not task_id:
        return jsonify({"success": False, "error": "task_id is required"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE study_tasks SET is_completed = 1 - is_completed WHERE id = ? AND user_id = ?",
        (task_id, current_user_id()),
    )
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"success": False, "error": "Study task not found"}), 404
    conn.commit()

    cursor.execute("SELECT is_completed FROM study_tasks WHERE id = ? AND user_id = ?", (task_id, current_user_id()))
    new_status = cursor.fetchone()["is_completed"]
    conn.close()
    return jsonify({"success": True, "task_id": task_id, "is_completed": bool(new_status)})

@app.route("/api/teacher-analytics", methods=["GET"])
@roles_required("teacher", "admin")
def get_teacher_analytics():
    """Teacher view aggregating student performance, common gaps, and recommendations."""
    conn = get_db()
    cursor = conn.cursor()

    # Aggregate quiz performance per topic across all students
    cursor.execute("""
    SELECT 
        t.name as topic_name,
        s.name as subject_name,
        COUNT(qa.id) as attempts,
        ROUND(AVG(qa.percentage), 1) as class_average,
        MIN(qa.percentage) as min_score,
        MAX(qa.percentage) as max_score
    FROM topics t
    JOIN subjects s ON t.subject_id = s.id
    LEFT JOIN quiz_attempts qa ON t.id = qa.topic_id
    WHERE s.category = 'School'
    GROUP BY t.id
    ORDER BY class_average ASC
    """)
    topic_stats = [dict(row) for row in cursor.fetchall()]

    # Student list
    cursor.execute("""
    SELECT id, full_name, grade, preferred_language FROM users
    WHERE role = 'student' AND grade IN ('Class 8', 'Class 9', 'Class 10')
    """)
    students = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return jsonify({
        "success": True,
        "topic_stats": topic_stats,
        "students": students,
        "recommended_classroom_focus": "Newton's 2nd Law (F=ma) and Quadratic Equations need teacher demonstration and worked examples."
    })

import socket

def get_local_ips():
    """Detect all IPv4 network addresses of this machine."""
    ips = []
    # 1. Connect to an external address to find default outbound interface
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(("8.8.8.8", 80))
        primary = s.getsockname()[0]
        s.close()
        if primary and not primary.startswith("127."):
            ips.append(primary)
    except Exception:
        pass

    # 2. Add any other interface addresses
    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if not ip.startswith("127.") and ip not in ips:
                ips.append(ip)
    except Exception:
        pass

    return ips or ["127.0.0.1"]

@app.route("/api/network-info", methods=["GET"])
def get_network_info():
    """Returns local network IP addresses for hosting and LAN sharing."""
    ips = get_local_ips()
    return jsonify({
        "success": True,
        "primary_ip": ips[0] if ips else "127.0.0.1",
        "all_ips": ips,
        "port": 5000,
        "urls": [f"http://{ip}:5000" for ip in ips] + ["http://localhost:5000"]
    })

if __name__ == "__main__":
    init_db()
    detected_ips = get_local_ips()
    primary_ip = detected_ips[0] if detected_ips else "127.0.0.1"

    print("=" * 70)
    print(">> LearnSphere AI - Personalized Learning Support System")
    print("   Karnataka DSERT School Curriculum | Classes 8, 9 and 10")
    print("=" * 70)
    print(f">> Local Computer Access:       http://localhost:5000")
    print(f">> Mobile / LAN Network Access: http://{primary_ip}:5000")
    if len(detected_ips) > 1:
        for extra_ip in detected_ips[1:]:
            print(f">> Alternate Network URL:       http://{extra_ip}:5000")
    print("=" * 70)
    print(">> Host: 0.0.0.0 (Accepts connections from any device on your Wi-Fi)")
    print("=" * 70)
    
    app.run(host="0.0.0.0", port=5000, debug=True)
