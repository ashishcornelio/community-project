"""
LearnSphere AI - Personalized Learning Support System
Main Flask Application Server
SMVITM Bantakal | Department of AI & Data Science | Team 11
"""

import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from database import get_db, init_db
from ai_engine import ai_engine

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = "learnsphere-smvitm-idt-team11-2026"

# Ensure DB is created on startup
init_db()

@app.route("/")
def index():
    """Serves the main single-page application prototype."""
    return render_template("index.html")

# ==========================================
# REST API ENDPOINTS
# ==========================================

@app.route("/api/users", methods=["GET"])
def get_users():
    """Returns available users for demo persona switching."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, full_name, role, grade, school, preferred_language, avatar FROM users")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"success": True, "users": users})

@app.route("/api/subjects", methods=["GET"])
def get_subjects():
    """Returns all available subjects with topic count and color codes."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT s.id, s.name, s.code, s.icon, s.color, s.description,
           COUNT(t.id) as topic_count
    FROM subjects s
    LEFT JOIN topics t ON s.id = t.subject_id
    GROUP BY s.id
    ORDER BY s.id
    """)
    subjects = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"success": True, "subjects": subjects})

@app.route("/api/topics", methods=["GET"])
def get_topics():
    """Returns topics with optional subject filtering."""
    subject_id = request.args.get("subject_id")
    conn = get_db()
    cursor = conn.cursor()
    if subject_id:
        cursor.execute("""
        SELECT t.id, t.subject_id, t.name, t.slug, t.grade_level, t.difficulty,
               t.summary, t.visual_type, s.name as subject_name, s.color as subject_color
        FROM topics t
        JOIN subjects s ON t.subject_id = s.id
        WHERE t.subject_id = ?
        ORDER BY t.id
        """, (subject_id,))
    else:
        cursor.execute("""
        SELECT t.id, t.subject_id, t.name, t.slug, t.grade_level, t.difficulty,
               t.summary, t.visual_type, s.name as subject_name, s.color as subject_color
        FROM topics t
        JOIN subjects s ON t.subject_id = s.id
        ORDER BY t.id
        """)
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
    WHERE t.slug = ?
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
    SELECT id, topic_id, question, option_a, option_b, option_c, option_d, correct_option, explanation
    FROM quizzes
    WHERE topic_id = ?
    ORDER BY id
    """, (topic_id,))
    quizzes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"success": True, "quizzes": quizzes})

