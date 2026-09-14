/**
 * SchemeMitra v2 — Conversational Voice & Text Profile Builder (Fully Localized)
 */

class ProfileBuilderComponent {
  constructor() {
    this.extractedProfile = {};
    this.recognition = null;
    this.isRecording = false;
    this.voiceFinalTranscript = "";
    this.voiceRestartAttempts = 0;
    this.voiceRestartTimer = null;
    this.voiceSilenceTimer = null;
    this.voiceLastSpeechAt = 0;
    this.voiceSilenceMs = 3000;
    this.voiceFatalError = false;
    this.speechSupported = "SpeechRecognition" in window || "webkitSpeechRecognition" in window;
  }

  render() {
    const container = document.getElementById("viewProfile");
    if (!container) return;

    const t = (k) => window.i18n.get(k);

    container.innerHTML = `
      <section class="section-padding" style="padding-top: 1.5rem;">
        <div class="container">
          <div class="section-header" style="margin-bottom: 1.75rem;">
            <h2 class="section-title" data-i18n="nav_set_profile">${t('nav_set_profile')}</h2>
            <p class="section-subtitle" data-i18n="profile_builder_sub">${t('profile_builder_sub')}</p>
          </div>

          <!-- Desktop: 70% Left Form / 30% Right Assistant Split; Mobile: Vertical Stack -->
          <div class="profile-layout-grid">
            
            <!-- LEFT COLUMN: Structured Profile Form (Primary Method) -->
            <div id="leftFormColumn">
              <div id="manualFormContainer"></div>
            </div>

            <!-- RIGHT COLUMN: Voice Assistant Panel -->
            <div id="rightAssistantColumn">
              <div style="background: #ffffff; border: 1.5px solid var(--border-color); border-top: 4px solid var(--primary-saffron); border-radius: 16px; padding: 1.5rem; box-shadow: var(--shadow-sm); position: sticky; top: 90px;">
                
                <h3 style="font-size: 1.15rem; color: var(--primary-navy); margin: 0 0 0.35rem; font-weight: 800;">
                  🤖 Talk to SchemeMitra
                </h3>
                <p style="font-size: 0.875rem; color: var(--text-muted); margin-bottom: 1.25rem; line-height: 1.45;">
                  Tell us about yourself and your business idea in simple natural language or voice.
                </p>

                <div id="voiceAlert" style="display: ${this.speechSupported ? 'none' : 'block'}; background: var(--amber-bg); color: var(--amber); padding: 0.65rem; border-radius: 8px; font-size: 0.85rem; margin-bottom: 1rem;">
                  ⚠️ <span data-i18n="voice_unsupported">${t('voice_unsupported')}</span>
                </div>

                <!-- Voice Input Control -->
                <div style="text-align: center; margin-bottom: 1.25rem;">
                  <button id="btnVoiceMic" class="btn-primary" onclick="profileBuilder.toggleVoice()" style="font-size: 0.95rem; padding: 0.75rem 1.4rem; border-radius: 9999px; width: 100%; justify-content: center; background: #138808;">
                    <span id="micIcon">🎤</span> <span data-i18n="btn_speak_profile">${t('btn_speak_profile')}</span>
                  </button>

                  <div id="voiceStatus" class="voice-status-lbl" style="margin-top: 0.6rem; font-size: 0.825rem; color: var(--text-muted); font-style: italic;" data-i18n="voice_status_default">
                    ${t('voice_status_default')}
                  </div>
                </div>

                <!-- Natural Text Input -->
                <div style="margin-bottom: 1rem;">
                  <label style="display: block; font-weight: 700; font-size: 0.85rem; margin-bottom: 0.35rem; color: var(--primary-navy);" data-i18n="tell_us_label">Or type naturally here...</label>
                  <textarea id="txtMessageInput" rows="4" data-i18n="txt_message_placeholder" placeholder="e.g. I am 24, from Chennai, completed B.Tech Computer Science and want to start an online clothing store." style="width: 100%; padding: 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; outline: none; font-family: inherit; font-size: 0.9rem; margin-bottom: 0.75rem; box-sizing: border-box;"></textarea>
                  <button class="btn-primary" onclick="profileBuilder.processInput()" style="width: 100%; font-size: 0.95rem; background: #FF9933; color: #ffffff;">
                    <span data-i18n="btn_extract_fields">${t('btn_extract_fields')}</span>
                  </button>
                </div>

                <div id="profileClarificationNotice" style="display:none; background:var(--amber-bg); color:var(--amber); border:1px solid #f59e0b33; border-radius:10px; padding:0.75rem; margin-top:0.75rem; font-size:0.85rem; line-height:1.4;"></div>

              </div>
            </div>

          </div>

        </div>
      </section>
    `;

    // Render manual structured form into left container
    window.profileForm.render(
      document.getElementById("manualFormContainer"),
      window.app.userProfile || {},
      (profile) => this.handleProfileConfirmed(profile)
    );
  }

