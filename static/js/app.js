/**
 * LearnSphere AI - Master Controller & Router
 * SMVITM Bantakal | Department of AI & Data Science | Team 11
 */

class AppState {
  constructor() {
    this.currentView = "landing";
    this.currentLanguage = "en";
    this.currentUser = {
      id: 1,
      username: "arjun_student",
      full_name: "Arjun Rao",
      role: "student",
      grade: "Class 10"
    };
    this.currentTopicSlug = "linear-equations";
    this.currentTopicData = null;
    this.allTopics = [];
  }
}

window.appState = new AppState();

// Global Navigation Function
window.navigateTo = function(viewName) {
  // Update State
  window.appState.currentView = viewName;

  // Update Nav Buttons
  document.querySelectorAll(".nav-tab-btn").forEach(btn => {
    if (btn.dataset.view === viewName) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });

  // Switch View Sections
  document.querySelectorAll(".view-section").forEach(sec => {
    sec.classList.remove("active");
  });

  const targetSec = document.getElementById(`view-${viewName}`);
  if (targetSec) {
    targetSec.classList.add("active");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  // View-specific trigger hooks
  if (viewName === "visual-lab" && window.visualLab) {
    setTimeout(() => {
      window.visualLab.drawGraph();
    }, 100);
  } else if (viewName === "progress" && window.progressTracker) {
    window.progressTracker.loadUserProgress();
  } else if (viewName === "study-plan" && window.progressTracker) {
    window.progressTracker.loadStudyPlan();
  } else if (viewName === "admin" && window.loadAdminDashboard) {
    window.loadAdminDashboard();
  }
};

window.switchAdaptiveMode = function(modeName) {
  document.querySelectorAll(".mode-pill-btn").forEach(btn => {
    btn.classList.toggle("active", btn.textContent.includes(modeName));
  });
  if (window.quizEngine) {
    window.quizEngine.currentMode = modeName;
  }
};


window.startRevisionForTopic = function(topicId) {
  if (window.quizEngine) {
    window.navigateTo("quiz");
    const select = document.getElementById("quiz-topic-select");
    if (select) select.value = topicId;
    window.quizEngine.startQuizForTopic(topicId);
  }
};

document.addEventListener("DOMContentLoaded", async () => {
  // Initialize Components
  setupThemeToggle();
  setupLanguageSwitcher();
  setupPersonaSwitcher();
  setupSearchAutocomplete();
  setupNotesGenerator();
  setupNetworkInfoBadge();

  // Initialize Sub-Engines
  if (window.doubtSolver) window.doubtSolver.init();
  if (window.quizEngine) await window.quizEngine.init();
  if (window.visualLab) window.visualLab.init();
  if (window.progressTracker) await window.progressTracker.init();

  // Load Initial Data
  await loadDashboardSubjects();
  await loadTopicLearningSidebar();
  await loadTopicContent("linear-equations");

  // Hook navigation buttons
  document.querySelectorAll(".nav-tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const view = btn.dataset.view;
      if (view) window.navigateTo(view);
    });
  });

  // Check URL hash or default to landing
  const hash = window.location.hash.replace("#", "");
  if (hash && document.getElementById(`view-${hash}`)) {
    window.navigateTo(hash);
  }
});

// ==========================================
// NETWORK & LAN SHARING BADGE
// ==========================================
async function setupNetworkInfoBadge() {
  const badge = document.getElementById("lan-share-badge");
  if (!badge) return;

  try {
    const res = await fetch("/api/network-info");
    const data = await res.json();
    if (data.success && data.primary_ip) {
      const lanUrl = `http://${data.primary_ip}:${data.port}`;
      badge.textContent = `🌐 LAN: ${data.primary_ip}:${data.port}`;
      badge.title = `Hosted on local IP! Click to copy: ${lanUrl}`;
      badge.style.display = "inline-flex";

      badge.onclick = () => {
        navigator.clipboard.writeText(lanUrl);
        const orig = badge.textContent;
        badge.textContent = "✅ Copied URL!";
        badge.style.borderColor = "var(--secondary)";
        badge.style.color = "#34d399";
        setTimeout(() => {
          badge.textContent = orig;
          badge.style.borderColor = "var(--primary)";
          badge.style.color = "#c7d2fe";
        }, 2200);
      };
    }
  } catch (err) {
    console.warn("Could not fetch network info:", err);
  }
}

