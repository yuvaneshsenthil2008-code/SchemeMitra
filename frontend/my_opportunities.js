/**
 * SchemeMitra v2 — My Opportunities Dashboard & Inline Roadmap Component
 * Clean, scheme-centric navigation: Best Matches, More Information Needed, Needs Verification, and Opportunity Roadmap.
 */

class MyOpportunitiesComponent {
  constructor() {
    this.analysisResult = null;
    this.activeTab = "recommended"; // 'recommended', 'potentially', 'verification', 'graph'
    this.selectedOppId = null;
    this.graphSelectionMode = "TOP_3";
    this.graphData = null;
    this.graphZoom = 1.0;
    this.graphPanX = 0;
    this.graphPanY = 0;
    this.selectedRequirementNode = null;
    this.selectedSupportNode = null;
    this.expandedInlineRoadmaps = {};
    this.pathwayCache = {};
    this.goalPathwayData = null;
    this.completedActionsCount = 0;
    this.completedActionsList = [];
    this.userArtifactsCount = 0;
    this.userArtifactsList = [];
    this.userProgressOverlay = this.loadUserProgressOverlay();
  }

  resetLocalState() {
    this.analysisResult = null;
    this.goalPathwayData = null;
    this.completedActionsCount = 0;
    this.completedActionsList = [];
    this.userArtifactsCount = 0;
    this.userArtifactsList = [];
    this.userProgressOverlay = {};
    this.expandedInlineRoadmaps = {};
    this.pathwayCache = {};
  }

  getClientId() {
    let cid = localStorage.getItem("schememitra_client_id");
    if (!cid) {
      if (typeof crypto !== "undefined" && crypto.randomUUID) {
        cid = crypto.randomUUID();
      } else {
        cid = 'client_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
      }
      localStorage.setItem("schememitra_client_id", cid);
    }
    return cid;
  }

  async fetchCompletedActions() {
    const cid = this.getClientId();
    try {
      const res = await fetch(`/api/pathway/goal/completed-actions?client_id=${encodeURIComponent(cid)}`);
      if (res.ok) {
        const data = await res.json();
        this.completedActionsList = data.completed_actions || [];
        this.completedActionsCount = data.count || 0;
      }
    } catch (err) {
      console.error("Failed to fetch completed actions:", err);
    }
  }

  async fetchUserArtifacts() {
    const cid = this.getClientId();
    try {
      const res = await fetch(`/api/pathway/artifacts?client_id=${encodeURIComponent(cid)}`);
      if (res.ok) {
        const data = await res.json();
        this.userArtifactsList = data.artifacts || [];
        this.userArtifactsCount = data.count || 0;
      }
    } catch (err) {
      console.error("Failed to fetch user artifacts:", err);
    }
  }

