/**
 * OpportunityOS v2 — My Opportunities Dashboard Component
 * Clean, scheme-centric navigation: Best Matches, More Information Needed, Needs Verification, and Opportunity Graph.
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

  async render() {
    const container = document.getElementById("viewDashboard");
    if (!container) return;

    const t = (k) => window.i18n.get(k);
    const profile = window.app.userProfile;

    if (!profile) {
      container.innerHTML = `
        <section class="section-padding">
          <div class="container" style="text-align: center;">
            <h3 data-i18n="no_profile_title">${t('no_profile_title')}</h3>
            <p style="color: var(--text-muted); margin-bottom: 1.5rem;" data-i18n="no_profile_msg">${t('no_profile_msg')}</p>
            <button class="btn-primary" onclick="app.showPage('profile')" data-i18n="btn_set_profile">${t('btn_set_profile')}</button>
          </div>
        </section>
      `;
      return;
    }

    // Show loading state if initial fetch
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

    container.innerHTML = `
      <section class="section-padding" style="background: var(--bg-light);">
        <div class="container">
          
          <!-- Profile Summary Header Card -->
          <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: 16px; padding: 1.25rem; margin-bottom: 1.75rem; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 1rem; box-shadow: var(--shadow-sm);">
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
            <button class="tab-btn ${this.activeTab === 'graph' ? 'active' : ''}" onclick="myOpportunities.switchTab('graph')">
              🕸️ Opportunity Graph
            </button>
          </div>

          <!-- Active Tab Content Container -->
          <div id="tabContentArea">
            ${this.renderActiveTabContent(data, bestMatches, needsInfoOpps, needsVerif, notEligible)}
          </div>

        </div>
      </section>

      <!-- Requirement Detail Popover Modal -->
      <div id="reqDetailModal" class="modal-overlay" style="display: none;">
        <div class="modal-card" style="max-width: 540px; padding: 1.75rem;">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.6rem;">
              <span style="font-size: 1.5rem;">📌</span>
              <h3 style="font-size: 1.2rem; color: var(--primary-navy); margin: 0;" id="reqModalTitle">Requirement Details</h3>
            </div>
            <button class="close-modal" onclick="myOpportunities.closeReqModal()" style="position: relative; top: 0; right: 0;">&times;</button>
          </div>
          <div id="reqModalBody"></div>
          <div style="margin-top: 1.25rem; text-align: right;">
            <button class="btn-outline" onclick="myOpportunities.closeReqModal()">Close</button>
          </div>
        </div>
      </div>

      <!-- Support Detail Popover Modal -->
      <div id="supDetailModal" class="modal-overlay" style="display: none;">
        <div class="modal-card" style="max-width: 540px; padding: 1.75rem;">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.6rem;">
              <span style="font-size: 1.5rem;">💡</span>
              <h3 style="font-size: 1.2rem; color: var(--primary-navy); margin: 0;" id="supModalTitle">Support Benefit Details</h3>
            </div>
            <button class="close-modal" onclick="myOpportunities.closeSupModal()" style="position: relative; top: 0; right: 0;">&times;</button>
          </div>
          <div id="supModalBody"></div>
          <div style="margin-top: 1.25rem; text-align: right;">
            <button class="btn-outline" onclick="myOpportunities.closeSupModal()">Close</button>
          </div>
        </div>
      </div>

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
          color: var(--accent-blue);
          border-bottom-color: var(--accent-blue);
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
        ${recs.map(r => {
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

          return `
            <div class="opp-card" style="border-left: 4px solid ${r.eligibility_status === 'ELIGIBLE' ? 'var(--emerald)' : 'var(--amber)'};">
              <div class="opp-card-header">
                <div>
                  <span class="opp-sector-tag">${window.i18n.getSectorLabel(r.primary_sector)}</span>
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

              <div class="opp-meta">
                <span>${t('lbl_support')}: <strong>${supportLabels}</strong></span>
                <button class="btn-primary" onclick="app.showSchemeDetail('${r.opportunity_id}', 'dashboard', 'recommended')" style="font-size: 0.85rem; padding: 0.4rem 0.9rem;">
                  View Details & Pathway
                </button>
              </div>
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

          return `
            <div class="opp-card" style="border-left: 4px solid var(--amber);">
              <div class="opp-card-header">
                <div>
                  <span class="opp-sector-tag">${window.i18n.getSectorLabel(r.primary_sector)}</span>
                  <h3 class="opp-title" onclick="app.showSchemeDetail('${r.opportunity_id}', 'dashboard', 'potentially')">
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

              <div class="opp-meta" style="justify-content: flex-end;">
                <button class="btn-primary" onclick="app.showSchemeDetail('${r.opportunity_id}', 'dashboard', 'potentially')" style="font-size: 0.85rem; padding: 0.4rem 0.9rem;">
                  View Details & Pathway
                </button>
              </div>
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

          return `
            <div class="opp-card" style="border-left: 4px solid #7e22ce;">
              <div class="opp-card-header">
                <h3 class="opp-title" onclick="app.showSchemeDetail('${v.opportunity_id}', 'dashboard', 'verification')">${titleContent}</h3>
                <span class="badge badge-verification" data-i18n="badge_needs_verification">${t('badge_needs_verification')}</span>
              </div>
              <p style="font-size: 0.875rem; color: var(--text-muted);">${v.lifecycle_warning || 'Scheme guideline period reached verification milestone.'}</p>
              ${v.official_source_url ? `
                <div style="margin-top: 0.5rem; font-size: 0.85rem;">
                  Official Source: <a href="${v.official_source_url}" target="_blank" rel="noopener" style="color: var(--accent-blue); word-break: break-all;">${v.official_source_url} ↗</a>
                </div>
              ` : ''}
            </div>
          `;
        }).join('')}
      </div>
    `;
  }

  /* REBUILT OPPORTUNITY-CENTRIC GRAPH RENDERER */
  async switchGraphMode(mode) {
    this.graphSelectionMode = mode;
    const profile = window.app.userProfile || {};
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
    console.log('OpportunityOS graph runtime v2');

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
    const profile = window.app.userProfile || (this.analysisResult && this.analysisResult.profile) || {};

    // 1. Authoritative candidate selection from M4 best_matches
    let candidateOpps = (this.analysisResult && this.analysisResult.best_matches) || [];

    if (!candidateOpps || candidateOpps.length === 0) {
      // Fallback to graphData nodes if available
      const rawNodes = (graphData && graphData.nodes) || (this.graphData && this.graphData.nodes) || [];
      candidateOpps = rawNodes.filter(n => n.type === "OPPORTUNITY").map(n => ({
        opportunity_id: n.opportunity_id || n.id.replace('opp_', ''),
        opportunity_name: n.label,
        eligibility_status: n.status === "Eligible" ? "ELIGIBLE" : "POTENTIALLY_ELIGIBLE",
        benefit_summary: n.metadata && n.metadata.benefit_summary,
        support_types: n.metadata && n.metadata.support_types
      }));
    }

    // Exclude NOT_ELIGIBLE
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

    // 2. Build Profile Card Fields
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
      const secLabel = window.i18n.getSectorLabel(profile.sector || profile.target_sector);
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

      // Get requirements for opp
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

      if (oppReqs.length === 0) {
        // Fallback default requirements from profile check
        oppReqs = [
          { id: `req_${oppId}_age`, label: 'Age 18+ requirement', status: profile.age && profile.age >= 18 ? '✓ Completed' : '? Need to Confirm' },
          { id: `req_${oppId}_unit`, label: 'New enterprise / unit status', status: profile.is_new_unit === True || profile.is_new_unit === true ? '✓ Completed' : '? Need to Confirm' },
          { id: `req_${oppId}_sub`, label: 'No prior government subsidy availed', status: profile.prior_gov_subsidy === False || profile.prior_gov_subsidy === false ? '✓ Completed' : '? Need to Confirm' }
        ];
      }

      // Get verified support types for opp
      let supportTypes = opp.support_types || [];
      if ((!supportTypes || supportTypes.length === 0) && graphData && graphData.nodes) {
        supportTypes = graphData.nodes.filter(n => n.type === 'SUPPORT' && n.metadata && n.metadata.connected_opportunities && n.metadata.connected_opportunities.includes(oppId)).map(n => n.metadata.support_type || n.label);
      }

      if (!supportTypes || supportTypes.length === 0) {
        supportTypes = ["SUP_CREDIT", "SUP_SUBSIDY"];
      }

      const visibleReqs = isShowAllReqs ? oppReqs : oppReqs.slice(0, 4);
      const remainingReqCount = oppReqs.length - visibleReqs.length;

      // Estimate heights
      const oppCardH = 150;
      const reqPanelH = isReqExpanded ? 50 + (visibleReqs.length * 48) + (remainingReqCount > 0 || isShowAllReqs ? 36 : 0) : 0;
      const benPanelH = isBenExpanded ? 50 + (supportTypes.length * 45) : 0;

      const clusterH = Math.max(oppCardH, reqPanelH, benPanelH);
      const oppY = currentY;
      const reqY = oppY;

      // If both panels expanded, place Benefits panel adjacent or below
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

    // Dynamic right edge calculation
    const maxDetailX = oppLayouts.some(l => l.isReqExpanded && l.isBenExpanded) ? colX.DETAILS + 560 : (oppLayouts.some(l => l.isReqExpanded || l.isBenExpanded) ? colX.DETAILS + 290 : colX.OPPORTUNITY + 300);
    const totalCanvasW = Math.max(1200, maxDetailX + 60);

    const profileY = Math.max(40, (totalCanvasH - 240) / 2);

    // Build SVG Connection Lines
    const svgPaths = [];

    oppLayouts.forEach(layout => {
      // 1. Profile -> Opportunity Line
      const x1 = colX.PROFILE + 270;
      const y1 = profileY + 120;
      const x2 = colX.OPPORTUNITY;
      const y2 = layout.oppY + 65;

      const ctrlDist = Math.min(80, Math.abs(x2 - x1) / 2);
      svgPaths.push(`<path d="M ${x1} ${y1} C ${x1 + ctrlDist} ${y1}, ${x2 - ctrlDist} ${y2}, ${x2} ${y2}" fill="none" stroke="#2563eb" stroke-width="2.5" opacity="0.8" />`);

      // 2. Opportunity -> Requirements Panel Line
      if (layout.isReqExpanded) {
        const rx1 = colX.OPPORTUNITY + 280;
        const ry1 = layout.oppY + 65;
        const rx2 = colX.DETAILS;
        const ry2 = layout.reqY + 40;
        svgPaths.push(`<path d="M ${rx1} ${ry1} C ${rx1 + 40} ${ry1}, ${rx2 - 40} ${ry2}, ${rx2} ${ry2}" fill="none" stroke="#d97706" stroke-width="2" stroke-dasharray="5,4" opacity="0.85" />`);
      }

      // 3. Opportunity -> Benefits Panel Line
      if (layout.isBenExpanded) {
        const bx1 = colX.OPPORTUNITY + 280;
        const by1 = layout.oppY + 105;
        const bx2 = layout.benX;
        const by2 = layout.benY + 40;
        svgPaths.push(`<path d="M ${bx1} ${by1} C ${bx1 + 40} ${by1}, ${bx2 - 40} ${by2}, ${bx2} ${by2}" fill="none" stroke="#7e22ce" stroke-width="2" stroke-dasharray="3,3" opacity="0.85" />`);
      }
    });

    // Profile Box HTML
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

    // Opportunity Cards & Expanded Panels HTML
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

      const nameObj = window.i18n.getLocalizedSchemeName(opp);

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
              <span>📋 Requirements (${layout.oppReqs.length})</span>
              <button class="close-modal" onclick="myOpportunities.toggleOppReqs('${oppId}')" style="position: static; width: 22px; height: 22px; font-size: 0.8rem;">&times;</button>
            </div>
            <div style="display: flex; flex-direction: column; gap: 0.45rem;">
              ${layout.visibleReqs.map(r => {
                const isComp = r.status.includes('Completed') || r.status.includes('✓');
                const isAct = r.status.includes('Action') || r.status.includes('!');
                const icon = isComp ? '✓' : (isAct ? '!' : '?');
                const iconBg = isComp ? '#ecfdf5; color: #047857;' : (isAct ? '#fffbe6; color: #b45309;' : '#eff6ff; color: #1d4ed8;');
                return `
                  <div style="display: flex; align-items: flex-start; gap: 0.4rem; font-size: 0.8rem; background: #f8fafc; padding: 0.45rem 0.6rem; border-radius: 6px; border: 1px solid var(--border-color);">
                    <span style="font-weight: 800; font-size: 0.75rem; padding: 0.05rem 0.3rem; border-radius: 4px; background: ${iconBg}">${icon}</span>
                    <span style="color: var(--primary-navy); font-weight: 600; line-height: 1.25;">${r.label}</span>
                  </div>
                `;
              }).join('')}
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
              ${layout.supportTypes.map(st => {
                const label = window.i18n.getSupportTypeLabel(st);
                return `
                  <div style="display: flex; align-items: center; gap: 0.45rem; font-size: 0.8rem; background: #fcf5ff; padding: 0.5rem 0.65rem; border-radius: 6px; border: 1px solid #e9d5ff; color: #6b21a8; font-weight: 700;">
                    <span>${label}</span>
                  </div>
                `;
              }).join('')}
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
            <span style="color: #047857; font-weight: 600;">✓ Completed</span>
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

  showRequirementModal(nodeId) {
    if (!this.graphData || !this.graphData.nodes) return;
    const node = this.graphData.nodes.find(n => n.id === nodeId);
    if (!node) return;

    const modal = document.getElementById("reqDetailModal");
    const titleEl = document.getElementById("reqModalTitle");
    const bodyEl = document.getElementById("reqModalBody");

    if (!modal || !bodyEl) return;

    titleEl.textContent = node.label || "Requirement Details";
    const meta = node.metadata || {};
    const status = node.status || "? Need to Confirm";
    const connOppIds = meta.connected_opportunities || [];

    let connOppsHtml = "";
    if (connOppIds.length > 0 && this.analysisResult) {
      const allOpps = [
        ...(this.analysisResult.best_matches || []),
        ...(this.analysisResult.more_information_needed || [])
      ];
      const matched = allOpps.filter(o => connOppIds.includes(o.opportunity_id));
      if (matched.length > 0) {
        connOppsHtml = `
          <div style="margin-top: 1rem;">
            <strong style="color: var(--primary-navy); font-size: 0.875rem;">Connected Schemes Requiring This:</strong>
            <div style="display: flex; flex-direction: column; gap: 0.4rem; margin-top: 0.35rem;">
              ${matched.map(m => `
                <div onclick="myOpportunities.closeReqModal(); app.showSchemeDetail('${m.opportunity_id}', 'dashboard', 'graph');" 
                     style="background: #f8fafc; border: 1px solid var(--border-color); padding: 0.5rem 0.75rem; border-radius: 6px; cursor: pointer; font-size: 0.85rem; color: var(--accent-blue); font-weight: 600;">
                  🎯 ${m.opportunity_name || m.name} ↗
                </div>
              `).join('')}
            </div>
          </div>
        `;
      }
    }

    bodyEl.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 0.85rem; margin-top: 0.5rem;">
        <div>
          <span style="font-size: 0.8rem; color: var(--text-muted);">Current Profile State:</span>
          <div style="font-size: 1rem; font-weight: 700; color: ${status.includes('Completed') ? 'var(--emerald)' : (status.includes('Action Needed') ? 'var(--amber)' : 'var(--accent-blue)')}; margin-top: 0.2rem;">
            ${status}
          </div>
        </div>

        <div style="background: #f8fafc; padding: 0.85rem; border-radius: 8px; border: 1px solid var(--border-color); font-size: 0.875rem; color: var(--text-main);">
          <strong>Why it matters:</strong> This requirement is an officially documented prerequisite for establishing eligibility and proceeding with application appraisal.
        </div>

        ${meta.official_source_url ? `
          <div style="font-size: 0.85rem;">
            Official Source: <a href="${meta.official_source_url}" target="_blank" rel="noopener" style="color: var(--accent-blue); font-weight: 600;">${meta.official_source_url} ↗</a>
          </div>
        ` : ''}

        ${connOppsHtml}
      </div>
    `;

    modal.style.display = "flex";
  }

  closeReqModal() {
    const modal = document.getElementById("reqDetailModal");
    if (modal) modal.style.display = "none";
  }

  showSupportModal(nodeId) {
    if (!this.graphData || !this.graphData.nodes) return;
    const node = this.graphData.nodes.find(n => n.id === nodeId);
    if (!node) return;

    const modal = document.getElementById("supDetailModal");
    const titleEl = document.getElementById("supModalTitle");
    const bodyEl = document.getElementById("supModalBody");

    if (!modal || !bodyEl) return;

    titleEl.textContent = node.label || "Support Benefit Details";
    const meta = node.metadata || {};
    const connOppIds = meta.connected_opportunities || [];

    let connOppsHtml = "";
    if (connOppIds.length > 0 && this.analysisResult) {
      const allOpps = [
        ...(this.analysisResult.best_matches || []),
        ...(this.analysisResult.more_information_needed || [])
      ];
      const matched = allOpps.filter(o => connOppIds.includes(o.opportunity_id));
      if (matched.length > 0) {
        connOppsHtml = `
          <div style="margin-top: 1rem;">
            <strong style="color: var(--primary-navy); font-size: 0.875rem;">Schemes Providing This Support Benefit:</strong>
            <div style="display: flex; flex-direction: column; gap: 0.4rem; margin-top: 0.35rem;">
              ${matched.map(m => `
                <div onclick="myOpportunities.closeSupModal(); app.showSchemeDetail('${m.opportunity_id}', 'dashboard', 'graph');" 
                     style="background: #f8fafc; border: 1px solid var(--border-color); padding: 0.5rem 0.75rem; border-radius: 6px; cursor: pointer; font-size: 0.85rem; color: var(--accent-blue); font-weight: 600;">
                  🎯 ${m.opportunity_name || m.name} ↗
                </div>
              `).join('')}
            </div>
          </div>
        `;
      }
    }

    bodyEl.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 0.85rem; margin-top: 0.5rem;">
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 0.85rem; border-radius: 8px; font-size: 0.875rem; color: #166534;">
          <strong>Benefit Scope:</strong> This support assistance is directly provided by matched schemes to contribute toward your business goals.
        </div>

        ${connOppsHtml}
      </div>
    `;

    modal.style.display = "flex";
  }

  closeSupModal() {
    const modal = document.getElementById("supDetailModal");
    if (modal) modal.style.display = "none";
  }
}

window.myOpportunities = new MyOpportunitiesComponent();
