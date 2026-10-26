/**
 * LearnSphere AI - Advanced Practice Quiz Engine
 * Integrates:
 * 1. Hint Ladder (4 Progressive assistance levels - Section 8)
 * 2. Mistake Detective (Misconception diagnosis - Section 7)
 * 3. Confidence vs. Knowledge Tracker (Section 9)
 * 4. Adaptive Learning Paths (Foundation, Standard, Challenge - Section 6)
 */

class QuizEngine {
  constructor() {
    this.currentTopicId = 3; // Newton's Laws default
    this.questions = [];
    this.currentIndex = 0;
    this.userAnswers = {};
    this.activeHints = {};
    this.confidenceRatings = {};
    this.timerSeconds = 45;
    this.timerInterval = null;
    this.currentMode = "Standard";
  }

  async init() {
    await this.loadQuizTopics();
    this.attachEventListeners();
    await this.startQuizForTopic(this.currentTopicId);
  }

  attachEventListeners() {
    const topicSelect = document.getElementById("quiz-topic-select");
    if (topicSelect) {
      topicSelect.addEventListener("change", (e) => {
        this.currentTopicId = parseInt(e.target.value);
        this.startQuizForTopic(this.currentTopicId);
      });
    }
  }

  async loadQuizTopics() {
    const topicSelect = document.getElementById("quiz-topic-select");
    if (!topicSelect) return;

    try {
      const res = await fetch("/api/topics");
      const data = await res.json();
      if (data.success) {
        topicSelect.innerHTML = data.topics.map(t => `
          <option value="${t.id}" ${t.id === this.currentTopicId ? "selected" : ""}>
            [${t.subject_name}] ${t.name}
          </option>
        `).join("");
      }
    } catch (err) {
      console.error("Error loading quiz topics:", err);
    }
  }

  async startQuizForTopic(topicId) {
    this.currentTopicId = topicId;
    this.currentIndex = 0;
    this.userAnswers = {};
    this.activeHints = {};
    this.confidenceRatings = {};

    const quizArea = document.getElementById("quiz-content-area");
    if (quizArea) {
      quizArea.innerHTML = `<div style="text-align:center; padding:3rem;"><div class="chip">Loading adaptive questions... ⏳</div></div>`;
    }

    try {
      const res = await fetch(`/api/quizzes/${topicId}`);
      const data = await res.json();
      if (data.success && data.quizzes.length > 0) {
        this.questions = data.quizzes;
        this.renderCurrentQuestion();
      } else {
        if (quizArea) {
          quizArea.innerHTML = `
            <div style="text-align:center; padding:3rem;">
              <p style="color:var(--text-secondary); margin-bottom:1rem;">No questions configured for this topic yet.</p>
              <button class="btn-primary" onclick="window.quizEngine.loadQuizTopics()">Try Another Topic</button>
            </div>
          `;
        }
      }
    } catch (err) {
      console.error("Failed to load questions:", err);
    }
  }