// ==========================================
// THEME & LANGUAGE CONTROLLERS
// ==========================================
function setupThemeToggle() {
  const btn = document.getElementById("theme-toggle-btn");
  if (!btn) return;


  const savedTheme = localStorage.getItem("learnsphere_theme") || "dark";
  document.documentElement.setAttribute("data-theme", savedTheme);
  btn.textContent = savedTheme === "dark" ? "☀️" : "🌙";

  btn.addEventListener("click", () => {
    const curr = document.documentElement.getAttribute("data-theme");
    const next = curr === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("learnsphere_theme", next);
    btn.textContent = next === "dark" ? "☀️" : "🌙";
  });
}

function setupLanguageSwitcher() {
  const select = document.getElementById("global-lang-select");
  if (!select) return;

  select.addEventListener("change", (e) => {
    const lang = e.target.value;
    window.appState.currentLanguage = lang;
    
    // Refresh topic view if active
    if (window.appState.currentTopicSlug) {
      loadTopicContent(window.appState.currentTopicSlug);
    }
  });
}

function setupPersonaSwitcher() {
  const select = document.getElementById("global-user-select");
  if (!select) return;

  select.addEventListener("change", (e) => {
    const val = e.target.value;
    if (val === "arjun") {
      window.appState.currentUser = { id: 1, full_name: "Arjun Rao", role: "student", grade: "Class 10" };
    } else if (val === "ananya") {
      window.appState.currentUser = { id: 2, full_name: "Ananya Shenoy", role: "student", grade: "Class 9" };
    } else if (val === "pooja") {
      window.appState.currentUser = { id: 3, full_name: "Mrs. Pooja", role: "teacher", grade: "Faculty" };
      window.navigateTo("teacher");
    } else if (val === "admin") {
      window.appState.currentUser = { id: 4, full_name: "Administrator", role: "admin", grade: "Coordinator" };
      window.navigateTo("admin");
      if (window.loadAdminDashboard) window.loadAdminDashboard();
    }


    // Refresh greeting and stats
    const nameEl = document.getElementById("dash-user-name");
    if (nameEl) nameEl.textContent = window.appState.currentUser.full_name;

    if (window.progressTracker) {
      window.progressTracker.loadUserProgress();
      window.progressTracker.loadStudyPlan();
    }
  });
}

// ==========================================
// GLOBAL SEARCH & AUTOCOMPLETE
// ==========================================
async function setupSearchAutocomplete() {
  const searchInput = document.getElementById("global-search-input");
  const searchBtn = document.getElementById("global-search-btn");
  const suggestionsBox = document.getElementById("search-autocomplete-box");

  if (!searchInput) return;

  try {
    const res = await fetch("/api/topics");
    const data = await res.json();
    if (data.success) {
      window.appState.allTopics = data.topics;
    }
  } catch (e) {
    console.error("Search data load error:", e);
  }

  const handleSearch = () => {
    const query = searchInput.value.trim().toLowerCase();
    if (!query) return;

    const matched = window.appState.allTopics.find(t => 
      t.name.toLowerCase().includes(query) || t.summary.toLowerCase().includes(query)
    );

    if (matched) {
      loadTopicContent(matched.slug);
      window.navigateTo("learn");
      if (suggestionsBox) suggestionsBox.style.display = "none";
    } else {
      // Direct query to Doubt Solver
      window.navigateTo("doubt-solver");
      const chatIn = document.getElementById("chat-input");
      if (chatIn) {
        chatIn.value = searchInput.value;
        if (window.doubtSolver) window.doubtSolver.handleSend();
      }
    }
  };

  searchInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") handleSearch();
  });

  if (searchBtn) searchBtn.addEventListener("click", handleSearch);
}

