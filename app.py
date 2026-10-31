"""
LearnSphere AI - Personalized Learning Support System
Main Flask Application Server
Karnataka DSERT School Curriculum | Classes 8, 9 and 10
"""

import functools
import hashlib
import hmac
import json
import os
import csv
import io
import re
import secrets
import uuid
from flask import Flask, request, jsonify, render_template, send_from_directory, send_file, session, redirect, url_for
from database import get_db, init_db
from ai_engine import ai_engine
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.environ.get("LEARNSPHERE_SECRET_KEY") or secrets.token_hex(32)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

TEXTBOOKS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "text books")
CLASSROOM_UPLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(CLASSROOM_UPLOADS_DIR, exist_ok=True)

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
            active_account=session.get("full_name") if session.get("user_id") else None,
        )

    return render_template(
        "login.html", mode="login", next_url=next_url,
        active_account=session.get("full_name") if session.get("user_id") else None,
    )


@app.errorhandler(413)
def request_entity_too_large(_error):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Uploads must be smaller than 25 MB."}), 413
    return "Upload is too large. Maximum file size is 25 MB.", 413


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
        role = request.form.get("role", "student").strip().lower()
        grade = request.form.get("grade", "Class 10")

        if role not in ("student", "teacher"):
            role = "student"
        if role == "student" and grade not in ("Class 8", "Class 9", "Class 10"):
            grade = "Class 10"
        elif role == "teacher":
            grade = "Faculty"

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
                ) VALUES (?, ?, ?, ?, ?, 'School', ?, ?, 'en', ?, 0, 0)
                """, (
                    username, email, hash_password(password), full_name, role, grade,
                    "Shri Vishnumoorthi Hayavadanaswami High School, Innanje",
                    "👩‍🏫" if role == "teacher" else "👨‍🎓",
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
            username=username, email=email, full_name=full_name, grade=grade, role=role,
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
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO doubt_conversations (user_id, question, answer, topic, subject, grade, related_actions)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        current_user_id(),
        query,
        result.get("response", ""),
        result.get("topic", ""),
        subject,
        grade or session.get("grade", ""),
        json.dumps(result.get("related_actions", [])),
    ))
    result["conversation_id"] = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify(result)

@app.route("/api/doubt-conversations", methods=["GET"])
def get_doubt_conversations():
    """Returns the signed-in user's saved doubt-solver conversation history."""
    conn = get_db()
    rows = conn.execute("""
    SELECT id, question, answer, topic, subject, grade, related_actions, created_at
    FROM doubt_conversations
    WHERE user_id = ?
    ORDER BY id ASC
    """, (current_user_id(),)).fetchall()
    conn.close()
    conversations = []
    for row in rows:
        conversation = dict(row)
        conversation["related_actions"] = json.loads(conversation["related_actions"] or "[]")
        conversations.append(conversation)
    return jsonify({"success": True, "conversations": conversations})


@app.route("/api/textbook-index/stats", methods=["GET"])
def get_textbook_index_stats():
    """Returns how many textbook PDFs/pages are searchable by the doubt solver."""
    from textbook_search import textbook_search_engine
    return jsonify({"success": True, "stats": textbook_search_engine.stats()})

@app.route("/api/generate-notes", methods=["POST"])
def generate_notes():
    """Generates notes using the selected topic's curated curriculum content."""
    data = request.get_json() or {}
    topic_slug = data.get("topic_slug", "linear-equations")
    format_type = data.get("format_type", "short_notes")
    language = data.get("language", "en")

    if not isinstance(topic_slug, str) or not topic_slug:
        return jsonify({"success": False, "error": "A valid topic_slug is required"}), 400
    if format_type not in ("short_notes", "important_points", "mind_map"):
        return jsonify({"success": False, "error": "Unsupported notes format"}), 400
    if language not in ("en", "kn", "hi"):
        return jsonify({"success": False, "error": "Unsupported language"}), 400

    conn = get_db()
    topic = conn.execute("""
    SELECT t.*, s.name AS subject_name FROM topics t
    JOIN subjects s ON t.subject_id = s.id
    WHERE t.slug = ? AND s.category = 'School'
    """, (topic_slug,)).fetchone()
    conn.close()
    if not topic:
        return jsonify({"success": False, "error": "School topic not found"}), 404

    result = ai_engine.generate_notes(dict(topic), format_type, language)
    return jsonify(result)