  async markArtifactAvailable(artifactType, notes = "") {
    const cid = this.getClientId();
    try {
      const res = await fetch("/api/pathway/artifacts/mark-available", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          client_id: cid,
          artifact_type: artifactType,
          notes: notes
        })
      });
      if (res.ok) {
        await this.fetchGoalPathway();
        if (document.getElementById("preparedDocumentsModal")?.classList.contains("active")) {
          this.openPreparedDocumentsModal();
        }
      } else {
        alert("Could not update document availability. Please try again.");
      }
    } catch (err) {
      console.error("Failed to mark artifact available:", err);
      alert("Could not update document availability. Please try again.");
    }
  }

  async removeArtifact(artifactType) {
    const warningMsg = "This document was previously used for completed requirement records.\nChanging availability does not automatically change your confirmed scheme progress.\n\nAre you sure you want to mark this document as Not Available?";
    if (!window.confirm(warningMsg)) {
      return;
    }

    const cid = this.getClientId();
    try {
      const res = await fetch("/api/pathway/artifacts/remove", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          client_id: cid,
          artifact_type: artifactType
        })
      });
      if (res.ok) {
        await this.fetchGoalPathway();
        if (document.getElementById("preparedDocumentsModal")?.classList.contains("active")) {
          this.openPreparedDocumentsModal();
        }
      } else {
        alert("Could not update document availability. Please try again.");
      }
    } catch (err) {
      console.error("Failed to remove artifact:", err);
      alert("Could not update document availability. Please try again.");
    }
  }

  async confirmSchemeRequirementWithArtifact(reqId, schemeName, artifactTitle = "document") {
    if (!reqId || reqId === "undefined" || reqId === "null") {
      console.error("confirmSchemeRequirementWithArtifact received invalid requirement_id:", reqId);
      alert("Could not save your progress. Invalid requirement ID.");
      return;
    }
    const confirmMsg = `Confirm that your existing ${artifactTitle} satisfies this scheme requirement (${schemeName})?\n\nThis records your own progress and is not official government verification.`;
    if (!window.confirm(confirmMsg)) {
      return;
    }
    await this.toggleGoalRequirement(reqId, false, true);
  }

  async openPreparedDocumentsModal() {
    await this.fetchUserArtifacts();
    let modal = document.getElementById("preparedDocumentsModal");
    if (!modal) {
      modal = document.createElement("div");
      modal.id = "preparedDocumentsModal";
      modal.className = "modal-overlay";
      document.body.appendChild(modal);
    }

    const arts = this.userArtifactsList || [];
    const availableTypes = new Set(arts.map(a => a.artifact_type));

    const commonTypes = [
      { type: "DPR", title: "Detailed Project Report (DPR)", btnLabel: "I Have a DPR" },
      { type: "IDENTITY_PROOF", title: "Identity / KYC Proof (Aadhaar, PAN, Voter ID)", btnLabel: "I Have Identity / KYC Proof" },
      { type: "REGISTRATION_CERTIFICATE", title: "Business Registration / Udyam Certificate", btnLabel: "I Have This Registration Certificate" },
      { type: "LAND_OR_LEASE_DOCUMENT", title: "Land Ownership / Lease Agreement", btnLabel: "I Have Land / Lease Documents" },
      { type: "BANK_DOCUMENT", title: "Bank Statement / Financial Records", btnLabel: "I Have the Required Bank Document" }
    ];

    const listHtml = commonTypes.map(item => {
      const isAvail = availableTypes.has(item.type);
      return `
        <div style="background: #ffffff; border: 1px solid var(--border-color); border-left: 4px solid ${isAvail ? '#138808' : '#64748b'}; border-radius: 10px; padding: 0.85rem 1rem; margin-bottom: 0.75rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
          <div>
            <div style="font-size: 0.9rem; font-weight: 700; color: var(--primary-navy);">
              ${isAvail ? '✓' : '○'} ${item.title}
            </div>
            <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 0.15rem;">
              ${isAvail ? 'Available in your prepared documents' : 'Not marked available yet'}
            </div>
          </div>
          <div>
            ${isAvail ? `
              <button class="btn-outline" onclick="myOpportunities.removeArtifact('${item.type}')" style="font-size: 0.78rem; padding: 0.3rem 0.65rem; border-color: #dc2626; color: #dc2626; background: #ffffff;">
                Remove
              </button>
            ` : `
              <button class="btn-primary" onclick="myOpportunities.markArtifactAvailable('${item.type}')" style="font-size: 0.78rem; padding: 0.35rem 0.75rem; background: #2563eb; color: #ffffff; font-weight: 700;">
                ${item.btnLabel}
              </button>
            `}
          </div>
        </div>
      `;
    }).join("");

    modal.innerHTML = `
      <div class="modal-card" style="max-width: 620px; max-height: 85vh; display: flex; flex-direction: column;">
        <button class="close-modal" onclick="document.getElementById('preparedDocumentsModal').classList.remove('active')">&times;</button>
        <div style="font-size: 0.8rem; font-weight: 800; color: #2563eb; text-transform: uppercase; margin-bottom: 0.35rem;">
          REUSABLE ARTIFACTS
        </div>
        <h3 style="font-size: 1.25rem; color: var(--primary-navy); font-weight: 800; margin-bottom: 0.3rem;">
          📄 PREPARED DOCUMENTS (${arts.length})
        </h3>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem; line-height: 1.4;">
          Documents and artifacts you possess. When an artifact is available, you can confirm whether it satisfies specific scheme requirements.
        </p>

        <div style="overflow-y: auto; flex: 1; padding-right: 0.25rem;">
          ${listHtml}
        </div>
      </div>
    `;

    modal.classList.add("active");
  }

  getClientId() {
    let cid = localStorage.getItem("schememitra_client_id");
    if (!cid) {
      if (typeof crypto !== "undefined" && crypto.randomUUID) {
        cid = crypto.randomUUID();
      } else {
        cid = 'client_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
      }
      localStorage.setItem("schememitra_client_id", cid);
    }
    return cid;
  }

  async fetchCompletedActions() {
    const cid = this.getClientId();
    try {
      const res = await fetch(`/api/pathway/goal/completed-actions?client_id=${encodeURIComponent(cid)}`);
      if (res.ok) {
        const data = await res.json();
        this.completedActionsList = data.completed_actions || [];
        this.completedActionsCount = data.count || 0;
      }
    } catch (err) {
      console.error("Failed to fetch completed actions:", err);
    }
  }

  async openCompletedActionsModal() {
    await this.fetchCompletedActions();
    let modal = document.getElementById("completedActionsModal");
    if (!modal) {
      modal = document.createElement("div");
      modal.id = "completedActionsModal";
      modal.className = "modal-overlay";
      document.body.appendChild(modal);
    }

    const items = this.completedActionsList || [];
    let itemsHtml = "";

    if (items.length === 0) {
      itemsHtml = `
        <div style="padding: 2rem 1rem; text-align: center; color: var(--text-muted); font-size: 0.9rem;">
          No actions have been marked completed yet.
        </div>
      `;
    } else {
      itemsHtml = items.map(item => {
        let formattedDate = "";
        if (item.completed_at) {
          try {
            const dt = new Date(item.completed_at);
            formattedDate = dt.toLocaleString('en-GB', {
              day: 'numeric',
              month: 'short',
              year: 'numeric',
              hour: 'numeric',
              minute: '2-digit',
              hour12: true
            });
          } catch(e) {
            formattedDate = item.completed_at;
          }
        }

        return `
          <div style="background: #ffffff; border: 1px solid var(--border-color); border-left: 4px solid #138808; border-radius: 10px; padding: 1rem; margin-bottom: 0.85rem; display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.75rem;">
            <div style="flex: 1; min-width: 240px;">
              <div style="display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.35rem;">
                <span style="font-size: 0.725rem; font-weight: 800; padding: 0.15rem 0.5rem; border-radius: 4px; background: #dcfce7; color: #15803d; border: 1px solid #86efac;">
                  ✓ Completed
                </span>
                <span style="font-size: 0.725rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">
                  ${item.requirement_type || 'REQUIREMENT'}
                </span>
              </div>
              <div style="font-size: 0.95rem; font-weight: 700; color: var(--primary-navy); margin-bottom: 0.3rem;">
                ${item.display_title || item.title}
              </div>
              ${(item.requirement_type === 'ENTITY_REGISTRATION' || item.supporting_text) ? `
                <div style="font-size: 0.78rem; color: #b45309; font-weight: 600; margin-bottom: 0.25rem;">
                  ${item.supporting_text || 'Exact registration type needs confirmation.'}
                </div>
              ` : ''}
              <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.25rem;">
                <strong>Source Scheme:</strong> ${item.source_opportunity_name || item.source_opportunity_id}
              </div>
              ${formattedDate ? `
                <div style="font-size: 0.775rem; color: #64748b;">
                  <strong>Completed:</strong> ${formattedDate}
                </div>
              ` : ''}
            </div>

            <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 0.5rem;">
              <button class="btn-outline" onclick="myOpportunities.toggleGoalRequirement('${item.requirement_id}', true)" style="font-size: 0.8rem; padding: 0.35rem 0.8rem; border-color: #dc2626; color: #dc2626; background: #ffffff;">
                Reopen
              </button>
              ${item.official_source_url ? `
                <a href="${item.official_source_url}" target="_blank" rel="noopener noreferrer" style="font-size: 0.78rem; color: var(--accent-blue); text-decoration: none; font-weight: 600;" title="Official Scheme Source">
                  Official Scheme Source ↗
                </a>
              ` : ''}
            </div>
          </div>
        `;
      }).join("");
    }

    modal.innerHTML = `
      <div class="modal-card" style="max-width: 650px; max-height: 85vh; display: flex; flex-direction: column;">
        <button class="close-modal" onclick="document.getElementById('completedActionsModal').classList.remove('active')">&times;</button>
        <div style="font-size: 0.8rem; font-weight: 800; color: #138808; text-transform: uppercase; margin-bottom: 0.35rem;">
          PATHWAY HISTORY
        </div>
        <h3 style="font-size: 1.25rem; color: var(--primary-navy); font-weight: 800; margin-bottom: 0.3rem;">
          COMPLETED ACTIONS
        </h3>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem; line-height: 1.4;">
          Actions you marked as completed.<br/>
          These are user-confirmed progress records, not official government verification.
        </p>

        <div style="overflow-y: auto; flex: 1; padding-right: 0.25rem;">
          ${itemsHtml}
        </div>
      </div>
    `;

    modal.classList.add("active");
  }

  loadUserProgressOverlay() {
    try {
      const saved = localStorage.getItem("schememitra_user_progress_overlay");
      return saved ? JSON.parse(saved) : { completed_requirements: [] };
    } catch (e) {
      return { completed_requirements: [] };
    }
  }

  saveUserProgressOverlay(overlay) {
    this.userProgressOverlay = overlay || { completed_requirements: [] };
    try {
      localStorage.setItem("schememitra_user_progress_overlay", JSON.stringify(this.userProgressOverlay));
    } catch (e) {
      console.warn("Failed to save progress overlay to localStorage:", e);
    }
  }

  async migrateLegacyProgressIfNeeded() {
    if (localStorage.getItem("schememitra_progress_server_migrated") === "true") {
      return;
    }

    const cid = this.getClientId();
    const legacyReqIds = new Set();

    try {
      const savedOverlayStr = localStorage.getItem("schememitra_user_progress_overlay");
      if (savedOverlayStr) {
        const parsed = JSON.parse(savedOverlayStr);
        const reqs = parsed.completed_requirements || [];
        reqs.forEach(r => {
          const rid = typeof r === "string" ? r : (r && r.requirement_id);
          if (rid) legacyReqIds.add(rid);
        });
      }

      const savedLegacyStr = localStorage.getItem("schememitra_goal_pathway_progress");
      if (savedLegacyStr) {
        const parsed = JSON.parse(savedLegacyStr);
        const reqs = Array.isArray(parsed) ? parsed : (parsed.completed_requirements || []);
        reqs.forEach(r => {
          const rid = typeof r === "string" ? r : (r && r.requirement_id);
          if (rid) legacyReqIds.add(rid);
        });
      }

      for (const reqId of legacyReqIds) {
        try {
          await fetch("/api/pathway/goal/progress/complete", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ client_id: cid, requirement_id: reqId })
          });
        } catch (e) {
          console.warn(`Failed to migrate legacy requirement ${reqId}:`, e);
        }
      }
    } catch (e) {
      console.warn("Legacy progress migration encountered error:", e);
    } finally {
      localStorage.setItem("schememitra_progress_server_migrated", "true");
    }
  }

  async fetchGoalPathway(forceGeneral = false) {
    const profile = (typeof window.app.getProfile === "function" ? window.app.getProfile() : window.app.userProfile) || {};
    const cid = this.getClientId();
    try {
      await this.migrateLegacyProgressIfNeeded();
      await Promise.all([
        this.fetchCompletedActions(),
        this.fetchUserArtifacts()
      ]);

      const serverOverlay = {
        completed_requirements: (this.completedActionsList || []).map(a => ({
          requirement_id: a.requirement_id,
          status: "COMPLETED",
          confirmed_by_user: true
        }))
      };

      const res = await fetch("/api/pathway/goal/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          client_id: cid,
          profile: profile,
          business_goal: profile.business_goal,
          user_progress_overlay: serverOverlay,
          force_general: forceGeneral
        })
      });
      if (res.ok) {
        const data = await res.json();
        this.goalPathwayData = data;
        if (data.user_artifacts) {
          this.userArtifactsList = data.user_artifacts;
          this.userArtifactsCount = data.user_artifacts.length;
        }
        if (data.user_progress_overlay) {
          this.userProgressOverlay = data.user_progress_overlay;
          this.saveUserProgressOverlay(data.user_progress_overlay);
        }
      }
    } catch (err) {
      console.error("Failed to fetch goal pathway:", err);
    }
    this.render();
  }

  async toggleGoalRequirement(reqId, isCurrentlyCompleted, skipConfirm = false) {
    if (!reqId || reqId === "undefined" || reqId === "null") {
      console.error("toggleGoalRequirement received invalid requirement_id:", reqId);
      alert("Could not save your progress. Invalid requirement ID.");
      return;
    }
    if (!isCurrentlyCompleted && !skipConfirm) {
      const confirmMsg = "Mark this requirement as completed?\n\nThis records your own progress and is not official government verification.";
      if (!window.confirm(confirmMsg)) {
        return;
      }
    }
    const profile = (typeof window.app.getProfile === "function" ? window.app.getProfile() : window.app.userProfile) || {};
    const cid = this.getClientId();
    const action = isCurrentlyCompleted ? "REOPEN" : "COMPLETE";
    try {
      const endpoint = isCurrentlyCompleted 
        ? "/api/pathway/goal/progress/reopen" 
        : "/api/pathway/goal/progress/complete";

      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          client_id: cid,
          requirement_id: reqId
        })
      });

      if (res.ok) {
        await this.fetchCompletedActions();
        await this.fetchUserArtifacts();

        const serverOverlay = {
          completed_requirements: (this.completedActionsList || []).map(a => ({
            requirement_id: a.requirement_id,
            status: "COMPLETED",
            confirmed_by_user: true
          }))
        };

        const updateRes = await fetch("/api/pathway/goal/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            client_id: cid,
            profile: profile,
            business_goal: profile.business_goal,
            user_progress_overlay: serverOverlay
          })
        });

        if (updateRes.ok) {
          const data = await updateRes.json();
          this.goalPathwayData = data;
          if (data.user_progress_overlay) {
            this.userProgressOverlay = data.user_progress_overlay;
            this.saveUserProgressOverlay(data.user_progress_overlay);
          }
        }
      } else {
        alert("Could not save your progress. Please try again.");
        return;
      }
    } catch (err) {
      console.error("Failed to update goal pathway requirement:", err);
      alert("Could not save your progress. Please try again.");
      return;
    }
    this.render();
    if (document.getElementById("completedActionsModal")?.classList.contains("active")) {
      this.openCompletedActionsModal();
    }
  }

  async setGoalClarification(selectedGoal) {
    if (!window.app.userProfile) window.app.userProfile = {};
    window.app.userProfile.business_goal = selectedGoal;
    if (typeof window.app.saveProfileToStorage === "function") {
      window.app.saveProfileToStorage(window.app.userProfile);
    }
    await this.fetchGoalPathway();
  }

  formatBusinessGoal(goal) {
    if (!goal) return 'Start a business';
    const g = String(goal).trim();
    const ENUM_MAP = {
      'START_BUSINESS': 'Start a business',
      'ESTABLISH_ENTERPRISE': 'Establish an enterprise',
      'EXPAND_BUSINESS': 'Expand existing business',
      'UPGRADE_UNIT': 'Upgrade micro enterprise unit',
      'TECH_INNOVATION': 'Technology innovation & commercialization',
      'EXPORT_DEVELOPMENT': 'Export development',
      'MODERNIZATION': 'Unit modernization',
      'WORKING_CAPITAL': 'Working capital assistance'
    };
    if (ENUM_MAP[g.toUpperCase()]) {
      return ENUM_MAP[g.toUpperCase()];
    }
    if (/^[A-Z0-9_]+$/.test(g)) {
      return g.split('_').map(w => w.charAt(0) + w.slice(1).toLowerCase()).join(' ');
    }
    return g;
  }

  formatMissingProfileFact(info) {
    if (!info) return '';
    const s = String(info).trim();
    const lower = s.toLowerCase();
    if (lower === 'shg_membership' || lower.includes('shg_membership') || lower.includes('shg membership')) return 'SHG membership';
    if (lower.includes('entity_type') || lower.includes('fpo/shg/cooperative')) return 'Entity type (FPO / SHG / Cooperative)';
    if (lower.includes('dpiit')) return 'DPIIT startup recognition';
    if (lower.includes('incubator') || lower.includes('prayas')) return 'Incubator / approved centre linkage';
    if (lower.includes('category')) return 'Social category';
    if (lower.includes('business stage')) return 'Business stage requirement';
    if (lower === 'is_new_unit' || lower.includes('is_new_unit')) return 'New micro-enterprise status';
    if (lower === 'prior_gov_subsidy' || lower.includes('prior_gov_subsidy')) return 'Prior government subsidy history';
    if (lower === 'family_pmegp_availed' || lower.includes('family_pmegp_availed')) return 'Family PMEGP beneficiary status';
    if (lower === 'udyam_registered' || lower.includes('udyam_registered')) return 'Udyam Registration status';
    if (lower === 'udyam_category' || lower.includes('udyam_category')) return 'Udyam Enterprise Category (Micro / Small)';
    if (lower === 'project_cost' || lower.includes('project_cost')) return 'Estimated project cost';
    if (lower === 'education' || lower.includes('education')) return 'Educational qualification';
    return s.replace(/_/g, ' ');
  }

  async toggleInlineRoadmap(opportunityId) {
    if (!this.expandedInlineRoadmaps) this.expandedInlineRoadmaps = {};
    const nextState = !this.expandedInlineRoadmaps[opportunityId];
    this.expandedInlineRoadmaps[opportunityId] = nextState;

    if (nextState && (!this.pathwayCache || !this.pathwayCache[opportunityId])) {
      if (!this.pathwayCache) this.pathwayCache = {};
      try {
        const res = await fetch("/api/pathway/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            profile: window.app.userProfile || {},
            opportunity_id: opportunityId
          })
        });
        if (res.ok) {
          this.pathwayCache[opportunityId] = await res.json();
        }
      } catch (err) {
        console.warn("Inline pathway fetch failed:", err);
      }
    }
    this.render();
  }

  buildInlineRoadmapHTML(scheme, profile) {
    const opportunityId = scheme.opportunity_id || scheme.id;
    const pathwayData = (this.pathwayCache && this.pathwayCache[opportunityId]) || null;

    // 1. WHAT YOU ALREADY HAVE
    const confirmedFacts = [];
    if (profile.age !== null && profile.age !== undefined && profile.age !== "") {
      confirmedFacts.push(`Age information available (${profile.age} yrs)`);
    }
    if (profile.state && String(profile.state).trim()) {
      confirmedFacts.push(`State location confirmed (${profile.state})`);
    }
    if (profile.sector && String(profile.sector).trim()) {
      confirmedFacts.push(`Business sector available (${profile.sector})`);
    }
    if ((profile.business_stage || profile.business_type) && String(profile.business_stage || profile.business_type).trim()) {
      confirmedFacts.push(`Business stage confirmed (${profile.business_stage || profile.business_type})`);
    }
    if (profile.gender && String(profile.gender).trim()) {
      confirmedFacts.push(`Gender specified (${profile.gender})`);
    }
    if (profile.education && String(profile.education).trim()) {
      confirmedFacts.push(`Qualification level specified (${profile.education})`);
    }

    // Requirements passed
    const requirements = pathwayData?.pathway?.requirements || [];
    const completedReqs = requirements.filter(r => r.state === 'PASSED' || r.state === 'COMPLETED');
    completedReqs.forEach(r => {
      confirmedFacts.push(r.label || r.requirement_id);
    });

    // 2. PLEASE CONFIRM (VERIFY / UNTESTED / missing_profile_info)
    const verifyFacts = [];
    const missingProfile = scheme.missing_profile_info || pathwayData?.eligibility?.missing_profile_fields || [];
    missingProfile.forEach(m => {
      verifyFacts.push(this.formatMissingProfileFact(m));
    });
    const verifyReqs = requirements.filter(r => r.state === 'VERIFY' || r.state === 'UNTESTED');
    verifyReqs.forEach(r => {
      verifyFacts.push(r.label || r.requirement_id);
    });

    // 3. MY NEXT STEPS (ACTION_NEEDED / FAILED / gaps)
    const nextSteps = [];
    if (verifyFacts.length > 0) {
      nextSteps.push("Confirm the missing information above");
    }
    const actionReqs = requirements.filter(r => r.state === 'ACTION_NEEDED' || r.state === 'FAILED');
    actionReqs.forEach(r => {
      nextSteps.push(r.label || r.requirement_id);
    });
    const gaps = scheme.scheme_gaps || scheme.missing_requirements || [];
    gaps.forEach(g => {
      if (!nextSteps.includes(g)) nextSteps.push(g);
    });
    nextSteps.push("Review the verified SchemeMitra Application Guide");
    nextSteps.push("Proceed to the official government portal for direct application submission");

    const rawStatus = scheme.eligibility_status || scheme.status || pathwayData?.eligibility?.status || 'POTENTIALLY_ELIGIBLE';
    const isReady = (rawStatus === 'ELIGIBLE') && actionReqs.length === 0 && gaps.length === 0;

    const officialAppUrl = scheme.application_url || pathwayData?.eligibility?.application_url || scheme.official_source_url || pathwayData?.eligibility?.official_source_url;

    return `
      <div class="inline-roadmap-panel" id="inlineRoadmap_${opportunityId}">
        <div style="font-size: 0.8rem; font-weight: 800; color: #FF9933; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 0.85rem; border-bottom: 1px solid #E8DDD0; padding-bottom: 0.4rem;">
          YOUR ROADMAP — ${scheme.opportunity_name || opportunityId}
        </div>

        <!-- 1. WHAT YOU ALREADY HAVE -->
        <div style="margin-bottom: 1rem;">
          <div style="font-size: 0.85rem; font-weight: 800; color: #138808; margin-bottom: 0.35rem; display: flex; align-items: center; gap: 0.35rem;">
            ✓ WHAT YOU ALREADY HAVE
          </div>
          <ul style="list-style: none; padding-left: 0; margin: 0; font-size: 0.85rem; color: #14532d; line-height: 1.6;">
            ${confirmedFacts.map(f => `<li style="margin-bottom: 0.2rem;">• ${f}</li>`).join('')}
          </ul>
        </div>

        <!-- 2. PLEASE CONFIRM -->
        ${verifyFacts.length > 0 ? `
          <div style="margin-bottom: 1rem;">
            <div style="font-size: 0.85rem; font-weight: 800; color: #000080; margin-bottom: 0.35rem; display: flex; align-items: center; gap: 0.35rem;">
              ? PLEASE CONFIRM
            </div>
            <ul style="list-style: none; padding-left: 0; margin: 0; font-size: 0.85rem; color: #1e3a8a; line-height: 1.6;">
              ${verifyFacts.map(f => `<li style="margin-bottom: 0.2rem;">• ${f}</li>`).join('')}
            </ul>
          </div>
        ` : ''}

        <!-- 3. MY NEXT STEPS -->
        <div style="margin-bottom: 1.15rem;">
          <div style="font-size: 0.85rem; font-weight: 800; color: #FF9933; margin-bottom: 0.35rem; display: flex; align-items: center; gap: 0.35rem;">
            ! MY NEXT STEPS
          </div>
          <ol style="padding-left: 1.2rem; margin: 0; font-size: 0.85rem; color: #2A2A2A; line-height: 1.6; font-weight: 600;">
            ${nextSteps.map(s => `<li style="margin-bottom: 0.25rem;">${s}</li>`).join('')}
          </ol>
        </div>

        <!-- 4. READY TO APPLY / ALMOST READY -->
        <div style="background: #eaf7ea; border: 1px solid #bbf7d0; border-radius: 10px; padding: 1rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem;">
          <div>
            <div style="font-weight: 800; font-size: 0.9rem; color: #14532d;">
              ${isReady ? '○ READY TO APPLY' : (verifyFacts.length > 0 ? '○ MORE INFORMATION NEEDED' : '○ ALMOST READY')}
            </div>
            <div style="font-size: 0.8rem; color: #166534; margin-top: 0.15rem;">
              ${isReady ? 'Official application process is open on verified government portal.' : 'Review requirements and guidance before official portal submission.'}
            </div>
          </div>
          <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
            <button class="btn-outline" onclick="myOpportunities.openSchemeDetail('${opportunityId}')" style="font-size: 0.8rem; padding: 0.4rem 0.8rem; border-color: #138808; color: #138808; background: #ffffff;">
              Open Application Guide
            </button>
            ${officialAppUrl ? `
              <a href="${officialAppUrl}" target="_blank" rel="noopener noreferrer" class="btn-primary" style="font-size: 0.8rem; padding: 0.4rem 0.8rem; background: #138808; color: #ffffff; text-decoration: none; border-radius: 8px;">
                Continue to Official Government Website ↗
              </a>
            ` : `
              <button class="btn-primary" onclick="schemeDetail.openApplyModal('${opportunityId}')" style="font-size: 0.8rem; padding: 0.4rem 0.8rem; background: #138808; color: #ffffff;">
                Continue to Official Government Website ↗
              </button>
            `}
          </div>
        </div>

      </div>
    `;
  }

  async render() {
    const container = document.getElementById("viewDashboard");
    if (!container) return;

    const t = (k) => window.i18n.get(k);
    const profile = window.app.userProfile;

    if (!profile || Object.keys(profile).length === 0) {
      container.innerHTML = `
        <section class="section-padding">
          <div class="container" style="max-width: 720px; margin: 0 auto; text-align: center;">
            <div style="background: #FFFDF8; border: 1px solid var(--border-color); border-top: 3px solid #FF9933; border-radius: 16px; padding: 2.5rem; box-shadow: var(--shadow-md);">
              <div style="font-size: 3rem; margin-bottom: 1rem;">🎯</div>
              <h2 style="font-size: 1.6rem; color: var(--primary-navy); margin-bottom: 0.75rem; font-weight: 800;">
                Your Personalized Opportunities
              </h2>
              <p style="color: var(--text-muted); font-size: 1rem; line-height: 1.6; margin-bottom: 2rem;">
                Complete your profile to discover schemes matched to your goals, location and eligibility.
              </p>
              
              <button class="btn-primary" onclick="app.showPage('profile')" style="font-size: 1.05rem; padding: 0.85rem 2.2rem; border-radius: 9999px; margin-bottom: 2rem; background: #138808;">
                Set Up My Profile →
              </button>

              <div style="background: #F5F7FA; border-radius: 12px; padding: 1.5rem; text-align: left;">
                <h4 style="font-size: 1rem; color: var(--primary-navy); margin-bottom: 1rem; font-weight: 700;">Why create a profile?</h4>
                <ul style="list-style: none; display: flex; flex-direction: column; gap: 0.75rem; font-size: 0.95rem; color: var(--primary-navy);">
                  <li><span style="color: #138808; font-weight: 800; margin-right: 0.5rem;">✓</span> Find relevant schemes</li>
                  <li><span style="color: #138808; font-weight: 800; margin-right: 0.5rem;">✓</span> Understand your potential eligibility</li>
                  <li><span style="color: #138808; font-weight: 800; margin-right: 0.5rem;">✓</span> See missing requirements</li>
                  <li><span style="color: #138808; font-weight: 800; margin-right: 0.5rem;">✓</span> Get a personalized preparation roadmap</li>
                </ul>
              </div>
            </div>
          </div>
        </section>
      `;
      return;
    }

    const hasAge = profile.age !== null && profile.age !== undefined && profile.age !== "" && !isNaN(Number(profile.age));
    const hasState = Boolean(profile.state && String(profile.state).trim());
    const hasSector = Boolean(profile.sector && String(profile.sector).trim());
    const hasStage = Boolean((profile.business_stage || profile.business_type) && String(profile.business_stage || profile.business_type).trim());

    if (!hasAge || !hasState || !hasSector || !hasStage) {
      container.innerHTML = `
        <section class="section-padding">
          <div class="container" style="max-width: 720px; margin: 0 auto; text-align: center;">
            <div style="background: #FFFDF8; border: 1px solid var(--border-color); border-top: 3px solid #FF9933; border-radius: 16px; padding: 2.5rem; box-shadow: var(--shadow-md);">
              <div style="font-size: 3rem; margin-bottom: 1rem;">⚠️</div>
              <h2 style="font-size: 1.6rem; color: var(--primary-navy); margin-bottom: 0.75rem; font-weight: 800;">
                Your Profile Needs Information
              </h2>
              <p style="color: var(--text-muted); font-size: 1rem; line-height: 1.6; margin-bottom: 2rem;">
                Your profile needs a little more information before we can generate reliable matches. Please complete the required core fields (Age, State, Business Sector, Business Stage).
              </p>
              
              <button class="btn-primary" onclick="app.showPage('profile')" style="font-size: 1.05rem; padding: 0.85rem 2.2rem; border-radius: 9999px; background: #FF9933; color: #ffffff;">
                Complete Profile →
              </button>
            </div>
          </div>
        </section>
      `;
      return;
    }

    if (!this.analysisResult) {
      container.innerHTML = `
        <section class="section-padding">
          <div class="container" style="text-align: center; padding: 4rem 0;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🔄</div>
            <h3 data-i18n="analyzing_title">${t('analyzing_title')}</h3>
            <p style="color: var(--text-muted);" data-i18n="analyzing_sub">${t('analyzing_sub')}</p>
          </div>
        </section>
      `;
    }

    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          profile: profile,
          selected_opportunity_id: this.selectedOppId
        })
      });

      if (!res.ok) throw new Error("Analysis failed");
      this.analysisResult = await res.json();

      if (this.analysisResult && this.analysisResult.graph && !this.graphData) {
        this.graphData = this.analysisResult.graph;
      }

      this.renderDashboard(container, profile);
    } catch (err) {
      console.error("Dashboard analysis error:", err);
      container.innerHTML = `
        <section class="section-padding">
          <div class="container">
            <div class="error-fallback">
              <h3>Analysis Service Error</h3>
              <p>${err.message}</p>
              <button class="btn-primary" onclick="myOpportunities.render()" style="margin-top: 1rem;" data-i18n="btn_retry">${t('btn_retry')}</button>
            </div>
          </div>
        </section>
      `;
    }
  }

  renderDashboard(container, profile) {
    const t = (k) => window.i18n.get(k);
    const data = this.analysisResult || {};
    const bestMatches = data.best_matches || [];
    const needsInfoOpps = data.more_information_needed || [];
    const needsVerif = data.needs_verification || [];
    const notEligible = data.not_eligible || [];

    const capVal = (profile.available_capital !== null && profile.available_capital !== undefined) 
      ? profile.available_capital 
      : (profile.extra && profile.extra.available_capital !== null && profile.extra.available_capital !== undefined ? Number(profile.extra.available_capital) : null);
    const formattedCapital = (capVal !== null && capVal !== undefined) ? `₹${capVal.toLocaleString('en-IN')}` : 'Not specified';
    const formattedIncome = profile.annual_income ? `₹${profile.annual_income.toLocaleString('en-IN')}` : 'N/A';
    const formattedGoal = this.formatBusinessGoal(profile.business_goal);

    if (data.applicability && data.applicability.personalized_matching_available === false) {
      container.innerHTML = `
        <section class="section-padding" style="background: var(--bg-light); min-height: 60vh;">
          <div class="container" style="max-width: 860px;">
            <div style="background:#ffffff;border:1px solid var(--border-color);border-radius:16px;padding:1.5rem;box-shadow:var(--shadow-sm);margin-bottom:1rem;">
              <span class="badge badge-active" style="margin-bottom:0.6rem;">${t('profile_summary_title')}</span>
              <h2 style="color:var(--primary-navy);margin:0 0 0.5rem;">${t('under18_title')}</h2>
              <p style="color:var(--text-muted);line-height:1.6;margin:0 0 1rem;">${t('under18_msg')}</p>
              <div style="display:flex;gap:0.75rem;flex-wrap:wrap;">
                <button class="btn-primary" onclick="app.showPage('explore')">${t('nav_explore')}</button>
                <button class="btn-outline" onclick="app.showPage('profile')">${t('btn_edit_profile')}</button>
              </div>
            </div>
          </div>
        </section>`;
      return;
    }

    container.innerHTML = `
      <section class="section-padding" style="background: var(--bg-light);">
        <div class="container">
          
          <!-- Profile Summary Header Card -->
          <div style="background: #ffffff; border: 1px solid var(--border-color); border-top: 3px solid #FF9933; border-radius: 16px; padding: 1.25rem; margin-bottom: 1.75rem; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 1rem; box-shadow: var(--shadow-sm);">
            <div>
              <span class="badge badge-active" style="margin-bottom: 0.4rem;" data-i18n="profile_summary_title">${t('profile_summary_title')}</span>
              <h2 style="font-size: 1.25rem; color: var(--primary-navy); line-height: 1.3;">
                ${profile.gender || 'Entrepreneur'} (${profile.age || 'N/A'} yrs) • ${profile.state || 'India'} ${profile.sector ? '• ' + profile.sector : ''}
              </h2>
              <div style="font-size: 0.875rem; color: var(--text-muted); margin-top: 0.35rem; line-height: 1.5;">
                ${profile.business_stage || 'Idea'} Stage • Annual income ${formattedIncome} • Available capital ${formattedCapital}
              </div>
              <div style="font-size: 0.875rem; color: var(--primary-navy); font-weight: 600; margin-top: 0.35rem;">
                Goal: ${formattedGoal}
              </div>
            </div>
            <button class="btn-outline" onclick="app.showPage('profile')" data-i18n="btn_edit_profile">${t('btn_edit_profile')}</button>
          </div>

          <!-- Clean Dashboard Navigation Tabs -->
          <div style="display: flex; gap: 0.5rem; border-bottom: 2px solid var(--border-color); margin-bottom: 1.75rem; overflow-x: auto; padding-bottom: 2px; -webkit-overflow-scrolling: touch;">
            <button class="tab-btn ${this.activeTab === 'recommended' ? 'active' : ''}" onclick="myOpportunities.switchTab('recommended')">
              🏆 Best Matches (${bestMatches.length})
            </button>
            <button class="tab-btn ${this.activeTab === 'potentially' ? 'active' : ''}" onclick="myOpportunities.switchTab('potentially')">
              ⚠️ More Information Needed (${needsInfoOpps.length})
            </button>
            <button class="tab-btn ${this.activeTab === 'verification' ? 'active' : ''}" onclick="myOpportunities.switchTab('verification')">
              📋 Needs Verification (${needsVerif.length})
            </button>
            <button class="tab-btn ${this.activeTab === 'goal_pathway' ? 'active' : ''}" onclick="myOpportunities.switchTab('goal_pathway')">
              🎯 Goal Pathway
            </button>
            <button class="tab-btn ${this.activeTab === 'graph' ? 'active' : ''}" onclick="myOpportunities.switchTab('graph')">
              🌐 ${t('tab_roadmap')}
            </button>
          </div>

          <!-- Active Tab Content Container -->
          <div id="tabContentArea">
            ${this.renderActiveTabContent(data, bestMatches, needsInfoOpps, needsVerif, notEligible)}
          </div>

        </div>
      </section>

      <style>
        .tab-btn {
          padding: 0.65rem 1.1rem;
          border: none;
          background: transparent;
          font-size: 0.925rem;
          font-weight: 600;
          color: var(--text-muted);
          cursor: pointer;
          border-bottom: 3px solid transparent;
          margin-bottom: -2px;
          white-space: nowrap;
          min-height: 44px;
        }
        .tab-btn.active {
          color: var(--primary-saffron);
          border-bottom-color: var(--primary-saffron);
        }
      </style>
    `;
  }

  async switchTab(tabKey) {
    this.activeTab = tabKey;
    if (tabKey === 'graph' && (!this.graphData || !this.graphData.nodes)) {
      await this.switchGraphMode(this.graphSelectionMode || 'TOP_3');
      return;
    }
    if (tabKey === 'goal_pathway' && !this.goalPathwayData) {
      await this.fetchGoalPathway();
      return;
    }
    this.render();
  }

  renderActiveTabContent(data, recs, needsInfoOpps, needsVerif, notEligible) {
    try {
      if (this.activeTab === "recommended") {
        return this.renderBestMatchesList(recs);
      } else if (this.activeTab === "potentially") {
        return this.renderNeedsInfoList(needsInfoOpps);
      } else if (this.activeTab === "verification") {
        return this.renderNeedsVerificationList(needsVerif);
      } else if (this.activeTab === "goal_pathway") {
        return this.renderGoalPathwayView(this.goalPathwayData);
      } else if (this.activeTab === "graph") {
        try {
          return this.renderGraphView(this.graphData || (data && data.graph));
        } catch (graphErr) {
          console.error("Graph tab rendering isolated error:", graphErr);
          return `
            <div class="graph-viewport-card">
              <div style="padding: 3rem 1.5rem; text-align: center;">
                <div style="font-size: 2.5rem; margin-bottom: 1rem;">⚠️</div>
                <h3 style="color: var(--primary-navy); margin-bottom: 0.5rem;">We couldn't load your opportunity graph</h3>
                <p style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 1.5rem;">${graphErr.message || 'Error rendering graph view.'}</p>
                <button class="btn-primary" onclick="myOpportunities.switchGraphMode('TOP_3')">Retry Graph Generation</button>
              </div>
            </div>
          `;
        }
      } else {
        return this.renderBestMatchesList(recs);
      }
    } catch (err) {
      console.error("Dashboard tab rendering error:", err);
      return `<div style="padding: 2rem; text-align: center; color: var(--crimson);">Error loading content: ${err.message}</div>`;
    }
  }

  renderGoalPathwayView(data) {
    if (!data) {
      return `
        <div style="background: #ffffff; padding: 3rem 1.5rem; border-radius: 16px; text-align: center; border: 1px solid var(--border-color);">
          <div style="font-size: 2.5rem; margin-bottom: 1rem;">🔄</div>
          <h3 style="color: var(--primary-navy); margin-bottom: 0.5rem;">Assembling Your Goal Pathway</h3>
          <p style="color: var(--text-muted); font-size: 0.95rem;">Evaluating your profile facts, matched schemes, and verified requirements...</p>
        </div>
      `;
    }

    if (data.pathway_type === "NEEDS_CLARIFICATION") {
      const promptInfo = data.clarification_prompt || {};
      const options = promptInfo.options || [];
      return `
        <div style="background: #fffdf8; border: 1px solid #fde68a; border-top: 4px solid #ff9933; border-radius: 16px; padding: 2rem; box-shadow: var(--shadow-sm); margin-bottom: 1.5rem;">
          <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
            <span style="font-size: 2.2rem;">🎯</span>
            <div>
              <span class="badge" style="background: #fef3c7; color: #b45309; border: 1px solid #fde68a;">Clarification Needed</span>
              <h3 style="font-size: 1.3rem; color: var(--primary-navy); margin: 0.25rem 0 0 0; font-weight: 800;">
                Clarify Your Primary Business Goal
              </h3>
            </div>
          </div>

          <p style="color: var(--text-muted); font-size: 0.95rem; line-height: 1.6; margin-bottom: 1.5rem;">
            ${data.disclaimer || "Please clarify your primary business objective to generate a goal-specific pathway."}
          </p>

          <div style="font-weight: 700; color: var(--primary-navy); font-size: 1rem; margin-bottom: 1rem;">
            ${promptInfo.question || "What are you hoping to do next?"}
          </div>

          <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1.5rem;">
            ${options.map(opt => `
              <button class="btn-primary" onclick="myOpportunities.setGoalClarification('${opt.key}')" style="font-size: 0.9rem; padding: 0.65rem 1.25rem; background: #138808; border-radius: 8px; font-weight: 600;">
                ${opt.label}
              </button>
            `).join("")}
          </div>

          <div style="border-top: 1px solid #fde68a; padding-top: 1rem; text-align: right;">
            <button class="btn-outline" onclick="myOpportunities.fetchGoalPathway(true)" style="font-size: 0.85rem; padding: 0.45rem 1rem;">
              Continue with General Business Readiness →
            </button>
          </div>
        </div>
      `;
    }

    const summary = data.summary || {};
    const goalInfo = data.goal || {};
    const currState = data.current_state_summary || {};
    const nextActions = data.next_actions || [];
    const sections = data.sections || [];
    const profile = window.app ? (typeof window.app.getProfile === "function" ? window.app.getProfile() : window.app.userProfile) || {} : {};

    const isGeneral = data.pathway_type === "GENERAL_READINESS";

    const secA = sections.find(s => s.section_id === "sec_matched_opportunities") || { steps: [] };
    const secB = sections.find(s => s.section_id === "sec_requirements") || { steps: [] };
    const secC = sections.find(s => s.section_id === "sec_support") || { steps: [] };

    // --- SECTION A: YOUR GOAL ---
    const goalSectionHtml = `
      <div style="background: #ffffff; border: 1px solid var(--border-color); border-top: 4px solid #FF9933; border-radius: 16px; padding: 1.5rem; box-shadow: var(--shadow-sm); margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem; margin-bottom: 1rem;">
          <div>
            <span class="badge badge-active" style="margin-bottom: 0.4rem;">
              ${isGeneral ? '🏢 General Business Readiness' : '🎯 YOUR GOAL'}
            </span>
            <h2 style="font-size: 1.4rem; color: var(--primary-navy); font-weight: 800; margin: 0.25rem 0 0.35rem 0;">
              ${goalInfo.display_label || goalInfo.raw_text || 'General Business Readiness'}
            </h2>
            <div style="font-size: 0.875rem; color: var(--text-muted);">
              Stage: <strong>${currState.business_stage || 'Idea'}</strong> • Sector: <strong>${currState.sector || 'Not specified'}</strong>
            </div>
          </div>
          <button class="btn-outline" onclick="myOpportunities.fetchGoalPathway(false)" style="font-size: 0.85rem; padding: 0.4rem 0.9rem;">
            ↺ Refresh Pathway
          </button>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1rem; background: #f8fafc; border: 1px solid var(--border-color); border-radius: 12px; padding: 1rem;">
          <div>
            <div style="font-size: 0.75rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Matched Opportunities</div>
            <div style="font-size: 1.35rem; font-weight: 800; color: var(--primary-navy);">${summary.matched_schemes_count || 0}</div>
          </div>
          <div>
            <div style="font-size: 0.75rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Unresolved Actions</div>
            <div style="font-size: 1.35rem; font-weight: 800; color: ${summary.unresolved_actions_count > 0 ? '#d97706' : '#138808'};">
              ${summary.unresolved_actions_count || 0}
            </div>
          </div>
          <div>
            <div style="font-size: 0.75rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Total Pathway Steps</div>
            <div style="font-size: 1.35rem; font-weight: 800; color: #2563eb;">${summary.total_steps || 0}</div>
          </div>
        </div>

        <div style="font-size: 0.8rem; color: #b45309; background: #fffbe6; border: 1px solid #fde68a; border-radius: 8px; padding: 0.5rem 0.75rem; margin-top: 0.85rem; font-weight: 600; display: flex; align-items: center; gap: 0.4rem;">
          <span>ℹ️</span> Suggested planning pathway — not an official scheme sequence.
        </div>
      </div>
    `;

    // --- SECTION B: WHERE YOU ARE NOW (Safeguard 4: Only actual available profile fields) ---
    const capVal = (profile.available_capital !== null && profile.available_capital !== undefined) 
      ? profile.available_capital 
      : (profile.extra && profile.extra.available_capital !== null && profile.extra.available_capital !== undefined ? profile.extra.available_capital : null);
    
    const formattedCap = (capVal !== null && capVal !== undefined && capVal !== "") 
      ? `₹${Number(capVal).toLocaleString('en-IN')}` 
      : 'Not provided';
      
    const incVal = profile.annual_income;
    const formattedInc = (incVal !== null && incVal !== undefined && incVal !== "" && Number(incVal) > 0)
      ? `₹${Number(incVal).toLocaleString('en-IN')}`
      : 'Not provided';

    const whereYouAreHtml = `
      <div style="background: #ffffff; border: 1px solid var(--border-color); border-left: 4px solid #138808; border-radius: 14px; padding: 1.25rem; margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem;">
          <h3 style="font-size: 1.1rem; color: var(--primary-navy); font-weight: 800; margin: 0; display: flex; align-items: center; gap: 0.4rem;">
            <span>👤</span> WHERE YOU ARE NOW
          </h3>
          <span style="font-size: 0.775rem; font-weight: 700; color: #138808; background: #f0fdf4; border: 1px solid #bbf7d0; padding: 0.2rem 0.55rem; border-radius: 6px;">
            Confirmed Profile Context
          </span>
        </div>
        <p style="font-size: 0.825rem; color: var(--text-muted); margin-bottom: 1rem;">
          SchemeMitra understands your current situation based on confirmed profile facts.
        </p>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.85rem; font-size: 0.875rem;">
          <div style="background: #f8fafc; padding: 0.65rem 0.85rem; border-radius: 8px; border: 1px solid #e2e8f0;">
            <div style="font-size: 0.75rem; color: var(--text-muted); font-weight: 600;">Business Stage</div>
            <div style="font-weight: 700; color: var(--primary-navy); margin-top: 0.15rem;">${currState.business_stage || profile.business_stage || profile.business_type || 'Idea'}</div>
          </div>
          <div style="background: #f8fafc; padding: 0.65rem 0.85rem; border-radius: 8px; border: 1px solid #e2e8f0;">
            <div style="font-size: 0.75rem; color: var(--text-muted); font-weight: 600;">Primary Sector</div>
            <div style="font-weight: 700; color: var(--primary-navy); margin-top: 0.15rem;">${currState.sector || profile.sector || profile.target_sector || 'Not provided'}</div>
          </div>
          <div style="background: #f8fafc; padding: 0.65rem 0.85rem; border-radius: 8px; border: 1px solid #e2e8f0;">
            <div style="font-size: 0.75rem; color: var(--text-muted); font-weight: 600;">Available Capital</div>
            <div style="font-weight: 700; color: var(--primary-navy); margin-top: 0.15rem;">${formattedCap}</div>
          </div>
          <div style="background: #f8fafc; padding: 0.65rem 0.85rem; border-radius: 8px; border: 1px solid #e2e8f0;">
            <div style="font-size: 0.75rem; color: var(--text-muted); font-weight: 600;">Annual Income</div>
            <div style="font-weight: 700; color: var(--primary-navy); margin-top: 0.15rem;">${formattedInc}</div>
          </div>
          <div style="background: #f8fafc; padding: 0.65rem 0.85rem; border-radius: 8px; border: 1px solid #e2e8f0;">
            <div style="font-size: 0.75rem; color: var(--text-muted); font-weight: 600;">Known Facts Count</div>
            <div style="font-weight: 700; color: var(--primary-navy); margin-top: 0.15rem;">${currState.known_facts_count || 0} facts</div>
          </div>
          <div style="background: #f8fafc; padding: 0.65rem 0.85rem; border-radius: 8px; border: 1px solid #e2e8f0;">
            <div style="font-size: 0.75rem; color: var(--text-muted); font-weight: 600;">Selected Goal</div>
            <div style="font-weight: 700; color: var(--primary-navy); margin-top: 0.15rem;">${goalInfo.display_label || this.formatBusinessGoal(profile.business_goal)}</div>
          </div>
        </div>
      </div>
    `;

    // --- SECTION C: WHAT NEEDS ATTENTION (Gap Summary) ---
    const actionNeededCount = nextActions.filter(a => a.status === "ACTION_NEEDED").length;
    const needToConfirmCount = nextActions.filter(a => a.status === "NEEDS_CONFIRMATION").length;

    const gapSummaryHtml = `
      <div style="background: #ffffff; border: 1px solid var(--border-color); border-left: 4px solid #d97706; border-radius: 14px; padding: 1.25rem; margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem;">
          <h3 style="font-size: 1.1rem; color: var(--primary-navy); font-weight: 800; margin: 0; display: flex; align-items: center; gap: 0.4rem;">
            <span>🔍</span> WHAT NEEDS ATTENTION
          </h3>
          <span style="font-size: 0.775rem; font-weight: 700; color: #b45309; background: #fffbe6; border: 1px solid #fde68a; padding: 0.2rem 0.55rem; border-radius: 6px;">
            Unresolved Requirements Summary
          </span>
        </div>
        <p style="font-size: 0.825rem; color: var(--text-muted); margin-bottom: 1rem;">
          Backend gap evaluation breakdown across your matched opportunities (excluding completed items).
        </p>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
          <div style="background: #fffbebf5; border: 1px solid #fde68a; border-radius: 10px; padding: 0.85rem; display: flex; align-items: center; justify-content: space-between;">
            <div>
              <div style="font-size: 0.75rem; font-weight: 800; color: #b45309; text-transform: uppercase;">! Action Needed</div>
              <div style="font-size: 1.4rem; font-weight: 800; color: #b45309; margin-top: 0.15rem;">${actionNeededCount} ${actionNeededCount === 1 ? 'item' : 'items'}</div>
            </div>
            <span style="font-size: 1.8rem;">!</span>
          </div>

          <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 10px; padding: 0.85rem; display: flex; align-items: center; justify-content: space-between;">
            <div>
              <div style="font-size: 0.75rem; font-weight: 800; color: #1d4ed8; text-transform: uppercase;">? Need to Confirm</div>
              <div style="font-size: 1.4rem; font-weight: 800; color: #1d4ed8; margin-top: 0.15rem;">${needToConfirmCount} ${needToConfirmCount === 1 ? 'item' : 'items'}</div>
            </div>
            <span style="font-size: 1.8rem;">?</span>
          </div>
        </div>
      </div>
    `;

    // --- SECTION D: NEXT ACTIONS TO REVIEW (Safeguards 1 & 10) ---
    // Priority order for display: ACTION_NEEDED items first, then NEEDS_CONFIRMATION ("Items requiring attention first")
    const sortedNextActions = [...nextActions].sort((a, b) => {
      if (a.status === "ACTION_NEEDED" && b.status !== "ACTION_NEEDED") return -1;
      if (a.status !== "ACTION_NEEDED" && b.status === "ACTION_NEEDED") return 1;
      return 0;
    });

    // Safeguard 1: Grouping by requirement_type (for shared artifacts) or normalized title.
    const SHARED_ARTIFACT_TYPES = new Set([
      "DPR",
      "IDENTITY_PROOF",
      "REGISTRATION_CERTIFICATE",
      "LAND_OR_LEASE_DOCUMENT",
      "BANK_DOCUMENT"
    ]);

    const SHARED_ARTIFACT_NAMES = {
      "DPR": "Detailed Project Report (DPR)",
      "IDENTITY_PROOF": "Identity / KYC Proof",
      "REGISTRATION_CERTIFICATE": "Registration Certificate",
      "LAND_OR_LEASE_DOCUMENT": "Land / Lease Document",
      "BANK_DOCUMENT": "Bank Account / Financial Statement"
    };

    const groupedActionsMap = new Map();
    sortedNextActions.forEach(act => {
      const typeStr = (act.requirement_type || 'REQ').trim().toUpperCase();
      const titleStr = (act.title || act.node_id || '').trim().toLowerCase();

      let groupKey = "";
      if (SHARED_ARTIFACT_TYPES.has(typeStr)) {
        groupKey = `ARTIFACT:${typeStr}`;
      } else {
        groupKey = `${typeStr}:${titleStr}`;
      }

      if (!groupedActionsMap.has(groupKey)) {
        groupedActionsMap.set(groupKey, {
          groupKey: groupKey,
          title: act.display_title || act.title || act.node_id,
          display_title: act.display_title || act.title || act.node_id,
          requirement_type: typeStr,
          isSharedArtifact: SHARED_ARTIFACT_TYPES.has(typeStr),
          items: []
        });
      }
      groupedActionsMap.get(groupKey).items.push(act);
    });

    let nextActionsContentHtml = "";
    if (sortedNextActions.length === 0) {
      nextActionsContentHtml = `
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 1rem; text-align: center; color: #15803d; font-weight: 700;">
          ✓ All outstanding requirements confirmed! Check your Requirement Progress below.
        </div>
      `;
    } else {
      nextActionsContentHtml = Array.from(groupedActionsMap.values()).map(group => {
        if (group.isSharedArtifact) {
          const availArtifact = (this.userArtifactsList || []).find(a => a.artifact_type === group.requirement_type);
          const isArtifactAvailable = !!availArtifact;
          const artifactTitle = SHARED_ARTIFACT_NAMES[group.requirement_type] || group.title || group.requirement_type;

          const buttonLabels = {
            "DPR": "I Have a DPR",
            "IDENTITY_PROOF": "I Have Identity / KYC Proof",
            "REGISTRATION_CERTIFICATE": "I Have This Registration Certificate",
            "LAND_OR_LEASE_DOCUMENT": "I Have Land / Lease Documents",
            "BANK_DOCUMENT": "I Have the Required Bank Document"
          };
          const markAvailableLabel = buttonLabels[group.requirement_type] || `I Have This ${artifactTitle}`;

          const confirmBtnLabel = group.requirement_type === "DPR"
            ? "✓ Confirm DPR for this Scheme"
            : "✓ Confirm for this Scheme";

          return `
            <div style="background: #ffffff; border: 1.5px solid #2563eb; border-radius: 12px; padding: 1.1rem; margin-bottom: 0.5rem;">
              <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; flex-wrap: wrap; gap: 0.5rem;">
                <div>
                  <div style="font-size: 0.725rem; font-weight: 800; color: #2563eb; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.15rem;">
                    📄 Document You Can Reuse
                  </div>
                  <h4 style="font-size: 1.05rem; font-weight: 800; color: var(--primary-navy); margin: 0 0 0.2rem 0;">
                    ${artifactTitle}
                  </h4>
                  <div style="font-size: 0.78rem; color: #2563eb; font-weight: 700;">
                    Applies to ${group.items.length} matched ${group.items.length === 1 ? 'opportunity' : 'opportunities'}
                  </div>
                </div>

                <div>
                  ${isArtifactAvailable ? `
                    <div style="display: flex; align-items: center; gap: 0.4rem;">
                      <span class="badge" style="background: #dcfce7; color: #15803d; border: 1px solid #86efac; padding: 0.25rem 0.6rem; font-size: 0.8rem; font-weight: 700;">
                        ✓ ${artifactTitle} Available
                      </span>
                      <button class="btn-outline" onclick="myOpportunities.removeArtifact('${group.requirement_type}')" style="font-size: 0.75rem; padding: 0.2rem 0.5rem; border-color: #cbd5e1; color: #475569;">
                        Change
                      </button>
                    </div>
                  ` : `
                    <button class="btn-primary" onclick="myOpportunities.markArtifactAvailable('${group.requirement_type}')" style="font-size: 0.8rem; padding: 0.35rem 0.85rem; background: #2563eb; color: #ffffff; font-weight: 700;">
                      ${markAvailableLabel}
                    </button>
                  `}
                </div>
              </div>

              ${group.requirement_type === 'DPR' && isArtifactAvailable ? `
                <div style="font-size: 0.78rem; color: #b45309; background: #fffbe6; border: 1px solid #fde68a; border-radius: 6px; padding: 0.4rem 0.65rem; margin-bottom: 0.6rem; font-weight: 600;">
                  ℹ️ Your DPR may need changes to meet each scheme's specific requirements.
                </div>
              ` : ''}

              <div style="font-size: 0.825rem; color: var(--text-muted); margin-bottom: 0.75rem; line-height: 1.4;">
                ${isArtifactAvailable
                  ? `Artifact is marked available in your prepared documents. Confirm whether your existing ${artifactTitle} satisfies each scheme requirement below:`
                  : `Possess this document? Mark it available above. Scheme-specific requirements must still be confirmed below:`
                }
              </div>

              <div style="display: flex; flex-direction: column; gap: 0.6rem; border-top: 1px solid #f1f5f9; padding-top: 0.75rem;">
                ${group.items.map(act => {
                  const schemeName = act.source_opportunity_name || act.opportunity_name || act.opportunity_id;
                  const safeScheme = schemeName.replace(/'/g, "");
                  const safeTitle = artifactTitle.replace(/'/g, "");
                  return `
                    <div style="display: flex; justify-content: space-between; align-items: center; background: #f8fafc; padding: 0.65rem 0.85rem; border-radius: 8px; border: 1px solid #e2e8f0; gap: 0.75rem; flex-wrap: wrap;">
                      <div style="flex: 1; min-width: 220px;">
                        <div style="font-size: 0.875rem; font-weight: 700; color: var(--primary-navy);">
                          🏛️ ${schemeName}
                        </div>
                        <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 0.15rem;">
                          ${isArtifactAvailable ? 'Confirm that your existing ' + artifactTitle + ' satisfies this scheme requirement' : 'Requirement: ' + act.title}
                        </div>
                      </div>
                      <button class="btn-outline" onclick="myOpportunities.confirmSchemeRequirementWithArtifact('${act.node_id}', '${safeScheme}', '${safeTitle}')" style="font-size: 0.8rem; padding: 0.35rem 0.85rem; border-color: #138808; color: #138808; background: #ffffff; font-weight: 700;">
                        ${confirmBtnLabel}
                      </button>
                    </div>
                  `;
                }).join("")}
              </div>
            </div>
          `;
        }

        if (group.items.length === 1) {
          const act = group.items[0];
          const isAct = act.status === "ACTION_NEEDED";
          const badgeStyle = isAct 
            ? "background: #fef3c7; color: #b45309; border: 1px solid #fde68a;" 
            : "background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe;";

          return `
            <div style="display: flex; justify-content: space-between; align-items: center; background: #ffffff; padding: 0.85rem 1rem; border-radius: 10px; border: 1px solid var(--border-color); gap: 0.75rem; flex-wrap: wrap;">
              <div style="flex: 1; min-width: 240px;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.35rem;">
                  <span style="font-size: 0.725rem; font-weight: 800; padding: 0.15rem 0.5rem; border-radius: 4px; ${badgeStyle}">
                    ${act.status_label || (isAct ? '! Action Needed' : '? Need to Confirm')}
                  </span>
                  <span style="font-size: 0.725rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">
                    ${act.requirement_type || 'REQUIREMENT'}
                  </span>
                </div>
                <div style="font-size: 0.925rem; color: var(--primary-navy); font-weight: 700;">
                  ${act.display_title || act.title}
                </div>
                <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 0.2rem;">
                  Source Scheme: <strong>${act.source_opportunity_name || act.opportunity_name || act.opportunity_id}</strong>
                </div>
                ${(act.requirement_type === 'ENTITY_REGISTRATION' || act.supporting_text) ? `
                  <div style="font-size: 0.78rem; color: #b45309; font-weight: 600; margin-top: 0.25rem; display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                    <span>${act.supporting_text || 'Exact registration type needs confirmation.'}</span>
                    ${act.official_source_url ? `<a href="${act.official_source_url}" target="_blank" rel="noopener noreferrer" style="color: var(--accent-blue); text-decoration: underline;">Official Scheme Source ↗</a>` : ''}
                  </div>
                ` : ((act.requirement_type === 'DOCUMENT' || act.requirement_type === 'DOCUMENTATION') ? `
                  <div style="font-size: 0.78rem; color: #b45309; font-weight: 600; margin-top: 0.25rem; display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                    <span>Exact documents need confirmation.</span>
                    ${act.official_source_url ? `<a href="${act.official_source_url}" target="_blank" rel="noopener noreferrer" style="color: var(--accent-blue); text-decoration: underline;">Official Scheme Source ↗</a>` : ''}
                  </div>
                ` : (act.official_source_url ? `
                  <div style="font-size: 0.78rem; margin-top: 0.25rem;">
                    <a href="${act.official_source_url}" target="_blank" rel="noopener noreferrer" style="color: var(--accent-blue); text-decoration: underline; font-weight: 600;">Official Scheme Source ↗</a>
                  </div>
                ` : ''))}
              </div>
              <button class="btn-outline" onclick="myOpportunities.toggleGoalRequirement('${act.node_id}', false)" style="font-size: 0.8rem; padding: 0.4rem 0.85rem; border-color: #138808; color: #138808; background: #ffffff; min-height: 38px;">
                ✓ Mark Completed
              </button>
            </div>
          `;
        } else {
          return `
            <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: 10px; padding: 0.85rem 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                <div>
                  <div style="font-size: 0.925rem; color: var(--primary-navy); font-weight: 800;">
                    ${group.display_title || group.title}
                  </div>
                  <div style="font-size: 0.78rem; color: #2563eb; font-weight: 700; margin-top: 0.15rem;">
                    Applies to ${group.items.length} matched opportunities (Mark each canonical requirement separately below)
                  </div>
                </div>
              </div>
              <div style="display: flex; flex-direction: column; gap: 0.5rem; margin-top: 0.5rem; border-top: 1px solid #f1f5f9; padding-top: 0.5rem;">
                ${group.items.map(act => {
                  const isAct = act.status === "ACTION_NEEDED";
                  const badgeStyle = isAct 
                    ? "background: #fef3c7; color: #b45309; border: 1px solid #fde68a;" 
                    : "background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe;";

                  return `
                    <div style="display: flex; justify-content: space-between; align-items: center; background: #f8fafc; padding: 0.6rem 0.8rem; border-radius: 8px; border: 1px solid #e2e8f0; gap: 0.75rem; flex-wrap: wrap;">
                      <div style="flex: 1; min-width: 220px;">
                        <div style="display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.2rem;">
                          <span style="font-size: 0.7rem; font-weight: 800; padding: 0.1rem 0.4rem; border-radius: 4px; ${badgeStyle}">
                            ${act.status_label || (isAct ? '! Action Needed' : '? Need to Confirm')}
                          </span>
                        </div>
                        <div style="font-size: 0.8rem; color: var(--text-muted);">
                          Source Scheme: <strong>${act.source_opportunity_name || act.opportunity_name || act.opportunity_id}</strong>
                        </div>
                        ${(act.requirement_type === 'ENTITY_REGISTRATION' || act.supporting_text) ? `
                          <div style="font-size: 0.75rem; color: #b45309; font-weight: 600; margin-top: 0.2rem; display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                            <span>${act.supporting_text || 'Exact registration type needs confirmation.'}</span>
                            ${act.official_source_url ? `<a href="${act.official_source_url}" target="_blank" rel="noopener noreferrer" style="color: var(--accent-blue); text-decoration: underline;">Official Scheme Source ↗</a>` : ''}
                          </div>
                        ` : ((act.requirement_type === 'DOCUMENT' || act.requirement_type === 'DOCUMENTATION') ? `
                          <div style="font-size: 0.75rem; color: #b45309; font-weight: 600; margin-top: 0.2rem; display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                            <span>Exact documents need confirmation.</span>
                            ${act.official_source_url ? `<a href="${act.official_source_url}" target="_blank" rel="noopener noreferrer" style="color: var(--accent-blue); text-decoration: underline;">Official Scheme Source ↗</a>` : ''}
                          </div>
                        ` : (act.official_source_url ? `
                          <div style="font-size: 0.75rem; margin-top: 0.2rem;">
                            <a href="${act.official_source_url}" target="_blank" rel="noopener noreferrer" style="color: var(--accent-blue); text-decoration: underline; font-weight: 600;">Official Scheme Source ↗</a>
                          </div>
                        ` : ''))}
                      </div>
                      <button class="btn-outline" onclick="myOpportunities.toggleGoalRequirement('${act.node_id}', false)" style="font-size: 0.775rem; padding: 0.35rem 0.75rem; border-color: #138808; color: #138808; background: #ffffff; min-height: 36px;">
                        ✓ Mark Completed
                      </button>
                    </div>
                  `;
                }).join("")}
              </div>
            </div>
          `;
        }
      }).join("");
    }

    const nextActionsHtml = `
      <div style="background: #fffbebf5; border: 1px solid #fde68a; border-radius: 14px; padding: 1.25rem; margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; flex-wrap: wrap; gap: 0.5rem;">
          <div style="font-weight: 800; font-size: 1.1rem; color: #b45309; display: flex; align-items: center; gap: 0.4rem;">
            <span>✅</span> NEXT ACTIONS TO REVIEW (${sortedNextActions.length})
          </div>
          <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
            <button class="btn-outline" onclick="myOpportunities.openPreparedDocumentsModal()" style="font-size: 0.8rem; padding: 0.35rem 0.75rem; border-color: #2563eb; color: #2563eb; background: #ffffff; font-weight: 700; cursor: pointer;">
              📄 Prepared Documents (${this.userArtifactsCount || 0})
            </button>
            <button class="btn-outline" onclick="myOpportunities.openCompletedActionsModal()" style="font-size: 0.8rem; padding: 0.35rem 0.75rem; border-color: #138808; color: #138808; background: #ffffff; font-weight: 700; cursor: pointer;">
              ✓ Completed Actions (${this.completedActionsCount || 0})
            </button>
          </div>
        </div>
        <p style="font-size: 0.825rem; color: #78350f; margin-bottom: 1rem;">
          Review and confirm these action items to progress towards your goal.
        </p>

        <div style="display: flex; flex-direction: column; gap: 0.75rem;">
          ${nextActionsContentHtml}
        </div>
      </div>
    `;

    // --- SECTION E: OPPORTUNITIES THIS PATHWAY CONNECTS TO (formerly Section A) ---
    // Safeguard 3: M4 rank/order strictly preserved from backend `secA.steps`.
    const secASteps = secA.steps || [];
    const oppsHtml = `
      <div style="margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--border-color); padding-bottom: 0.5rem; margin-bottom: 1rem;">
          <h3 style="font-size: 1.1rem; color: var(--primary-navy); font-weight: 800; margin: 0;">
            🏛️ OPPORTUNITIES THIS PATHWAY CONNECTS TO
          </h3>
          <span style="font-size: 0.8rem; color: var(--text-muted); font-weight: 600;">
            ${secASteps.length} matched scheme${secASteps.length !== 1 ? 's' : ''} (M4 Rank Order Preserved)
          </span>
        </div>

        <div style="display: flex; flex-direction: column; gap: 1rem;">
          ${secASteps.map(step => `
            <div style="background: #ffffff; border: 1px solid var(--border-color); border-left: 4px solid #2563eb; border-radius: 12px; padding: 1.15rem;">
              <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.4rem;">
                <span style="font-size: 0.75rem; font-weight: 800; color: #2563eb; text-transform: uppercase;">CONNECTED SCHEME</span>
                <span class="badge ${step.status === 'ELIGIBLE' ? 'badge-eligible' : 'badge-potentially'}">${step.status_label || step.status}</span>
              </div>
              <h4 onclick="myOpportunities.openSchemeDetail('${step.opportunity_id}')" style="font-size: 1.05rem; font-weight: 800; color: var(--primary-navy); margin: 0 0 0.5rem 0; cursor: pointer;">
                🎯 ${step.title || step.opportunity_name}
              </h4>
              <p style="font-size: 0.875rem; color: var(--text-muted); line-height: 1.5; margin: 0 0 0.85rem 0;">
                ${step.verified_benefit_summary || ''}
              </p>
              <div style="font-size: 0.8rem; color: var(--accent-blue); font-weight: 600; margin-bottom: 0.65rem;">
                Supports eligibility assessment for your goal
              </div>
              <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; border-top: 1px solid #f1f5f9; padding-top: 0.65rem;">
                <div style="font-size: 0.8rem; color: var(--text-muted);">
                  Support: <strong>${(step.verified_support_types || []).join(', ') || 'Official Support'}</strong>
                </div>
                <div style="display: flex; gap: 0.5rem;">
                  <button class="btn-outline" onclick="myOpportunities.openSchemeDetail('${step.opportunity_id}')" style="font-size: 0.8rem; padding: 0.35rem 0.75rem;">
                    View Scheme Details
                  </button>
                  ${step.official_source_url ? `
                    <a href="${step.official_source_url}" target="_blank" rel="noopener noreferrer" class="btn-primary" style="font-size: 0.8rem; padding: 0.35rem 0.75rem; background: #138808; color: #ffffff; text-decoration: none; border-radius: 8px;">
                      Official Scheme Source ↗
                    </a>
                  ` : ''}
                </div>
              </div>
            </div>
          `).join("")}
        </div>
      </div>
    `;

    // --- SECTION F: VERIFIED SUPPORT AVAILABLE (formerly Section C) ---
    const secCSteps = secC.steps || [];
    const supportByOppMap = new Map();
    secCSteps.forEach(step => {
      const oppName = step.source_opportunity_name || step.opportunity_name || step.source_opportunity_id || 'Matched Scheme';
      if (!supportByOppMap.has(oppName)) {
        supportByOppMap.set(oppName, []);
      }
      supportByOppMap.get(oppName).push(step);
    });

    const supportHtml = `
      <div style="margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--border-color); padding-bottom: 0.5rem; margin-bottom: 1rem;">
          <h3 style="font-size: 1.1rem; color: var(--primary-navy); font-weight: 800; margin: 0;">
            🎁 VERIFIED SUPPORT AVAILABLE
          </h3>
          <span style="font-size: 0.8rem; color: var(--text-muted); font-weight: 600;">
            ${secCSteps.length} support item${secCSteps.length !== 1 ? 's' : ''}
          </span>
        </div>

        <div style="display: flex; flex-direction: column; gap: 1.25rem;">
          ${Array.from(supportByOppMap.entries()).map(([oppName, items]) => `
            <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: 12px; padding: 1.1rem;">
              <div style="font-size: 0.95rem; font-weight: 800; color: #6b21a8; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.4rem;">
                <span>🏛️</span> ${oppName}
              </div>
              <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 0.85rem;">
                ${items.map(step => `
                  <div style="background: #fcf5ff; border: 1px solid #e9d5ff; border-radius: 10px; padding: 0.85rem;">
                    <div style="font-size: 0.75rem; font-weight: 800; color: #6b21a8; text-transform: uppercase; margin-bottom: 0.35rem;">
                      🎁 ${step.display_label || step.support_type}
                    </div>
                    <div style="font-size: 0.825rem; color: #581c87; line-height: 1.4; margin-bottom: 0.65rem;">
                      ${step.benefit_summary || ''}
                    </div>
                    ${step.official_source_url ? `
                      <a href="${step.official_source_url}" target="_blank" rel="noopener noreferrer" style="font-size: 0.775rem; color: #7e22ce; font-weight: 600; text-decoration: none;">
                        Official Scheme Source ↗
                      </a>
                    ` : ''}
                  </div>
                `).join("")}
              </div>
            </div>
          `).join("")}
        </div>
      </div>
    `;

    // --- SECTION G: YOUR REQUIREMENT PROGRESS (COMPACT SCHEME-GROUPED LEDGER) ---
    const secBSteps = secB.steps || [];

    // Group requirements by source scheme
    const reqsBySchemeMap = new Map();
    secBSteps.forEach(step => {
      const oppName = step.source_opportunity_name || step.opportunity_name || step.source_opportunity_id || 'Matched Scheme';
      if (!reqsBySchemeMap.has(oppName)) {
        reqsBySchemeMap.set(oppName, {
          opportunity_id: step.source_opportunity_id || step.opportunity_id,
          opportunity_name: oppName,
          steps: []
        });
      }
      reqsBySchemeMap.get(oppName).steps.push(step);
    });

    const schemeLedgerGroupsHtml = Array.from(reqsBySchemeMap.values()).map(group => {
      const completedCount = group.steps.filter(s => s.status === "COMPLETED").length;
      const actionNeededCount = group.steps.filter(s => s.status === "ACTION_NEEDED").length;
      const needToConfirmCount = group.steps.filter(s => s.status === "NEEDS_CONFIRMATION").length;

      return `
        <details class="scheme-ledger-group" style="background: #ffffff; border: 1px solid var(--border-color); border-radius: 12px; padding: 0.85rem 1.1rem; margin-bottom: 0.75rem;" open>
          <summary style="cursor: pointer; display: flex; justify-content: space-between; align-items: center; list-style: none; user-select: none;">
            <div>
              <div style="font-size: 0.95rem; font-weight: 800; color: var(--primary-navy); display: flex; align-items: center; gap: 0.4rem;">
                <span>🏛️</span> ${group.opportunity_name}
              </div>
              <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 0.2rem; font-weight: 600;">
                <span style="color: #15803d;">${completedCount} Completed</span> • 
                <span style="color: #b45309;">${actionNeededCount} Action Needed</span> • 
                <span style="color: #1d4ed8;">${needToConfirmCount} Need to Confirm</span>
              </div>
            </div>
            <span style="font-size: 0.8rem; color: var(--accent-blue); font-weight: 700; background: #eff6ff; padding: 0.25rem 0.6rem; border-radius: 6px; border: 1px solid #bfdbfe;">
              ${group.steps.length} requirement${group.steps.length !== 1 ? 's' : ''} ▼
            </span>
          </summary>

          <div style="display: flex; flex-direction: column; gap: 0.5rem; margin-top: 0.75rem; border-top: 1px solid #f1f5f9; padding-top: 0.75rem;">
            ${group.steps.map(step => {
              const isComp = step.status === "COMPLETED";
              const isAct = step.status === "ACTION_NEEDED";
              
              let statusIcon = "✓";
              let badgeStyle = "background: #dcfce7; color: #15803d; border: 1px solid #86efac;";
              let machineLabel = "Completed";
              let rowBg = "#f0fdf4";
              let borderLeftCol = "#138808";

              if (!isComp) {
                if (isAct) {
                  statusIcon = "!";
                  badgeStyle = "background: #fef3c7; color: #b45309; border: 1px solid #fde68a;";
                  machineLabel = "Action Needed";
                  rowBg = "#ffffff";
                  borderLeftCol = "#d97706";
                } else {
                  statusIcon = "?";
                  badgeStyle = "background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe;";
                  machineLabel = "Need to Confirm";
                  rowBg = "#ffffff";
                  borderLeftCol = "#2563eb";
                }
              }

              return `
                <div style="background: ${rowBg}; border: 1px solid var(--border-color); border-left: 3px solid ${borderLeftCol}; border-radius: 8px; padding: 0.6rem 0.85rem;">
                  <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; flex: 1; min-width: 220px;">
                      <span style="font-size: 0.7rem; font-weight: 800; padding: 0.1rem 0.4rem; border-radius: 4px; ${badgeStyle}">
                        ${statusIcon} ${machineLabel}
                      </span>
                      <span style="font-size: 0.875rem; font-weight: 700; color: var(--primary-navy);">
                        ${step.display_title || step.title}
                      </span>
                      <span style="font-size: 0.7rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">
                        [${step.requirement_type || 'REQUIREMENT'}]
                      </span>
                    </div>

                    <details style="display: inline-block;">
                      <summary style="cursor: pointer; font-size: 0.775rem; color: var(--accent-blue); font-weight: 700; outline: none;">
                        View Details
                      </summary>
                      <div style="margin-top: 0.4rem; padding: 0.5rem 0.75rem; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 0.78rem; color: var(--primary-navy); display: flex; flex-direction: column; gap: 0.3rem;">
                        <div><strong>Requirement ID:</strong> <code>${step.node_id || step.step_id}</code></div>
                        <div><strong>Source Scheme:</strong> ${step.source_opportunity_name || step.opportunity_name}</div>
                        ${(step.requirement_type === 'ENTITY_REGISTRATION' || step.supporting_text) ? `
                          <div style="color: #b45309; font-weight: 600;">${step.supporting_text || 'Exact registration type needs confirmation.'}</div>
                        ` : ''}
                        ${SHARED_ARTIFACT_TYPES.has(step.requirement_type) ? `
                          <div><strong>Artifact Available:</strong> <span style="font-weight: 700; color: ${(this.userArtifactsList || []).some(a => a.artifact_type === step.requirement_type) ? '#15803d' : '#475569'};">${(this.userArtifactsList || []).some(a => a.artifact_type === step.requirement_type) ? 'Yes ✓' : 'No'}</span></div>
                        ` : ''}
                        <div><strong>Basis:</strong> ${step.ui_label || step.basis}</div>
                        <div style="display: flex; gap: 0.75rem; align-items: center; margin-top: 0.25rem; flex-wrap: wrap;">
                          <button class="btn-outline" onclick="myOpportunities.toggleGoalRequirement('${step.node_id}', ${isComp})" style="font-size: 0.75rem; padding: 0.25rem 0.6rem; border-color: ${isComp ? '#dc2626' : '#138808'}; color: ${isComp ? '#dc2626' : '#138808'}; background: #ffffff;">
                            ${isComp ? '↺ Reopen Requirement' : '✓ Mark as Completed'}
                          </button>
                          ${step.official_source_url ? `
                            <a href="${step.official_source_url}" target="_blank" rel="noopener noreferrer" style="font-size: 0.75rem; color: var(--accent-blue); font-weight: 600; text-decoration: none;">
                              Official Scheme Source ↗
                            </a>
                          ` : ''}
                        </div>
                      </div>
                    </details>
                  </div>
                </div>
              `;
            }).join("")}
          </div>
        </details>
      `;
    }).join("");

    const reqProgressHtml = `
      <div style="margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--border-color); padding-bottom: 0.5rem; margin-bottom: 1rem;">
          <div>
            <h3 style="font-size: 1.1rem; color: var(--primary-navy); font-weight: 800; margin: 0;">
              📋 YOUR REQUIREMENT PROGRESS
            </h3>
            <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 0.15rem;">
              Full requirement ledger grouped by scheme • Where do I currently stand?
            </div>
          </div>
          <span style="font-size: 0.8rem; color: var(--text-muted); font-weight: 600;">
            ${secBSteps.length} canonical requirement${secBSteps.length !== 1 ? 's' : ''}
          </span>
        </div>

        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
          ${schemeLedgerGroupsHtml}
        </div>
      </div>
    `;

    // --- SECTION H: GOAL DESTINATION / PATHWAY END ---
    const destinationHtml = `
      <div style="background: #f0fdf4; border: 1.5px solid #bbf7d0; border-radius: 16px; padding: 1.75rem; text-align: center; margin-bottom: 1.5rem;">
        <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">🏁</div>
        <span class="badge badge-active" style="margin-bottom: 0.5rem;">YOUR GOAL DESTINATION</span>
        <h3 style="font-size: 1.3rem; color: #14532d; font-weight: 800; margin: 0.35rem 0 0.5rem 0;">
          ${goalInfo.display_label || goalInfo.raw_text || 'General Business Readiness'}
        </h3>
        <p style="font-size: 0.9rem; color: #166534; max-width: 680px; margin: 0 auto; line-height: 1.5;">
          Progress toward your goal updates dynamically as you confirm completed requirements and refine your profile information.
        </p>
      </div>
    `;

    return `
      <div class="goal-pathway-vertical-container" style="display: flex; flex-direction: column; gap: 0.5rem;">
        ${goalSectionHtml}
        ${whereYouAreHtml}
        ${gapSummaryHtml}
        ${nextActionsHtml}
        ${oppsHtml}
        ${supportHtml}
        ${reqProgressHtml}
        ${destinationHtml}
      </div>
    `;
  }

  /* REBUILT OPPORTUNITY-CENTRIC GRAPH RENDERER */
  async switchGraphMode(mode) {
    this.graphSelectionMode = mode;
    const profile = (typeof window.app.getProfile === "function" ? window.app.getProfile() : window.app.userProfile) || {};
    try {
      const res = await fetch("/api/graph/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          profile: profile,
          selection_mode: mode
        })
      });
      if (res.ok) {
        this.graphData = await res.json();
        this.graphError = null;
      } else {
        this.graphError = `Graph server returned status ${res.status}`;
      }
    } catch (e) {
      console.error("Failed to switch graph mode:", e);
      this.graphError = e.message;
    }
    this.render();
    setTimeout(() => this.fitGraphView(), 60);
  }

  toggleOppReqs(oppId) {
    if (!this.expandedOppReqs) this.expandedOppReqs = {};
    this.expandedOppReqs[oppId] = !this.expandedOppReqs[oppId];
    this.render();
    setTimeout(() => this.fitGraphView(), 60);
  }

  toggleOppBens(oppId) {
    if (!this.expandedOppBens) this.expandedOppBens = {};
    this.expandedOppBens[oppId] = !this.expandedOppBens[oppId];
    this.render();
    setTimeout(() => this.fitGraphView(), 60);
  }

  toggleReqShowAll(oppId) {
    if (!this.expandedReqShowAll) this.expandedReqShowAll = {};
    this.expandedReqShowAll[oppId] = !this.expandedReqShowAll[oppId];
    this.render();
    setTimeout(() => this.fitGraphView(), 60);
  }

  fitGraphView() {
    const container = document.getElementById("graphCanvasWrapper");
    const stage = document.getElementById("graphZoomStage");
    if (!container || !stage) return;

    const containerW = container.clientWidth || 1000;
    const containerH = container.clientHeight || 600;

    const elements = stage.querySelectorAll(".graph-profile-box, .graph-opp-card, .graph-expanded-panel");
    if (!elements || elements.length === 0) return;

    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;

    elements.forEach(el => {
      const x = parseFloat(el.getAttribute("data-x") || el.offsetLeft);
      const y = parseFloat(el.getAttribute("data-y") || el.offsetTop);
      const w = el.offsetWidth || 270;
      const h = el.offsetHeight || 120;

      if (x < minX) minX = x;
      if (y < minY) minY = y;
      if (x + w > maxX) maxX = x + w;
      if (y + h > maxY) maxY = y + h;
    });

    if (minX === Infinity) { minX = 0; maxX = 1200; minY = 0; maxY = 600; }

    const padding = 60;
    const contentW = (maxX - minX) + (padding * 2);
    const contentH = (maxY - minY) + (padding * 2);

    const scaleX = containerW / contentW;
    const scaleY = containerH / contentH;
    let scale = Math.min(scaleX, scaleY);
    scale = Math.max(0.55, Math.min(scale, 1.15));

    const contentCenterX = minX - padding + (contentW / 2);
    const contentCenterY = minY - padding + (contentH / 2);

    const viewCenterX = containerW / 2;
    const viewCenterY = containerH / 2;

    this.graphZoom = scale;
    this.graphPanX = viewCenterX - (contentCenterX * scale);
    this.graphPanY = viewCenterY - (contentCenterY * scale);

    this.applyGraphTransform();
  }

  resetGraphView() {
    this.graphZoom = 1.0;
    this.graphPanX = 30;
    this.graphPanY = 30;
    this.applyGraphTransform();
  }

  zoomGraph(delta) {
    this.graphZoom = Math.min(Math.max(0.4, (this.graphZoom || 1.0) + delta), 2.5);
    this.applyGraphTransform();
  }

  applyGraphTransform() {
    const stage = document.getElementById("graphZoomStage");
    if (stage) {
      stage.style.transform = `translate(${this.graphPanX || 0}px, ${this.graphPanY || 0}px) scale(${this.graphZoom || 1.0})`;
    }
  }

  attachCanvasPanListeners() {
    const wrapper = document.getElementById("graphCanvasWrapper");
    if (!wrapper || wrapper.dataset.panAttached) return;
    wrapper.dataset.panAttached = "true";

    let isPanning = false;
    let startX = 0, startY = 0;
    let initialPanX = 0, initialPanY = 0;

    wrapper.addEventListener("mousedown", (e) => {
      if (e.target.closest("button, input, select, .graph-mode-pill, a")) return;
      isPanning = true;
      this.dragMoved = false;
      startX = e.clientX;
      startY = e.clientY;
      initialPanX = this.graphPanX || 0;
      initialPanY = this.graphPanY || 0;
      wrapper.style.cursor = "grabbing";
    });

    window.addEventListener("mousemove", (e) => {
      if (!isPanning) return;
      const dx = e.clientX - startX;
      const dy = e.clientY - startY;
      if (Math.abs(dx) > 4 || Math.abs(dy) > 4) {
        this.dragMoved = true;
      }
      this.graphPanX = initialPanX + dx;
      this.graphPanY = initialPanY + dy;
      this.applyGraphTransform();
    });

    window.addEventListener("mouseup", () => {
      if (isPanning) {
        isPanning = false;
        wrapper.style.cursor = "grab";
      }
    });

    window.addEventListener("resize", () => {
      this.fitGraphView();
    });
  }

  renderGraphView(graphData) {
    console.log('SchemeMitra opportunity graph runtime');

    if (this.graphError) {
      return `
        <div class="graph-viewport-card">
          <div style="padding: 3rem 1.5rem; text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">⚠️</div>
            <h3 style="color: var(--primary-navy); margin-bottom: 0.5rem;">We couldn't load your opportunity graph</h3>
            <p style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 1.5rem;">${this.graphError}</p>
            <button class="btn-primary" onclick="myOpportunities.switchGraphMode('${this.graphSelectionMode || 'TOP_3'}')">Retry Graph Generation</button>
          </div>
        </div>
      `;
    }

    const mode = this.graphSelectionMode || "TOP_3";
    const profile = (window.app && window.app.userProfile) || (this.analysisResult && this.analysisResult.profile) || {};

    let candidateOpps = (this.analysisResult && this.analysisResult.best_matches) || [];

    if (!candidateOpps || candidateOpps.length === 0) {
      const rawNodes = (graphData && graphData.nodes) || (this.graphData && this.graphData.nodes) || [];
      candidateOpps = rawNodes.filter(n => n.type === "OPPORTUNITY").map(n => ({
        opportunity_id: n.opportunity_id || n.id.replace('opp_', ''),
        opportunity_name: n.label,
        eligibility_status: n.status === "Eligible" ? "ELIGIBLE" : "POTENTIALLY_ELIGIBLE",
        benefit_summary: n.metadata && n.metadata.benefit_summary,
        support_types: n.metadata && n.metadata.support_types
      }));
    }

    candidateOpps = candidateOpps.filter(o => (o.eligibility_status || o.status) !== "NOT_ELIGIBLE");

    let limit = 3;
    if (mode === "TOP_5") limit = 5;
    if (mode === "ALL_RELEVANT") limit = Math.max(1, candidateOpps.length);

    const selectedOpps = candidateOpps.slice(0, limit);

    if (selectedOpps.length === 0) {
      return `
        <div class="graph-viewport-card">
          <div style="padding: 3rem 1.5rem; text-align: center; color: var(--text-muted);">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">🕸️</div>
            <h3 style="color: var(--primary-navy); margin-bottom: 0.5rem;">No relevant opportunities yet</h3>
            <p style="font-size: 0.9rem;">Complete your profile or review opportunities that need more information to populate your graph.</p>
          </div>
        </div>
      `;
    }

    const profileLines = [];

    if (profile.gender || profile.age) {
      const g = profile.gender || '';
      const a = profile.age ? `${profile.age} yrs` : '';
      profileLines.push(`👤 ${[g, a].filter(Boolean).join(', ')}`);
    }

    if (profile.state) {
      profileLines.push(`📍 ${profile.state}`);
    }

    if (profile.sector || profile.target_sector) {
      const secLabel = window.i18n ? window.i18n.getSectorLabel(profile.sector || profile.target_sector) : (profile.sector || profile.target_sector);
      profileLines.push(`🏢 ${secLabel}`);
    }

    if (profile.annual_income !== null && profile.annual_income !== undefined && profile.annual_income > 0) {
      profileLines.push(`💰 Annual Income: ₹${Number(profile.annual_income).toLocaleString('en-IN')}`);
    }

    if (profile.available_capital !== null && profile.available_capital !== undefined && profile.available_capital > 0) {
      profileLines.push(`💵 Available Capital: ₹${Number(profile.available_capital).toLocaleString('en-IN')}`);
    }

    if (profile.project_cost !== null && profile.project_cost !== undefined && profile.project_cost > 0) {
      profileLines.push(`🏗️ Project Cost: ₹${Number(profile.project_cost).toLocaleString('en-IN')}`);
    }

    if (profile.business_goal) {
      profileLines.push(`🏁 Goal: ${this.formatBusinessGoal(profile.business_goal)}`);
    }

    const colX = {
      PROFILE: 40,
      OPPORTUNITY: 380,
      DETAILS: 730
    };

    if (!this.expandedOppReqs) this.expandedOppReqs = {};
    if (!this.expandedOppBens) this.expandedOppBens = {};
    if (!this.expandedReqShowAll) this.expandedReqShowAll = {};

    let currentY = 40;
    const oppGap = 30;

    const oppLayouts = [];

    selectedOpps.forEach(opp => {
      const oppId = opp.opportunity_id;
      const isReqExpanded = !!this.expandedOppReqs[oppId];
      const isBenExpanded = !!this.expandedOppBens[oppId];
      const isShowAllReqs = !!this.expandedReqShowAll[oppId];

      let oppReqs = [];
      if (opp.scheme_gaps && opp.scheme_gaps.length > 0) {
        oppReqs = opp.scheme_gaps.map((g, idx) => ({
          id: `req_${oppId}_${idx}`,
          label: g,
          status: g.includes('Completed') || g.includes('✓') ? '✓ Completed' : (g.includes('Action') || g.includes('!') ? '! Action Needed' : '? Need to Confirm')
        }));
      } else if (graphData && graphData.nodes) {
        oppReqs = graphData.nodes.filter(n => n.type === 'REQUIREMENT' && n.metadata && n.metadata.connected_opportunities && n.metadata.connected_opportunities.includes(oppId)).map(n => ({
          id: n.id,
          label: n.label,
          status: n.status || '? Need to Confirm'
        }));
      }

      // Filter OUT satisfied/completed requirements for the user-facing Opportunity Graph
      oppReqs = oppReqs.filter(r => {
        const s = String(r.status || '');
        return !s.includes('Completed') && !s.includes('✓') && !s.includes('PASSED');
      });

      let supportTypes = opp.support_types || [];
      if ((!supportTypes || supportTypes.length === 0) && graphData && graphData.nodes) {
        supportTypes = graphData.nodes.filter(n => n.type === 'SUPPORT' && n.metadata && n.metadata.connected_opportunities && n.metadata.connected_opportunities.includes(oppId)).map(n => n.metadata.support_type || n.label);
      }

      const visibleReqs = isShowAllReqs ? oppReqs : oppReqs.slice(0, 4);
      const remainingReqCount = oppReqs.length - visibleReqs.length;

      const oppCardH = 150;
      const reqPanelH = isReqExpanded ? 50 + (visibleReqs.length * 48) + (remainingReqCount > 0 || isShowAllReqs ? 36 : 0) : 0;
      const benPanelH = isBenExpanded ? 50 + (supportTypes.length * 45) : 0;

      const clusterH = Math.max(oppCardH, reqPanelH, benPanelH);
      const oppY = currentY;
      const reqY = oppY;

      let benX = colX.DETAILS;
      let benY = oppY;
      if (isReqExpanded && isBenExpanded) {
        benX = colX.DETAILS + 290;
      }

      oppLayouts.push({
        opp: opp,
        oppId: oppId,
        oppY: oppY,
        reqY: reqY,
        benX: benX,
        benY: benY,
        clusterH: clusterH,
        isReqExpanded: isReqExpanded,
        isBenExpanded: isBenExpanded,
        isShowAllReqs: isShowAllReqs,
        oppReqs: oppReqs,
        visibleReqs: visibleReqs,
        remainingReqCount: remainingReqCount,
        supportTypes: supportTypes
      });

      currentY += clusterH + oppGap;
    });

    const totalCanvasH = Math.max(550, currentY + 40);

    const maxDetailX = oppLayouts.some(l => l.isReqExpanded && l.isBenExpanded) ? colX.DETAILS + 560 : (oppLayouts.some(l => l.isReqExpanded || l.isBenExpanded) ? colX.DETAILS + 290 : colX.OPPORTUNITY + 300);
    const totalCanvasW = Math.max(1200, maxDetailX + 60);

    const profileY = Math.max(40, (totalCanvasH - 240) / 2);

    const svgPaths = [];

    oppLayouts.forEach(layout => {
      const x1 = colX.PROFILE + 270;
      const y1 = profileY + 120;
      const x2 = colX.OPPORTUNITY;
      const y2 = layout.oppY + 65;

      const ctrlDist = Math.min(80, Math.abs(x2 - x1) / 2);
      svgPaths.push(`<path d="M ${x1} ${y1} C ${x1 + ctrlDist} ${y1}, ${x2 - ctrlDist} ${y2}, ${x2} ${y2}" fill="none" stroke="#2563eb" stroke-width="2.5" opacity="0.8" />`);

      if (layout.isReqExpanded) {
        const rx1 = colX.OPPORTUNITY + 280;
        const ry1 = layout.oppY + 65;
        const rx2 = colX.DETAILS;
        const ry2 = layout.reqY + 40;
        svgPaths.push(`<path d="M ${rx1} ${ry1} C ${rx1 + 40} ${ry1}, ${rx2 - 40} ${ry2}, ${rx2} ${ry2}" fill="none" stroke="#d97706" stroke-width="2" stroke-dasharray="5,4" opacity="0.85" />`);
      }

      if (layout.isBenExpanded) {
        const bx1 = colX.OPPORTUNITY + 280;
        const by1 = layout.oppY + 105;
        const bx2 = layout.benX;
        const by2 = layout.benY + 40;
        svgPaths.push(`<path d="M ${bx1} ${by1} C ${bx1 + 40} ${by1}, ${bx2 - 40} ${by2}, ${bx2} ${by2}" fill="none" stroke="#7e22ce" stroke-width="2" stroke-dasharray="3,3" opacity="0.85" />`);
      }
    });

    const profileBoxHtml = `
      <div class="graph-profile-box" data-x="${colX.PROFILE}" data-y="${profileY}" style="left: ${colX.PROFILE}px; top: ${profileY}px;">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.6rem; border-bottom: 1px solid #bae6fd; padding-bottom: 0.5rem;">
          <span style="font-size: 1.3rem;">👤</span>
          <h4 style="margin: 0; font-size: 0.95rem; color: var(--primary-navy); font-weight: 800; text-transform: uppercase;">YOUR PROFILE</h4>
        </div>
        <div style="display: flex; flex-direction: column; gap: 0.45rem; font-size: 0.825rem; color: var(--primary-navy); font-weight: 600;">
          ${profileLines.map(line => `<div>${line}</div>`).join('')}
        </div>
      </div>
    `;

    const oppsHtml = oppLayouts.map(layout => {
      const opp = layout.opp;
      const oppId = layout.oppId;

      const st = opp.eligibility_status || opp.status || 'POTENTIALLY_ELIGIBLE';
      let badgeStyle = 'background: #fffbe6; color: #b45309; border: 1px solid #fde68a;';
      let badgeText = 'Potential Match';

      if (st === 'ELIGIBLE') {
        badgeStyle = 'background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0;';
        badgeText = 'Eligible';
      } else if (st === 'NEEDS_VERIFICATION') {
        badgeStyle = 'background: #f3e8ff; color: #7e22ce; border: 1px solid #d8b4fe;';
        badgeText = 'Needs Verification';
      }

      const nameObj = window.i18n ? window.i18n.getLocalizedSchemeName(opp) : { official: opp.opportunity_name || oppId, localized: null };

      const cardHtml = `
        <div class="graph-opp-card" data-x="${colX.OPPORTUNITY}" data-y="${layout.oppY}" style="left: ${colX.OPPORTUNITY}px; top: ${layout.oppY}px;">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.4rem; margin-bottom: 0.35rem;">
            <span style="font-size: 0.7rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">OPPORTUNITY</span>
            <span style="font-size: 0.7rem; font-weight: 800; padding: 0.15rem 0.5rem; border-radius: 4px; ${badgeStyle}">${badgeText}</span>
          </div>

          <h4 onclick="if(!myOpportunities.dragMoved) app.showSchemeDetail('${oppId}', 'dashboard', 'graph')"
              style="margin: 0 0 0.5rem 0; font-size: 0.95rem; font-weight: 800; color: var(--primary-navy); cursor: pointer; line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;"
              title="${nameObj.official}">
            🎯 ${nameObj.official}
          </h4>

          <div style="display: flex; gap: 0.4rem; margin-top: 0.65rem; border-top: 1px solid var(--border-color); padding-top: 0.5rem;">
            <button class="graph-btn-action ${layout.isReqExpanded ? 'active' : ''}" onclick="if(!myOpportunities.dragMoved) myOpportunities.toggleOppReqs('${oppId}')">
              📋 Requirements ${layout.isReqExpanded ? '▲' : '▼'}
            </button>
            <button class="graph-btn-action ${layout.isBenExpanded ? 'active' : ''}" onclick="if(!myOpportunities.dragMoved) myOpportunities.toggleOppBens('${oppId}')">
              🎁 Benefits ${layout.isBenExpanded ? '▲' : '▼'}
            </button>
          </div>
        </div>
      `;

      let reqPanelHtml = '';
      if (layout.isReqExpanded) {
        reqPanelHtml = `
          <div class="graph-expanded-panel" data-x="${colX.DETAILS}" data-y="${layout.reqY}" style="left: ${colX.DETAILS}px; top: ${layout.reqY}px;">
            <div style="font-size: 0.825rem; font-weight: 800; color: var(--primary-navy); border-bottom: 1px solid var(--border-color); padding-bottom: 0.4rem; display: flex; justify-content: space-between; align-items: center;">
              <span>📋 Outstanding Requirements (${layout.oppReqs.length})</span>
              <button class="close-modal" onclick="myOpportunities.toggleOppReqs('${oppId}')" style="position: static; width: 22px; height: 22px; font-size: 0.8rem;">&times;</button>
            </div>
            <div style="display: flex; flex-direction: column; gap: 0.45rem;">
              ${layout.oppReqs.length > 0 ? layout.visibleReqs.map(r => {
                const isAct = r.status.includes('Action') || r.status.includes('!');
                const icon = isAct ? '!' : '?';
                const iconBg = isAct ? '#fffbe6; color: #b45309;' : '#eff6ff; color: #1d4ed8;';
                return `
                  <div style="display: flex; align-items: flex-start; gap: 0.4rem; font-size: 0.8rem; background: #f8fafc; padding: 0.45rem 0.6rem; border-radius: 6px; border: 1px solid var(--border-color);">
                    <span style="font-weight: 800; font-size: 0.75rem; padding: 0.05rem 0.3rem; border-radius: 4px; background: ${iconBg}">${icon}</span>
                    <span style="color: var(--primary-navy); font-weight: 600; line-height: 1.25;">${r.label}</span>
                  </div>
                `;
              }).join('') : '<div style="font-size: 0.8rem; color: var(--text-muted); font-style: italic;">No outstanding requirements</div>'}
              ${layout.remainingReqCount > 0 ? `
                <button onclick="myOpportunities.toggleReqShowAll('${oppId}')" style="background: none; border: none; color: var(--accent-blue); font-size: 0.775rem; font-weight: 700; cursor: pointer; text-align: left; padding: 0.2rem 0;">
                  + ${layout.remainingReqCount} more requirement${layout.remainingReqCount > 1 ? 's' : ''}...
                </button>
              ` : (layout.isShowAllReqs && layout.oppReqs.length > 4 ? `
                <button onclick="myOpportunities.toggleReqShowAll('${oppId}')" style="background: none; border: none; color: var(--accent-blue); font-size: 0.775rem; font-weight: 700; cursor: pointer; text-align: left; padding: 0.2rem 0;">
                  Show less
                </button>
              ` : '')}
            </div>
          </div>
        `;
      }

      let benPanelHtml = '';
      if (layout.isBenExpanded) {
        benPanelHtml = `
          <div class="graph-expanded-panel" data-x="${layout.benX}" data-y="${layout.benY}" style="left: ${layout.benX}px; top: ${layout.benY}px;">
            <div style="font-size: 0.825rem; font-weight: 800; color: #6b21a8; border-bottom: 1px solid var(--border-color); padding-bottom: 0.4rem; display: flex; justify-content: space-between; align-items: center;">
              <span>🎁 Verified Benefits / Support</span>
              <button class="close-modal" onclick="myOpportunities.toggleOppBens('${oppId}')" style="position: static; width: 22px; height: 22px; font-size: 0.8rem;">&times;</button>
            </div>
            <div style="display: flex; flex-direction: column; gap: 0.45rem;">
              ${layout.supportTypes.length > 0 ? layout.supportTypes.map(st => {
                const label = window.i18n ? window.i18n.getSupportTypeLabel(st) : st;
                return `
                  <div style="display: flex; align-items: center; gap: 0.45rem; font-size: 0.8rem; background: #fcf5ff; padding: 0.5rem 0.65rem; border-radius: 6px; border: 1px solid #e9d5ff; color: #6b21a8; font-weight: 700;">
                    <span>${label}</span>
                  </div>
                `;
              }).join('') : '<div style="font-size: 0.8rem; color: var(--text-muted); font-style: italic;">Verified details unavailable</div>'}
            </div>
          </div>
        `;
      }

      return cardHtml + '\n' + reqPanelHtml + '\n' + benPanelHtml;
    }).join('\n');

    setTimeout(() => {
      this.attachCanvasPanListeners();
      this.fitGraphView();
    }, 50);

    return `
      <div class="graph-viewport-card">
        <!-- Header & Selection Controls -->
        <div class="graph-header-toolbar">
          <div>
            <h3 style="color: var(--primary-navy); margin: 0 0 0.25rem 0; font-size: 1.25rem;">Opportunity Graph</h3>
            <p style="color: var(--text-muted); font-size: 0.875rem; margin: 0;">
              See how your confirmed profile connects directly to matched opportunities, requirements, and support benefits.
            </p>
          </div>

          <div style="display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;">
            <button class="graph-mode-pill ${mode === 'TOP_3' ? 'active' : ''}" onclick="myOpportunities.switchGraphMode('TOP_3')">Top 3 Best Matches</button>
            <button class="graph-mode-pill ${mode === 'TOP_5' ? 'active' : ''}" onclick="myOpportunities.switchGraphMode('TOP_5')">Top 5</button>
            <button class="graph-mode-pill ${mode === 'ALL_RELEVANT' ? 'active' : ''}" onclick="myOpportunities.switchGraphMode('ALL_RELEVANT')">All Relevant</button>

            <div style="display: flex; gap: 0.35rem; margin-left: 0.5rem;">
              <button class="btn-outline" onclick="myOpportunities.zoomGraph(0.15)" style="min-height: 38px; padding: 0.3rem 0.65rem; font-size: 0.85rem;" title="Zoom In">🔍 +</button>
              <button class="btn-outline" onclick="myOpportunities.zoomGraph(-0.15)" style="min-height: 38px; padding: 0.3rem 0.65rem; font-size: 0.85rem;" title="Zoom Out">🔍 -</button>
              <button class="btn-outline" onclick="myOpportunities.fitGraphView()" style="min-height: 38px; padding: 0.3rem 0.75rem; font-size: 0.85rem; font-weight: 600; color: var(--accent-blue);" title="Fit View to Content">⤢ Fit View</button>
              <button class="btn-outline" onclick="myOpportunities.resetGraphView()" style="min-height: 38px; padding: 0.3rem 0.75rem; font-size: 0.85rem;" title="Reset View">↺ Reset</button>
            </div>
          </div>
        </div>

        <!-- Interactive Canvas Viewport -->
        <div class="graph-canvas-wrapper" id="graphCanvasWrapper" style="cursor: grab;">
          <div class="graph-zoom-stage" id="graphZoomStage" style="width: ${totalCanvasW}px; height: ${totalCanvasH}px; transform: translate(${this.graphPanX || 30}px, ${this.graphPanY || 30}px) scale(${this.graphZoom || 1.0});">
            <svg width="${totalCanvasW}" height="${totalCanvasH}" style="position: absolute; top: 0; left: 0; pointer-events: none;">
              ${svgPaths.join('\n')}
            </svg>
            ${profileBoxHtml}
            ${oppsHtml}
          </div>
        </div>

        <!-- Simplified Legend -->
        <div class="graph-legend-bar">
          <div style="display: flex; gap: 1.25rem; align-items: center; flex-wrap: wrap;">
            <span><strong>Node Types:</strong></span>
            <span>👤 Your Profile</span>
            <span>🎯 Opportunity</span>
            <span>📋 Requirements</span>
            <span>🎁 Benefits / Support</span>
          </div>
          <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
            <span><strong>Status:</strong></span>
            <span style="color: #047857; font-weight: 600;">🟢 Eligible</span>
            <span style="color: #b45309; font-weight: 600;">🟠 Potential Match</span>
            <span style="color: #7e22ce; font-weight: 600;">🔵 Needs Verification</span>
          </div>
          <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
            <span><strong>Requirement State:</strong></span>
            <span style="color: #b45309; font-weight: 600;">! Action Needed</span>
            <span style="color: #1d4ed8; font-weight: 600;">? Need to Confirm</span>
          </div>
        </div>

        <div style="font-size: 0.8rem; color: var(--text-muted); text-align: right; margin-top: -0.25rem;">
          Only verified connections from official scheme requirements are displayed. Click any opportunity card for scheme details.
        </div>
      </div>
    `;
  }


  openSchemeDetail(opportunityId) {
    app.showSchemeDetail(opportunityId, 'dashboard', this.activeTab);
  }


  renderBestMatchesList(recs) {
    const t = (k) => window.i18n.get(k);

    if (!recs || recs.length === 0) {
      return `
        <div style="background: #ffffff; padding: 2.5rem 1.5rem; border-radius: 12px; text-align: center; color: var(--text-muted);">
          No top matching opportunities currently meet all profile parameters. Review <strong>More Information Needed</strong> schemes to provide missing profile details.
        </div>
      `;
    }

    return `
      <div style="display: flex; flex-direction: column; gap: 1.25rem;">
        ${recs.map((r, idx) => {
          const nameObj = window.i18n.getLocalizedSchemeName(r);
          const titleContent = nameObj.localized
            ? `<span>${nameObj.localized}</span> <span style="font-size:0.85rem; color:var(--text-muted); font-weight:500;">(${nameObj.official})</span>`
            : nameObj.official;
          const supportLabels = (r.support_types || []).map(s => window.i18n.getSupportTypeLabel(s)).join(', ');

          let badgeHtml = '';
          if (r.eligibility_status === 'ELIGIBLE') {
            badgeHtml = `<span class="badge badge-eligible" data-i18n="badge_eligible">${t('badge_eligible')}</span>`;
          } else {
            badgeHtml = `<span class="badge badge-potentially" data-i18n="badge_potentially">${t('badge_potentially')}</span>`;
          }

          const gaps = r.scheme_gaps || r.missing_requirements || [];
          const displayedGaps = gaps.slice(0, 3);
          const remainingCount = gaps.length - displayedGaps.length;

          const isExpanded = !!(this.expandedInlineRoadmaps && this.expandedInlineRoadmaps[r.opportunity_id]);

          return `
            <div class="opp-card ${idx === 0 ? 'best-match' : ''}">
              <div class="opp-card-header">
                <div>
                  <span class="opp-sector-tag">${window.i18n.getSectorLabel(r.primary_sector)}</span>
                  ${idx === 0 ? '<span style="margin-left: 0.5rem; font-size: 0.75rem; font-weight: 800; color: #FF9933; text-transform: uppercase;">#1 Best Match</span>' : ''}
                  <h3 class="opp-title" onclick="app.showSchemeDetail('${r.opportunity_id}', 'dashboard', 'recommended')">
                    ${titleContent}
                  </h3>
                </div>
                ${badgeHtml}
              </div>

              <p class="opp-benefit">${r.benefit_summary || ''}</p>

              ${(r.why_match || []).length > 0 ? `
                <div style="background: var(--emerald-bg); padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem;">
                  <strong style="color: var(--emerald); font-size: 0.85rem;" data-i18n="why_match_title">${t('why_match_title')}</strong>
                  <ul style="margin-left: 1.25rem; font-size: 0.85rem; color: #065f46;">
                    ${r.why_match.map(w => `<li>${w}</li>`).join('')}
                  </ul>
                </div>
              ` : ''}

              ${displayedGaps.length > 0 ? `
                <div class="opp-gaps-summary" style="background: #fffbebf5; border: 1px solid #fde68a; padding: 0.75rem 0.9rem; border-radius: 8px; margin-bottom: 1rem;">
                  <strong style="color: var(--amber); font-size: 0.85rem;">Your next actions:</strong>
                  <ul style="margin-left: 1.25rem; font-size: 0.85rem; color: #92400e; margin-top: 0.25rem;">
                    ${displayedGaps.map(g => `<li>${g}</li>`).join('')}
                  </ul>
                  ${remainingCount > 0 ? `<div style="font-size: 0.8rem; color: #b45309; margin-top: 0.25rem; font-weight: 600;">+${remainingCount} more requirement${remainingCount > 1 ? 's' : ''}</div>` : ''}
                </div>
              ` : ''}

              <div class="opp-meta" style="margin-top: 1rem; display: flex; align-items: center; flex-wrap: wrap; gap: 0.75rem;">
                <span>${t('lbl_support')}: <strong>${supportLabels}</strong></span>
                <div style="margin-left: auto; display: flex; gap: 0.6rem; flex-wrap: wrap;">
                  <button class="btn-outline" onclick="myOpportunities.openSchemeDetail('${r.opportunity_id}')" style="font-size: 0.85rem; padding: 0.4rem 0.85rem;">
                    View Scheme Details
                  </button>
                  <button class="btn-primary" onclick="myOpportunities.toggleInlineRoadmap('${r.opportunity_id}')" style="font-size: 0.85rem; padding: 0.4rem 0.85rem; background: #FF9933;">
                    ${isExpanded ? 'Hide Roadmap Steps' : 'View Roadmap Steps'}
                  </button>
                </div>
              </div>

              ${isExpanded ? this.buildInlineRoadmapHTML(r, window.app.userProfile || {}) : ''}
            </div>
          `;
        }).join('')}
      </div>
    `;
  }

  renderNeedsInfoList(needsInfoOpps) {
    if (!needsInfoOpps || needsInfoOpps.length === 0) {
      return `
        <div style="background: #ffffff; padding: 2.5rem 1.5rem; border-radius: 12px; text-align: center; color: var(--text-muted);">
          No schemes currently require additional profile information.
        </div>
      `;
    }

    return `
      <div style="display: flex; flex-direction: column; gap: 1.25rem;">
        ${needsInfoOpps.map(r => {
          const nameObj = window.i18n.getLocalizedSchemeName(r);
          const titleContent = nameObj.localized
            ? `<span>${nameObj.localized}</span> <span style="font-size:0.85rem; color:var(--text-muted); font-weight:500;">(${nameObj.official})</span>`
            : nameObj.official;

          const missingFacts = r.missing_profile_info || [];
          const isExpanded = !!(this.expandedInlineRoadmaps && this.expandedInlineRoadmaps[r.opportunity_id]);

          return `
            <div class="opp-card">
              <div class="opp-card-header">
                <div>
                  <span class="opp-sector-tag">${window.i18n.getSectorLabel(r.primary_sector)}</span>
                  <h3 class="opp-title" onclick="myOpportunities.openSchemeDetail('${r.opportunity_id}')">
                    ${titleContent}
                  </h3>
                </div>
                <span class="badge" style="background: #fef3c7; color: #b45309; border: 1px solid #fde68a;">More information needed</span>
              </div>

              <p class="opp-benefit">${r.benefit_summary || ''}</p>

              ${missingFacts.length > 0 ? `
                <div class="needs-profile-info-box" style="background: #fffbebf5; border: 1px solid #fde68a; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                  <strong style="color: #b45309; font-size: 0.9rem; display: block; margin-bottom: 0.6rem;">We need a little more information to assess this opportunity:</strong>
                  <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                    ${missingFacts.map(info => {
                      const lower = String(info).toLowerCase();
                      if (lower.includes('is_new_unit') || lower.includes('new micro-enterprise status')) {
                        return `
                          <div style="display: flex; justify-content: space-between; align-items: center; background: #ffffff; padding: 0.6rem 0.85rem; border-radius: 8px; border: 1px solid #fde68a; flex-wrap: wrap; gap: 0.5rem;">
                            <span style="font-size: 0.85rem; font-weight: 600; color: var(--primary-navy);">Is this project for a new unit?</span>
                            <div style="display: flex; gap: 0.5rem;">
                              <button class="btn-outline" style="padding: 0.25rem 0.75rem; font-size: 0.8rem;" onclick="myOpportunities.quickAnswerFact('is_new_unit', true)">[Yes]</button>
                              <button class="btn-outline" style="padding: 0.25rem 0.75rem; font-size: 0.8rem;" onclick="myOpportunities.quickAnswerFact('is_new_unit', false)">[No]</button>
                            </div>
                          </div>
                        `;
                      }
                      if (lower.includes('prior_gov_subsidy') || lower.includes('prior government subsidy')) {
                        return `
                          <div style="display: flex; justify-content: space-between; align-items: center; background: #ffffff; padding: 0.6rem 0.85rem; border-radius: 8px; border: 1px solid #fde68a; flex-wrap: wrap; gap: 0.5rem;">
                            <span style="font-size: 0.85rem; font-weight: 600; color: var(--primary-navy);">Have you already received government subsidy for this unit?</span>
                            <div style="display: flex; gap: 0.5rem;">
                              <button class="btn-outline" style="padding: 0.25rem 0.75rem; font-size: 0.8rem;" onclick="myOpportunities.quickAnswerFact('prior_gov_subsidy', true)">[Yes]</button>
                              <button class="btn-outline" style="padding: 0.25rem 0.75rem; font-size: 0.8rem;" onclick="myOpportunities.quickAnswerFact('prior_gov_subsidy', false)">[No]</button>
                            </div>
                          </div>
                        `;
                      }
                      if (lower.includes('family_pmegp_availed') || lower.includes('family pmegp beneficiary')) {
                        return `
                          <div style="display: flex; justify-content: space-between; align-items: center; background: #ffffff; padding: 0.6rem 0.85rem; border-radius: 8px; border: 1px solid #fde68a; flex-wrap: wrap; gap: 0.5rem;">
                            <span style="font-size: 0.85rem; font-weight: 600; color: var(--primary-navy);">Have you or your spouse already availed PMEGP?</span>
                            <div style="display: flex; gap: 0.5rem;">
                              <button class="btn-outline" style="padding: 0.25rem 0.75rem; font-size: 0.8rem;" onclick="myOpportunities.quickAnswerFact('family_pmegp_availed', true)">[Yes]</button>
                              <button class="btn-outline" style="padding: 0.25rem 0.75rem; font-size: 0.8rem;" onclick="myOpportunities.quickAnswerFact('family_pmegp_availed', false)">[No]</button>
                            </div>
                          </div>
                        `;
                      }
                      return `<div style="font-size: 0.85rem; color: #92400e;">📌 ${this.formatMissingProfileFact(info)}</div>`;
                    }).join('')}
                  </div>
                </div>
              ` : ''}

              <div class="opp-meta" style="justify-content: flex-end; margin-top: 1rem; display: flex; gap: 0.6rem; flex-wrap: wrap;">
                <button class="btn-outline" onclick="myOpportunities.openSchemeDetail('${r.opportunity_id}')" style="font-size: 0.85rem; padding: 0.4rem 0.85rem;">
                  View Scheme Details
                </button>
                <button class="btn-primary" onclick="myOpportunities.toggleInlineRoadmap('${r.opportunity_id}')" style="font-size: 0.85rem; padding: 0.4rem 0.85rem; background: #FF9933;">
                  ${isExpanded ? 'Hide Roadmap Steps' : 'View Roadmap Steps'}
                </button>
              </div>

              ${isExpanded ? this.buildInlineRoadmapHTML(r, window.app.userProfile || {}) : ''}
            </div>
          `;
        }).join('')}
      </div>
    `;
  }

  quickAnswerFact(field, val) {
    if (!window.app.userProfile) window.app.userProfile = {};
    window.app.userProfile[field] = val;
    if (!window.app.userProfile.extra) window.app.userProfile.extra = {};
    window.app.userProfile.extra[field] = val;
    window.app.saveProfileToStorage(window.app.userProfile);
    this.render();
  }

  renderNeedsVerificationList(needsVerif) {
    const t = (k) => window.i18n.get(k);

    if (!needsVerif || needsVerif.length === 0) {
      return `
        <div style="background: #ffffff; padding: 2.5rem 1.5rem; border-radius: 12px; text-align: center; color: var(--text-muted);">
          No schemes currently flagged for verification updates.
        </div>
      `;
    }

    return `
      <div style="display: flex; flex-direction: column; gap: 1.25rem;">
        <div style="background: #f3e8ff; border: 1px solid #d8b4fe; padding: 0.85rem; border-radius: 8px; color: #6b21a8; font-size: 0.875rem;" data-i18n="needs_verification_notice">
          ${t('needs_verification_notice')}
        </div>

        ${needsVerif.map(v => {
          const nameObj = window.i18n.getLocalizedSchemeName(v);
          const titleContent = nameObj.localized
            ? `<span>${nameObj.localized}</span> <span style="font-size:0.85rem; color:var(--text-muted); font-weight:500;">(${nameObj.official})</span>`
            : nameObj.official;

          const isExpanded = !!(this.expandedInlineRoadmaps && this.expandedInlineRoadmaps[v.opportunity_id]);

          return `
            <div class="opp-card">
              <div class="opp-card-header">
                <h3 class="opp-title" onclick="myOpportunities.openSchemeDetail('${v.opportunity_id}')">${titleContent}</h3>
                <span class="badge badge-verification" data-i18n="badge_needs_verification">${t('badge_needs_verification')}</span>
              </div>
              <p style="font-size: 0.875rem; color: var(--text-muted);">${v.lifecycle_warning || 'Scheme guideline period reached verification milestone.'}</p>
              ${v.official_source_url ? `
                <div style="margin-top: 0.5rem; font-size: 0.85rem;">
                  Official Source: <a href="${v.official_source_url}" target="_blank" rel="noopener" style="color: var(--accent-blue); word-break: break-all;">${v.official_source_url} ↗</a>
                </div>
              ` : ''}
              <div class="opp-meta" style="justify-content: flex-end; margin-top: 1rem; display: flex; gap: 0.6rem; flex-wrap: wrap;">
                <button class="btn-outline" onclick="myOpportunities.openSchemeDetail('${v.opportunity_id}')" style="font-size: 0.85rem; padding: 0.4rem 0.85rem;">
                  View Scheme Details
                </button>
                <button class="btn-primary" onclick="myOpportunities.toggleInlineRoadmap('${v.opportunity_id}')" style="font-size: 0.85rem; padding: 0.4rem 0.85rem; background: #FF9933;">
                  ${isExpanded ? 'Hide Roadmap Steps' : 'View Roadmap Steps'}
                </button>
              </div>

              ${isExpanded ? this.buildInlineRoadmapHTML(v, window.app.userProfile || {}) : ''}
            </div>
          `;
        }).join('')}
      </div>
    `;
  }
}

window.myOpportunities = new MyOpportunitiesComponent();