// ==========================================
// SUBJECTS & DASHBOARD
// ==========================================
async function loadDashboardSubjects() {
  try {
    const res = await fetch("/api/subjects");
    const data = await res.json();
    if (!data.success) return;

    const grid = document.getElementById("dash-subjects-grid");
    if (!grid) return;

    grid.innerHTML = data.subjects.map(s => `
      <div class="subject-card glass-panel" onclick="window.filterBySubject(${s.id})">
        <div class="subject-card-header">
          <span class="subject-card-icon">${s.icon}</span>
          <span class="chip" style="font-size:0.75rem; border-color:${s.color}; color:${s.color};">
            ${s.code}
          </span>
        </div>
        <div class="subject-card-title">${s.name}</div>
        <div class="subject-card-desc">${s.description}</div>
        <div class="subject-progress-bar-bg">
          <div class="subject-progress-bar-fill" style="width:70%; background:${s.color};"></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:0.78rem; color:var(--text-muted);">
          <span>${s.topic_count || 2} Core Topics</span>
          <span style="color:${s.color}; font-weight:700;">Explore →</span>
        </div>
      </div>
    `).join("");
  } catch (err) {
    console.error("Error loading subjects:", err);
  }
}

window.filterBySubject = function(subjectId) {
  window.navigateTo("learn");
  loadTopicLearningSidebar(subjectId);
};

// ==========================================
// TOPIC LEARNING VIEW
// ==========================================
async function loadTopicLearningSidebar(subjectId = null) {
  const sidebar = document.getElementById("learn-topics-sidebar");
  if (!sidebar) return;

  try {
    const url = subjectId ? `/api/topics?subject_id=${subjectId}` : "/api/topics";
    const res = await fetch(url);
    const data = await res.json();
    if (!data.success) return;

    sidebar.innerHTML = `
      <div style="font-size:0.8rem; text-transform:uppercase; font-weight:700; color:var(--text-muted); margin-bottom:0.5rem; padding:0 0.5rem;">
        Available Modules (${data.topics.length})
      </div>
    ` + data.topics.map(t => `
      <button class="topic-item-btn ${t.slug === window.appState.currentTopicSlug ? "active" : ""}" 
              onclick="window.loadTopicContent('${t.slug}')">
        <div class="topic-item-name">${t.name}</div>
        <div class="topic-item-subject" style="color:${t.subject_color};">
          ${t.subject_name} • <span class="badge-tag" style="padding:0.1rem 0.4rem; font-size:0.68rem;">${t.difficulty}</span>
        </div>
      </button>
    `).join("");
  } catch (err) {
    console.error("Error loading topic sidebar:", err);
  }
}

window.loadTopicContent = async function(slug) {
  window.appState.currentTopicSlug = slug;

  // Highlight active sidebar item
  document.querySelectorAll(".topic-item-btn").forEach(btn => {
    btn.classList.toggle("active", btn.innerHTML.includes(slug));
  });

  try {
    const res = await fetch(`/api/topics/${slug}`);
    const data = await res.json();
    if (!data.success) return;

    const topic = data.topic;
    window.appState.currentTopicData = topic;

    // Update Breadcrumb & Title
    const titleEl = document.getElementById("topic-main-title");
    const breadcrumbEl = document.getElementById("topic-breadcrumb");
    const summaryEl = document.getElementById("topic-summary-box");
    const formulaBox = document.getElementById("topic-formula-card");

    if (titleEl) titleEl.textContent = topic.name;
    if (breadcrumbEl) {
      breadcrumbEl.innerHTML = `
        <span style="color:var(--text-muted);">${topic.subject_name}</span> &gt; 
        <span style="color:var(--text-muted);">${topic.grade_level}</span> &gt; 
        <span style="color:${topic.subject_color}; font-weight:700;">${topic.name}</span>
      `;
    }

    if (summaryEl) summaryEl.textContent = topic.summary;

    if (formulaBox) {
      if (topic.formula_box) {
        formulaBox.style.display = "block";
        formulaBox.textContent = topic.formula_box;
      } else {
        formulaBox.style.display = "none";
      }
    }

    // Default to Simple Explanation
    switchExplanationMode("simple");

    // Hook Quiz & Notes shortcut buttons
    const quizBtn = document.getElementById("topic-take-quiz-btn");
    const notesBtn = document.getElementById("topic-gen-notes-btn");

    if (quizBtn) {
      quizBtn.onclick = () => {
        window.quizEngine.currentTopicId = topic.id;
        window.navigateTo("quiz");
        const select = document.getElementById("quiz-topic-select");
        if (select) select.value = topic.id;
        window.quizEngine.startQuizForTopic(topic.id);
      };
    }

    if (notesBtn) {
      notesBtn.onclick = () => {
        window.navigateTo("notes");
        const select = document.getElementById("notes-topic-select");
        if (select) select.value = topic.slug;
        triggerNotesGeneration();
      };
    }
  } catch (err) {
    console.error("Error loading topic:", err);
  }
};

