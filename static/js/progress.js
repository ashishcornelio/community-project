/**
 * LearnSphere AI - School Progress, Study Plan & Classroom Analytics
 */

class ProgressTracker {
  constructor() {
  }

  async init() {
    await this.loadUserProgress();
    await this.loadStudyPlan();
    const role = window.appState && window.appState.currentUser.role;
    if (role === "teacher" || role === "admin") {
      await this.loadTeacherAnalytics();
    }
  }

  // ==========================================
  // 1. PROGRESS TRACKING & LEARNING GAP DETECTION
  // ==========================================
  async loadUserProgress() {
    const grade = window.appState ? window.appState.currentGrade : "10";
    try {
      const res = await fetch(`/api/progress?grade=${grade}`);
      const data = await res.json();
      if (!data.success) return;

      // Update Circle Gauge
      const scoreValEl = document.getElementById("circle-score-val");
      const circleSvgFill = document.getElementById("circle-svg-fill");
      if (scoreValEl) scoreValEl.textContent = `${Math.round(data.overall_mastery)}%`;
      const dashboardMastery = document.getElementById("metric-overall-mastery");
      if (dashboardMastery) dashboardMastery.textContent = `${Math.round(data.overall_mastery)}%`;

      if (circleSvgFill) {
        const circumference = 2 * Math.PI * 70; // r=70
        const offset = circumference - (data.overall_mastery / 100) * circumference;
        circleSvgFill.style.strokeDasharray = `${circumference}`;
        circleSvgFill.style.strokeDashoffset = `${offset}`;
      }

      // Update Breakdown Counts
      const compEl = document.getElementById("stat-completed-count");
      const progEl = document.getElementById("stat-in-progress-count");
      const gapsEl = document.getElementById("stat-critical-count");
      const unEl = document.getElementById("stat-not-started-count");

      if (compEl) compEl.textContent = data.completed;
      if (progEl) progEl.textContent = data.in_progress;
      if (gapsEl) gapsEl.textContent = data.critical_gaps;
      if (unEl) unEl.textContent = data.not_started;
      const dashboardCompleted = document.getElementById("metric-completed-count");
      const dashboardGaps = document.getElementById("metric-critical-count");
      if (dashboardCompleted) dashboardCompleted.textContent = data.completed;
      if (dashboardGaps) dashboardGaps.textContent = data.critical_gaps;

      // Update Subject Progress Bars
      const subjectBarsContainer = document.getElementById("subject-progress-bars");
      if (subjectBarsContainer && data.subject_breakdown) {
        subjectBarsContainer.innerHTML = data.subject_breakdown.map(sb => `
          <div style="margin-bottom: 1.1rem;">
            <div style="display:flex; justify-content:space-between; font-size:0.9rem; font-weight:600; margin-bottom:0.35rem;">
              <span>${sb.subject}</span>
              <span style="color:${sb.color}; font-family:var(--font-mono);">${sb.average}%</span>
            </div>
            <div class="subject-progress-bar-bg">
              <div class="subject-progress-bar-fill" style="width:${sb.average}%; background:${sb.color};"></div>
            </div>
          </div>
        `).join("");
      }

      // Update Gap Table
      const gapTableBody = document.getElementById("gap-table-body");
      if (gapTableBody && data.topics_gaps) {
        gapTableBody.innerHTML = data.topics_gaps.map(g => {
          let badgeText = "Mastered";
          if (g.status === "critical_gap") badgeText = "⚠️ Critical Gap";
          else if (g.status === "needs_revision") badgeText = "🔄 Needs Revision";
          else if (g.status === "in_progress") badgeText = "⏳ In Progress";
          else if (g.status === "not_started") badgeText = "⚪ Not Started";

          return `
            <tr>
              <td>
                <strong style="color:var(--text-primary); font-size:0.95rem;">${g.topic_name}</strong>
                <div style="font-size:0.75rem; color:${g.subject_color};">${g.subject_name}</div>
              </td>
              <td>
                <span class="status-badge ${g.status}">${badgeText}</span>
              </td>
              <td style="font-family:var(--font-mono); font-weight:700;">
                ${g.score}% <span style="font-size:0.75rem; color:var(--text-muted);">(${g.attempts} tests)</span>
              </td>
              <td style="font-size:0.85rem; color:var(--text-secondary); max-width:320px;">
                ${g.recommendation}
              </td>
              <td>
                <button class="btn-primary" style="padding:0.4rem 0.8rem; font-size:0.82rem;" 
                        onclick="window.startRevisionForTopic(${g.topic_id})">
                  Start Revision
                </button>
              </td>
            </tr>
          `;
        }).join("");
      }

      // Update Prerequisite Gap Map
      const prereqContainer = document.getElementById("prereq-map-container");
      if (prereqContainer) {
        try {
          const pres = await fetch("/api/prerequisites/1");
          const pdata = await pres.json();
          if (pdata.success && pdata.prerequisites) {
            prereqContainer.innerHTML = pdata.prerequisites.map(p => `
              <div class="prereq-tree-item">
                <div>
                  <strong style="color:var(--text-primary); font-size:0.92rem;">${p.prerequisite_name}</strong>
                  <p style="font-size:0.8rem; color:var(--text-secondary); margin-top:0.2rem;">${p.recommendation}</p>
                </div>
                <div>
                  <span class="status-badge ${p.mastery_status === 'demonstrated' ? 'mastered' : 'needs_revision'}">
                    ${p.mastery_status === 'demonstrated' ? '✓ Mastered' : '⏳ Needs Practice'}
                  </span>
                </div>
              </div>
            `).join("");
          }
        } catch (e) {
          console.error("Prereq load error:", e);
        }
      }

      // Update Dashboard Alert if critical gaps exist
      const gapAlertCard = document.getElementById("dash-gap-alert");
      if (gapAlertCard) {
        if (data.critical_gaps > 0) {
          gapAlertCard.style.display = "flex";
          const criticalGap = data.topics_gaps.find(g => g.status === "critical_gap");
          const alertTitle = document.getElementById("dash-gap-alert-title");
          if (alertTitle && criticalGap) {
            alertTitle.textContent = `Learning Gap Detected: ${criticalGap.topic_name} (${criticalGap.score}%)`;
          }
          const alertMsg = document.getElementById("dash-gap-alert-msg");
          if (alertMsg) {
            alertMsg.innerHTML = `<strong>Attention Required:</strong> ${data.critical_gaps} learning gap(s) detected. AI has recommended targeted revision in your Study Plan.`;
          }
        } else {
          gapAlertCard.style.display = "none";
        }
      }
    } catch (err) {
      console.error("Error loading progress:", err);
    }

  }

