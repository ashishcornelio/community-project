/**
 * LearnSphere AI - Master Controller & Router
 * SMVITM Bantakal | Department of AI & Data Science | Team 11
 */

class AppState {
  constructor() {
    const sessionUser = window.__LEARNSPHERE_USER__ || {};
    this.currentView = "landing";
    this.currentLanguage = "en";
    this.currentUser = {
      id: sessionUser.id || 1,
      username: sessionUser.username || "arjun_student",
      full_name: sessionUser.full_name || "Arjun Rao",
      role: sessionUser.role || "student",
      grade: sessionUser.grade || "Class 10",
      school: sessionUser.school || "Shri Vishnumoorthi Hayavadanaswami High School, Innanje"
    };
    const gradeMatch = String(this.currentUser.grade).match(/(8|9|10)/);
    this.currentGrade = gradeMatch ? gradeMatch[1] : "10";
    this.currentTopicSlug = "linear-equations";
    this.currentTopicData = null;
    this.allTopics = [];
  }
}

window.appState = new AppState();

// Global Navigation Function
window.navigateTo = function(viewName) {
  const targetSec = document.getElementById(`view-${viewName}`);
  const role = window.appState.currentUser.role;
  if (!targetSec || (role === "teacher" && targetSec.classList.contains("student-only-view"))) return;

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

  if (targetSec) {
    targetSec.classList.add("active");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  // View-specific trigger hooks
  if (viewName === "progress" && window.progressTracker) {
    window.progressTracker.loadUserProgress();
  } else if (viewName === "admin" && window.loadAdminDashboard) {
    window.loadAdminDashboard();
  } else if (viewName === "textbooks" && window.loadTextbooks) {
    window.loadTextbooks();
  } else if (viewName === "bookmarks" && window.loadBookmarks) {
    window.loadBookmarks();
  } else if (viewName === "teacher" && window.loadClassroomResources) {
    window.loadClassroomResources("teacher");
  } else if (viewName === "quiz" && window.loadClassroomResources) {
    window.loadClassroomResources("quiz");
  } else if ((viewName === "notes" || viewName === "learn") && window.loadClassroomResources) {
    window.loadClassroomResources("note");
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
  setupGradeSelector();
  setupSearchAutocomplete();
  setupNotesGenerator();
  setupTeacherResourceForm();

  // Initialize Sub-Engines
  if (window.doubtSolver) await window.doubtSolver.init();
  if (window.quizEngine) await window.quizEngine.init();
  if (window.progressTracker) await window.progressTracker.init();
  await loadClassroomSubjects();
  await window.loadClassroomResources("all");

  // Load Initial Data
  await loadDashboardSubjects();
  await loadTopicLearningSidebar();
  if (window.appState.currentTopicSlug) {
    await loadTopicContent(window.appState.currentTopicSlug);
  }

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
// THEME CONTROLLER
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

function setupGradeSelector() {
  const select = document.getElementById("dash-grade-select");
  const nameEl = document.getElementById("dash-user-name");
  const badge = document.getElementById("session-user-badge");

  if (nameEl) nameEl.textContent = window.appState.currentUser.full_name;
  if (badge) badge.textContent = `👤 ${window.appState.currentUser.full_name}`;

  if (window.appState.currentUser.role !== "admin") return;
  if (!select) return;
  select.value = window.appState.currentGrade;

  select.addEventListener("change", async (e) => {
    window.appState.currentGrade = e.target.value;
    window.appState.currentUser.grade = `Class ${e.target.value}`;
    await loadDashboardSubjects();
    await loadTopicLearningSidebar();
    if (window.appState.currentTopicSlug) {
      await loadTopicContent(window.appState.currentTopicSlug);
    }
    await loadNotesTopics(window.appState.currentTopicSlug);
    if (window.quizEngine) await window.quizEngine.loadQuizTopics();
    if (window.progressTracker) await window.progressTracker.loadUserProgress();
    window.navigateTo("learn");
  });
}

function escapeResourceHtml(value) {
  return String(value || "").replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[char]);
}

function setupTeacherResourceForm() {
  const form = document.getElementById("teacher-resource-form");
  if (!form) return;
  const typeSelect = document.getElementById("teacher-resource-type");
  const fileInput = document.getElementById("teacher-resource-file");
  const fileField = document.getElementById("teacher-resource-file-field");
  const contentField = document.getElementById("teacher-resource-content-field");
  const help = document.getElementById("teacher-upload-help");
  const status = document.getElementById("teacher-upload-status");

  const updateUploadFields = () => {
    const isNote = typeSelect.value === "note";
    contentField.hidden = !isNote;
    fileInput.accept = isNote ? ".pdf,.doc,.docx,.ppt,.pptx" : ".csv,.pdf";
    fileInput.required = !isNote;
    help.textContent = isNote
      ? "Optional: PDF, Word (.doc/.docx), or PowerPoint (.ppt/.pptx). Typed notes can be shared without a file."
      : "CSV headers: qno, question, options, answer. Separate choices with |, use JSON for commas, or use option_a through option_f columns. Or upload a PDF.";
  };
  typeSelect.addEventListener("change", updateUploadFields);
  updateUploadFields();

  form.addEventListener("submit", async event => {
    event.preventDefault();
    status.textContent = "Publishing resource…";
    status.classList.remove("is-error", "is-success");
    try {
      const response = await fetch("/api/classroom-resources", {
        method: "POST",
        body: new FormData(form)
      });
      const data = await response.json();
      if (!response.ok || !data.success) throw new Error(data.error || "Could not publish resource.");
      status.textContent = "Published to the selected class.";
      status.classList.add("is-success");
      form.reset();
      updateUploadFields();
      await window.loadClassroomResources("all");
    } catch (error) {
      status.textContent = error.message || "Could not publish resource. Please try again.";
      status.classList.add("is-error");
    }
  });
}

async function loadClassroomSubjects() {
  const subjectSelect = document.getElementById("teacher-resource-subject");
  if (!subjectSelect) return;
  try {
    const response = await fetch("/api/subjects");
    const data = await response.json();
    if (!response.ok || !data.success) throw new Error(data.error || "Could not load subjects.");
    subjectSelect.innerHTML = `<option value="" selected disabled>Choose a subject</option>` + data.subjects.map(subject =>
      `<option value="${Number(subject.id)}">${escapeResourceHtml(subject.name)}</option>`
    ).join("");
  } catch (error) {
    subjectSelect.innerHTML = `<option value="">Subjects could not be loaded</option>`;
    console.error("Classroom subjects load error:", error);
  }
}

window.loadClassroomResources = async function(filter = "all") {
  try {
    const response = await fetch("/api/classroom-resources");
    const data = await response.json();
    if (!response.ok || !data.success) throw new Error(data.error || "Could not load classroom resources.");
    const resources = data.resources;
    const containers = [];
    if (filter === "all" || filter === "teacher") containers.push(["teacher-resources", null]);
    if (filter === "all" || filter === "quiz") containers.push(["assigned-quizzes", "quiz"]);
    if (filter === "all" || filter === "note") {
      containers.push(["classroom-notes", "note"], ["learn-classroom-notes", "note"]);
    }
    containers.forEach(([containerId, type]) => {
      const container = document.getElementById(containerId);
      if (!container) return;
      const visibleResources = resources.filter(resource => !type || resource.resource_type === type);
      if (!visibleResources.length) {
        container.innerHTML = `<p class="resource-empty">${containerId === "teacher-resources" ? "You have not shared any resources yet." : "No class resources have been shared yet."}</p>`;
        return;
      }
      container.innerHTML = visibleResources.map(resource => {
        const isQuiz = resource.resource_type === "quiz";
        const details = `${escapeResourceHtml(resource.subject_name)} · ${escapeResourceHtml(resource.grade)} · ${escapeResourceHtml(resource.teacher_name)}`;
        let action = "";
        if (window.appState.currentUser.role === "student" && isQuiz && resource.has_questions) {
          action = `<button class="btn-primary" onclick="window.openClassroomQuiz(${Number(resource.id)})">Take quiz</button>`;
        } else if (resource.download_url) {
          action = `<a class="btn-secondary" href="${escapeResourceHtml(resource.download_url)}" target="_blank" rel="noopener">Download ${isQuiz ? "quiz" : "notes"}</a>`;
        }
        const typedNote = !isQuiz && resource.content
          ? `<p class="resource-note-content">${escapeResourceHtml(resource.content)}</p>`
          : "";
        const filename = resource.original_filename
          ? `<span class="resource-filename">${escapeResourceHtml(resource.original_filename)}</span>`
          : "";
        return `<article class="resource-card">
          <div class="resource-card-main">
            <span class="resource-kind">${isQuiz ? "🎯 Quiz" : "📝 Notes"}</span>
            <h4>${escapeResourceHtml(resource.title)}</h4>
            <p class="resource-subtitle">${details}</p>${filename}${typedNote}
          </div>
          <div class="resource-card-action">${action}</div>
        </article>`;
      }).join("");
    });
  } catch (error) {
    document.querySelectorAll(".resource-list").forEach(container => {
      container.innerHTML = `<p class="resource-status is-error">${escapeResourceHtml(error.message || "Could not load classroom resources.")}</p>`;
    });
    console.error("Classroom resources load error:", error);
  }
};

window.openClassroomQuiz = async function(resourceId) {
  const runner = document.getElementById("assigned-quiz-runner");
  if (!runner) return;
  runner.innerHTML = `<p class="resource-subtitle">Loading quiz…</p>`;
  try {
    const response = await fetch(`/api/classroom-resources/${resourceId}/questions`);
    const data = await response.json();
    if (!response.ok || !data.success) throw new Error(data.error || "Could not load this quiz.");
    runner.innerHTML = `<form id="assigned-quiz-form" class="assigned-quiz-form">
      <h3>${escapeResourceHtml(data.title)}</h3>
      ${data.questions.map((question, index) => `<fieldset class="assigned-question">
        <legend>${escapeResourceHtml(question.question_number)}. ${escapeResourceHtml(question.question)}</legend>
        ${question.options.map((option, optionIndex) => `<label class="assigned-option">
          <input type="radio" name="question-${index}" value="${optionIndex}" required>
          <span>${escapeResourceHtml(option)}</span>
        </label>`).join("")}
      </fieldset>`).join("")}
      <button class="btn-primary" type="submit">Submit quiz</button>
      <p class="resource-status" id="assigned-quiz-result" role="status"></p>
    </form>`;
    document.getElementById("assigned-quiz-form").addEventListener("submit", async event => {
      event.preventDefault();
      const answers = data.questions.map((_question, index) =>
        Number(new FormData(event.currentTarget).get(`question-${index}`))
      );
      const submit = event.currentTarget.querySelector('button[type="submit"]');
      submit.disabled = true;
      const result = document.getElementById("assigned-quiz-result");
      try {
        const submitResponse = await fetch(`/api/classroom-resources/${resourceId}/submit`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ answers })
        });
        const scoreData = await submitResponse.json();
        if (!submitResponse.ok || !scoreData.success) throw new Error(scoreData.error || "Could not submit quiz.");
        result.textContent = `You scored ${scoreData.score} out of ${scoreData.total_questions}.`;
        result.classList.add("is-success");
      } catch (error) {
        result.textContent = error.message || "Could not submit quiz.";
        result.classList.add("is-error");
        submit.disabled = false;
      }
    });
    runner.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    runner.innerHTML = `<p class="resource-status is-error">${escapeResourceHtml(error.message || "Could not load this quiz.")}</p>`;
  }
};