  renderCurrentQuestion() {
    this.resetTimer();
    if (!this.questions || this.questions.length === 0) return;

    const q = this.questions[this.currentIndex];
    const total = this.questions.length;
    const selectedAns = this.userAnswers[this.currentIndex];
    const quizArea = document.getElementById("quiz-content-area");
    if (!quizArea) return;

    const options = [
      { key: "A", text: q.option_a },
      { key: "B", text: q.option_b },
      { key: "C", text: q.option_c },
      { key: "D", text: q.option_d }
    ];

    const isAnswered = selectedAns !== undefined;
    const isCorrect = isAnswered && selectedAns === q.correct_option;

    // Render Options
    const optionsHtml = options.map(opt => {
      let optClass = "quiz-option-btn";
      if (isAnswered) {
        if (opt.key === q.correct_option) {
          optClass += " correct";
        } else if (opt.key === selectedAns && selectedAns !== q.correct_option) {
          optClass += " wrong";
        }
      } else if (opt.key === selectedAns) {
        optClass += " selected";
      }

      return `
        <button class="${optClass}" ${isAnswered ? "disabled" : ""} onclick="window.quizEngine.selectOption('${opt.key}')">
          <span class="quiz-opt-letter">${opt.key}</span>
          <span class="quiz-opt-text">${opt.text}</span>
        </button>
      `;
    }).join("");

    // Hints list
    const currentHints = this.activeHints[this.currentIndex] || [];
    let hintsHtml = "";
    if (currentHints.length > 0) {
      hintsHtml = `
        <div class="hint-ladder-container">
          <div style="font-size:0.85rem; font-weight:700; color:#fbbf24; display:flex; align-items:center; gap:0.4rem;">
            <span>🪜 Hint Ladder Assistance (Level ${currentHints.length} of 4)</span>
          </div>
          ${currentHints.map(h => `
            <div class="hint-step-item">
              <strong style="color:#a5b4fc; font-size:0.85rem;">${h.title}:</strong>
              <p style="color:var(--text-secondary); font-size:0.88rem; margin-top:0.2rem;">${h.hint_text}</p>
            </div>
          `).join("")}
        </div>
      `;
    }

    // Feedback & Mistake Detective
    let feedbackHtml = "";
    if (isAnswered) {
      feedbackHtml = `
        <div class="quiz-feedback-box ${isCorrect ? "correct" : "wrong"}" style="display:block;">
          <div style="font-weight:700; font-size:1.05rem; margin-bottom:0.35rem;">
            ${isCorrect ? "🎉 Correct Answer!" : "❌ Incorrect Answer"}
          </div>
          <div style="font-size:0.92rem; color:var(--text-secondary); line-height:1.5;">
            <strong>Explanation:</strong> ${q.explanation}
          </div>
        </div>
        <div id="mistake-detective-placeholder"></div>
        <div id="confidence-tracker-placeholder"></div>
      `;
    }

    const nextLabel = (this.currentIndex === total - 1) ? "Finish & Submit 🎯" : "Next Question →";
    const prevDisabled = (this.currentIndex === 0) ? "disabled" : "";

    quizArea.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
        <div style="font-size:0.85rem; color:var(--text-muted); font-weight:700;" id="quiz-question-counter">
          Question ${this.currentIndex + 1} of ${total} • <span class="badge-tag">${q.difficulty_mode || "Standard"} Mode</span>
        </div>
        ${!isAnswered ? `
          <button class="chip" onclick="window.quizEngine.requestNextHint(${q.id})" style="border-color:#fbbf24; color:#fbbf24; font-size:0.78rem;">
            💡 Request Hint Ladder (${currentHints.length}/4)
          </button>
        ` : ""}
      </div>

      <h3 class="question-text" id="quiz-question-text">
        ${q.question}
      </h3>

      <div class="quiz-options-list" id="quiz-options-container">
        ${optionsHtml}
      </div>

      ${hintsHtml}
      ${feedbackHtml}

      <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--border-color); padding-top:1.25rem; margin-top:1.25rem;">
        <button id="quiz-prev-btn" class="btn-secondary" ${prevDisabled} onclick="window.quizEngine.previousQuestion()">← Previous</button>
        <button id="quiz-next-btn" class="btn-primary" onclick="window.quizEngine.nextQuestion()">${nextLabel}</button>
      </div>
    `;

    // If answered, load Mistake Detective & Confidence Tracker
    if (isAnswered) {
      if (!isCorrect) {
        this.loadMistakeDetective(q.id, selectedAns);
      }
      this.renderConfidenceTracker(q.id, selectedAns, isCorrect);
    }
  }

  async selectOption(optKey) {
    if (this.userAnswers[this.currentIndex] !== undefined) return;
    this.userAnswers[this.currentIndex] = optKey;
    clearInterval(this.timerInterval);
    this.renderCurrentQuestion();
  }

  async requestNextHint(quizId) {
    try {
      const res = await fetch(`/api/hints/${quizId}`);
      const data = await res.json();
      if (data.success && data.hints.length > 0) {
        if (!this.activeHints[this.currentIndex]) {
          this.activeHints[this.currentIndex] = [];
        }
        const currentCount = this.activeHints[this.currentIndex].length;
        if (currentCount < data.hints.length) {
          this.activeHints[this.currentIndex].push(data.hints[currentCount]);
          this.renderCurrentQuestion();
        } else {
          alert("All 4 Hint Ladder levels have been revealed for this question.");
        }
      } else {
        // Fallback progressive hint
        if (!this.activeHints[this.currentIndex]) this.activeHints[this.currentIndex] = [];
        this.activeHints[this.currentIndex].push({
          title: "Recall Core Formula",
          hint_text: "Break down the given quantities and test which law or balancing property applies."
        });
        this.renderCurrentQuestion();
      }
    } catch (e) {
      console.error("Error requesting hint:", e);
    }
  }

  async loadMistakeDetective(quizId, wrongOption) {
    const el = document.getElementById("mistake-detective-placeholder");
    if (!el) return;

    try {
      const res = await fetch(`/api/mistake-detective/${quizId}/${wrongOption}`);
      const data = await res.json();
      if (data.success && data.detective) {
        const d = data.detective;
        el.innerHTML = `
          <div class="mistake-detective-card">
            <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.4rem;">
              <span style="font-size:1.3rem;">🔍</span>
              <strong style="color:#f87171; font-size:1rem;">Mistake Detective: ${d.misconception_name}</strong>
            </div>
            <p style="font-size:0.88rem; color:var(--text-secondary); margin-bottom:0.5rem; line-height:1.5;">
              <strong>Why this mistake happens:</strong> ${d.why_it_happens}
            </p>
            <p style="font-size:0.88rem; color:#34d399; margin-bottom:0.5rem; line-height:1.5;">
              <strong>How to fix:</strong> ${d.how_to_fix}
            </p>
            ${d.follow_up_practice ? `
              <div style="background:rgba(255,255,255,0.04); padding:0.6rem 0.85rem; border-radius:6px; font-size:0.82rem; color:#fde047;">
                <strong>⚡ Targeted Practice:</strong> ${d.follow_up_practice}
              </div>
            ` : ""}
          </div>
        `;
      }
    } catch (e) {
      console.error("Mistake detective error:", e);
    }
  }

  renderConfidenceTracker(quizId, selectedOption, isCorrect) {
    const el = document.getElementById("confidence-tracker-placeholder");
    if (!el) return;

    const rated = this.confidenceRatings[this.currentIndex];

    if (rated) {
      el.innerHTML = `
        <div class="confidence-box" style="border-color:${rated.evaluation.classification === 'mastery_confirmed' ? 'var(--secondary)' : 'var(--accent)'};">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
              <span class="chip" style="font-size:0.75rem;">${rated.evaluation.badge}</span>
              <p style="font-size:0.88rem; color:var(--text-primary); margin-top:0.35rem;">
                ${rated.evaluation.message}
              </p>
            </div>
          </div>
        </div>
      `;
      return;
    }

    el.innerHTML = `
      <div class="confidence-box">
        <strong style="font-size:0.88rem; color:var(--text-secondary);">
          🎯 Confidence Tracker: How sure were you about this answer?
        </strong>
        <div class="confidence-btn-group">
          <button class="confidence-btn" onclick="window.quizEngine.submitConfidence(${quizId}, '${selectedOption}', ${isCorrect}, 'not_sure')">
            😕 Not Sure
          </button>
          <button class="confidence-btn" onclick="window.quizEngine.submitConfidence(${quizId}, '${selectedOption}', ${isCorrect}, 'somewhat_sure')">
            🙂 Somewhat Sure
          </button>
          <button class="confidence-btn" onclick="window.quizEngine.submitConfidence(${quizId}, '${selectedOption}', ${isCorrect}, 'very_sure')">
            🎯 Very Sure
          </button>
        </div>
      </div>
    `;
  }

  async submitConfidence(quizId, selectedOption, isCorrect, level) {
    const activeUserId = window.appState ? window.appState.currentUser.id : 1;
    try {
      const res = await fetch("/api/confidence-record", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: activeUserId,
          quiz_id: quizId,
          selected_option: selectedOption,
          is_correct: isCorrect,
          confidence_level: level
        })
      });
      const data = await res.json();
      if (data.success) {
        this.confidenceRatings[this.currentIndex] = data;
        this.renderConfidenceTracker(quizId, selectedOption, isCorrect);
      }
    } catch (e) {
      console.error("Confidence submission error:", e);
    }
  }

  resetTimer() {
    clearInterval(this.timerInterval);
    this.timerSeconds = 45;
    const timerDisplay = document.getElementById("quiz-timer-display");

    const updateTimer = () => {
      const mins = Math.floor(this.timerSeconds / 60);
      const secs = this.timerSeconds % 60;
      if (timerDisplay) {
        timerDisplay.textContent = `⏱️ ${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
      }