window.switchExplanationMode = async function(mode) {
  const topic = window.appState.currentTopicData;
  if (!topic) return;

  // Update tabs
  document.querySelectorAll(".mode-tab-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.mode === mode);
  });
  document.querySelectorAll(".format-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.mode === mode);
  });

  const bodyEl = document.getElementById("topic-explanation-body");
  const audioBtn = document.getElementById("topic-audio-btn");
  if (!bodyEl) return;

  let contentText = "";
  let speechText = "";

  if (mode === "simple") {
    contentText = `
      <div style="font-size:1.05rem; line-height:1.7; margin-bottom:1.5rem;">
        ${topic.simple_explanation}
      </div>
      <div style="background:rgba(255,255,255,0.03); border-radius:var(--radius-md); padding:1.25rem; border:1px solid var(--border-color);">
        <strong style="color:#fbbf24; display:block; margin-bottom:0.5rem;">💡 Everyday Analogy:</strong>
        <p style="color:var(--text-secondary); line-height:1.6;">${topic.real_life_example}</p>
      </div>
    `;
    speechText = `${topic.name}. ${topic.simple_explanation}. Example: ${topic.real_life_example}`;
  } else if (mode === "pointwise") {
    const points = topic.pointwise_notes || topic.simple_explanation;
    contentText = `
      <div style="background:rgba(99,102,241,0.05); border-radius:var(--radius-md); padding:1.5rem; border:1px solid var(--border-color);">
        <h4 style="color:#a5b4fc; margin-bottom:0.75rem;">📝 Structured Point-Wise Notes:</h4>
        <div style="white-space:pre-line; line-height:1.8; font-size:1rem; color:var(--text-primary);">
          ${points}
        </div>
      </div>
    `;
    speechText = points;
  } else if (mode === "detailed") {
    contentText = `
      <div style="font-size:1.05rem; line-height:1.7; margin-bottom:1.5rem;">
        ${topic.detailed_explanation}
      </div>
    `;
    speechText = topic.detailed_explanation;
  } else if (mode === "exam_ready") {
    const examNotes = topic.exam_ready_notes || "Review key definitions, formula derivations, and common textbook problems.";
    contentText = `
      <div style="background:linear-gradient(135deg, rgba(245,158,11,0.08), rgba(17,24,39,0.8)); border-radius:var(--radius-md); padding:1.5rem; border:1px solid rgba(245,158,11,0.3); border-left:5px solid var(--accent);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
          <h4 style="color:#fbbf24;">🎯 Exam-Ready Syllabus Blueprint:</h4>
          <span class="chip" style="font-size:0.75rem;">High Yield</span>
        </div>
        <div style="white-space:pre-line; line-height:1.8; font-size:0.98rem; color:var(--text-primary);">
          ${examNotes}
        </div>
      </div>
    `;
    speechText = examNotes;
  } else if (mode === "kannada") {
    contentText = `
      <div style="background:rgba(99,102,241,0.08); border-radius:var(--radius-md); padding:1.5rem; border:1px solid rgba(99,102,241,0.25);">
        <h4 style="color:#a5b4fc; margin-bottom:0.75rem; font-size:1.2rem;">ಕನ್ನಡ ವಿವರಣೆ (Kannada Explanation):</h4>
        <div style="font-size:1.05rem; line-height:1.8; color:var(--text-primary); white-space:pre-line;">
          ${topic.kannada_explanation}
        </div>
      </div>
    `;
    speechText = topic.kannada_explanation;
  } else if (mode === "hindi") {
    contentText = `
      <div style="background:rgba(236,72,153,0.08); border-radius:var(--radius-md); padding:1.5rem; border:1px solid rgba(236,72,153,0.25);">
        <h4 style="color:#f472b6; margin-bottom:0.75rem; font-size:1.2rem;">हिंदी व्याख्या (Hindi Explanation):</h4>
        <div style="font-size:1.05rem; line-height:1.8; color:var(--text-primary); white-space:pre-line;">
          ${topic.hindi_explanation}
        </div>
      </div>
    `;
    speechText = topic.hindi_explanation;
  } else if (mode === "teach_back") {
    renderTeachBackInterface(topic, bodyEl);
    return;
  } else if (mode === "flashcards") {
    await renderFlashcardsInterface(topic.id, bodyEl);
    return;
  }

  bodyEl.innerHTML = contentText;

  if (audioBtn) {
    audioBtn.onclick = () => {
      if (window.doubtSolver) window.doubtSolver.speakText(speechText);
    };
  }
};