def parse_quiz_csv(upload):
    raw_content = upload.stream.read(5 * 1024 * 1024 + 1)
    if len(raw_content) > 5 * 1024 * 1024:
        return None, "Quiz CSV files must be smaller than 5 MB."
    try:
        csv_text = raw_content.decode("utf-8-sig")
    except UnicodeDecodeError:
        return None, "Quiz CSV files must use UTF-8 encoding."

    reader = csv.DictReader(io.StringIO(csv_text))
    if not reader.fieldnames:
        return None, "The CSV needs a header row with question, options, and answer columns."
    headers = {
        re.sub(r"[^a-z0-9]", "", name.lower()): name
        for name in reader.fieldnames if name
    }
    if "question" not in headers or "answer" not in headers:
        return None, "The CSV needs question and answer columns."
    has_options_column = "options" in headers
    has_choice_columns = any(f"option{letter}" in headers for letter in "abcdef")
    if not has_options_column and not has_choice_columns:
        return None, "Add an options column or option_a, option_b, and similar columns."

    questions = []
    for row_number, row in enumerate(reader, start=1):
        question = str(row.get(headers["question"]) or "").strip()
        answer = str(row.get(headers["answer"]) or "").strip()
        question_number = str(row.get(headers.get("qno", "")) or row_number).strip()
        if not question or not answer:
            return None, f"CSV row {row_number + 1} needs both a question and an answer."

        options = []
        if has_options_column and row.get(headers["options"]):
            raw_options = str(row[headers["options"]]).strip()
            if raw_options.startswith("["):
                try:
                    parsed_options = json.loads(raw_options)
                except json.JSONDecodeError:
                    return None, f"CSV row {row_number + 1} has invalid JSON in its options column."
                if not isinstance(parsed_options, list):
                    return None, f"CSV row {row_number + 1} options must be a list."
                options = [str(option).strip() for option in parsed_options]
            else:
                options = [option.strip() for option in re.split(r"\s*[|;]\s*", raw_options)]
        else:
            for letter in "abcdef":
                header = f"option{letter}"
                if header not in headers:
                    break
                option = str(row.get(headers[header]) or "").strip()
                if not option:
                    break
                options.append(option)

        if len(options) < 2 or len(options) > 6 or any(not option for option in options):
            return None, f"CSV row {row_number + 1} needs between 2 and 6 non-empty options."
        answer_match = re.fullmatch(r"(?:option\s*)?([a-f])[\s).:-]*", answer, re.IGNORECASE)
        if answer_match:
            answer_index = ord(answer_match.group(1).upper()) - ord("A")
        elif answer.isdigit():
            answer_index = int(answer) - 1
        else:
            normalized_answer = answer.casefold()
            answer_index = next(
                (index for index, option in enumerate(options) if option.casefold() == normalized_answer),
                -1,
            )
        if answer_index < 0 or answer_index >= len(options):
            return None, f"CSV row {row_number + 1} answer must be an option letter, 1-based number, or exact option text."
        questions.append({
            "question_number": question_number,
            "question": question,
            "options": options,
            "answer_index": answer_index,
        })
        if len(questions) > 200:
            return None, "A quiz can contain no more than 200 questions."

    if not questions:
        return None, "The CSV does not contain any quiz questions."
    return questions, None


@app.route("/api/classroom-resources", methods=["GET"])
def list_classroom_resources():
    """List resources visible to the signed-in class or teacher."""
    conn = get_db()
    cursor = conn.cursor()
    if session.get("role") == "student":
        cursor.execute("""
        SELECT r.id, r.resource_type, r.title, r.grade, r.content, r.original_filename,
               r.created_at, s.name AS subject_name, u.full_name AS teacher_name,
               EXISTS (
                   SELECT 1 FROM classroom_quiz_questions q WHERE q.resource_id = r.id
               ) AS has_questions
        FROM classroom_resources r
        JOIN subjects s ON s.id = r.subject_id
        JOIN users u ON u.id = r.teacher_id
        WHERE r.grade = ?
        ORDER BY r.created_at DESC, r.id DESC
        """, (session.get("grade"),))
    elif session.get("role") == "admin":
        cursor.execute("""
        SELECT r.id, r.resource_type, r.title, r.grade, r.content, r.original_filename,
               r.created_at, s.name AS subject_name, u.full_name AS teacher_name,
               EXISTS (
                   SELECT 1 FROM classroom_quiz_questions q WHERE q.resource_id = r.id
               ) AS has_questions
        FROM classroom_resources r
        JOIN subjects s ON s.id = r.subject_id
        JOIN users u ON u.id = r.teacher_id
        ORDER BY r.created_at DESC, r.id DESC
        """)
    else:
        cursor.execute("""
        SELECT r.id, r.resource_type, r.title, r.grade, r.content, r.original_filename,
               r.created_at, s.name AS subject_name, u.full_name AS teacher_name,
               EXISTS (
                   SELECT 1 FROM classroom_quiz_questions q WHERE q.resource_id = r.id
               ) AS has_questions
        FROM classroom_resources r
        JOIN subjects s ON s.id = r.subject_id
        JOIN users u ON u.id = r.teacher_id
        WHERE r.teacher_id = ?
        ORDER BY r.created_at DESC, r.id DESC
        """, (current_user_id(),))
    resources = []
    for row in cursor.fetchall():
        resource = dict(row)
        is_student = session.get("role") == "student"
        is_csv_quiz = (
            resource["resource_type"] == "quiz"
            and (os.path.splitext(resource["original_filename"] or "")[1].lower() == ".csv")
        )
        resource["download_url"] = (
            url_for("download_classroom_resource", resource_id=resource["id"])
            if resource["original_filename"] and (not is_student or not is_csv_quiz)
            else None
        )
        resources.append(resource)
    conn.close()
    return jsonify({"success": True, "resources": resources})