// ==========================================
// GLOBAL SEARCH & AUTOCOMPLETE
// ==========================================
async function setupSearchAutocomplete() {
  const searchInput = document.getElementById("global-search-input");
  const searchBtn = document.getElementById("global-search-btn");
  const suggestionsBox = document.getElementById("search-autocomplete-box");

  if (!searchInput) return;

  try {
    const res = await fetch(`/api/topics?grade=${window.appState.currentGrade}`);
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
    const res = await fetch(`/api/subjects?grade=${window.appState.currentGrade}`);
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

    // Load featured textbooks row on dashboard
    await loadDashboardTextbooks();
  } catch (err) {
    console.error("Error loading subjects:", err);
  }
}

window.filterBySubject = async function(subjectId) {
  window.navigateTo("learn");
  await loadTopicLearningSidebar(subjectId);
  if (window.appState.currentTopicSlug) {
    await loadTopicContent(window.appState.currentTopicSlug);
  }
};

// ==========================================
// TOPIC LEARNING VIEW
// ==========================================
async function loadTopicLearningSidebar(subjectId = null) {
  const sidebar = document.getElementById("learn-topics-sidebar");
  if (!sidebar) return;

  try {
    const params = new URLSearchParams({ grade: window.appState.currentGrade });
    if (subjectId) params.set("subject_id", subjectId);
    const url = `/api/topics?${params}`;
    const res = await fetch(url);
    const data = await res.json();
    if (!data.success) return;
    window.appState.allTopics = data.topics;

    if (!data.topics.some(t => t.slug === window.appState.currentTopicSlug)) {
      window.appState.currentTopicSlug = data.topics.length ? data.topics[0].slug : null;
    }

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

    // Load official Karnataka textbook reference for this topic
    loadRelatedTextbookReference(topic.slug);

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
      notesBtn.onclick = async () => {
        window.navigateTo("notes");
        await loadNotesTopics(topic.slug);
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
        explanation: text
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
  loadNotesTopics();
}

async function loadNotesTopics(preferredSlug = null) {
  const topicSelect = document.getElementById("notes-topic-select");
  if (!topicSelect) return;

  try {
    const grade = window.appState ? window.appState.currentGrade : "10";
    const res = await fetch(`/api/topics?grade=${grade}`);
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error || "Could not load curriculum topics");
    }

    const currentSlug = preferredSlug
      || (window.appState.currentTopicData && window.appState.currentTopicData.slug)
      || topicSelect.value
      || window.appState.currentTopicSlug;
    topicSelect.innerHTML = data.topics.map(topic => `
      <option value="${topic.slug}">[${topic.subject_name}] ${topic.name}</option>
    `).join("");
    const selectedTopic = data.topics.find(topic => topic.slug === currentSlug) || data.topics[0];
    if (selectedTopic) topicSelect.value = selectedTopic.slug;
  } catch (err) {
    console.error("Notes topic load error:", err);
    topicSelect.innerHTML = `<option value="">Topics could not be loaded</option>`;
  }
}
window.loadNotesTopics = loadNotesTopics;