function renderTeachBackInterface(topic, container) {
  container.innerHTML = `
    <div class="teach-back-card glass-panel">
      <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem;">
        <span style="font-size:1.5rem;">🗣️</span>
        <h3 style="font-size:1.3rem;">Teach-Back Mode: Master Through Explaining</h3>
      </div>
      <p style="color:var(--text-secondary); font-size:0.92rem;">
        Explaining a concept in your own words is the gold standard of learning science (Feynman Technique). Explain <strong>${topic.name}</strong> as if teaching a friend:
      </p>

      <textarea id="teach-back-input" class="teach-back-textarea" 
                placeholder="Type your explanation here in your own words... (e.g. Photosynthesis happens when leaves take in sunlight...)"></textarea>

      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.75rem;">
        <button class="btn-primary" onclick="window.submitTeachBack('${topic.slug}')">
          ✨ Evaluate My Explanation (+25 Points)
        </button>
        <span style="font-size:0.82rem; color:var(--text-muted);">AI checks required core concepts & completeness.</span>
      </div>

      <div id="teach-back-results-area" style="margin-top:1.5rem;"></div>
    </div>
  `;
}

window.submitTeachBack = async function(topicSlug) {
  const inputEl = document.getElementById("teach-back-input");
  const resultsEl = document.getElementById("teach-back-results-area");
  if (!inputEl || !resultsEl) return;

  const text = inputEl.value.trim();
  if (!text) {
    alert("Please write a short explanation before submitting.");
    return;
  }

  resultsEl.innerHTML = `<div class="chip">Evaluating explanation against concept rubrics... ⏳</div>`;

  try {
    const res = await fetch("/api/teach-back", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        topic_slug: topicSlug,
        explanation: text,
        user_id: window.appState.currentUser.id
      })
    });
    const data = await res.json();
    if (!data.success) {
      resultsEl.innerHTML = `<p style="color:var(--danger);">Evaluation error. Please retry.</p>`;
      return;
    }

    resultsEl.innerHTML = `
      <div class="glass-panel" style="padding:1.5rem; border-color:${data.score_pct >= 70 ? 'var(--secondary)' : 'var(--accent)'}; animation:fadeIn 0.3s ease;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
          <div>
            <span class="chip" style="font-size:0.75rem; color:#34d399; border-color:#34d399;">+25 Learning Points Earned! 🪙</span>
            <h4 style="font-size:1.3rem; margin-top:0.35rem;">${data.assessment}</h4>
          </div>
          <div style="font-size:2.2rem; font-weight:800; color:var(--primary); font-family:var(--font-heading);">
            ${data.score_pct}% <span style="font-size:0.9rem; color:var(--text-muted);">Concept Match</span>
          </div>
        </div>

        <p style="font-size:0.95rem; color:var(--text-primary); line-height:1.6; margin-bottom:1rem;">
          ${data.feedback}
        </p>

        <div style="background:rgba(255,255,255,0.03); padding:1rem; border-radius:8px; margin-bottom:1rem; border:1px solid var(--border-color);">
          <strong style="color:#fbbf24; display:block; margin-bottom:0.3rem;">📖 Teacher Model Answer:</strong>
          <p style="color:var(--text-secondary); font-size:0.9rem; line-height:1.6;">${data.model_answer}</p>
        </div>

        <div style="font-size:0.85rem; color:#a5b4fc;">
          <strong>💡 Pedagogical Tip:</strong> ${data.pro_tip}
        </div>
      </div>
    `;
  } catch (err) {
    console.error("Teach back error:", err);
  }
};

async function renderFlashcardsInterface(topicId, container) {
  try {
    const res = await fetch(`/api/flashcards/${topicId}`);
    const data = await res.json();
    if (!data.success || data.flashcards.length === 0) {
      container.innerHTML = `<p style="color:var(--text-secondary); padding:2rem; text-align:center;">No flashcards available for this topic yet.</p>`;
      return;
    }

    const cards = data.flashcards;
    window.topicFlashcards = cards;
    window.currentFlashcardIndex = 0;

    renderSingleFlashcard(container);
  } catch (err) {
    console.error("Flashcards load error:", err);
  }
}

