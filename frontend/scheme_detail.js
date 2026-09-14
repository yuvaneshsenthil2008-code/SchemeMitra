/**
 * SchemeMitra v2 — Dedicated Scheme Detail & Pathway Component
 * Manages full-screen rendering of scheme metadata, personalized match evaluation, M2 pathway, and Application Guide.
 */

class SchemeDetailComponent {
  constructor() {
    this.opportunityId = null;
    this.returnPage = "explore";
    this.returnTab = "recommended";
    this.schemeData = null;
    this.analysisResult = null;
    this.pathwayData = null;
  }

  openApplyModal() {
    const opp = this.schemeData || {};
    const modal = document.getElementById("applyHandoffModal");
    if (!modal) return;

    const t = (k) => window.i18n.get(k);

    const dedicatedApplyUrl = opp.application_url && String(opp.application_url).trim();
    const officialSourceUrl = opp.official_source_url && String(opp.official_source_url).trim();
    const destinationUrl = dedicatedApplyUrl || officialSourceUrl || null;
    const isDirectApply = Boolean(dedicatedApplyUrl);

    const urlHealth = opp.url_health || {};
    const appHealth = urlHealth.application_url_health || {};
    const srcHealth = urlHealth.official_source_url_health || {};
    const activeHealth = isDirectApply ? appHealth : srcHealth;

    const isUnderMaintenance = activeHealth.status === "UNDER_MAINTENANCE";

    const descEl = document.getElementById("applyModalDesc");
    const ctaArea = document.getElementById("applyModalCtaArea");

    const maintenanceNote = isUnderMaintenance ? `
      <div style="background: #fffbe6; border: 1px solid #fde68a; color: #b45309; padding: 0.75rem; border-radius: 8px; font-size: 0.85rem; margin-bottom: 1rem; text-align: left;">
        📌 <strong>Notice:</strong> The official portal is currently under maintenance. You can try again later or visit the official scheme website.
      </div>
    ` : '';

    if (descEl) {
      if (!destinationUrl) {
        descEl.innerHTML = maintenanceNote + t("apply_modal_no_url");
      } else if (isDirectApply) {
        descEl.innerHTML = maintenanceNote + t("apply_modal_desc");
      } else {
        descEl.innerHTML = maintenanceNote + t("apply_modal_desc_fallback");
      }
    }

    if (ctaArea) {
      if (destinationUrl) {
        const btnLabel = isDirectApply ? t("btn_visit_official_apply") : t("btn_visit_official_scheme");
        ctaArea.innerHTML = `
          <a href="${destinationUrl}" target="_blank" rel="noopener" class="btn-primary" id="btnApplyDestination" onclick="schemeDetail.closeApplyModal()" style="display: block; text-align: center; font-size: 1rem; padding: 0.8rem 1.5rem; text-decoration: none; font-weight: 700;">
            ${btnLabel} ↗
          </a>
        `;
      } else {
        ctaArea.innerHTML = `
          <div style="background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; padding: 0.85rem; border-radius: 8px; font-size: 0.875rem; text-align: center;" id="applyModalNoUrlMsg">
            ${t("apply_modal_no_url")}
          </div>
        `;
      }
    }

    modal.classList.add("active");
    modal.style.display = "flex";
  }

  closeApplyModal() {
    const modal = document.getElementById("applyHandoffModal");
    if (modal) {
      modal.classList.remove("active");
      modal.style.display = "none";
    }
  }

  formatBusinessGoal(goal) {
    if (!goal) return 'Establish an enterprise';
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
    if (ENUM_MAP[g.toUpperCase()]) return ENUM_MAP[g.toUpperCase()];
    if (/^[A-Z0-9_]+$/.test(g)) return g.split('_').map(w => w.charAt(0) + w.slice(1).toLowerCase()).join(' ');
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
    return s.replace(/_/g, ' ');
  }

  formatStateLabel(state) {
    if (!state) return 'Need to Confirm';
    const st = String(state).trim().toUpperCase();
    if (st === 'COMPLETED') return 'Completed';
    if (st === 'ACTION_NEEDED') return 'Action Needed';
    if (st === 'VERIFY' || st === 'VERIFY_PREREQUISITE' || st === 'NEED_TO_CONFIRM') return 'Need to Confirm';
    if (st === 'POTENTIAL') return 'Potential';
    if (st === 'TARGET') return 'Target Goal';
    return st.replace(/_/g, ' ');
  }