async function triggerNotesGeneration() {
  const topicSelect = document.getElementById("notes-topic-select");
  const formatSelect = document.getElementById("notes-format-select");
  const outputContainer = document.getElementById("notes-output-area");

  if (!outputContainer) return;
  const slug = topicSelect ? topicSelect.value : "";
  const format = formatSelect ? formatSelect.value : "short_notes";
  const lang = window.appState ? window.appState.currentLanguage : "en";
  if (!slug) {
    outputContainer.innerHTML = `<p style="color:var(--danger);">Choose a topic before generating notes.</p>`;
    return;
  }

  outputContainer.innerHTML = `<div style="text-align:center; padding:3rem;"><div class="chip">Preparing notes for this topic... ⏳</div></div>`;

  try {
    const res = await fetch("/api/generate-notes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic_slug: slug, format_type: format, language: lang })
    });

    const data = await res.json();
    if (!res.ok || !data.success) {
      outputContainer.innerHTML = `<p style="color:var(--danger);">${data.error || "Failed to generate notes. Please retry."}</p>`;
      return;
    }

    if (data.format === "mind_map") {
      renderMindMapSVG(data.mind_map_data, outputContainer);
    } else {
      renderTextNotes(data, outputContainer);
    }
  } catch (err) {
    console.error("Notes generation error:", err);
    outputContainer.innerHTML = `<p style="color:var(--danger);">Could not generate notes. Check your connection and try again.</p>`;
  }
}

