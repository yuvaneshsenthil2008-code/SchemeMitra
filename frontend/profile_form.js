/**
 * SchemeMitra v2 — Structured Profile Form & Readiness Gate Component
 */

class ProfileFormComponent {
  constructor() {
    this.currentProfile = {};
    this.onSaveCallback = null;
  }

  render(container, initialProfile = {}, onSaveCallback) {
    this.currentProfile = { ...initialProfile };
    this.onSaveCallback = onSaveCallback;
    this.updateForm(container);
  }

  calculateReadiness(p) {
    const coreFields = [
      { key: "age", label: "Age", valid: p.age !== null && p.age !== undefined && p.age !== "" && !isNaN(Number(p.age)) && Number(p.age) >= 1 && Number(p.age) <= 120 },
      { key: "state", label: "State", valid: Boolean(p.state && String(p.state).trim()) },
      { key: "sector", label: "Business Sector", valid: Boolean(p.sector && String(p.sector).trim()) },
      { key: "business_stage", label: "Business Stage", valid: Boolean((p.business_stage || p.business_type) && String(p.business_stage || p.business_type).trim()) }
    ];

    const completed = coreFields.filter(f => f.valid).length;
    const total = coreFields.length;
    const percentage = Math.round((completed / total) * 100);
    const isComplete = completed === total;

    return { completed, total, percentage, isComplete, coreFields };
  }

  getStatusBadge(fieldKey, p) {
    const val = p[fieldKey];
    const isSet = val !== null && val !== undefined && String(val).trim() !== "";
    const isDetected = p._detectedFields && p._detectedFields.has(fieldKey);
    const t = (k) => window.i18n ? window.i18n.get(k) : k;

    // Core Required fields
    if (["age", "state", "sector", "business_stage"].includes(fieldKey)) {
      if (isSet) {
        return `<span style="font-size: 0.725rem; font-weight: 700; color: #138808; background: #eaf7ea; padding: 0.15rem 0.5rem; border-radius: 9999px;">${isDetected ? t('status_detected') : t('status_confirmed')}</span>`;
      }
      return `<span style="font-size: 0.725rem; font-weight: 700; color: #dc2626; background: #fef2f2; padding: 0.15rem 0.5rem; border-radius: 9999px;">${t('status_required')}</span>`;
    }

    // Qualification specific confirmation check
    if (fieldKey === "education" && !isSet && p.education_field) {
      return `<span style="font-size: 0.725rem; font-weight: 700; color: #d97706; background: #fffbe6; padding: 0.15rem 0.5rem; border-radius: 9999px;">${t('status_please_confirm')}</span>`;
    }

    // Financial fields
    if (["annual_income", "available_capital", "project_cost"].includes(fieldKey)) {
      if (isSet) {
        return `<span style="font-size: 0.725rem; font-weight: 700; color: #138808; background: #eaf7ea; padding: 0.15rem 0.5rem; border-radius: 9999px;">${isDetected ? t('status_detected') : t('status_confirmed')}</span>`;
      }
      return `<span style="font-size: 0.725rem; font-weight: 700; color: #16335B; background: #f0f4f9; padding: 0.15rem 0.5rem; border-radius: 9999px;">${t('status_optional')}</span>`;
    }

    // Social Category
    if (fieldKey === "category") {
      if (isSet) {
        return `<span style="font-size: 0.725rem; font-weight: 700; color: #138808; background: #eaf7ea; padding: 0.15rem 0.5rem; border-radius: 9999px;">${isDetected ? t('status_detected') : t('status_confirmed')}</span>`;
      }
      return `<span style="font-size: 0.725rem; font-weight: 700; color: #7c3aed; background: #f3e8ff; padding: 0.15rem 0.5rem; border-radius: 9999px;">${t('status_needed_some')}</span>`;
    }

    // Generic optional fields
    if (isSet) {
      return `<span style="font-size: 0.725rem; font-weight: 700; color: #138808; background: #eaf7ea; padding: 0.15rem 0.5rem; border-radius: 9999px;">${isDetected ? t('status_detected') : t('status_confirmed')}</span>`;
    }
    return `<span style="font-size: 0.725rem; font-weight: 700; color: #5a6e85; background: #f1f5f9; padding: 0.15rem 0.5rem; border-radius: 9999px;">${t('status_optional')}</span>`;
  }