      if (this.timerSeconds <= 0) {
        clearInterval(this.timerInterval);
        if (this.userAnswers[this.currentIndex] === undefined) {
          this.selectOption("TIMEOUT");
        }
      }
      this.timerSeconds--;
    };

    updateTimer();
    this.timerInterval = setInterval(updateTimer, 1000);
  }

  previousQuestion() {
    if (this.currentIndex > 0) {
      this.currentIndex--;
      this.renderCurrentQuestion();
    }
  }

  async nextQuestion() {
    const total = this.questions.length;
    if (this.currentIndex < total - 1) {
      this.currentIndex++;
      this.renderCurrentQuestion();
    } else {
      clearInterval(this.timerInterval);
      await this.submitQuizResults();
    }
  }

  async submitQuizResults() {
    const total = this.questions.length;
    let score = 0;

    this.questions.forEach((q, idx) => {
      if (this.userAnswers[idx] === q.correct_option) {
        score++;
      }
    });

    const activeUserId = window.appState ? window.appState.currentUser.id : 1;

    try {
      const res = await fetch("/api/quiz-attempts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: activeUserId,
          topic_id: this.currentTopicId,
          score: score,
          total_questions: total
        })
      });

      const data = await res.json();
      this.showQuizSummary(score, total, data);
      
      if (window.progressTracker) {
        window.progressTracker.loadUserProgress();
      }
    } catch (err) {
      console.error("Quiz submission error:", err);
    }
  }

  showQuizSummary(score, total, attemptResult) {
    const pct = Math.round((score / total) * 100);
    const quizArea = document.getElementById("quiz-content-area");
    if (!quizArea) return;

    let gapBadge = "";
    if (pct < 50) {
      gapBadge = `<div class="status-badge critical_gap" style="margin-bottom:1rem; font-size:0.9rem;">⚠️ Critical Learning Gap Detected</div>`;
    } else if (pct < 70) {
      gapBadge = `<div class="status-badge needs_revision" style="margin-bottom:1rem; font-size:0.9rem;">🔄 Revision Recommended</div>`;
    } else {
      gapBadge = `<div class="status-badge mastered" style="margin-bottom:1rem; font-size:0.9rem;">🏆 Topic Mastered!</div>`;
    }

    quizArea.innerHTML = `
      <div style="text-align:center; padding:2rem 1rem;">
        ${gapBadge}
        <h2 style="font-size:2.2rem; margin-bottom:0.5rem;">Assessment Completed!</h2>
        <div style="font-size:3.5rem; font-weight:800; color:var(--primary); font-family:var(--font-heading); margin:1rem 0;">
          ${score} / ${total}
          <span style="font-size:1.5rem; color:var(--text-secondary);">(${pct}%)</span>
        </div>
        <p style="color:var(--text-secondary); max-width:550px; margin:0 auto 1.75rem;">
          ${attemptResult.recommendation || "Your performance has been analyzed by LearnSphere AI. Check your personalized study plan for tailored revision tasks."}
        </p>

        <div style="display:flex; justify-content:center; gap:1rem; flex-wrap:wrap;">
          <button class="btn-primary" onclick="window.quizEngine.startQuizForTopic(${this.currentTopicId})">
            🔄 Retake This Quiz
          </button>
          <button class="btn-secondary" onclick="window.navigateTo('progress')">
            📊 View Learning Gaps
          </button>
          <button class="btn-secondary" onclick="window.navigateTo('study-plan')">
            📅 Open Study Plan
          </button>
        </div>
      </div>
    `;
  }
}

window.quizEngine = new QuizEngine();