function renderTextNotes(data, container) {
  let notesHtml = `
    <div class="glass-panel" style="padding:2rem; position:relative;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem; border-bottom:1px solid var(--border-color); padding-bottom:1rem;">
        <div>
          <span class="chip" style="font-size:0.75rem; margin-bottom:0.4rem;">${data.subject} • ${data.grade_level}</span>
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
  const escapeSvg = value => String(value || "").replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[char]);
  container.innerHTML = `
    <div class="glass-panel" style="padding:1.5rem;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
        <h3 style="font-size:1.4rem;">🧠 Interactive Concept Tree: ${escapeSvg(mindMapData.name)}</h3>
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
            ${escapeSvg(mindMapData.name)}
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
                ${escapeSvg(branch.name)}
              </text>

              <!-- Leaf Children -->
              ${branch.children ? branch.children.map((child, cIdx) => {
                const cY = bY - 18 + cIdx * 24;
                const cX = 680;
                return `
                  <line x1="${bX + 110}" y1="${bY}" x2="${cX}" y2="${cY}" stroke="#10b981" stroke-width="1.5" stroke-dasharray="3,3" opacity="0.6"/>
                  <rect x="${cX}" y="${cY - 12}" width="145" height="24" rx="6" fill="rgba(16, 185, 129, 0.15)" stroke="#10b981" stroke-width="1"/>
                  <text x="${cX + 72}" y="${cY + 4}" fill="#a7f3d0" font-family="Plus Jakarta Sans" font-size="10.5" font-weight="600" text-anchor="middle">
                    ${escapeSvg(child.name)}
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

// ==========================================
// 13. OFFICIAL TEXTBOOKS LIBRARY (SECTION 5 & 21)
// ==========================================
window.textbookFilters = {
  class_num: "all",
  medium: "All",
  subject: "All",
  search: ""
};

window.loadTextbooks = async function() {
  setupTextbookControls();
  await window.fetchAndRenderTextbooks();
};

function setupTextbookControls() {
  const searchIn = document.getElementById("textbooks-search-input");
  const medSelect = document.getElementById("textbooks-medium-select");
  const subSelect = document.getElementById("textbooks-subject-select");
  const classTabs = document.querySelectorAll("#textbooks-class-tabs .format-ribbon-btn");

  if (searchIn && !searchIn.dataset.hooked) {
    searchIn.dataset.hooked = "true";
    let timer = null;
    searchIn.addEventListener("input", () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        window.textbookFilters.search = searchIn.value.trim();
        window.fetchAndRenderTextbooks();
      }, 300);
    });
  }

  if (medSelect && !medSelect.dataset.hooked) {
    medSelect.dataset.hooked = "true";
    medSelect.addEventListener("change", () => {
      window.textbookFilters.medium = medSelect.value;
      window.fetchAndRenderTextbooks();
    });
  }

  if (subSelect && !subSelect.dataset.hooked) {
    subSelect.dataset.hooked = "true";
    subSelect.addEventListener("change", () => {
      window.textbookFilters.subject = subSelect.value;
      window.fetchAndRenderTextbooks();
    });
  }

  classTabs.forEach(tab => {
    if (!tab.dataset.hooked) {
      tab.dataset.hooked = "true";
      tab.addEventListener("click", () => {
        classTabs.forEach(t => t.classList.remove("active"));
        tab.classList.add("active");
        window.textbookFilters.class_num = tab.dataset.class;
        window.fetchAndRenderTextbooks();
      });
    }
  });
}

window.fetchAndRenderTextbooks = async function() {
  const grid = document.getElementById("textbooks-grid");
  const summaryChip = document.getElementById("textbooks-summary-chip");
  if (!grid) return;

  grid.innerHTML = `<div style="grid-column:1/-1; text-align:center; padding:3rem;"><div class="chip">Loading official Karnataka textbooks from disk... ⏳</div></div>`;

  try {
    let url = "/api/textbooks?";
    if (window.textbookFilters.class_num !== "all") {
      url += `class=${window.textbookFilters.class_num}&`;
    }
    if (window.textbookFilters.medium !== "All") {
      url += `medium=${encodeURIComponent(window.textbookFilters.medium)}&`;
    }
    if (window.textbookFilters.subject !== "All") {
      url += `subject=${encodeURIComponent(window.textbookFilters.subject)}&`;
    }
    if (window.textbookFilters.search) {
      url += `search=${encodeURIComponent(window.textbookFilters.search)}&`;
    }

    const res = await fetch(url);
    const data = await res.json();
    if (!data.success) return;

    if (summaryChip) {
      summaryChip.textContent = `Showing: ${data.total} Books (${data.total_size_mb} MB on local disk)`;
    }

    if (data.textbooks.length === 0) {
      grid.innerHTML = `
        <div style="grid-column:1/-1; text-align:center; padding:3.5rem;" class="glass-panel">
          <div style="font-size:3rem; margin-bottom:1rem;">🔍</div>
          <h3>No matching textbooks found</h3>
          <p style="color:var(--text-muted); font-size:0.95rem;">Try adjusting the subject, medium, or search query filters.</p>
        </div>
      `;
      return;
    }

    const subjectIcons = {
      "Maths": "📐",
      "Science": "🔬",
      "English": "📖",
      "Kannada": "📝",
      "Hindi": "✍️"
    };

    const mediumBadges = {
      "english-medium": { flag: "🇬🇧", label: "English Medium", color: "#6366f1" },
      "kannada-medium": { flag: "🇮🇳", label: "ಕನ್ನಡ ಮಾಧ್ಯಮ", color: "#10b981" },
      "hindi-medium": { flag: "🇮🇳", label: "हिन्दी माध्यम", color: "#ec4899" }
    };

    grid.innerHTML = data.textbooks.map(b => {
      const sIcon = subjectIcons[b.subject] || "📚";
      const med = mediumBadges[b.medium] || { flag: "🌐", label: b.medium, color: "#6366f1" };
      const safeTitle = b.title.replace(/'/g, "\\'");

      return `
        <div class="textbook-card">
          <div>
            <div class="textbook-badges-row">
              <span class="chip" style="font-size:0.75rem; border-color:${med.color}; color:${med.color};">
                ${med.flag} ${med.label}
              </span>
              <span class="chip" style="font-size:0.75rem; border-color:rgba(255,255,255,0.2);">
                Class ${b.class_num}
              </span>
              <span class="chip" style="font-size:0.75rem; border-color:rgba(255,255,255,0.2);">
                ${sIcon} ${b.subject}
              </span>
            </div>

            <div class="textbook-title" title="${b.title}">${b.title}</div>
          </div>

          <div>
            <div class="textbook-meta">
              <span>💾 Size: <strong>${b.file_size_mb} MB</strong></span>
              <span style="color:#34d399;">✓ 100% Offline Ready</span>
            </div>

            <div class="textbook-actions">
              <button class="btn-primary" style="font-size:0.85rem; padding:0.55rem 0.8rem;" 
                      onclick="window.openTextbookReader(${b.id}, '${safeTitle}', '${b.read_url}', '${b.download_url}')">
                📖 Read Online
              </button>
              <a href="${b.download_url}" class="btn-secondary" style="font-size:0.85rem; padding:0.55rem 0.8rem; text-align:center; text-decoration:none;" download>
                ⬇️ Download PDF
              </a>
            </div>
            
            <div style="margin-top:0.65rem; text-align:center;">
              <button class="chip" style="cursor:pointer; font-size:0.75rem; width:100%; justify-content:center;" onclick="window.toggleBookmark('textbook', '${b.id}', '${safeTitle}')">
                ⭐ Pin to My Bookmarks
              </button>
            </div>
          </div>
        </div>
      `;
    }).join("");
  } catch (err) {
    console.error("Error fetching textbooks:", err);
    grid.innerHTML = `<p style="color:var(--danger); grid-column:1/-1;">Failed to load textbooks. Please verify server connection.</p>`;
  }
};

window.openTextbookReader = function(bookId, title, readUrl, downloadUrl) {
  const modal = document.getElementById("textbook-modal");
  const titleEl = document.getElementById("textbook-modal-title");
  const subEl = document.getElementById("textbook-modal-subtitle");
  const iframe = document.getElementById("textbook-modal-iframe");
  const dlBtn = document.getElementById("textbook-modal-download-btn");
  const tabBtn = document.getElementById("textbook-modal-tab-btn");

  if (!modal || !iframe) return;

  if (titleEl) titleEl.textContent = title;
  if (subEl) subEl.textContent = "Official Karnataka DSERT / KTBS Prescribed Textbook";
  if (dlBtn) dlBtn.href = downloadUrl;
  if (tabBtn) tabBtn.href = readUrl;

  iframe.src = readUrl;
  modal.style.display = "flex";
  document.body.style.overflow = "hidden";
};

window.closeTextbookReader = function() {
  const modal = document.getElementById("textbook-modal");
  const iframe = document.getElementById("textbook-modal-iframe");
  if (modal) modal.style.display = "none";
  if (iframe) iframe.src = "about:blank";
  document.body.style.overflow = "auto";
};

// Official Textbook Reference on Topic Learning Page
async function loadRelatedTextbookReference(slug) {
  const container = document.getElementById("topic-textbook-ref-box");
  if (!container) return;

  try {
    const res = await fetch(`/api/textbooks/related/${slug}?class=${window.appState.currentGrade}`);
    const data = await res.json();
    if (data.success && data.related_books && data.related_books.length > 0) {
      const b = data.related_books[0];
      const safeTitle = b.title.replace(/'/g, "\\'");
      container.style.display = "block";
      container.innerHTML = `
        <div style="background:linear-gradient(135deg, rgba(99,102,241,0.08), rgba(15,23,42,0.7)); border:1px solid rgba(99,102,241,0.3); border-radius:var(--radius-md); padding:1rem 1.25rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.75rem;">
          <div style="display:flex; align-items:center; gap:0.85rem;">
            <div style="font-size:2rem; background:rgba(99,102,241,0.15); width:48px; height:48px; border-radius:10px; display:flex; align-items:center; justify-content:center;">📖</div>
            <div>
              <div style="font-size:0.75rem; text-transform:uppercase; color:#a5b4fc; font-weight:700; letter-spacing:0.05em;">Prescribed Karnataka State Board Textbook</div>
              <div style="font-size:1.02rem; font-weight:700; color:var(--text-primary);">${b.title}</div>
              <div style="font-size:0.8rem; color:var(--text-muted);">${b.medium.replace("-", " ")} • ${b.file_size_mb} MB • 100% Offline Disk Hosted</div>
            </div>
          </div>
          <div style="display:flex; gap:0.6rem; align-items:center;">
            <button class="btn-primary" style="font-size:0.82rem; padding:0.45rem 0.9rem;" onclick="window.openTextbookReader(${b.id}, '${safeTitle}', '${b.read_url}', '${b.download_url}')">
              📖 Open in Reader
            </button>
            <a href="${b.download_url}" class="btn-secondary" style="font-size:0.82rem; padding:0.45rem 0.9rem; text-decoration:none;" download>
              ⬇️ Download PDF
            </a>
          </div>
        </div>
      `;
    } else {
      container.style.display = "none";
    }
  } catch (e) {
    container.style.display = "none";
  }
}

// Prescribed Textbooks Row on Student Dashboard
async function loadDashboardTextbooks() {
  const container = document.getElementById("dash-textbooks-row");
  if (!container) return;

  try {
    const res = await fetch(`/api/textbooks?class=${window.appState.currentGrade}`);
    const data = await res.json();
    if (!data.success || !data.textbooks) return;

    // Show 4 representative core textbooks (Maths, Science, English, Kannada)
    const featured = data.textbooks.slice(0, 4);
    container.innerHTML = featured.map(b => {
      const safeTitle = b.title.replace(/'/g, "\\'");
      return `
        <div class="textbook-card" style="padding:1.25rem;">
          <div>
            <div class="textbook-badges-row">
              <span class="chip" style="font-size:0.72rem; border-color:var(--primary); color:#a5b4fc;">Class ${b.class_num}</span>
              <span class="chip" style="font-size:0.72rem;">${b.subject}</span>
            </div>
            <div class="textbook-title" style="font-size:0.95rem; margin-bottom:0.6rem;">${b.title}</div>
          </div>
          <div>
            <div class="textbook-meta" style="padding-top:0.6rem; margin-bottom:0.75rem;">
              <span>💾 ${b.file_size_mb} MB</span>
              <span style="color:#34d399;">✓ Offline</span>
            </div>
            <div class="textbook-actions">
              <button class="btn-primary" style="font-size:0.8rem; padding:0.4rem 0.6rem;" 
                      onclick="window.openTextbookReader(${b.id}, '${safeTitle}', '${b.read_url}', '${b.download_url}')">
                📖 Read
              </button>
              <a href="${b.download_url}" class="btn-secondary" style="font-size:0.8rem; padding:0.4rem 0.6rem; text-align:center; text-decoration:none;" download>
                ⬇️ PDF
              </a>
            </div>
          </div>
        </div>
      `;
    }).join("");
  } catch (e) {
    console.error("Dashboard textbooks load error:", e);
  }
}

// ==========================================
// 15. BOOKMARKS & SAVED MATERIALS (SECTION 19)
// ==========================================
window.loadBookmarks = async function() {
  const container = document.getElementById("bookmarks-container");
  if (!container) return;

  container.innerHTML = `<div class="chip">Loading saved bookmarks... ⏳</div>`;

  try {
    const res = await fetch("/api/bookmarks");
    const data = await res.json();
    if (!data.success) return;

    if (data.bookmarks.length === 0) {
      container.innerHTML = `
        <div style="text-align:center; padding:3rem;">
          <div style="font-size:3rem; margin-bottom:1rem;">⭐</div>
          <h3>No saved bookmarks yet</h3>
          <p style="color:var(--text-muted); font-size:0.95rem;">
            Click the "⭐ Bookmark" button on any textbook, topic note, or formula sheet to save it here for fast retrieval.
          </p>
        </div>
      `;
      return;
    }

    const typeIcons = {
      "topic": "📖",
      "textbook": "📚",
      "formula": "📐",
      "flashcard": "🔄"
    };

    container.innerHTML = `
      <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(320px, 1fr)); gap:1.25rem;">
        ${data.bookmarks.map(b => `
          <div class="glass-panel" style="padding:1.25rem; display:flex; flex-direction:column; justify-content:space-between;">
            <div>
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                <span class="chip" style="font-size:0.75rem; text-transform:uppercase;">
                  ${typeIcons[b.item_type] || "📌"} ${b.item_type}
                </span>
                <span style="font-size:0.75rem; color:var(--text-muted);">${b.created_at ? b.created_at.split(" ")[0] : "Saved"}</span>
              </div>
              <h4 style="font-size:1.05rem; line-height:1.5; margin-bottom:1rem;">${b.title}</h4>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--border-color); padding-top:0.75rem;">
              <button class="btn-primary" style="font-size:0.8rem; padding:0.4rem 0.85rem;" onclick="window.navigateTo('${b.item_type === "textbook" ? "textbooks" : "learn"}')">
                Open Resource →
              </button>
              <button class="btn-secondary" style="font-size:0.8rem; padding:0.4rem 0.65rem;" onclick="window.toggleBookmark('${b.item_type}', '${b.item_id}', '${b.title.replace(/'/g, "\\'")}')">
                🗑️ Remove
              </button>
            </div>
          </div>
        `).join("")}
      </div>
    `;
  } catch (e) {
    container.innerHTML = `<p style="color:var(--danger);">Error loading bookmarks.</p>`;
  }
};

window.toggleBookmark = async function(itemType, itemId, title) {
  try {
    const res = await fetch("/api/bookmarks/toggle", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        item_type: itemType,
        item_id: String(itemId),
        title: title
      })
    });
    const data = await res.json();
    if (data.success) {
      if (data.bookmarked) {
        alert(`⭐ Added "${title}" to your saved Bookmarks!`);
      } else {
        alert(`Removed "${title}" from Bookmarks.`);
      }
      if (document.getElementById("view-bookmarks") && document.getElementById("view-bookmarks").classList.contains("active")) {
        window.loadBookmarks();
      }
    }
  } catch (e) {
    console.error("Bookmark toggle error:", e);
  }
};