function renderSingleFlashcard(container) {
  const cards = window.topicFlashcards;
  const idx = window.currentFlashcardIndex;
  const card = cards[idx];
  const total = cards.length;

  container.innerHTML = `
    <div style="text-align:center; margin-bottom:1rem;">
      <span class="chip" style="font-size:0.75rem;">Spaced Repetition • Review Interval: Day ${card.interval_day}</span>
      <div style="font-size:0.85rem; color:var(--text-muted); margin-top:0.3rem;">Card ${idx + 1} of ${total} (Click card to flip)</div>
    </div>

    <div class="flashcard-wrapper" onclick="this.classList.toggle('flipped')">
      <div class="flashcard-inner">
        <div class="flashcard-front">
          <div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em; color:var(--text-muted); margin-bottom:0.5rem;">Prompt / Question</div>
          <h3 style="font-size:1.35rem; line-height:1.5;">${card.front_prompt}</h3>
          <div style="margin-top:1.5rem; font-size:0.8rem; color:var(--primary);">🔄 Click card to reveal answer</div>
        </div>
        <div class="flashcard-back">
          <div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em; color:#34d399; margin-bottom:0.5rem;">Verified Answer</div>
          <p style="font-size:1.1rem; line-height:1.6; color:var(--text-primary);">${card.back_answer}</p>
        </div>
      </div>
    </div>

    <div style="display:flex; justify-content:center; gap:1rem; margin-top:1.5rem;">
      <button class="btn-secondary" ${idx === 0 ? "disabled" : ""} onclick="window.currentFlashcardIndex--; renderSingleFlashcard(document.getElementById('topic-explanation-body'))">
        ← Previous Card
      </button>
      <button class="btn-primary" ${idx === total - 1 ? "disabled" : ""} onclick="window.currentFlashcardIndex++; renderSingleFlashcard(document.getElementById('topic-explanation-body'))">
        Next Card →
      </button>
    </div>
  `;
}

// ==========================================
// ADMINISTRATOR DASHBOARD LOADER
// ==========================================
window.loadAdminDashboard = async function() {
  try {
    const res = await fetch("/api/admin-stats");
    const data = await res.json();
    if (!data.success) return;

    const uEl = document.getElementById("admin-total-users");
    const sEl = document.getElementById("admin-total-subjects");
    const tEl = document.getElementById("admin-total-topics");
    const aEl = document.getElementById("admin-total-attempts");
    const cEl = document.getElementById("admin-total-confidence");

    if (uEl) uEl.textContent = data.total_users;
    if (sEl) sEl.textContent = data.total_subjects;
    if (tEl) tEl.textContent = data.total_topics;
    if (aEl) aEl.textContent = data.total_attempts;
    if (cEl) cEl.textContent = data.total_confidence_evaluations;
  } catch (err) {
    console.error("Admin stats error:", err);
  }
};



// ==========================================
// SHORT NOTES & CONCEPT MIND MAP GENERATOR
// ==========================================
function setupNotesGenerator() {
  const genBtn = document.getElementById("generate-notes-btn");
  if (genBtn) {
    genBtn.addEventListener("click", () => triggerNotesGeneration());
  }
}

async function triggerNotesGeneration() {
  const topicSelect = document.getElementById("notes-topic-select");
  const formatSelect = document.getElementById("notes-format-select");
  const outputContainer = document.getElementById("notes-output-area");

  if (!outputContainer) return;
  const slug = topicSelect ? topicSelect.value : "linear-equations";
  const format = formatSelect ? formatSelect.value : "short_notes";
  const lang = window.appState.currentLanguage;

  outputContainer.innerHTML = `<div style="text-align:center; padding:3rem;"><div class="chip">Generating concise notes with AI... ⏳</div></div>`;

  try {
    const res = await fetch("/api/generate-notes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic_slug: slug, format_type: format, language: lang })
    });

    const data = await res.json();
    if (!data.success) {
      outputContainer.innerHTML = `<p style="color:var(--danger);">Failed to generate notes. Please retry.</p>`;
      return;
    }

    if (data.format === "mind_map") {
      renderMindMapSVG(data.mind_map_data, outputContainer);
    } else {
      renderTextNotes(data, outputContainer);
    }
  } catch (err) {
    console.error("Notes generation error:", err);
  }
}