@app.route("/api/classroom-resources", methods=["POST"])
@roles_required("teacher", "admin")
def create_classroom_resource():
    """Publish a class-scoped teacher note or quiz file."""
    data = request.form if not request.is_json else request.get_json()
    resource_type = str(data.get("resource_type", "")).strip().lower()
    title = str(data.get("title", "")).strip()
    grade = str(data.get("grade", "")).strip()
    subject_id = str(data.get("subject_id", "")).strip()
    content = str(data.get("content", "")).strip()
    upload = request.files.get("file")
    if upload and not upload.filename:
        upload = None
    valid_grades = ("Class 8", "Class 9", "Class 10")

    if resource_type not in ("quiz", "note"):
        return jsonify({"success": False, "error": "Choose whether this is a quiz or a note."}), 400
    if grade not in valid_grades:
        return jsonify({"success": False, "error": "Choose a valid class."}), 400
    if not subject_id.isdigit() or not title or len(title) > 150:
        return jsonify({"success": False, "error": "A title and school subject are required."}), 400
    if not upload and not (resource_type == "note" and content):
        return jsonify({"success": False, "error": "Add note text or choose a supported file."}), 400
    if resource_type == "quiz" and not upload:
        return jsonify({"success": False, "error": "Choose a CSV or PDF quiz file."}), 400
    if resource_type == "note" and content and len(content) > 200000:
        return jsonify({"success": False, "error": "Typed notes must be 200,000 characters or fewer."}), 400

    conn = get_db()
    subject = conn.execute(
        "SELECT id FROM subjects WHERE id = ? AND category = 'School'",
        (int(subject_id),),
    ).fetchone()
    if not subject:
        conn.close()
        return jsonify({"success": False, "error": "Choose a valid school subject."}), 400

    parsed_questions = []
    original_filename = None
    stored_filename = None
    if upload and upload.filename:
        safe_name = secure_filename(upload.filename)
        extension = os.path.splitext(safe_name)[1].lower()
        allowed_extensions = (
            {".csv", ".pdf"} if resource_type == "quiz"
            else {".pdf", ".doc", ".docx", ".ppt", ".pptx"}
        )
        if not safe_name or extension not in allowed_extensions:
            conn.close()
            allowed = ", ".join(sorted(allowed_extensions))
            return jsonify({"success": False, "error": f"Supported file types: {allowed}."}), 400
        original_filename = safe_name
        stored_filename = f"{uuid.uuid4().hex}{extension}"
        if resource_type == "quiz" and extension == ".csv":
            parsed_questions, error = parse_quiz_csv(upload)
            if error:
                conn.close()
                return jsonify({"success": False, "error": error}), 400
            upload.stream.seek(0)
        upload.save(os.path.join(CLASSROOM_UPLOADS_DIR, stored_filename))
        if resource_type == "quiz":
            content = None

    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO classroom_resources
        (resource_type, title, subject_id, grade, teacher_id, content, original_filename, stored_filename)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        resource_type, title, int(subject_id), grade, current_user_id(),
        content or None, original_filename, stored_filename,
    ))
    resource_id = cursor.lastrowid
    if parsed_questions:
        cursor.executemany("""
        INSERT INTO classroom_quiz_questions
            (resource_id, question_number, question, options_json, answer_index)
        VALUES (?, ?, ?, ?, ?)
        """, [
            (
                resource_id, question["question_number"], question["question"],
                json.dumps(question["options"]), question["answer_index"],
            )
            for question in parsed_questions
        ])
    conn.commit()
    conn.close()
    return jsonify({"success": True, "resource_id": resource_id}), 201


def get_classroom_resource(cursor, resource_id):
    cursor.execute("""
    SELECT id, resource_type, title, grade, teacher_id, stored_filename, original_filename
    FROM classroom_resources WHERE id = ?
    """, (resource_id,))
    resource = cursor.fetchone()
    if not resource:
        return None, (jsonify({"success": False, "error": "Classroom resource not found."}), 404)
    if session.get("role") == "student" and resource["grade"] != session.get("grade"):
        return None, (jsonify({"success": False, "error": "This resource is not assigned to your class."}), 403)
    if session.get("role") == "teacher" and resource["teacher_id"] != current_user_id():
        return None, (jsonify({"success": False, "error": "You can only access your own classroom resources."}), 403)
    return resource, None