  // ==========================================
  // 2. PERSONALIZED STUDY PLAN
  // ==========================================
  async loadStudyPlan() {
    try {
      const res = await fetch("/api/study-plan");
      const data = await res.json();
      if (!data.success) return;

      const container = document.getElementById("study-tasks-container");
      const taskCount = document.getElementById("metric-task-count");
      if (taskCount) taskCount.textContent = data.tasks.length;
      if (!container) return;

      if (data.tasks.length === 0) {
        container.innerHTML = `<p style="color:var(--text-secondary); padding:2rem; text-align:center;">No scheduled tasks for this period.</p>`;
        return;
      }

      container.innerHTML = data.tasks.map(t => {
        let typeIcon = "📖";
        if (t.task_type === "quiz") typeIcon = "🎯";
        else if (t.task_type === "video") typeIcon = "🎥";
        else if (t.task_type === "notes") typeIcon = "📝";

        return `
          <div class="study-task-item ${t.is_completed ? "completed" : ""}" id="task-${t.id}">
            <div class="task-left">
              <input type="checkbox" class="task-checkbox" ${t.is_completed ? "checked" : ""} 
                     onchange="window.progressTracker.toggleTask(${t.id})">
              <div>
                <div class="task-title" style="font-weight:700; font-size:0.95rem;">
                  ${typeIcon} ${t.title}
                </div>
                <div style="font-size:0.8rem; color:var(--text-muted); display:flex; gap:0.75rem; margin-top:0.25rem;">
                  <span style="color:${t.subject_color}; font-weight:600;">${t.subject_name}</span>
                  <span>📅 ${t.scheduled_day}</span>
                  <span>⏰ ${t.time_slot}</span>
                </div>
              </div>
            </div>
            <div>
              <span class="chip" style="font-size:0.78rem;">${t.task_type.toUpperCase()}</span>
            </div>
          </div>
        `;
      }).join("");
    } catch (err) {
      console.error("Error loading study plan:", err);
    }
  }

  async toggleTask(taskId) {
    try {
      const res = await fetch("/api/study-tasks/toggle", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task_id: taskId })
      });
      const data = await res.json();
      if (data.success) {
        const itemEl = document.getElementById(`task-${taskId}`);
        if (itemEl) {
          if (data.is_completed) itemEl.classList.add("completed");
          else itemEl.classList.remove("completed");
        }
      }
    } catch (err) {
      console.error("Error toggling task:", err);
    }
  }

  // ==========================================
  // 3. SCHOOL CLASSROOM ANALYTICS
  // ==========================================
  async loadTeacherAnalytics() {
    try {
      const res = await fetch("/api/teacher-analytics");
      const data = await res.json();
      if (!data.success) return;

      const statsContainer = document.getElementById("teacher-topic-stats");
      if (statsContainer && data.topic_stats) {
        statsContainer.innerHTML = data.topic_stats.map(ts => {
          const avg = ts.class_average || 0;
          let badgeColor = "#10b981";
          if (avg < 50) badgeColor = "#ef4444";
          else if (avg < 70) badgeColor = "#f59e0b";

          return `
            <tr>
              <td><strong>${ts.topic_name}</strong></td>
              <td>${ts.subject_name}</td>
              <td style="font-family:var(--font-mono); font-weight:700; color:${badgeColor};">${avg}%</td>
              <td>${ts.attempts || 0}</td>
              <td style="font-size:0.85rem;">
                ${avg < 60 ? "<span style='color:#ef4444; font-weight:600;'>Needs classroom revision</span>" : "<span style='color:#10b981;'>Satisfactory</span>"}
              </td>
            </tr>
          `;
        }).join("");
      }

      const recEl = document.getElementById("teacher-rec-box");
      if (recEl && data.recommended_classroom_focus) {
        recEl.textContent = data.recommended_classroom_focus;
      }
    } catch (err) {
      console.error("Error loading teacher analytics:", err);
    }
  }
}

window.progressTracker = new ProgressTracker();