  updateDependentUI() {
    const p = this.currentProfile;
    const readiness = this.calculateReadiness(p);
    const t = (k) => window.i18n ? window.i18n.get(k) : k;

    const rTitle = document.getElementById("readinessTitle");
    if (rTitle) {
      rTitle.textContent = readiness.isComplete ? t('profile_readiness_100') : t('profile_readiness_title');
    }

    const rBadge = document.getElementById("readinessBadge");
    if (rBadge) {
      rBadge.textContent = t('profile_core_progress').replace('{completed}', readiness.completed).replace('{total}', readiness.total).replace('{percentage}', readiness.percentage);
      rBadge.style.color = readiness.isComplete ? "#138808" : "#C96F00";
      rBadge.style.background = readiness.isComplete ? "#eaf7ea" : "#FFF4E5";
    }

    const rBar = document.getElementById("readinessProgressBar");
    if (rBar) {
      rBar.style.width = `${readiness.percentage}%`;
      rBar.style.background = readiness.isComplete ? "#138808" : "#FF9933";
    }

    const allFieldKeys = [
      "age", "gender", "state", "district", "category",
      "annual_income", "available_capital", "project_cost",
      "education", "education_field", "sector", "business_stage"
    ];
    allFieldKeys.forEach(fieldKey => {
      const badgeEl = document.getElementById(`badge_${fieldKey}`);
      if (badgeEl) {
        badgeEl.innerHTML = this.getStatusBadge(fieldKey, p);
      }
    });

    const btn = document.getElementById("btnFindOpportunities");
    if (btn) {
      btn.className = readiness.isComplete ? "btn-primary" : "btn-outline";
      btn.textContent = t('btn_find_my_opportunities') + " →";
      if (readiness.isComplete) {
        btn.removeAttribute("disabled");
        btn.style.opacity = "1";
        btn.style.cursor = "pointer";
        btn.style.background = "#138808";
        btn.style.color = "#ffffff";
        btn.style.borderColor = "#138808";
      } else {
        btn.setAttribute("disabled", "disabled");
        btn.style.opacity = "0.6";
        btn.style.cursor = "not-allowed";
        btn.style.background = "#e2e8f0";
        btn.style.color = "#64748b";
        btn.style.borderColor = "#cbd5e1";
      }
    }

    const noticeEl = document.getElementById("readinessNotice");
    if (noticeEl) {
      if (readiness.isComplete) {
        noticeEl.style.color = "#138808";
        noticeEl.textContent = t('profile_notice_complete');
      } else {
        noticeEl.style.color = "var(--crimson)";
        noticeEl.textContent = t('profile_notice_incomplete');
      }
    }
  }