@app.route("/api/classroom-resources/<int:resource_id>/download", methods=["GET"])
def download_classroom_resource(resource_id):
    conn = get_db()
    resource, error_response = get_classroom_resource(conn.cursor(), resource_id)
    conn.close()
    if error_response:
        return error_response
    if resource["resource_type"] == "quiz" and session.get("role") == "student":
        if os.path.splitext(resource["original_filename"] or "")[1].lower() == ".csv":
            return jsonify({"success": False, "error": "Use the interactive quiz to keep its answer key private."}), 403
    if not resource["stored_filename"]:
        return jsonify({"success": False, "error": "This resource has no attached file."}), 404
    return send_from_directory(
        CLASSROOM_UPLOADS_DIR, resource["stored_filename"], as_attachment=True,
        download_name=resource["original_filename"],
    )


@app.route("/api/classroom-resources/<int:resource_id>/questions", methods=["GET"])
def get_classroom_quiz_questions(resource_id):
    conn = get_db()
    cursor = conn.cursor()
    resource, error_response = get_classroom_resource(cursor, resource_id)
    if error_response:
        conn.close()
        return error_response
    if resource["resource_type"] != "quiz":
        conn.close()
        return jsonify({"success": False, "error": "This resource is not a quiz."}), 400
    cursor.execute("""
    SELECT question_number, question, options_json
    FROM classroom_quiz_questions WHERE resource_id = ? ORDER BY id
    """, (resource_id,))
    questions = [
        {
            "question_number": row["question_number"],
            "question": row["question"],
            "options": json.loads(row["options_json"]),
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    if not questions:
        return jsonify({"success": False, "error": "This uploaded quiz is available as a PDF download."}), 400
    return jsonify({"success": True, "title": resource["title"], "questions": questions})


@app.route("/api/classroom-resources/<int:resource_id>/submit", methods=["POST"])
@roles_required("student")
def submit_classroom_quiz(resource_id):
    data = request.get_json() or {}
    answers = data.get("answers")
    if not isinstance(answers, list):
        return jsonify({"success": False, "error": "Submit one selected option for each question."}), 400
    conn = get_db()
    cursor = conn.cursor()
    resource, error_response = get_classroom_resource(cursor, resource_id)
    if error_response:
        conn.close()
        return error_response
    if resource["resource_type"] != "quiz":
        conn.close()
        return jsonify({"success": False, "error": "This resource is not a quiz."}), 400
    cursor.execute("""
    SELECT answer_index, options_json
    FROM classroom_quiz_questions WHERE resource_id = ? ORDER BY id
    """, (resource_id,))
    questions = cursor.fetchall()
    if not questions:
        conn.close()
        return jsonify({"success": False, "error": "This quiz does not contain interactive questions."}), 400
    if len(answers) != len(questions):
        conn.close()
        return jsonify({"success": False, "error": "Answer every question before submitting."}), 400
    score = 0
    for answer, question in zip(answers, questions):
        options = json.loads(question["options_json"])
        if type(answer) is not int or answer < 0 or answer >= len(options):
            conn.close()
            return jsonify({"success": False, "error": "An answer choice is invalid."}), 400
        if answer == question["answer_index"]:
            score += 1
    conn.close()
    return jsonify({"success": True, "score": score, "total_questions": len(questions)})


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
    conn.close()
    return jsonify({
        "success": True,
        "total_users": total_users,
        "total_subjects": total_subjects,
        "total_topics": total_topics,
        "total_attempts": total_attempts,
        "total_confidence_evaluations": total_confidence,
        "total_textbooks": total_textbooks,
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

    doubts = conn.execute("""
    SELECT id, question, answer, topic, subject, grade, created_at
    FROM doubt_conversations
    WHERE user_id = ?
    ORDER BY id DESC
    """, (user_id,)).fetchall()
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
        "topics_gaps": gaps,
        "doubts": [dict(row) for row in doubts]
    })

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

if __name__ == "__main__":
    init_db()

    print("=" * 70)
    print(">> LearnSphere AI - Personalized Learning Support System")
    print("   Karnataka DSERT School Curriculum | Classes 8, 9 and 10")
    print("=" * 70)
    print(f">> Local Computer Access:       http://localhost:5000")
    print("=" * 70)
    print(">> Host: 0.0.0.0 (Accepts connections from any device on your Wi-Fi)")
    print("=" * 70)
    
    app.run(host="0.0.0.0", port=5000, debug=True)