  async loadAndRender(opportunityId, returnPage = "explore", returnTab = "recommended") {
    this.opportunityId = opportunityId;
    this.returnPage = returnPage;
    this.returnTab = returnTab;

    const container = document.getElementById("viewSchemeDetail");
    if (!container) return;

    // Show loading state
    container.innerHTML = `
      <section class="section-padding">
        <div class="container" style="text-align: center; padding: 4rem 0;">
          <div style="font-size: 2rem; margin-bottom: 1rem;">🔄</div>
          <h3>Loading Scheme Information...</h3>
          <p style="color: var(--text-muted);">Fetching verified scheme criteria and personalized pathway.</p>
        </div>
      </section>
    `;

    try {
      // 1. Fetch public scheme detail from M1
      const resScheme = await fetch(`/api/opportunities/${opportunityId}`);
      if (!resScheme.ok) throw new Error("Failed to load scheme details");
      this.schemeData = await resScheme.json();

      const profile = window.app.userProfile;

      // 2. If confirmed profile exists, fetch personalized analyze & pathway data
      if (profile) {
        const resPath = await fetch("/api/pathway/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            profile: profile,
            opportunity_id: opportunityId
          })
        });
        if (resPath.ok) {
          this.pathwayData = await resPath.json();
        }

        const resAna = await fetch("/api/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            profile: profile,
            selected_opportunity_id: opportunityId
          })
        });
        if (resAna.ok) {
          this.analysisResult = await resAna.json();
        }
      } else {
        this.pathwayData = null;
        this.analysisResult = null;
      }

    this.renderScreen(container, profile);
    window.scrollTo(0, 0);
    } catch (err) {
      console.error("Scheme detail error:", err);
      container.innerHTML = `
        <section class="section-padding">
          <div class="container">
            <div class="error-fallback">
              <h3>Unable to Load Scheme Details</h3>
              <p>${err.message}</p>
              <button class="btn-primary" onclick="schemeDetail.goBack()" style="margin-top: 1rem;">← Go Back</button>
            </div>
          </div>
        </section>
      `;
    }
  }

  goBack() {
    if (this.returnPage === "dashboard") {
      window.app.showPage("dashboard");
      if (window.myOpportunities) {
        window.myOpportunities.activeTab = this.returnTab || "recommended";
        window.myOpportunities.render();
      }
    } else {
      window.app.showPage("explore");
    }
  }

  handleCheckEligibilityClick() {
    window.app.targetSchemeAfterProfile = this.opportunityId;
    window.app.showPage("profile");
  }

  renderScreen(container, profile) {
    const t = (k) => window.i18n.get(k);
    const opp = this.schemeData || {};
    const nameObj = window.i18n.getLocalizedSchemeName(opp);
    const titleContent = nameObj.localized
      ? `<h1 style="font-size: 1.6rem; color: var(--primary-navy); margin: 0.4rem 0 0.15rem 0; line-height: 1.3;">${nameObj.localized}</h1>
         <div style="font-size: 0.95rem; color: var(--text-muted); font-weight: 500;">${nameObj.official}</div>`
      : `<h1 style="font-size: 1.65rem; color: var(--primary-navy); margin: 0.4rem 0; line-height: 1.3;">${nameObj.official}</h1>`;

    const backLabel = this.returnPage === "dashboard"
      ? (this.returnTab === "potentially" ? "← Back to My Opportunities (More Information Needed)" : "← Back to My Opportunities (Best Matches)")
      : "← Back to Explore Schemes";

    // Extract personalized match info if profile exists
    let matchCardHtml = '';
    let pathwayBlockHtml = '';

    if (profile && this.analysisResult) {
      const recs = this.analysisResult.recommendations || [];
      const needsInfo = this.analysisResult.more_information_needed || [];
      const needsVerif = this.analysisResult.needs_verification || [];
      
      let recMatch = recs.find(r => r.opportunity_id === this.opportunityId) ||
                     needsInfo.find(r => r.opportunity_id === this.opportunityId) ||
                     needsVerif.find(r => r.opportunity_id === this.opportunityId);

      const isNeedsInfo = recMatch ? (recMatch.relevance_state === "RELEVANT_NEEDS_PROFILE_INFO" || (recMatch.missing_profile_info && recMatch.missing_profile_info.length > 0)) : false;

      let badgeHtml = '';
      if (opp.lifecycle_status !== 'ACTIVE') {
        badgeHtml = `<span class="badge badge-verification" data-i18n="badge_needs_verification">${t('badge_needs_verification')}</span>`;
      } else if (recMatch && recMatch.eligibility_status === 'ELIGIBLE') {
        badgeHtml = `<span class="badge badge-eligible" data-i18n="badge_eligible">${t('badge_eligible')}</span>`;
      } else if (isNeedsInfo) {
        badgeHtml = `<span class="badge" style="background: #fef3c7; color: #b45309; border: 1px solid #fde68a;">More information needed</span>`;
      } else {
        badgeHtml = `<span class="badge badge-potentially" data-i18n="badge_potentially">${t('badge_potentially')}</span>`;
      }

      const missingFacts = recMatch ? (recMatch.missing_profile_info || []) : [];
      const whyMatches = recMatch ? (recMatch.why_match || []) : [];
      const gaps = recMatch ? (recMatch.scheme_gaps || recMatch.missing_requirements || []) : [];

      matchCardHtml = `
        <div style="background: #ffffff; border: 2px solid var(--accent-blue); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.75rem; box-shadow: var(--shadow-md);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
            <h3 style="color: var(--primary-navy); margin: 0; font-size: 1.2rem;">Your Personalized Match Evaluation</h3>
            ${badgeHtml}
          </div>

          ${isNeedsInfo ? `
            <div style="background: #fffbebf5; border: 1px solid #fde68a; padding: 0.85rem; border-radius: 8px; margin-bottom: 1rem;">
              <strong style="color: #b45309; font-size: 0.9rem;">More information needed to evaluate this opportunity:</strong>
              <ul style="margin-left: 1.25rem; font-size: 0.875rem; color: #92400e; margin-top: 0.35rem;">
                ${missingFacts.map(fact => `<li>${this.formatMissingProfileFact(fact)}</li>`).join('')}
              </ul>
              <p style="font-size: 0.8rem; color: #78350f; margin-top: 0.4rem; font-style: italic;">
                Update your profile to provide these facts and confirm precise eligibility.
              </p>
            </div>
          ` : ''}

          ${whyMatches.length > 0 ? `
            <div style="background: var(--emerald-bg); padding: 0.85rem; border-radius: 8px; margin-bottom: 1rem;">
              <strong style="color: var(--emerald); font-size: 0.875rem;" data-i18n="why_match_title">${t('why_match_title')}</strong>
              <ul style="margin-left: 1.25rem; font-size: 0.875rem; color: #065f46; margin-top: 0.25rem;">
                ${whyMatches.map(w => `<li>${w}</li>`).join('')}
              </ul>
            </div>
          ` : ''}

          ${gaps.length > 0 ? `
            <div style="background: var(--amber-bg); padding: 0.85rem; border-radius: 8px;">
              <strong style="color: var(--amber); font-size: 0.875rem;">Action Gaps & Requirements:</strong>
              <ul style="margin-left: 1.25rem; font-size: 0.875rem; color: #92400e; margin-top: 0.25rem;">
                ${gaps.map(g => `<li>${g}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
        </div>
      `;
    }

    // Render Personalized Pathway if profile and pathway data exist
    if (profile && this.pathwayData) {
      const pathway = this.pathwayData;
      const steps = pathway.steps || [];
      const isOfficialSeq = pathway.ordering_confidence === 'OFFICIAL_SEQUENCE';
      const disclaimer = pathway.disclaimer || "Your pathway is based on verified scheme requirements and the information in your profile. The suggested order is guidance unless an official sequence is specified.";
      const formattedUserGoal = this.formatBusinessGoal(pathway.user_business_goal || profile.business_goal);

      pathwayBlockHtml = `
        <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.75rem; box-shadow: var(--shadow-sm);">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; flex-wrap: wrap; gap: 0.5rem;">
            <h3 style="color: var(--primary-navy); margin: 0; font-size: 1.25rem;">Your Personalized Pathway</h3>
            <span class="badge ${pathway.eligibility_status === 'ELIGIBLE' ? 'badge-success' : 'badge-warning'}">${pathway.eligibility_status || ''}</span>
          </div>
          <p style="color: var(--text-muted); font-size: 0.825rem; margin-bottom: 1.5rem; background: #f8fafc; padding: 0.6rem 0.85rem; border-radius: 8px; border-left: 3px solid var(--accent-blue);">
            ${disclaimer}
          </p>

          <div style="display: flex; flex-direction: column; gap: 1.25rem;">
            ${steps.map((step, idx) => {
              let badgeBg = '#cbd5e1';
              let badgeColor = '#1e293b';
              let stateLabel = this.formatStateLabel(step.state);

              if (step.step_type === 'USER_PROFILE_STATE') {
                badgeBg = 'var(--emerald)'; badgeColor = '#ffffff'; stateLabel = 'Completed';
              } else if (step.step_type === 'REQUIREMENT') {
                if (step.state === 'COMPLETED') { badgeBg = 'var(--emerald)'; badgeColor = '#ffffff'; stateLabel = 'Completed'; }
                else if (step.state === 'ACTION_NEEDED') { badgeBg = '#f59e0b'; badgeColor = '#ffffff'; stateLabel = 'Action Needed'; }
                else { badgeBg = '#3b82f6'; badgeColor = '#ffffff'; stateLabel = 'Need to Confirm'; }
              } else if (step.step_type === 'TARGET_OPPORTUNITY') {
                badgeBg = 'var(--primary-navy)'; badgeColor = '#ffffff';
              } else if (step.step_type === 'PARALLEL_POTENTIAL_SUPPORTS') {
                badgeBg = '#8b5cf6'; badgeColor = '#ffffff'; stateLabel = 'Potential';
              } else if (step.step_type === 'USER_GOAL') {
                badgeBg = '#059669'; badgeColor = '#ffffff'; stateLabel = 'Target Goal';
              }

              let sectionHeaderHtml = '';
              if (!isOfficialSeq && step.step_type === 'REQUIREMENT') {
                const reqSteps = steps.filter(s => s.step_type === 'REQUIREMENT');
                if (reqSteps.length > 0 && reqSteps[0] === step) {
                  sectionHeaderHtml = `
                    <div style="margin-top: 0.5rem; margin-bottom: 0.75rem; border-bottom: 1px dashed var(--border-color); padding-bottom: 0.5rem;">
                      <h4 style="color: var(--primary-navy); font-size: 1.05rem; margin: 0 0 0.25rem 0;">What you need to prepare</h4>
                      <p style="color: var(--text-muted); font-size: 0.825rem; margin: 0; font-style: italic;">
                        These actions may not need to be completed in this exact order.
                      </p>
                    </div>
                  `;
                }
              }

              const stepIcon = isOfficialSeq 
                ? (step.step_number || (idx + 1))
                : (step.step_type === 'REQUIREMENT' ? '📌' : (step.step_type === 'USER_PROFILE_STATE' ? '👤' : (step.step_type === 'TARGET_OPPORTUNITY' ? '🎯' : (step.step_type === 'USER_GOAL' ? '🏁' : '✨'))));

              if (step.step_type === 'PARALLEL_POTENTIAL_SUPPORTS') {
                const supportsList = step.supports || [];
                return `
                  <div>
                    ${sectionHeaderHtml}
                    <div style="display: flex; align-items: flex-start; gap: 1rem;">
                      <div style="width: 32px; height: 32px; border-radius: 50%; background: ${badgeBg}; color: ${badgeColor}; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.85rem; flex-shrink: 0;">
                        ${stepIcon}
                      </div>
                      <div style="background: #f8fafc; border: 1px solid var(--border-color); border-radius: 10px; padding: 0.85rem 1rem; flex: 1;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                          <span style="font-weight: 700; color: var(--primary-navy); font-size: 0.95rem;">${step.title || 'Potential Support Benefits'}</span>
                          <span style="font-size: 0.75rem; background: #8b5cf6; color: #ffffff; padding: 0.15rem 0.5rem; border-radius: 4px; font-weight: 600;">${stateLabel}</span>
                        </div>
                        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem;">
                          ${supportsList.map(sup => `
                            <div style="background: #ffffff; border: 1px solid #ddd6fe; padding: 0.4rem 0.75rem; border-radius: 6px; font-size: 0.85rem; color: #5b21b6; font-weight: 600;">
                              ${sup.title} <span style="font-size: 0.75rem; font-weight: normal; color: #6b7280;">(${sup.description})</span>
                            </div>
                          `).join('')}
                        </div>
                      </div>
                    </div>
                  </div>
                `;
              }

              const stepTitle = step.step_type === 'USER_GOAL' 
                ? `User Goal: ${formattedUserGoal}` 
                : (step.title || step.action_label || 'Step ' + (idx + 1));

              return `
                <div>
                  ${sectionHeaderHtml}
                  <div style="display: flex; align-items: flex-start; gap: 1rem;">
                    <div style="width: 32px; height: 32px; border-radius: 50%; background: ${badgeBg}; color: ${badgeColor}; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.85rem; flex-shrink: 0;">
                      ${stepIcon}
                    </div>
                    <div style="background: #f8fafc; border: 1px solid var(--border-color); border-radius: 10px; padding: 0.85rem 1rem; flex: 1;">
                      <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; color: var(--primary-navy); font-size: 0.95rem;">${stepTitle}</span>
                        <span style="font-size: 0.75rem; background: ${badgeBg}; color: ${badgeColor}; padding: 0.15rem 0.5rem; border-radius: 4px; font-weight: 600;">${stateLabel}</span>
                      </div>
                      ${step.why_this_matters ? `
                        <div style="font-size: 0.825rem; color: #475569; margin-top: 0.35rem;">
                          <strong>Why this matters:</strong> ${step.why_this_matters}
                        </div>
                      ` : (step.description ? `<div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.25rem;">${step.description}</div>` : '')}
                      ${step.official_source_url ? `
                        <div style="margin-top: 0.45rem;">
                          <a href="${step.official_source_url}" target="_blank" rel="noopener" style="font-size: 0.775rem; color: var(--accent-blue); font-weight: 600; text-decoration: none;">
                            View official source →
                          </a>
                        </div>
                      ` : ''}
                    </div>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      `;
    }

    // No-Profile Eligibility CTA block (ONLY rendered if no profile exists)
    let noProfileCtaHtml = '';
    if (!profile) {
      noProfileCtaHtml = `
        <div style="background: #e0f2fe; border: 1px solid #bae6fd; border-radius: 16px; padding: 1.5rem; margin-bottom: 1.75rem; text-align: center;">
          <h3 style="color: #0369a1; margin-bottom: 0.5rem; font-size: 1.25rem;">Want to see if you are eligible for this scheme?</h3>
          <p style="color: #0c4a6e; font-size: 0.9rem; margin-bottom: 1.25rem; max-width: 600px; margin-left: auto; margin-right: auto;">
            Set your profile to get a personalized match evaluation and step-by-step action pathway.
          </p>
          <button class="btn-primary" onclick="schemeDetail.handleCheckEligibilityClick()" style="font-size: 1rem; padding: 0.75rem 1.8rem;">
            Check My Eligibility for This Scheme
          </button>
        </div>
      `;
    }

    container.innerHTML = `
      <section class="section-padding" style="background: var(--bg-light); min-height: 80vh;">
        <div class="container" style="max-width: 960px; margin: 0 auto;">

          <!-- Top Back Navigation -->
          <div style="margin-bottom: 1.25rem;">
            <button class="btn-outline" onclick="schemeDetail.goBack()" style="padding: 0.45rem 0.9rem; font-size: 0.875rem;">
              ${backLabel}
            </button>
          </div>

          <!-- Concise Scheme Header Card -->
          <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.75rem; box-shadow: var(--shadow-sm);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.5rem;">
              <div>
                <span class="opp-sector-tag">${window.i18n.getSectorLabel(opp.primary_sector)}</span>
                <span style="font-size: 0.8rem; color: var(--text-muted); margin-left: 0.5rem;">${opp.ministry_department || 'Government of India'}</span>
              </div>
              <span class="badge ${opp.lifecycle_status === 'ACTIVE' ? 'badge-active' : 'badge-verification'}">
                ${opp.lifecycle_status === 'ACTIVE' ? window.i18n.get('badge_active') : window.i18n.get('badge_needs_verification')}
              </span>
            </div>

            ${titleContent}

            <!-- Primary Action Bar: Apply -->
            <div style="display: flex; gap: 0.75rem; align-items: center; margin-top: 1.25rem; flex-wrap: wrap;">
              <button class="btn-primary" id="btnHeaderApply" onclick="schemeDetail.openApplyModal()" style="padding: 0.65rem 1.6rem; font-size: 1rem; font-weight: 700; box-shadow: var(--shadow-sm);">
                <span data-i18n="btn_apply">${t('btn_apply')}</span>
              </button>
            </div>

            <div style="display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 1.25rem; font-size: 0.875rem; color: var(--text-muted); border-top: 1px solid var(--border-color); padding-top: 0.85rem;">
              <span>Scope: <strong>${window.i18n.getScopeLabel(opp.scope)}</strong></span>
              <span>Target: <strong>${opp.target_beneficiary || 'Eligible Citizens'}</strong></span>
            </div>
          </div>

          <!-- Scheme Overview Card -->
          <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.75rem; box-shadow: var(--shadow-sm);" id="cardAboutScheme">
            <h3 style="color: var(--primary-navy); margin-bottom: 1rem; font-size: 1.15rem;">About this Scheme</h3>
            
            <div style="display: grid; gap: 1.25rem;">
              <div>
                <h4 style="color: var(--primary-navy); margin-bottom: 0.3rem; font-size: 0.95rem;">${window.i18n.get('detail_benefits')}</h4>
                <p style="color: var(--text-main); font-size: 0.925rem; line-height: 1.5;">${opp.benefit_summary || 'N/A'}</p>
              </div>

              <div>
                <h4 style="color: var(--primary-navy); margin-bottom: 0.3rem; font-size: 0.95rem;">${window.i18n.get('detail_eligibility')}</h4>
                <p style="color: var(--text-main); font-size: 0.925rem; line-height: 1.5;">${opp.eligibility_summary || 'N/A'}</p>
              </div>

              <div>
                <h4 style="color: var(--primary-navy); margin-bottom: 0.3rem; font-size: 0.95rem;">${window.i18n.get('detail_application')}</h4>
                <p style="color: var(--text-main); font-size: 0.925rem;">${opp.application_route || 'Official Portal / Designated Bank Branch'}</p>
              </div>

              <div>
                <h4 style="color: var(--primary-navy); margin-bottom: 0.3rem; font-size: 0.95rem;">Ministry / Department</h4>
                <p style="color: var(--text-main); font-size: 0.925rem;">${opp.ministry_department || 'Government of India'}</p>
              </div>

              <div>
                <h4 style="color: var(--primary-navy); margin-bottom: 0.3rem; font-size: 0.95rem;">${window.i18n.get('detail_official_website') || 'Official Website'}</h4>
                ${(opp.official_source_url || opp.application_url) ? `
                  <a href="${opp.official_source_url || opp.application_url}" target="_blank" rel="noopener noreferrer" style="color: var(--accent-blue); font-size: 0.925rem; font-weight: 600; text-decoration: none; word-break: break-all;" id="linkAboutOfficialWebsite">
                    ${opp.official_source_url || opp.application_url} ↗
                  </a>
                ` : `
                  <p style="color: var(--text-muted); font-size: 0.925rem; margin: 0;">A verified official website link is not currently available in SchemeMitra.</p>
                `}
              </div>
            </div>
          </div>

          <!-- Personalized Match Card (If Profile Exists) -->
          ${matchCardHtml}

          <!-- Personalized Pathway Block (If Profile Exists) -->
          ${pathwayBlockHtml}



          <!-- No-Profile CTA Block (Only If No Profile Exists) -->
          ${noProfileCtaHtml}

          <!-- Application Guide & Document Checklist -->
          <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.75rem; box-shadow: var(--shadow-sm);">
            <h3 style="color: var(--primary-navy); margin-bottom: 0.35rem; font-size: 1.15rem;" data-i18n="guide_title">${t('guide_title')}</h3>
            <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1.25rem;" data-i18n="guide_sub">${t('guide_sub')}</p>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.25rem; margin-bottom: 1.25rem;">
              <div style="background: #f8fafc; padding: 1.1rem; border-radius: 10px; border: 1px solid var(--border-color);">
                <h4 style="color: var(--primary-navy); margin-bottom: 0.4rem; font-size: 0.925rem;">📁 <span data-i18n="guide_docs">${t('guide_docs')}</span></h4>
                <p style="font-size: 0.875rem; color: var(--text-main);">${opp.required_documents_summary || 'Entity Registration, KYC, Project Report/DPR'}</p>
              </div>

              <div style="background: #f8fafc; padding: 1.1rem; border-radius: 10px; border: 1px solid var(--border-color);">
                <h4 style="color: var(--primary-navy); margin-bottom: 0.4rem; font-size: 0.925rem;">🌐 <span data-i18n="guide_channel">${t('guide_channel')}</span></h4>
                <p style="font-size: 0.875rem; color: var(--text-main);">${opp.application_route || 'Official Portal or Designated Bank Branch'}</p>
              </div>

              <div style="background: #f8fafc; padding: 1.1rem; border-radius: 10px; border: 1px solid var(--border-color);">
                <h4 style="color: var(--primary-navy); margin-bottom: 0.4rem; font-size: 0.925rem;">🔍 <span data-i18n="guide_verification">${t('guide_verification')}</span></h4>
                <p style="font-size: 0.875rem; color: var(--text-main);">District Level Committee / Nodal Agency Appraisal</p>
              </div>
            </div>

            <div style="background: #f1f5f9; border-left: 4px solid var(--primary-navy); padding: 0.85rem 1.15rem; border-radius: 8px; font-size: 0.85rem; color: #334155; line-height: 1.5;" data-i18n="platform_positioning_disclaimer">
              ${t('platform_positioning_disclaimer')}
            </div>
          </div>

        </div>
      </section>
    `;
  }

  async fetchAndRenderCopilot(opportunityId, profile) {
    const copilotContainer = document.getElementById("aiPathwayCopilotBlock");
    if (!copilotContainer) return;

    if (!profile) {
      copilotContainer.innerHTML = `
        <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.75rem; box-shadow: var(--shadow-sm);">
          <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.5rem;">
            <span style="font-size: 1.3rem;">🤖</span>
            <h3 style="color: var(--primary-navy); margin: 0; font-size: 1.2rem;">AI Pathway Copilot</h3>
          </div>
          <p style="color: var(--text-muted); font-size: 0.875rem; margin: 0 0 1rem 0;">Personalized guidance based on your profile and verified scheme information.</p>
          <div style="background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 10px; padding: 1.25rem; text-align: center; color: var(--text-muted); font-size: 0.9rem;">
            “Build your profile to get personalized pathway guidance.”
          </div>
        </div>
      `;
      return;
    }

    copilotContainer.innerHTML = `
      <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.75rem; box-shadow: var(--shadow-sm);">
        <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.5rem;">
          <span style="font-size: 1.3rem;">🤖</span>
          <h3 style="color: var(--primary-navy); margin: 0; font-size: 1.2rem;">AI Pathway Copilot</h3>
        </div>
        <p style="color: var(--text-muted); font-size: 0.875rem; margin: 0 0 1.25rem 0;">Personalized guidance based on your profile and verified scheme information.</p>
        <div style="background: #f8fafc; border: 1px solid var(--border-color); border-radius: 12px; padding: 2rem; text-align: center; color: var(--text-muted);">
          <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">⏳</div>
          <h4 style="color: var(--primary-navy); margin: 0 0 0.25rem 0; font-size: 1rem;">Generating personalized explanation...</h4>
          <p style="font-size: 0.825rem; margin: 0;">Analyzing verified pathway facts and profile compatibility.</p>
        </div>
      </div>
    `;

    try {
      const currentLang = window.i18n ? window.i18n.currentLang || 'English' : 'English';
      const langNameMap = { 'en': 'English', 'ta': 'Tamil', 'hi': 'Hindi' };
      const reqLang = langNameMap[currentLang] || currentLang;

      const res = await fetch("/api/pathway/copilot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          opportunity_id: opportunityId,
          language: reqLang,
          profile: profile
        })
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      this.renderCopilotCard(copilotContainer, data, opportunityId, profile);
    } catch (err) {
      console.warn("Copilot fetch error:", err);
      this.renderCopilotFallback(copilotContainer, opportunityId, profile);
    }
  }

  formatSupportTypeLabel(supType) {
    if (!supType) return '';
    const parts = String(supType).split(';');
    const map = {
      'credit': 'Loan / Credit',
      'subsidy': 'Capital Subsidy',
      'grant': 'Grant / Seed Funding',
      'training': 'Training & Skill Support',
      'infrastructure': 'Infrastructure & Equipment',
      'certification': 'Certification',
      'credit guarantee': 'Credit Guarantee',
      'equipment support': 'Equipment Support',
      'export support': 'Export Support',
      'fellowship': 'Fellowship',
      'incubation': 'Incubation',
      'market access': 'Market Access',
      'mentorship': 'Mentorship',
      'skill development': 'Skill Development'
    };
    const formatted = parts.map(p => {
      const trimmed = p.trim();
      const lower = trimmed.toLowerCase();
      return map[lower] || trimmed;
    });
    return formatted.join(', ');
  }

  renderCopilotCard(container, data, opportunityId, profile) {
    const copilotData = data.copilot_data || {};
    const aiAvailable = data.ai_available !== false;
    const officialSources = data.official_sources || [];

    if (!aiAvailable) {
      this.renderCopilotFallback(container, opportunityId, profile, data.fallback_message);
      return;
    }

    const currentPosition = copilotData.current_position || '';
    const whyFits = copilotData.why_this_opportunity_fits || '';
    const priorityActions = copilotData.priority_actions || [];
    const supports = copilotData.support_explanation || [];
    const goalConn = copilotData.goal_connection || '';
    const importantNote = copilotData.important_note || '';

    const isPlanningGuidance = priorityActions.some(a => a.ordering_basis === 'PLANNING_GUIDANCE');

    container.innerHTML = `
      <div style="background: #ffffff; border: 1.5px solid #8b5cf6; border-radius: 16px; padding: 1.5rem; margin-bottom: 1.75rem; box-shadow: var(--shadow-sm);" id="cardAiPathwayCopilot">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; flex-wrap: wrap; gap: 0.5rem;">
          <div style="display: flex; align-items: center; gap: 0.6rem;">
            <span style="font-size: 1.4rem;">🤖</span>
            <div>
              <h3 style="color: var(--primary-navy); margin: 0; font-size: 1.25rem;">AI Pathway Copilot</h3>
              <div style="font-size: 0.775rem; color: #6d28d9; font-weight: 600;">Grounded explanation based strictly on verified scheme facts</div>
            </div>
          </div>
          <span style="font-size: 0.75rem; background: #f3e8ff; color: #7e22ce; padding: 0.2rem 0.65rem; border-radius: 6px; font-weight: 700; border: 1px solid #d8b4fe;">
            AI Assisted
          </span>
        </div>

        <p style="color: var(--text-muted); font-size: 0.85rem; margin: 0 0 1.25rem 0;">Personalized guidance based on your profile and verified scheme information.</p>

        <div style="display: flex; flex-direction: column; gap: 1.25rem;">

          ${currentPosition ? `
            <div style="background: #f8fafc; border-left: 4px solid var(--accent-blue); padding: 0.85rem 1.1rem; border-radius: 8px;">
              <strong style="color: var(--primary-navy); font-size: 0.875rem; display: block; margin-bottom: 0.25rem;">📍 Your Current Position</strong>
              <div style="font-size: 0.9rem; color: #334155; line-height: 1.5;">${currentPosition}</div>
            </div>
          ` : ''}

          ${whyFits ? `
            <div style="background: #ecfdf5; border: 1px solid #a7f3d0; padding: 0.85rem 1.1rem; border-radius: 8px;">
              <strong style="color: #065f46; font-size: 0.875rem; display: block; margin-bottom: 0.25rem;">✨ Why This Opportunity May Fit</strong>
              <div style="font-size: 0.9rem; color: #047857; line-height: 1.5;">${whyFits}</div>
            </div>
          ` : ''}

          ${priorityActions.length > 0 ? `
            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem; flex-wrap: wrap; gap: 0.4rem;">
                <strong style="color: var(--primary-navy); font-size: 0.95rem;">📋 What to Focus On</strong>
                <span style="font-size: 0.75rem; background: #fffbe6; color: #b45309; border: 1px solid #fde68a; padding: 0.15rem 0.5rem; border-radius: 4px; font-weight: 600;">
                  ${isPlanningGuidance ? 'Suggested preparation order' : 'Official sequence'}
                </span>
              </div>

              ${isPlanningGuidance ? `
                <div style="font-size: 0.775rem; color: #b45309; font-style: italic; margin-bottom: 0.65rem;">
                  📌 This order is planning guidance and is not an official government sequence.
                </div>
              ` : ''}

              <div style="display: flex; flex-direction: column; gap: 0.65rem;">
                ${priorityActions.map((act, idx) => {
                  let pBg = '#f1f5f9'; let pCol = '#475569';
                  if (act.priority === 'HIGH') { pBg = '#fef2f2'; pCol = '#991b1b'; }
                  else if (act.priority === 'MEDIUM') { pBg = '#fffbe6'; pCol = '#b45309'; }

                  return `
                    <div style="background: #f8fafc; border: 1px solid var(--border-color); border-radius: 8px; padding: 0.75rem 0.9rem;">
                      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                        <span style="font-weight: 700; color: var(--primary-navy); font-size: 0.875rem;">${idx + 1}. ${act.title}</span>
                        <span style="font-size: 0.7rem; background: ${pBg}; color: ${pCol}; padding: 0.1rem 0.45rem; border-radius: 4px; font-weight: 700;">${act.priority || 'MEDIUM'} PRIORITY</span>
                      </div>
                      <div style="font-size: 0.825rem; color: #475569; line-height: 1.4;">${act.explanation}</div>
                    </div>
                  `;
                }).join('')}
              </div>
            </div>
          ` : ''}

          ${supports.length > 0 ? `
            <div>
              <strong style="color: var(--primary-navy); font-size: 0.95rem; display: block; margin-bottom: 0.5rem;">🎁 Available Support</strong>
              <div style="display: grid; gap: 0.5rem;">
                ${supports.map(s => `
                  <div style="background: #f3e8ff; border: 1px solid #d8b4fe; padding: 0.65rem 0.85rem; border-radius: 8px; font-size: 0.85rem; color: #5b21b6;">
                    <strong>${this.formatSupportTypeLabel(s.support_type)}:</strong> ${s.explanation}
                  </div>
                `).join('')}
              </div>
            </div>
          ` : ''}

          ${goalConn ? `
            <div style="background: #e0f2fe; border: 1px solid #bae6fd; padding: 0.85rem 1.1rem; border-radius: 8px;">
              <strong style="color: #0369a1; font-size: 0.875rem; display: block; margin-bottom: 0.25rem;">🏁 How This Supports Your Business Goal</strong>
              <div style="font-size: 0.875rem; color: #0c4a6e; line-height: 1.4;">${goalConn}</div>
            </div>
          ` : ''}

          ${importantNote ? `
            <div style="background: #fffbe6; border: 1px solid #fde68a; padding: 0.85rem 1.1rem; border-radius: 8px;">
              <strong style="color: #b45309; font-size: 0.875rem; display: block; margin-bottom: 0.25rem;">📌 Important Note</strong>
              <div style="font-size: 0.85rem; color: #92400e; line-height: 1.4;">${importantNote}</div>
            </div>
          ` : ''}

          ${officialSources.length > 0 ? `
            <div style="border-top: 1px solid var(--border-color); padding-top: 0.75rem; font-size: 0.8rem; color: var(--text-muted);">
              <strong>Official sources used for this guidance:</strong>
              <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.35rem;">
                ${officialSources.map(u => `
                  <a href="${u}" target="_blank" rel="noopener" style="color: var(--accent-blue); text-decoration: none; font-weight: 600;">
                    ${u} ↗
                  </a>
                `).join('')}
              </div>
            </div>
          ` : ''}

        </div>
      </div>
    `;
  }

  renderCopilotFallback(container, opportunityId, profile, customMsg) {
    const msg = customMsg || "Personalized AI explanation is temporarily unavailable. Your verified pathway is still available above.";

    container.innerHTML = `
      <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.75rem; box-shadow: var(--shadow-sm);">
        <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.5rem;">
          <span style="font-size: 1.3rem;">🤖</span>
          <h3 style="color: var(--primary-navy); margin: 0; font-size: 1.2rem;">AI Pathway Copilot</h3>
        </div>
        <p style="color: var(--text-muted); font-size: 0.875rem; margin: 0 0 1rem 0;">Personalized guidance based on your profile and verified scheme information.</p>
        <div style="background: #fffbe6; border: 1px solid #fde68a; border-radius: 10px; padding: 1rem 1.25rem; color: #b45309; font-size: 0.875rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem;">
          <div>
            📌 <strong>Notice:</strong> ${msg}
          </div>
          <button class="btn-outline" onclick="schemeDetail.fetchAndRenderCopilot('${opportunityId}', window.app.userProfile)" style="padding: 0.35rem 0.75rem; font-size: 0.8rem; background: #ffffff;">
            🔄 Retry
          </button>
        </div>
      </div>
    `;
  }
}

window.schemeDetail = new SchemeDetailComponent();