  toggleVoice() {
    if (!this.speechSupported) {
      alert(window.i18n.get('voice_unsupported'));
      return;
    }

    if (this.isRecording) {
      this.stopVoice();
    } else {
      this.startVoice();
    }
  }

  startVoice() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const textArea = document.getElementById("txtMessageInput");
    const statusEl = document.getElementById("voiceStatus");
    const micIcon = document.getElementById("micIcon");

    this.voiceFinalTranscript = (textArea?.value || "").trim();
    this.voiceRestartAttempts = 0;
    this.voiceFatalError = false;
    this.isRecording = true;
    this.voiceLastSpeechAt = Date.now();
    clearTimeout(this.voiceSilenceTimer);

    const scheduleSilenceStop = () => {
      clearTimeout(this.voiceSilenceTimer);
      if (!this.isRecording) return;
      const remaining = Math.max(100, this.voiceSilenceMs - (Date.now() - this.voiceLastSpeechAt));
      this.voiceSilenceTimer = setTimeout(() => {
        if (this.isRecording && (Date.now() - this.voiceLastSpeechAt) >= this.voiceSilenceMs - 50) {
          this.stopVoice(true);
        } else if (this.isRecording) {
          scheduleSilenceStop();
        }
      }, remaining);
    };

    const createRecognition = () => {
      const recognition = new SpeechRecognition();
      recognition.lang = window.i18n.currentLang === "ta" ? "ta-IN" : (window.i18n.currentLang === "hi" ? "hi-IN" : "en-US");
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.maxAlternatives = 3;

      recognition.onstart = () => {
        if (!this.isRecording) return;
        statusEl.textContent = window.i18n.get("voice_status_listening");
        micIcon.textContent = "🔴";
        scheduleSilenceStop();
      };

      recognition.onresult = (e) => {
        let interim = "";
        let receivedFinal = false;
        for (let i = e.resultIndex; i < e.results.length; i += 1) {
          const part = (e.results[i][0]?.transcript || "").trim();
          if (!part) continue;
          if (e.results[i].isFinal) {
            this.voiceFinalTranscript = `${this.voiceFinalTranscript} ${part}`.trim();
            receivedFinal = true;
          } else {
            interim += `${part} `;
          }
        }
        if (receivedFinal || interim.trim()) {
          this.voiceRestartAttempts = 0;
          this.voiceLastSpeechAt = Date.now();
          scheduleSilenceStop();
        }
        if (textArea) textArea.value = `${this.voiceFinalTranscript} ${interim.trim()}`.trim();
      };

      recognition.onerror = (e) => {
        console.error("Speech error:", e);
        const fatalErrors = new Set(["not-allowed", "service-not-allowed", "audio-capture", "network"]);
        if (fatalErrors.has(e.error)) {
          this.voiceFatalError = true;
          this.isRecording = false;
          statusEl.textContent = `Speech recognition error: ${e.error}`;
          micIcon.textContent = "🎤";
        } else if (e.error !== "no-speech" && e.error !== "aborted") {
          statusEl.textContent = `Speech recognition error: ${e.error}`;
        }
      };

      recognition.onend = () => {
        if (textArea) textArea.value = this.voiceFinalTranscript || textArea.value;
        const silentFor = Date.now() - this.voiceLastSpeechAt;
        if (this.isRecording && !this.voiceFatalError && silentFor < this.voiceSilenceMs && this.voiceRestartAttempts < 8) {
          this.voiceRestartAttempts += 1;
          clearTimeout(this.voiceRestartTimer);
          this.voiceRestartTimer = setTimeout(() => {
            if (!this.isRecording) return;
            try {
              this.recognition = createRecognition();
              this.recognition.start();
            } catch (err) {
              console.error("Speech restart error:", err);
              this.stopVoice(false);
            }
          }, 200);
          return;
        }
        if (this.isRecording && silentFor >= this.voiceSilenceMs) {
          this.stopVoice(true);
          return;
        }
        this.isRecording = false;
        clearTimeout(this.voiceSilenceTimer);
        statusEl.textContent = window.i18n.get("voice_status_done");
        micIcon.textContent = "🎤";
      };

      return recognition;
    };

