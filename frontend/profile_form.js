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

    // Core Required fields
    if (["age", "state", "sector", "business_stage"].includes(fieldKey)) {
      if (isSet) {
        return `<span style="font-size: 0.725rem; font-weight: 700; color: #138808; background: #eaf7ea; padding: 0.15rem 0.5rem; border-radius: 9999px;">${isDetected ? '✓ Detected' : '✓ Confirmed'}</span>`;
      }
      return `<span style="font-size: 0.725rem; font-weight: 700; color: #dc2626; background: #fef2f2; padding: 0.15rem 0.5rem; border-radius: 9999px;">Required</span>`;
    }

    // Qualification specific confirmation check
    if (fieldKey === "education" && !isSet && p.education_field) {
      return `<span style="font-size: 0.725rem; font-weight: 700; color: #d97706; background: #fffbe6; padding: 0.15rem 0.5rem; border-radius: 9999px;">Please confirm</span>`;
    }

    // Financial fields
    if (["annual_income", "available_capital", "project_cost"].includes(fieldKey)) {
      if (isSet) {
        return `<span style="font-size: 0.725rem; font-weight: 700; color: #138808; background: #eaf7ea; padding: 0.15rem 0.5rem; border-radius: 9999px;">${isDetected ? '✓ Detected' : '✓ Confirmed'}</span>`;
      }
      return `<span style="font-size: 0.725rem; font-weight: 700; color: #16335B; background: #f0f4f9; padding: 0.15rem 0.5rem; border-radius: 9999px;">May improve matches</span>`;
    }

    // Social Category
    if (fieldKey === "category") {
      if (isSet) {
        return `<span style="font-size: 0.725rem; font-weight: 700; color: #138808; background: #eaf7ea; padding: 0.15rem 0.5rem; border-radius: 9999px;">${isDetected ? '✓ Detected' : '✓ Confirmed'}</span>`;
      }
      return `<span style="font-size: 0.725rem; font-weight: 700; color: #7c3aed; background: #f3e8ff; padding: 0.15rem 0.5rem; border-radius: 9999px;">Needed for some schemes</span>`;
    }

    // Generic optional fields
    if (isSet) {
      return `<span style="font-size: 0.725rem; font-weight: 700; color: #138808; background: #eaf7ea; padding: 0.15rem 0.5rem; border-radius: 9999px;">${isDetected ? '✓ Detected' : '✓ Confirmed'}</span>`;
    }
    return `<span style="font-size: 0.725rem; font-weight: 700; color: #5a6e85; background: #f1f5f9; padding: 0.15rem 0.5rem; border-radius: 9999px;">Optional</span>`;
  }

  updateForm(container) {
    if (!container) return;
    const p = this.currentProfile;
    const readiness = this.calculateReadiness(p);

    container.innerHTML = `
      <!-- Core Profile Completeness Readiness Card -->
      <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: 16px; padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.65rem; flex-wrap: wrap; gap: 0.5rem;">
          <div>
            <h3 style="font-size: 1.1rem; color: var(--primary-navy); margin: 0; font-weight: 800;">
              ${readiness.isComplete ? '✓ Profile Readiness: 100%' : 'Profile readiness'}
            </h3>
            <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.15rem;">
              Core required fields: Age, Location State, Business Sector, and Business Stage.
            </p>
          </div>
          <span style="font-size: 0.9rem; font-weight: 800; color: ${readiness.isComplete ? '#138808' : '#C96F00'}; background: ${readiness.isComplete ? '#eaf7ea' : '#FFF4E5'}; padding: 0.35rem 0.8rem; border-radius: 9999px;">
            Core profile: ${readiness.completed} / ${readiness.total} complete (${readiness.percentage}%)
          </span>
        </div>

        <!-- Progress Bar -->
        <div style="width: 100%; height: 10px; background: #e2e8f0; border-radius: 9999px; overflow: hidden;">
          <div style="width: ${readiness.percentage}%; height: 100%; background: ${readiness.isComplete ? '#138808' : '#FF9933'}; transition: width 0.3s ease;"></div>
        </div>
      </div>

      <form id="manualProfileForm" onsubmit="event.preventDefault(); window.profileForm.handleSubmit();">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.25rem; margin-bottom: 1.5rem;">
          
          <!-- Section 1: PERSONAL DETAILS -->
          <div style="background: #ffffff; padding: 1.25rem; border-radius: 14px; border: 1px solid var(--border-color); border-top: 3px solid var(--primary-navy); box-shadow: var(--shadow-sm);">
            <h4 style="color: var(--primary-navy); font-size: 1rem; margin-bottom: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; font-weight: 800;">
              1. PERSONAL DETAILS
            </h4>
            
            <div style="margin-bottom: 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">Age *</label>
                ${this.getStatusBadge('age', p)}
              </div>
              <input type="number" id="inpAge" min="1" max="120" value="${p.age || ''}" placeholder="e.g. 24" 
                     oninput="window.profileForm.handleInput('age', this.value ? parseInt(this.value) : null)"
                     style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem; outline: none;">
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">Required</div>
            </div>

            <div style="margin-bottom: 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">Gender</label>
                ${this.getStatusBadge('gender', p)}
              </div>
              <select id="inpGender" onchange="window.profileForm.handleInput('gender', this.value || null)" style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem;">
                <option value="">Select Gender</option>
                <option value="Male" ${p.gender === 'Male' ? 'selected' : ''}>Male</option>
                <option value="Female" ${p.gender === 'Female' ? 'selected' : ''}>Female</option>
                <option value="Transgender" ${p.gender === 'Transgender' ? 'selected' : ''}>Transgender</option>
              </select>
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">Optional</div>
            </div>

            <div style="margin-bottom: 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">State *</label>
                ${this.getStatusBadge('state', p)}
              </div>
              <input type="text" id="inpState" value="${p.state || ''}" placeholder="e.g. Tamil Nadu" 
                     oninput="window.profileForm.handleInput('state', this.value || null)"
                     style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem;">
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">Required</div>
            </div>

            <div style="margin-bottom: 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">District / City</label>
                ${this.getStatusBadge('district', p)}
              </div>
              <input type="text" id="inpDistrict" value="${p.district || ''}" placeholder="e.g. Chennai" 
                     oninput="window.profileForm.handleInput('district', this.value || null)"
                     style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem;">
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">Optional</div>
            </div>

            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">Social Category</label>
                ${this.getStatusBadge('category', p)}
              </div>
              <select id="inpCategory" onchange="window.profileForm.handleInput('category', this.value || null)" style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem;">
                <option value="">Select Category ▼</option>
                <option value="General" ${p.category === 'General' ? 'selected' : ''}>General</option>
                <option value="OBC" ${p.category === 'OBC' ? 'selected' : ''}>OBC</option>
                <option value="SC" ${p.category === 'SC' ? 'selected' : ''}>SC</option>
                <option value="ST" ${p.category === 'ST' ? 'selected' : ''}>ST</option>
                <option value="Minority" ${p.category === 'Minority' ? 'selected' : ''}>Minority</option>
              </select>
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">Needed for some schemes</div>
            </div>
          </div>

          <!-- Section 2: FINANCIAL INFORMATION -->
          <div style="background: #ffffff; padding: 1.25rem; border-radius: 14px; border: 1px solid var(--border-color); border-top: 3px solid #FF9933; box-shadow: var(--shadow-sm);">
            <h4 style="color: var(--primary-navy); font-size: 1rem; margin-bottom: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; font-weight: 800;">
              2. FINANCIAL INFORMATION
            </h4>
            
            <div style="margin-bottom: 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">Annual Income (₹)</label>
                ${this.getStatusBadge('annual_income', p)}
              </div>
              <input type="number" id="inpIncome" min="0" value="${p.annual_income !== null && p.annual_income !== undefined ? p.annual_income : ''}" placeholder="Enter annual income" 
                     oninput="window.profileForm.handleInput('annual_income', this.value ? parseFloat(this.value) : null)"
                     style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem;">
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">May improve matches</div>
            </div>

            <div style="margin-bottom: 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">Available Capital (₹)</label>
                ${this.getStatusBadge('available_capital', p)}
              </div>
              <input type="number" id="inpCapital" min="0" value="${p.available_capital !== null && p.available_capital !== undefined ? p.available_capital : ''}" placeholder="Enter available capital" 
                     oninput="window.profileForm.handleInput('available_capital', this.value ? parseFloat(this.value) : null)"
                     style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem;">
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">May improve matches</div>
            </div>

            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">Estimated Project Cost (₹)</label>
                ${this.getStatusBadge('project_cost', p)}
              </div>
              <input type="number" id="inpProjectCost" min="0" value="${p.project_cost !== null && p.project_cost !== undefined ? p.project_cost : ''}" placeholder="Enter estimated project cost" 
                     oninput="window.profileForm.handleInput('project_cost', this.value ? parseFloat(this.value) : null)"
                     style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem;">
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">May improve matches</div>
            </div>
          </div>

          <!-- Section 3: BUSINESS DETAILS -->
          <div style="background: #ffffff; padding: 1.25rem; border-radius: 14px; border: 1px solid var(--border-color); border-top: 3px solid #138808; box-shadow: var(--shadow-sm);">
            <h4 style="color: var(--primary-navy); font-size: 1rem; margin-bottom: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; font-weight: 800;">
              3. BUSINESS DETAILS
            </h4>

            <div style="margin-bottom: 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">Qualification</label>
                ${this.getStatusBadge('education', p)}
              </div>
              <select id="inpEducation" onchange="window.profileForm.handleInput('education', this.value || null)" style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem;">
                <option value="">Select Qualification ▼</option>
                <option value="Degree" ${p.education === 'Degree' ? 'selected' : ''}>Degree (Graduate)</option>
                <option value="Postgraduate" ${p.education === 'Postgraduate' ? 'selected' : ''}>Postgraduate (Masters)</option>
                <option value="Diploma" ${p.education === 'Diploma' ? 'selected' : ''}>Diploma / Polytechnic</option>
                <option value="ITI" ${p.education === 'ITI' ? 'selected' : ''}>ITI</option>
                <option value="12th Pass" ${p.education === '12th Pass' ? 'selected' : ''}>12th Pass</option>
                <option value="10th Pass" ${p.education === '10th Pass' ? 'selected' : ''}>10th Pass</option>
                <option value="8th Pass" ${p.education === '8th Pass' ? 'selected' : ''}>8th Pass</option>
              </select>
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">Optional</div>
            </div>

            <div style="margin-bottom: 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">Field of Study</label>
                ${this.getStatusBadge('education_field', p)}
              </div>
              <input type="text" id="inpEducationField" value="${p.education_field || ''}" placeholder="e.g. Computer Science, Mechanical" 
                     oninput="window.profileForm.handleInput('education_field', this.value || null)"
                     style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem;">
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">Optional</div>
            </div>

            <div style="margin-bottom: 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">Business / Activity Sector *</label>
                ${this.getStatusBadge('sector', p)}
              </div>
              <select id="inpSector" onchange="window.profileForm.handleInput('sector', this.value || null)" style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem;">
                <option value="">Select Primary Sector ▼</option>
                <option value="Agriculture & Allied" ${p.sector === 'Agriculture & Allied' ? 'selected' : ''}>Agriculture & Allied</option>
                <option value="Food Processing & Agri Value Addition" ${p.sector === 'Food Processing & Agri Value Addition' ? 'selected' : ''}>Food Processing & Agri Value Addition</option>
                <option value="MSME & Manufacturing" ${p.sector === 'MSME & Manufacturing' ? 'selected' : ''}>MSME & Manufacturing</option>
                <option value="Finance & Credit" ${p.sector === 'Finance & Credit' ? 'selected' : ''}>Finance & Credit</option>
                <option value="Startup & Innovation" ${p.sector === 'Startup & Innovation' ? 'selected' : ''}>Startup & Innovation</option>
                <option value="Skills & Employment" ${p.sector === 'Skills & Employment' ? 'selected' : ''}>Skills & Employment</option>
                <option value="Women & SHG Entrepreneurship" ${p.sector === 'Women & SHG Entrepreneurship' ? 'selected' : ''}>Women & SHG Entrepreneurship</option>
                <option value="Social Empowerment & Inclusive Entrepreneurship" ${p.sector === 'Social Empowerment & Inclusive Entrepreneurship' ? 'selected' : ''}>Social Empowerment & Inclusive Entrepreneurship</option>
                <option value="Handicrafts, Handloom & Artisan Economy" ${p.sector === 'Handicrafts, Handloom & Artisan Economy' ? 'selected' : ''}>Handicrafts, Handloom & Artisan Economy</option>
                <option value="Export, Market Access & Business Growth" ${p.sector === 'Export, Market Access & Business Growth' ? 'selected' : ''}>Export, Market Access & Business Growth</option>
              </select>
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">Required</div>
            </div>

            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-navy);">Business Stage *</label>
                ${this.getStatusBadge('business_stage', p)}
              </div>
              <select id="inpStage" onchange="window.profileForm.handleInput('business_stage', this.value || null)" style="width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem;">
                <option value="">Select Business Stage ▼</option>
                <option value="Idea" ${(p.business_stage === 'Idea' || p.business_type === 'Idea') ? 'selected' : ''}>Idea / New Business Intention</option>
                <option value="Startup" ${(p.business_stage === 'Startup' || p.business_type === 'Startup') ? 'selected' : ''}>Startup (Early Stage)</option>
                <option value="Existing" ${(p.business_stage === 'Existing' || p.business_type === 'Existing') ? 'selected' : ''}>Existing Operating Business</option>
              </select>
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">Required</div>
            </div>
          </div>

        </div>

        <!-- Submit & Gate Action Bar -->
        <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: 14px; padding: 1.25rem; display: flex; flex-direction: column; align-items: center; gap: 0.6rem; box-shadow: var(--shadow-sm);">
          
          <button type="submit" id="btnFindOpportunities" class="${readiness.isComplete ? 'btn-primary' : 'btn-outline'}" 
                  ${readiness.isComplete ? '' : 'disabled style="opacity: 0.6; cursor: not-allowed; background: #e2e8f0; color: #64748b; border-color: #cbd5e1;"'}
                  style="font-size: 1.05rem; padding: 0.85rem 2.2rem; border-radius: 9999px; font-weight: 700; width: 100%; max-width: 380px; ${readiness.isComplete ? 'background: #138808; color: #ffffff;' : ''}">
            Find My Opportunities →
          </button>

          ${!readiness.isComplete ? `
            <p style="color: var(--crimson); font-size: 0.85rem; font-weight: 600; text-align: center; margin: 0;">
              ⚠️ Complete the required core fields above (Age, State, Business Sector, Business Stage) to view personalized opportunities.
            </p>
          ` : `
            <p style="color: #138808; font-size: 0.85rem; font-weight: 600; text-align: center; margin: 0;">
              ✓ Your core profile is ready! Click above to generate personalized scheme matches.
            </p>
          `}
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
    const container = document.getElementById("manualFormContainer");
    if (container) {
      this.updateForm(container);
    }
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