function renderTextNotes(data, container) {
  let notesHtml = `
    <div class="glass-panel" style="padding:2rem; position:relative;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem; border-bottom:1px solid var(--border-color); padding-bottom:1rem;">
        <div>
          <span class="chip" style="font-size:0.75rem; margin-bottom:0.4rem;">High-Yield Revision Notes</span>
          <h3 style="font-size:1.6rem;">${data.title}</h3>
        </div>
        <div style="display:flex; gap:0.5rem;">
          <button class="btn-secondary" onclick="window.print()">🖨️ Print Notes</button>
          <button class="btn-primary" onclick="navigator.clipboard.writeText(document.getElementById('notes-raw-text').innerText); alert('Copied notes to clipboard!');">📋 Copy</button>
        </div>
      </div>

      <div id="notes-raw-text" style="font-size:1rem; line-height:1.7;">
        ${window.doubtSolver.formatMarkdown(data.content)}
      </div>
    </div>
  `;
  container.innerHTML = notesHtml;
}

function renderMindMapSVG(mindMapData, container) {
  container.innerHTML = `
    <div class="glass-panel" style="padding:1.5rem;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
        <h3 style="font-size:1.4rem;">🧠 Interactive Concept Tree: ${mindMapData.name}</h3>
        <span class="chip">SVG Visual Graph</span>
      </div>
      <div class="mind-map-svg-wrap">
        <svg id="mind-map-svg" width="100%" height="450" viewBox="0 0 850 450" style="background:#0b1120; border-radius:12px;">
          <defs>
            <linearGradient id="rootGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#6366f1"/>
              <stop offset="100%" stop-color="#4f46e5"/>
            </linearGradient>
            <linearGradient id="branchGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#10b981"/>
              <stop offset="100%" stop-color="#059669"/>
            </linearGradient>
          </defs>

          <!-- Central Core Node -->
          <circle cx="160" cy="225" r="55" fill="url(#rootGrad)" filter="drop-shadow(0 0 12px rgba(99,102,241,0.5))"/>
          <text x="160" y="222" fill="#fff" font-family="Outfit" font-size="14" font-weight="700" text-anchor="middle" dominant-baseline="middle">
            ${mindMapData.name}
          </text>

          <!-- Branches -->
          ${mindMapData.children.map((branch, bIdx) => {
            const bY = 70 + bIdx * 95;
            const bX = 420;
            return `
              <!-- Connector line -->
              <path d="M 215 225 C 300 225, 330 ${bY}, ${bX - 110} ${bY}" stroke="#6366f1" stroke-width="2.5" fill="none" opacity="0.75"/>
              
              <!-- Branch Node -->
              <rect x="${bX - 110}" y="${bY - 22}" width="220" height="44" rx="10" fill="rgba(30, 41, 59, 0.9)" stroke="#6366f1" stroke-width="1.5"/>
              <text x="${bX}" y="${bY + 5}" fill="#f8fafc" font-family="Plus Jakarta Sans" font-size="12" font-weight="700" text-anchor="middle">
                ${branch.name}
              </text>

              <!-- Leaf Children -->
              ${branch.children ? branch.children.map((child, cIdx) => {
                const cY = bY - 18 + cIdx * 24;
                const cX = 680;
                return `
                  <line x1="${bX + 110}" y1="${bY}" x2="${cX}" y2="${cY}" stroke="#10b981" stroke-width="1.5" stroke-dasharray="3,3" opacity="0.6"/>
                  <rect x="${cX}" y="${cY - 12}" width="145" height="24" rx="6" fill="rgba(16, 185, 129, 0.15)" stroke="#10b981" stroke-width="1"/>
                  <text x="${cX + 72}" y="${cY + 4}" fill="#a7f3d0" font-family="Plus Jakarta Sans" font-size="10.5" font-weight="600" text-anchor="middle">
                    ${child.name}
                  </text>
                `;
              }).join("") : ""}
            `;
          }).join("")}
        </svg>
      </div>
    </div>
  `;
}
