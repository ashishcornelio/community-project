"""
LearnSphere AI - Intelligent Learning Engine & Pedagogical Science
Implements:
1. Teach-Back Mode Evaluation (Section 12)
2. Mistake Detective Misconception Matching (Section 7)
3. Hint Ladder Progressive Assistance (Section 8)
4. Confidence vs Knowledge Tracker (Section 9)
5. Adaptive Mode Recommendation (Foundation, Standard, Challenge) (Section 6)
6. Multilingual & Multi-Format Notes Synthesis (Section 5A & 13)
"""

import os
import re
import json

class AIEngine:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY")

    def evaluate_teach_back(self, topic_slug: str, student_explanation: str) -> dict:
        """
        Teach-Back Mode (Section 12):
        Evaluates student's self-explanation against key concepts and provides constructive feedback.
        """
        explanation_lower = student_explanation.lower()
        
        # Domain Rubrics
        rubrics = {
            "photosynthesis": {
                "title": "Photosynthesis in Green Plants",
                "keywords": ["sunlight", "chlorophyll", "water", "carbon dioxide", "glucose", "oxygen"],
                "model_answer": "Green plants capture sunlight using chlorophyll in their leaves. They absorb water from roots and take in carbon dioxide from the air. In the chloroplasts, these raw materials react to create glucose (food energy) and release oxygen into the air.",
                "tip": "Remember to highlight the chemical inputs (water & CO2) and outputs (glucose & oxygen)!"
            },
            "newtons-laws-motion": {
                "title": "Newton's Third Law of Motion",
                "keywords": ["action", "reaction", "equal", "opposite", "force"],
                "model_answer": "Newton's Third Law states that forces always come in pairs. When body A exerts an action force on body B, body B simultaneously exerts an equal and opposite reaction force on body A.",
                "tip": "Make sure to emphasize that action and reaction act on TWO DIFFERENT objects!"
            },
            "linear-equations": {
                "title": "Solving Linear Equations",
                "keywords": ["balance", "variable", "both sides", "inverse", "equal"],
                "model_answer": "A linear equation is like a balance scale where the variable has degree 1. To solve for the unknown, we isolate the variable by performing inverse arithmetic operations equally on both sides.",
                "tip": "Explain the golden rule: whatever you do to the left side must be done to the right side."
            }
        }

        rubric = rubrics.get(topic_slug, {
            "title": "Concept Explanation",
            "keywords": ["concept", "example", "reason"],
            "model_answer": "A clear conceptual explanation identifies the main principle, how it works, and an everyday application.",
            "tip": "Add a real-world example to make your explanation even clearer!"
        })

        # Match concepts
        found_keywords = [kw for kw in rubric["keywords"] if kw in explanation_lower]
        missing_keywords = [kw for kw in rubric["keywords"] if kw not in explanation_lower]

        score_pct = int((len(found_keywords) / len(rubric["keywords"])) * 100) if rubric["keywords"] else 70

        # Formulate encouraging pedagogical feedback
        if score_pct >= 80:
            assessment = "🌟 Outstanding Explanation!"
            feedback = f"You captured almost all the essential concepts ({', '.join(found_keywords)}). Your explanation shows deep conceptual understanding."
        elif score_pct >= 50:
            assessment = "👍 Good Attempt - Needs A Few Key Details"
            feedback = f"You correctly mentioned {', '.join(found_keywords)}. To make it complete, be sure to also explain how **{', '.join(missing_keywords[:2])}** fit into the process."
        else:
            assessment = "🌱 Foundation Building - Keep Going!"
            feedback = f"You started well, but missed some critical elements such as **{', '.join(missing_keywords[:3])}**. Read the model answer below and try explaining it once more!"

        return {
            "success": True,
            "topic": rubric["title"],
            "score_pct": score_pct,
            "assessment": assessment,
            "feedback": feedback,
            "found_concepts": found_keywords,
            "missing_concepts": missing_keywords,
            "model_answer": rubric["model_answer"],
            "pro_tip": rubric["tip"],
            "points_earned": 25
        }

    def classify_confidence(self, is_correct: bool, confidence_level: str) -> dict:
        """
        Confidence vs Knowledge Tracker (Section 9):
        Combines correctness and confidence to classify student learning state without permanent labels.
        """
        if is_correct:
            if confidence_level == "very_sure":
                return {
                    "classification": "mastery_confirmed",
                    "badge": "🏆 Mastery Confirmed",
                    "message": "High accuracy with strong confidence! You have demonstrated solid command over this concept.",
                    "recommendation": "Ready for Challenge Mode advanced problems and cross-topic applications."
                }
            else:
                return {
                    "classification": "retrieval_needed",
                    "badge": "🤔 Correct, But Low Confidence",
                    "message": "You got this right, but felt unsure. This suggests you have partial understanding that needs reinforcement.",
                    "recommendation": "Complete 2 retrieval practice questions or flashcards to build conviction."
                }
        else:
            if confidence_level == "very_sure":
                return {
                    "classification": "misconception_warning",
                    "badge": "⚠️ High-Confidence Misconception",
                    "message": "You felt very confident, but the answer was incorrect! This indicates a specific conceptual misconception rather than a careless slip.",
                    "recommendation": "Review the Mistake Detective explanation below to unlearn the misunderstanding."
                }
            else:
                return {
                    "classification": "foundation_needed",
                    "badge": "💡 Foundational Support Recommended",
                    "message": "You were unsure and encountered difficulty. Don't worry—learning takes iteration!",
                    "recommendation": "Switch to Foundation Mode to review prerequisite analogies and guided steps."
                }

    def recommend_learning_path(self, quiz_score_pct: float, gap_count: int, confidence_history: list) -> str:
        """
        Adaptive Learning Path Recommendation (Section 6):
        Recommends Foundation, Standard, or Challenge mode based on verifiable progress.
        """
        if quiz_score_pct >= 85 and gap_count == 0:
            return "Challenge"
        elif quiz_score_pct < 60 or gap_count >= 2:
            return "Foundation"
        else:
            return "Standard"

    def solve_doubt(self, query: str, subject: str = "General", language: str = "en",
                    grade: str = None, textbook_id: int = None) -> dict:
        """
        AI Doubt Solver (Section 20), grounded in the local textbook PDF library.

        Answers are retrieved verbatim from a specific PDF page. If no matching
        passage exists, the engine refuses to invent an answer instead of
        returning a generic/random response.
        """
        from textbook_search import textbook_search_engine

        class_num = None
        if grade:
            match = re.search(r"(8|9|10)", str(grade))
            if match:
                class_num = int(match.group(1))

        result = textbook_search_engine.search(
            query,
            class_num=class_num,
            subject=subject,
            book_id=textbook_id,
        )
        result["language"] = language
        return result

    def generate_notes(self, topic: dict, format_type: str = "short_notes", language: str = "en") -> dict:
        """Build notes from the selected topic's curated curriculum content."""
        localized_explanations = {
            "kn": topic.get("kannada_explanation"),
            "hi": topic.get("hindi_explanation"),
        }
        summary = localized_explanations.get(language) or topic.get("summary") or ""
        key_points = topic.get("pointwise_notes") or topic.get("simple_explanation") or ""
        exam_notes = topic.get("exam_ready_notes") or ""
        formula = topic.get("formula_box") or ""
        example = topic.get("real_life_example") or ""

        if format_type == "short_notes":
            sections = [f"### Key idea\n{summary}", f"### Key points\n{key_points}"]
            if formula:
                sections.append(f"### Formula / key terms\n{formula}")
            if example:
                sections.append(f"### Example\n{example}")
            if exam_notes:
                sections.append(f"### Exam focus\n{exam_notes}")
            content = "\n\n".join(sections)
        elif format_type == "important_points":
            sections = [f"### Important points\n{key_points}"]
            if formula:
                sections.append(f"### Formula / key terms\n{formula}")
            if exam_notes:
                sections.append(f"### Exam focus\n{exam_notes}")
            content = "\n\n".join(sections)
        else:
            branches = [
                {"name": "Core idea", "children": [{"name": summary[:48]}] if summary else []},
                {
                    "name": "Key points",
                    "children": [
                        {"name": re.sub(r"^[\s•*\-\d.]+", "", line)[:34]}
                        for line in key_points.splitlines()
                        if line.strip()
                    ][:3],
                },
            ]
            if formula:
                branches.append({"name": "Formula / terms", "children": [{"name": formula.splitlines()[0][:34]}]})
            if exam_notes:
                branches.append({"name": "Exam focus", "children": [{"name": exam_notes.splitlines()[0][:34]}]})
            return {
                "success": True,
                "format": format_type,
                "title": topic["name"],
                "subject": topic.get("subject_name", ""),
                "grade_level": topic.get("grade_level", ""),
                "mind_map_data": {"name": topic["name"], "children": branches},
            }

        return {
            "success": True,
            "format": format_type,
            "title": topic["name"],
            "subject": topic.get("subject_name", ""),
            "grade_level": topic.get("grade_level", ""),
            "content": content,
        }

    def detect_learning_gaps(self, user_id: int, conn, grade_num: str) -> list:
        """Return mastery and revision status for school topics in the selected class."""
        cursor = conn.cursor()
        cursor.execute("""
        SELECT t.id AS topic_id, t.name AS topic_name, t.grade_level,
               s.name AS subject_name, s.color AS subject_color,
               COUNT(qa.id) AS attempts,
               AVG(qa.percentage) AS average_score,
               lg.mastery_score, lg.status, lg.recommended_action
        FROM topics t
        JOIN subjects s ON s.id = t.subject_id AND s.category = 'School'
        LEFT JOIN quiz_attempts qa ON qa.topic_id = t.id AND qa.user_id = ?
        LEFT JOIN learning_gaps lg ON lg.topic_id = t.id AND lg.user_id = ?
        WHERE t.grade_level LIKE ?
        GROUP BY t.id, s.id, lg.mastery_score, lg.status, lg.recommended_action
        ORDER BY s.id, t.id
        """, (user_id, user_id, f"%{grade_num}%"))

        topics = []
        for row in cursor.fetchall():
            attempts = row["attempts"]
            score = row["mastery_score"]
            if score is None:
                score = row["average_score"] or 0
            score = round(float(score), 1)

            status = row["status"]
            if status not in ("critical_gap", "needs_revision", "in_progress", "mastered"):
                if attempts == 0:
                    status = "not_started"
                elif score < 50:
                    status = "critical_gap"
                elif score < 70:
                    status = "needs_revision"
                else:
                    status = "mastered"

            recommendation = row["recommended_action"]
            if not recommendation:
                recommendation = {
                    "not_started": "Start with the simple explanation, then try a short practice quiz.",
                    "critical_gap": "Review the foundation notes and work through a guided example.",
                    "needs_revision": "Review recent mistakes and practise this topic again.",
                    "in_progress": "Continue practising this topic to strengthen recall.",
                    "mastered": "Topic mastered. Move on to another syllabus topic.",
                }[status]

            topics.append({
                "topic_id": row["topic_id"],
                "topic_name": row["topic_name"],
                "grade_level": row["grade_level"],
                "subject_name": row["subject_name"],
                "subject_color": row["subject_color"],
                "attempts": attempts,
                "score": score,
                "status": status,
                "recommendation": recommendation,
            })
        return topics

ai_engine = AIEngine()