@app.route("/api/quiz-attempts", methods=["POST"])
def submit_quiz_attempt():
    """
    Submits quiz score, updates learning gap detector,
    and auto-creates personalized revision tasks if score is low.
    """
    data = request.get_json() or {}
    user_id = data.get("user_id", 1)
    topic_id = data.get("topic_id")
    score = data.get("score", 0)
    total_questions = data.get("total_questions", 1)

    if not topic_id:
        return jsonify({"success": False, "error": "topic_id is required"}), 400

    percentage = round((score / total_questions) * 100.0, 1) if total_questions > 0 else 0.0

    conn = get_db()
    cursor = conn.cursor()

    # Record attempt
    cursor.execute("""
    INSERT INTO quiz_attempts (user_id, topic_id, score, total_questions, percentage)
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, topic_id, score, total_questions, percentage))

    # Evaluate Learning Gap
    if percentage < 50.0:
        gap_status = "gap_detected"
        action = f"Critical Gap ({percentage}%): Re-read simple explanation, review formula card, and take 1-on-1 practice."
    elif percentage < 70.0:
        gap_status = "in_progress"
        action = f"Needs Revision ({percentage}%): Review mistakes and attempt another quiz challenge."
    else:
        gap_status = "mastered"
        action = f"Mastered ({percentage}%): Well done! Ready for advanced problem sets."

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
    """AI Doubt Solver API (Slide 25 Mockup 5)."""
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    subject = data.get("subject", "General")
    language = data.get("language", "en")

    if not query:
        return jsonify({"success": False, "error": "Query cannot be empty"}), 400

    result = ai_engine.solve_doubt(query, subject, language)
    return jsonify(result)

@app.route("/api/generate-notes", methods=["POST"])
def generate_notes():
    """Generates Short Notes, Bullet Points, or Mind Map (Slide 25 Mockup 7)."""
    data = request.get_json() or {}
    topic_slug = data.get("topic_slug", "linear-equations")
    format_type = data.get("format_type", "short_notes")
    language = data.get("language", "en")

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
    WHERE topic_id = ?
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
    SELECT level, title, hint_text
    FROM quiz_hints
    WHERE quiz_id = ?
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
    SELECT misconception_name, why_it_happens, how_to_fix, follow_up_practice
    FROM mistake_detective
    WHERE quiz_id = ? AND wrong_option = ?
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
    user_id = data.get("user_id", 1)
    quiz_id = data.get("quiz_id")
    selected_option = data.get("selected_option", "")
    is_correct = bool(data.get("is_correct", False))
    confidence_level = data.get("confidence_level", "somewhat_sure")

    evaluation = ai_engine.classify_confidence(is_correct, confidence_level)

    conn = get_db()
    cursor = conn.cursor()
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
    SELECT id, topic_id, front_prompt, back_answer, interval_day, repetition_count
    FROM flashcards
    WHERE topic_id = ?
    ORDER BY id ASC
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
    user_id = data.get("user_id", 1)

    if not explanation:
        return jsonify({"success": False, "error": "Explanation cannot be empty"}), 400

    result = ai_engine.evaluate_teach_back(topic_slug, explanation)

    # Award learning points
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET learning_points = learning_points + 25 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    return jsonify(result)

@app.route("/api/admin-stats", methods=["GET"])
def get_admin_stats():
    """Administrator dashboard metrics (Section 17)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM subjects")
    total_subjects = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM topics")
    total_topics = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM quiz_attempts")
    total_attempts = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM confidence_records")
    total_confidence = cursor.fetchone()[0]
    conn.close()
    return jsonify({
        "success": True,
        "total_users": total_users,
        "total_subjects": total_subjects,
        "total_topics": total_topics,
        "total_attempts": total_attempts,
        "total_confidence_evaluations": total_confidence,
        "database_health": "Healthy (SQLite Persistent WAL)",
        "offline_ready": True
    })

@app.route("/api/progress/<int:user_id>", methods=["GET"])
def get_user_progress(user_id):

    """Returns analytics, overall completion %, topic breakdown, and detected gaps (Slide 25 Mockup 8)."""
    conn = get_db()
    gaps = ai_engine.detect_learning_gaps(user_id, conn)

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

@app.route("/api/study-plan/<int:user_id>", methods=["GET"])
def get_study_plan(user_id):
    """Returns study plan schedule grouped by day (Slide 25 Mockup 9)."""
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
    cursor.execute("UPDATE study_tasks SET is_completed = 1 - is_completed WHERE id = ?", (task_id,))
    conn.commit()

    cursor.execute("SELECT is_completed FROM study_tasks WHERE id = ?", (task_id,))
    new_status = cursor.fetchone()["is_completed"]
    conn.close()
    return jsonify({"success": True, "task_id": task_id, "is_completed": bool(new_status)})

@app.route("/api/career-guidance", methods=["GET"])
def get_career_guidance():
    """Returns career pathways matching student interests (Slide 25 Mockup 10)."""
    category = request.args.get("category")
    conn = get_db()
    cursor = conn.cursor()
    if category and category != "All":
        cursor.execute("SELECT * FROM career_paths WHERE category = ?", (category,))
    else:
        cursor.execute("SELECT * FROM career_paths")
    careers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"success": True, "careers": careers})

@app.route("/api/teacher-analytics", methods=["GET"])
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
    GROUP BY t.id
    ORDER BY class_average ASC
    """)
    topic_stats = [dict(row) for row in cursor.fetchall()]

    # Student list
    cursor.execute("SELECT id, full_name, grade, preferred_language FROM users WHERE role = 'student'")
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
    print("   SMVITM Bantakal | Department of AI & Data Science | Team 11")
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


