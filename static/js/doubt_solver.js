/**
 * LearnSphere AI - AI Doubt Solver
 * Interactive conversational assistant with Speech-to-Text and Text-to-Speech support.
 * Designed for Slide 25 Mockup 5.
 */

class DoubtSolver {
  constructor() {
    this.messagesContainer = null;
    this.chatInput = null;
    this.isListening = false;
    this.recognition = null;
    this.initSpeechRecognition();
  }

  async init() {
    this.messagesContainer = document.getElementById("chat-messages");
    this.chatInput = document.getElementById("chat-input");
    this.classSelect = document.getElementById("doubt-class-select");
    this.subjectSelect = document.getElementById("doubt-subject-select");
    const sendBtn = document.getElementById("send-btn");
    const micBtn = document.getElementById("mic-btn");

    if (this.classSelect && window.appState && window.appState.currentUser) {
      const match = String(window.appState.currentUser.grade || "").match(/(8|9|10)/);
      if (match) this.classSelect.value = match[1];
    }
    await this.loadConversationHistory();

    if (sendBtn) {
      sendBtn.addEventListener("click", () => this.handleSend());
    }

    if (this.chatInput) {
      this.chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") this.handleSend();
      });
    }

    if (micBtn) {
      micBtn.addEventListener("click", () => this.toggleVoiceRecognition());
    }
  }

  async loadConversationHistory() {
    if (!this.messagesContainer) return;
    try {
      const response = await fetch("/api/doubt-conversations");
      const data = await response.json();
      if (!response.ok || !data.success) {
        throw new Error(data.error || "Could not load saved conversations");
      }

      this.messagesContainer.innerHTML = "";
      if (!data.conversations.length) {
        this.showEmptyConversationState();
        return;
      }
      data.conversations.forEach(conversation => {
        this.appendMessage(conversation.question, "user");
        this.appendMessage(conversation.answer, "ai", conversation.related_actions, {
          topic: conversation.topic,
          query: conversation.question
        });
      });
      this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    } catch (error) {
      console.error("Conversation history load error:", error);
      this.messagesContainer.innerHTML = `<div class="chat-empty-state">Your saved conversations could not be loaded. Please refresh to try again.</div>`;
    }
  }

  showEmptyConversationState() {
    const emptyState = document.createElement("div");
    emptyState.className = "chat-empty-state";
    emptyState.textContent = "Your saved conversations will appear here.";
    this.messagesContainer.appendChild(emptyState);
  }

  initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = false;
      this.recognition.interimResults = false;
      this.recognition.lang = "en-IN"; // English (India) default

      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (this.chatInput) {
          this.chatInput.value = transcript;
        }
        this.stopVoiceRecognition();
        this.handleSend();
      };

      this.recognition.onerror = () => {
        this.stopVoiceRecognition();
      };

      this.recognition.onend = () => {
        this.stopVoiceRecognition();
      };
    }
  }

  toggleVoiceRecognition() {
    if (!this.recognition) {
      alert("Speech recognition is not supported in this browser. Please use Chrome/Edge or type directly.");
      return;
    }

    if (this.isListening) {
      this.stopVoiceRecognition();
    } else {
      this.startVoiceRecognition();
    }
  }

  startVoiceRecognition() {
    if (!this.recognition) return;
    try {
      this.isListening = true;
      const micBtn = document.getElementById("mic-btn");
      if (micBtn) micBtn.classList.add("listening");
      this.recognition.start();
    } catch (err) {
      console.warn("Speech recognition start error:", err);
    }
  }

  stopVoiceRecognition() {
    this.isListening = false;
    const micBtn = document.getElementById("mic-btn");
    if (micBtn) micBtn.classList.remove("listening");
    if (this.recognition) {
      try { this.recognition.stop(); } catch(e) {}
    }
  }

  async handleSend() {
    if (!this.chatInput) return;
    const text = this.chatInput.value.trim();
    if (!text) return;

    // Append user message
    this.appendMessage(text, "user");
    this.chatInput.value = "";

    // Show loading typing indicator
    const typingId = this.showTypingIndicator();

    // Call API
    try {
      const activeLang = window.appState ? window.appState.currentLanguage : "en";
      const grade = this.classSelect ? `Class ${this.classSelect.value}` : null;
      const subject = this.subjectSelect ? this.subjectSelect.value : "Auto";
      const response = await fetch("/api/doubt-solver", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: text,
          subject: subject,
          language: activeLang,
          grade: grade
        })
      });

      const data = await response.json();
      this.removeTypingIndicator(typingId);

      if (data.success) {
        this.appendMessage(data.response, "ai", data.related_actions, {
          topic: data.topic,
          query: text
        });
      } else {
        this.appendMessage("I couldn't process that question right now. Please try asking again!", "ai");
      }
    } catch (err) {
      this.removeTypingIndicator(typingId);
      this.appendMessage("Network connection interrupted. Please try again.", "ai");
    }
  }

  appendMessage(content, sender, actions = [], topicContext = {}) {
    if (!this.messagesContainer) return;
    this.messagesContainer.querySelector(".chat-empty-state")?.remove();

    const bubble = document.createElement("div");
    bubble.className = `chat-bubble ${sender}`;

    // Format content with simple markdown renderer
    const formattedHtml = this.formatMarkdown(content);
    bubble.innerHTML = formattedHtml;

    if (sender === "ai") {
      // Add text-to-speech speaker button
      const speakBtn = document.createElement("button");
      speakBtn.className = "audio-tts-btn";
      speakBtn.style.marginTop = "0.75rem";
      speakBtn.innerHTML = "🔊 Listen to Explanation";
      speakBtn.onclick = () => this.speakText(content);
      bubble.appendChild(speakBtn);

      // Add related action pills if available
      if (actions && actions.length > 0) {
        const actionsDiv = document.createElement("div");
        actionsDiv.style.display = "flex";
        actionsDiv.style.gap = "0.5rem";
        actionsDiv.style.marginTop = "0.75rem";
        actionsDiv.style.flexWrap = "wrap";

        actions.forEach(action => {
          const actBtn = document.createElement("button");
          actBtn.className = "chip";
          actBtn.textContent = `⚡ ${action}`;
          actBtn.onclick = () => this.handleActionClick(action, topicContext);
          actionsDiv.appendChild(actBtn);
        });
        bubble.appendChild(actionsDiv);
      }
    }

    this.messagesContainer.appendChild(bubble);
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
  }

  showTypingIndicator() {
    const id = "typing-" + Date.now();
    const bubble = document.createElement("div");
    bubble.className = "chat-bubble ai";
    bubble.id = id;
    bubble.innerHTML = `<span style="color:var(--text-muted); font-style:italic;">Searching your textbook PDFs for the exact chapter and page...</span>`;
    this.messagesContainer.appendChild(bubble);
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    return id;
  }

  removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  formatMarkdown(text) {
    let html = text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/### (.*?)\n/g, '<h4 style="color:#a5b4fc; margin-bottom:0.4rem;">$1</h4>')
      .replace(
        /\[([^\]]+)\]\((\/[^)\s]+|https?:\/\/[^)\s]+)\)/g,
        '<a href="$2" target="_blank" rel="noopener" style="color:#7dd3fc; text-decoration:underline;">$1</a>'
      )
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n\n/g, '<br><br>')
      .replace(/\n/g, '<br>');
    return html;
  }

  speakText(text) {
    if (!("speechSynthesis" in window)) {
      alert("Text-to-speech not supported in this browser.");
      return;
    }
    window.speechSynthesis.cancel(); // Stop any ongoing speech

    // Clean markdown symbols for clearer speech
    const cleanSpeech = text.replace(/###|\*\*|\*|✓|💡|📌/g, "");
    const utterance = new SpeechSynthesisUtterance(cleanSpeech);

    const lang = window.appState ? window.appState.currentLanguage : "en";
    if (lang === "kn") utterance.lang = "kn-IN";
    else if (lang === "hi") utterance.lang = "hi-IN";
    else utterance.lang = "en-IN";

    utterance.rate = 0.95; // Slightly slower for better high-school comprehension
    window.speechSynthesis.speak(utterance);
  }

  findRelatedTopic(context) {
    const topics = window.appState ? window.appState.allTopics || [] : [];
    const stopWords = new Set(["chapter", "class", "topic", "explain", "about", "what", "which", "from"]);
    const tokens = value => String(value || "").toLowerCase().match(/[a-z0-9]+/g)
      ?.filter(token => token.length > 2 && !stopWords.has(token)) || [];
    const sources = [context.topic, context.query].map(tokens).filter(source => source.length);

    for (const source of sources) {
      let bestTopic = null;
      let bestScore = 0;
      for (const topic of topics) {
        const topicTokens = new Set(tokens(`${topic.name} ${topic.slug} ${topic.summary}`));
        const score = source.filter(token => topicTokens.has(token)).length / source.length;
        if (score > bestScore) {
          bestTopic = topic;
          bestScore = score;
        }
      }
      if (bestScore >= 0.5) return bestTopic;
    }
    return null;
  }

  async handleActionClick(action, topicContext = {}) {
    const topic = this.findRelatedTopic(topicContext);
    if (action.includes("Quiz")) {
      window.navigateTo("quiz");
      if (topic && window.quizEngine) {
        window.quizEngine.currentTopicId = Number(topic.id);
        const select = document.getElementById("quiz-topic-select");
        if (select) select.value = String(topic.id);
        window.quizEngine.startQuizForTopic(topic.id);
      }
    } else if (action.includes("Notes")) {
      window.navigateTo("notes");
      if (topic) {
        if (window.loadNotesTopics) await window.loadNotesTopics(topic.slug);
        const select = document.getElementById("notes-topic-select");
        if (select) select.value = topic.slug;
        const generateButton = document.getElementById("generate-notes-btn");
        if (generateButton) generateButton.click();
      }
    }
  }
}

window.doubtSolver = new DoubtSolver();