    this.recognition = createRecognition();
    try {
      this.recognition.start();
    } catch (err) {
      console.error("Speech start error:", err);
      this.isRecording = false;
      statusEl.textContent = `Speech recognition error: ${err.message || err}`;
      micIcon.textContent = "🎤";
    }
  }

  stopVoice(stoppedForSilence = false) {
    this.isRecording = false;
    this.voiceFatalError = false;
    clearTimeout(this.voiceRestartTimer);
    clearTimeout(this.voiceSilenceTimer);
    if (this.recognition) {
      try { this.recognition.stop(); } catch (_) { /* already stopped */ }
    }
    const statusEl = document.getElementById("voiceStatus");
    const micIcon = document.getElementById("micIcon");
    if (statusEl) statusEl.textContent = window.i18n.get(stoppedForSilence ? "voice_status_silence" : "voice_status_done");
    if (micIcon) micIcon.textContent = "🎤";
  }

  async processInput() {
    const msg = document.getElementById("txtMessageInput").value;
    if (!msg || !msg.trim()) {
      alert(window.i18n.get("voice_status_default"));
      return;
    }

    try {
      const res = await fetch("/api/profile/parse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: msg,
          existing_profile: window.profileForm.currentProfile || {}
        })
      });

      if (!res.ok) throw new Error("Profile parsing failed");
      const data = await res.json();
      
      console.log('[PROFILE PARSE RAW]', data);
      const parsed = data.profile || {};

      // Track newly detected fields
      const detectedSet = new Set(window.profileForm.currentProfile._detectedFields || []);
      Object.keys(parsed).forEach(k => {
        if (parsed[k] !== null && parsed[k] !== undefined && parsed[k] !== "") {
          detectedSet.add(k);
        }
      });

      // Merge into structured form profile
      window.profileForm.currentProfile = {
        ...window.profileForm.currentProfile,
        ...parsed,
        _detectedFields: detectedSet
      };

      if (parsed.business_stage) {
        window.profileForm.currentProfile.business_type = parsed.business_stage;
        window.profileForm.currentProfile.new_business = (parsed.business_stage === "Idea" || parsed.business_stage === "Startup");
      }

      // Update the structured form on the left in real time!
      const formContainer = document.getElementById("manualFormContainer");
      if (formContainer) {
        window.profileForm.updateForm(formContainer);
      }

      // Update status notice
      const clarification = document.getElementById("profileClarificationNotice");
      if (clarification) {
        const readiness = window.profileForm.calculateReadiness(window.profileForm.currentProfile);
        const needsEducation = parsed.education_field && !parsed.education;
        const t = (k) => window.i18n ? window.i18n.get(k) : k;
        if (needsEducation) {
          noticeText = t('status_please_confirm') + ": " + (window.i18n.currentLang === 'ta' ? "உங்கள் கல்வித் தகுதியை உறுதிப்படுத்தவும் (Graduate, Diploma, 12th Pass)." : "Please confirm your qualification level (e.g. Degree, Diploma, 12th Pass).");
        } else if (!readiness.isComplete) {
          const missingNames = readiness.coreFields.filter(f => !f.valid).map(f => f.label).join(", ");
          noticeText = t('profile_notice_incomplete');
        } else {
          noticeText = t('profile_notice_complete');
        }
        clarification.textContent = noticeText;
        clarification.style.display = "block";
      }
    } catch (err) {
      console.error("Profile parse error:", err);
      alert("Error parsing profile message: " + err.message);
    }
  }

  handleProfileConfirmed(profile) {
    window.app.saveProfileToStorage(profile);
    window.app.showPage("dashboard");
  }
}

window.profileBuilder = new ProfileBuilderComponent();