  updateForm(container) {
    if (!container) return;
    const p = this.currentProfile;
    const readiness = this.calculateReadiness(p);
    const t = (k) => window.i18n ? window.i18n.get(k) : k;
    const getSec = (s) => window.i18n ? window.i18n.getSectorLabel(s) : s;

    const sectors = [
      "Agriculture & Allied",
      "Food Processing & Agri Value Addition",
      "MSME & Manufacturing",
      "Finance & Credit",
      "Startup & Innovation",
      "Skills & Employment",
      "Women & SHG Entrepreneurship",
      "Social Empowerment & Inclusive Entrepreneurship",
      "Handicrafts, Handloom & Artisan Economy",
      "Export, Market Access & Business Growth"
    ];

    container.innerHTML = `
      <!-- Core Profile Completeness Readiness Card -->
      <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: 16px; padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.65rem; flex-wrap: wrap; gap: 0.5rem;">
          <div>
            <h3 id="readinessTitle" style="font-size: 1.1rem; color: var(--primary-navy); margin: 0; font-weight: 800;">
              ${readiness.isComplete ? t('profile_readiness_100') : t('profile_readiness_title')}
            </h3>
            <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.15rem;">
              ${t('profile_core_required_note')}
            </p>
          </div>
          <span id="readinessBadge" style="font-size: 0.9rem; font-weight: 800; color: ${readiness.isComplete ? '#138808' : '#C96F00'}; background: ${readiness.isComplete ? '#eaf7ea' : '#FFF4E5'}; padding: 0.35rem 0.8rem; border-radius: 9999px;">
            ${t('profile_core_progress').replace('{completed}', readiness.completed).replace('{total}', readiness.total).replace('{percentage}', readiness.percentage)}
          </span>
        </div>

        <!-- Progress Bar -->
        <div style="width: 100%; height: 10px; background: #e2e8f0; border-radius: 9999px; overflow: hidden;">
          <div id="readinessProgressBar" style="width: ${readiness.percentage}%; height: 100%; background: ${readiness.isComplete ? '#138808' : '#FF9933'}; transition: width 0.3s ease;"></div>
        </div>
      </div>

      <form id="manualProfileForm" onsubmit="event.preventDefault(); window.profileForm.handleSubmit();">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.25rem; margin-bottom: 1.5rem;">
          
          <!-- Section 1: PERSONAL DETAILS -->
          <div style="background: #ffffff; padding: 1.25rem; border-radius: 14px; border: 1px solid var(--border-color); border-top: 3px solid var(--primary-navy); box-shadow: var(--shadow-sm);">
            <h4 style="color: var(--primary-navy); font-size: 1rem; margin-bottom: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; font-weight: 800;">
              ${t('profile_section_personal')}
            </h4>
            
            <div style="margin-bottom: 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">${t('lbl_age')} *</label>
                <span id="badge_age">${this.getStatusBadge('age', p)}</span>
              </div>
              <input type="number" id="inpAge" min="1" max="120" value="${p.age || ''}" placeholder="e.g. 24" 
                     oninput="window.profileForm.handleInput('age', this.value ? parseInt(this.value) : null)"
                     style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem; outline: none;">
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">${t('status_required')}</div>
            </div>

            <div style="margin-bottom: 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">${t('lbl_gender')}</label>
                <span id="badge_gender">${this.getStatusBadge('gender', p)}</span>
              </div>
              <select id="inpGender" onchange="window.profileForm.handleInput('gender', this.value || null)" style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem;">
                <option value="">${t('select_gender')}</option>
                <option value="Male" ${p.gender === 'Male' ? 'selected' : ''}>${t('gender_male')}</option>
                <option value="Female" ${p.gender === 'Female' ? 'selected' : ''}>${t('gender_female')}</option>
                <option value="Transgender" ${p.gender === 'Transgender' ? 'selected' : ''}>${t('gender_trans')}</option>
              </select>
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">${t('status_optional')}</div>
            </div>

            <div style="margin-bottom: 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">${t('lbl_state')} *</label>
                <span id="badge_state">${this.getStatusBadge('state', p)}</span>
              </div>
              <input type="text" id="inpState" value="${p.state || ''}" placeholder="e.g. Tamil Nadu" 
                     oninput="window.profileForm.handleInput('state', this.value || null)"
                     style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem;">
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">${t('status_required')}</div>
            </div>

            <div style="margin-bottom: 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">${t('lbl_district')}</label>
                <span id="badge_district">${this.getStatusBadge('district', p)}</span>
              </div>
              <input type="text" id="inpDistrict" value="${p.district || ''}" placeholder="e.g. Chennai" 
                     oninput="window.profileForm.handleInput('district', this.value || null)"
                     style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem;">
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">${t('status_optional')}</div>
            </div>

            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">${t('lbl_category')}</label>
                <span id="badge_category">${this.getStatusBadge('category', p)}</span>
              </div>
              <select id="inpCategory" onchange="window.profileForm.handleInput('category', this.value || null)" style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem;">
                <option value="">${t('select_category')} ▼</option>
                <option value="General" ${p.category === 'General' ? 'selected' : ''}>${t('cat_general')}</option>
                <option value="OBC" ${p.category === 'OBC' ? 'selected' : ''}>${t('cat_obc')}</option>
                <option value="SC" ${p.category === 'SC' ? 'selected' : ''}>${t('cat_sc')}</option>
                <option value="ST" ${p.category === 'ST' ? 'selected' : ''}>${t('cat_st')}</option>
                <option value="Minority" ${p.category === 'Minority' ? 'selected' : ''}>${t('cat_minority')}</option>
              </select>
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">${t('status_needed_some')}</div>
            </div>
          </div>

          <!-- Section 2: FINANCIAL INFORMATION -->
          <div style="background: #ffffff; padding: 1.25rem; border-radius: 14px; border: 1px solid var(--border-color); border-top: 3px solid #FF9933; box-shadow: var(--shadow-sm);">
            <h4 style="color: var(--primary-navy); font-size: 1rem; margin-bottom: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; font-weight: 800;">
              ${t('profile_section_financial')}
            </h4>
            
            <div style="margin-bottom: 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">${t('lbl_income')}</label>
                <span id="badge_annual_income">${this.getStatusBadge('annual_income', p)}</span>
              </div>
              <input type="number" id="inpIncome" min="0" value="${p.annual_income !== null && p.annual_income !== undefined ? p.annual_income : ''}" placeholder="Enter annual income" 
                     oninput="window.profileForm.handleInput('annual_income', this.value ? parseFloat(this.value) : null)"
                     style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem;">
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">${t('status_optional')}</div>
            </div>

            <div style="margin-bottom: 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">${t('lbl_capital')}</label>
                <span id="badge_available_capital">${this.getStatusBadge('available_capital', p)}</span>
              </div>
              <input type="number" id="inpCapital" min="0" value="${p.available_capital !== null && p.available_capital !== undefined ? p.available_capital : ''}" placeholder="Enter available capital" 
                     oninput="window.profileForm.handleInput('available_capital', this.value ? parseFloat(this.value) : null)"
                     style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem;">
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">${t('status_optional')}</div>
            </div>

            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">${t('lbl_project_cost')}</label>
                <span id="badge_project_cost">${this.getStatusBadge('project_cost', p)}</span>
              </div>
              <input type="number" id="inpProjectCost" min="0" value="${p.project_cost !== null && p.project_cost !== undefined ? p.project_cost : ''}" placeholder="Enter estimated project cost" 
                     oninput="window.profileForm.handleInput('project_cost', this.value ? parseFloat(this.value) : null)"
                     style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem;">
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">${t('status_optional')}</div>
            </div>
          </div>

          <!-- Section 3: BUSINESS DETAILS -->
          <div style="background: #ffffff; padding: 1.25rem; border-radius: 14px; border: 1px solid var(--border-color); border-top: 3px solid #138808; box-shadow: var(--shadow-sm);">
            <h4 style="color: var(--primary-navy); font-size: 1rem; margin-bottom: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; font-weight: 800;">
              ${t('profile_section_business')}
            </h4>

            <div style="margin-bottom: 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">${t('lbl_education')}</label>
                <span id="badge_education">${this.getStatusBadge('education', p)}</span>
              </div>
              <select id="inpEducation" onchange="window.profileForm.handleInput('education', this.value || null)" style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem;">
                <option value="">${t('select_stage')} ▼</option>
                <option value="Degree" ${p.education === 'Degree' ? 'selected' : ''}>Degree (Graduate)</option>
                <option value="Postgraduate" ${p.education === 'Postgraduate' ? 'selected' : ''}>Postgraduate (Masters)</option>
                <option value="Diploma" ${p.education === 'Diploma' ? 'selected' : ''}>Diploma / Polytechnic</option>
                <option value="ITI" ${p.education === 'ITI' ? 'selected' : ''}>ITI</option>
                <option value="12th Pass" ${p.education === '12th Pass' ? 'selected' : ''}>12th Pass</option>
                <option value="10th Pass" ${p.education === '10th Pass' ? 'selected' : ''}>10th Pass</option>
                <option value="8th Pass" ${p.education === '8th Pass' ? 'selected' : ''}>8th Pass</option>
              </select>
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">${t('status_optional')}</div>
            </div>

            <div style="margin-bottom: 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">${t('lbl_education_field')}</label>
                <span id="badge_education_field">${this.getStatusBadge('education_field', p)}</span>
              </div>
              <input type="text" id="inpEducationField" value="${p.education_field || ''}" placeholder="e.g. Computer Science, Mechanical" 
                     oninput="window.profileForm.handleInput('education_field', this.value || null)"
                     style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem;">
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">${t('status_optional')}</div>
            </div>

            <div style="margin-bottom: 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">${t('lbl_target_sector')} *</label>
                <span id="badge_sector">${this.getStatusBadge('sector', p)}</span>
              </div>
              <select id="inpSector" onchange="window.profileForm.handleInput('sector', this.value || null)" style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem;">
                <option value="">${t('select_sector')} ▼</option>
                ${sectors.map(sec => `<option value="${sec}" ${p.sector === sec ? 'selected' : ''}>${getSec(sec)}</option>`).join('')}
              </select>
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">${t('status_required')}</div>
            </div>

            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">${t('lbl_business_stage')} *</label>
                <span id="badge_business_stage">${this.getStatusBadge('business_stage', p)}</span>
              </div>
              <select id="inpStage" onchange="window.profileForm.handleInput('business_stage', this.value || null)" style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem;">
                <option value="">${t('select_stage')} ▼</option>
                <option value="Idea" ${(p.business_stage === 'Idea' || p.business_type === 'Idea') ? 'selected' : ''}>${t('stage_idea')}</option>
                <option value="Startup" ${(p.business_stage === 'Startup' || p.business_type === 'Startup') ? 'selected' : ''}>${t('stage_startup')}</option>
                <option value="Existing" ${(p.business_stage === 'Existing' || p.business_type === 'Existing') ? 'selected' : ''}>${t('stage_existing')}</option>
              </select>
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">${t('status_required')}</div>
            </div>
          </div>

        </div>

        <!-- Submit & Gate Action Bar -->
        <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: 14px; padding: 1.25rem; display: flex; flex-direction: column; align-items: center; gap: 0.6rem; box-shadow: var(--shadow-sm);">
          
          <button type="submit" id="btnFindOpportunities" class="${readiness.isComplete ? 'btn-primary' : 'btn-outline'}" 
                  ${readiness.isComplete ? '' : 'disabled style="opacity: 0.6; cursor: not-allowed; background: #e2e8f0; color: #64748b; border-color: #cbd5e1;"'}
                  style="font-size: 1.05rem; padding: 0.85rem 2.2rem; border-radius: 9999px; font-weight: 700; width: 100%; max-width: 380px; ${readiness.isComplete ? 'background: #138808; color: #ffffff;' : ''}">
            ${t('btn_find_my_opportunities')} →
          </button>

          <p id="readinessNotice" style="color: ${readiness.isComplete ? '#138808' : 'var(--crimson)'}; font-size: 0.85rem; font-weight: 600; text-align: center; margin: 0;">
            ${!readiness.isComplete 
              ? t('profile_notice_incomplete') 
              : t('profile_notice_complete')}
          </p>
        </div>
      </form>
    `;
  }

  handleInput(key, value) {
    if (!this.currentProfile._detectedFields) this.currentProfile._detectedFields = new Set();
    this.currentProfile._detectedFields.delete(key);

    this.currentProfile[key] = value;
    if (key === "business_stage") {
      this.currentProfile.business_type = value;
      this.currentProfile.new_business = (value === "Idea" || value === "Startup");
    }

    // Selective DOM mutation: update dependent readiness card, field badges, and submit button
    // WITHOUT re-rendering the complete form container (which destroys focused input elements)!
    this.updateDependentUI();
  }

  handleSubmit() {
    const readiness = this.calculateReadiness(this.currentProfile);
    if (!readiness.isComplete) {
      alert("Please complete the required core fields (Age, State, Business Sector, Business Stage) before proceeding.");
      return;
    }

    const p = this.currentProfile;
    if (p.age !== null && p.age !== undefined && (!Number.isInteger(Number(p.age)) || Number(p.age) < 1 || Number(p.age) > 120)) {
      alert("Please enter a valid age between 1 and 120.");
      return;
    }

    if (this.onSaveCallback) {
      this.onSaveCallback(p);
    }
  }
}

window.profileForm = new ProfileFormComponent();
