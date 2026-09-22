from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path, old, new):
    text = path.read_text(encoding='utf-8')
    if old not in text:
        raise RuntimeError(f'Pattern not found in {path}: {old[:120]!r}')
    text = text.replace(old, new, 1)
    path.write_text(text, encoding='utf-8')

# 1) Goal Pathway UI: remove Total Pathway Steps summary card only.
p = ROOT / 'frontend/my_opportunities.js'
replace_once(p, '''          <div>\n            <div style="font-size: 0.75rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Total Pathway Steps</div>\n            <div style="font-size: 1.35rem; font-weight: 800; color: #2563eb;">${summary.total_steps || 0}</div>\n          </div>\n''', '')

# Add Gender + Social Category to Where You Are Now (preserves existing Disability and Goal cards).
needle = '''          <div style="background: #f8fafc; padding: 0.65rem 0.85rem; border-radius: 8px; border: 1px solid #e2e8f0;">\n            <div style="font-size: 0.75rem; color: var(--text-muted); font-weight: 600;">Disability</div>\n            <div style="font-weight: 700; color: var(--primary-navy); margin-top: 0.15rem;">${this.formatDisabilityStatus(currState.disability_status || profile.disability_status)}</div>\n          </div>\n'''
replacement = '''          <div style="background: #f8fafc; padding: 0.65rem 0.85rem; border-radius: 8px; border: 1px solid #e2e8f0;">\n            <div style="font-size: 0.75rem; color: var(--text-muted); font-weight: 600;">Gender</div>\n            <div style="font-weight: 700; color: var(--primary-navy); margin-top: 0.15rem;">${currState.gender || profile.gender || 'Not provided'}</div>\n          </div>\n          <div style="background: #f8fafc; padding: 0.65rem 0.85rem; border-radius: 8px; border: 1px solid #e2e8f0;">\n            <div style="font-size: 0.75rem; color: var(--text-muted); font-weight: 600;">Social Category</div>\n            <div style="font-weight: 700; color: var(--primary-navy); margin-top: 0.15rem;">${currState.category || profile.category || 'Not provided'}</div>\n          </div>\n          <div style="background: #f8fafc; padding: 0.65rem 0.85rem; border-radius: 8px; border: 1px solid #e2e8f0;">\n            <div style="font-size: 0.75rem; color: var(--text-muted); font-weight: 600;">Disability</div>\n            <div style="font-weight: 700; color: var(--primary-navy); margin-top: 0.15rem;">${this.formatDisabilityStatus(currState.disability_status || profile.disability_status)}</div>\n          </div>\n'''
replace_once(p, needle, replacement)

# 2) Home/Explore cards + updated catalogue counts.
p = ROOT / 'frontend/app.js'
# Dynamic fallback counts and fetch >100 opportunities.
text = p.read_text(encoding='utf-8')
text = text.replace('this.stats.catalogue_count || 100', 'this.stats.catalogue_count || 102')
text = text.replace('this.stats.requirements_count || 371', 'this.stats.requirements_count || 379')
text = text.replace('this.stats.relationships_count || 522', 'this.stats.relationships_count || 534')
text = text.replace('let url = "/api/opportunities?limit=100";', 'let url = "/api/opportunities?limit=200";')
p.write_text(text, encoding='utf-8')

# Add formatting methods to SchemeMitraApp.
insert_after = '''  normalizeProfileDefaults(profile = {}) {\n    const normalized = { ...(profile || {}) };\n    if (!normalized.selected_goal) {\n      normalized.selected_goal = normalized.business_goal || "GENERAL_READINESS";\n    }\n    if (normalized.disability_status === undefined) {\n      normalized.disability_status = null;\n    }\n    // Keep the legacy business_goal field synchronized for older pathway/NLP consumers.\n    if (!normalized.business_goal && normalized.selected_goal && normalized.selected_goal !== "GENERAL_READINESS") {\n      normalized.business_goal = normalized.selected_goal;\n    }\n    return normalized;\n  }\n'''
methods = '''\n  formatEligibleGenders(values, opportunity = null) {\n    if (opportunity && opportunity.gender_eligibility_display) return opportunity.gender_eligibility_display;\n    const list = Array.isArray(values) ? values.filter(Boolean) : [];\n    const all = ["Male", "Female", "Transgender"];\n    if (all.every(v => list.includes(v))) return window.i18n.get("lbl_all_genders");\n    return list.length ? list.join(" / ") : window.i18n.get("lbl_all_genders");\n  }\n\n  formatEligibleCategories(values, opportunity = null) {\n    if (opportunity && opportunity.social_category_eligibility_display) return opportunity.social_category_eligibility_display;\n    const list = Array.isArray(values) ? values.filter(Boolean) : [];\n    const all = ["General", "OBC", "SC", "ST", "Minority"];\n    if (all.every(v => list.includes(v))) return window.i18n.get("lbl_all_social_categories");\n    return list.length ? list.join(" / ") : window.i18n.get("lbl_all_social_categories");\n  }\n\n  formatDisabilityEligibility(value) {\n    return String(value || "ANY").toUpperCase() === "PERSON_WITH_DISABILITY"\n      ? window.i18n.get("lbl_persons_with_disabilities")\n      : window.i18n.get("lbl_any_disability_status");\n  }\n'''
replace_once(p, insert_after, insert_after + methods)

# Add demographic eligibility rows to public opportunity cards.
needle = '''          <p class="opp-benefit">${o.benefit_summary || o.eligibility_summary || ''}</p>\n          <div class="opp-meta">\n            <span>${window.i18n.get('lbl_scope')}: <strong>${scopeLabel || 'Central'}</strong></span>\n            <span>${window.i18n.get('lbl_support')}: <strong>${supportLabels || 'Financial'}</strong></span>\n'''
replacement = '''          <p class="opp-benefit">${o.benefit_summary || o.eligibility_summary || ''}</p>\n          <div style="display:flex; flex-wrap:wrap; gap:0.45rem 1rem; margin:0.65rem 0 0.75rem; font-size:0.78rem; color:var(--text-muted);">\n            <span>${window.i18n.get('lbl_gender')}: <strong style="color:var(--text-main);">${this.formatEligibleGenders(o.eligible_genders, o)}</strong></span>\n            <span>${window.i18n.get('lbl_social_category')}: <strong style="color:var(--text-main);">${this.formatEligibleCategories(o.eligible_social_categories, o)}</strong></span>\n            ${String(o.disability_eligibility || 'ANY').toUpperCase() === 'PERSON_WITH_DISABILITY' ? `<span>${window.i18n.get('lbl_disability_eligibility')}: <strong style="color:var(--text-main);">${this.formatDisabilityEligibility(o.disability_eligibility)}</strong></span>` : ''}\n          </div>\n          <div class="opp-meta">\n            <span>${window.i18n.get('lbl_scope')}: <strong>${scopeLabel || 'Central'}</strong></span>\n            <span>${window.i18n.get('lbl_support')}: <strong>${supportLabels || 'Financial'}</strong></span>\n'''
replace_once(p, needle, replacement)

# 3) Scheme Detail helpers + demographic info + personalized benefits.
p = ROOT / 'frontend/scheme_detail.js'
insert_after = '''  formatStateLabel(state) {\n    if (!state) return 'Need to Confirm';\n    const st = String(state).trim().toUpperCase();\n    if (st === 'COMPLETED') return 'Completed';\n    if (st === 'ACTION_NEEDED') return 'Action Needed';\n    if (st === 'VERIFY' || st === 'VERIFY_PREREQUISITE' || st === 'NEED_TO_CONFIRM') return 'Need to Confirm';\n    if (st === 'POTENTIAL') return 'Potential';\n    if (st === 'TARGET') return 'Target Goal';\n    return st.replace(/_/g, ' ');\n  }\n'''
methods = '''\n  canonicalCategory(value) {\n    const v = String(value || '').trim().toLowerCase();\n    if (!v) return '';\n    if (v === 'sc' || v.includes('scheduled caste')) return 'SC';\n    if (v === 'st' || v.includes('scheduled tribe')) return 'ST';\n    if (v === 'obc' || v.includes('other backward') || v.includes('backward class')) return 'OBC';\n    if (v.includes('minority')) return 'Minority';\n    if (v === 'general' || v === 'gen') return 'General';\n    return String(value).trim();\n  }\n\n  formatEligibleGenders(opp) {\n    if (opp.gender_eligibility_display) return opp.gender_eligibility_display;\n    const list = Array.isArray(opp.eligible_genders) ? opp.eligible_genders.filter(Boolean) : [];\n    const all = ['Male', 'Female', 'Transgender'];\n    if (all.every(v => list.includes(v))) return window.i18n.get('lbl_all_genders');\n    return list.length ? list.join(' / ') : window.i18n.get('lbl_all_genders');\n  }\n\n  formatEligibleCategories(opp) {\n    if (opp.social_category_eligibility_display) return opp.social_category_eligibility_display;\n    const list = Array.isArray(opp.eligible_social_categories) ? opp.eligible_social_categories.filter(Boolean) : [];\n    const all = ['General', 'OBC', 'SC', 'ST', 'Minority'];\n    if (all.every(v => list.includes(v))) return window.i18n.get('lbl_all_social_categories');\n    return list.length ? list.join(' / ') : window.i18n.get('lbl_all_social_categories');\n  }\n\n  formatDisabilityEligibility(opp) {\n    return String(opp.disability_eligibility || 'ANY').toUpperCase() === 'PERSON_WITH_DISABILITY'\n      ? window.i18n.get('lbl_persons_with_disabilities')\n      : window.i18n.get('lbl_any_disability_status');\n  }\n\n  demographicVariantMatches(variant, profile) {\n    if (!variant || !profile) return false;\n    const actual = {\n      social_categories: this.canonicalCategory(profile.category),\n      genders: String(profile.gender || '').trim(),\n      disability_status: String(profile.disability_status || '').trim().toUpperCase()\n    };\n\n    const dimensionMatches = (rules) => Object.entries(rules || {}).map(([key, values]) => {\n      const allowed = Array.isArray(values) ? values.map(v => String(v)) : [];\n      if (!allowed.length) return true;\n      let value = actual[key] || '';\n      if (key === 'social_categories') value = this.canonicalCategory(value);\n      if (key === 'disability_status') value = String(value).toUpperCase();\n      return allowed.some(v => key === 'social_categories'\n        ? this.canonicalCategory(v) === value\n        : (key === 'disability_status' ? String(v).toUpperCase() === value : String(v) === value));\n    });\n\n    if (variant.match_all) {\n      const checks = dimensionMatches(variant.match_all);\n      if (!checks.length || !checks.every(Boolean)) return false;\n    }\n    if (variant.match_any) {\n      const checks = dimensionMatches(variant.match_any);\n      if (!checks.length || !checks.some(Boolean)) return false;\n    }\n    return Boolean(variant.match_all || variant.match_any);\n  }\n\n  getPersonalizedDemographicBenefit(opp, profile) {\n    if (!profile || !Array.isArray(opp.demographic_benefit_variants)) return null;\n    return opp.demographic_benefit_variants.find(v => this.demographicVariantMatches(v, profile)) || null;\n  }\n'''
replace_once(p, insert_after, insert_after + methods)

# Define personalized benefit once renderScreen has opp/profile.
needle = '''    const opp = this.schemeData || {};\n    const nameObj = window.i18n.getLocalizedSchemeName(opp);\n'''
replacement = '''    const opp = this.schemeData || {};\n    const personalizedDemographicBenefit = this.getPersonalizedDemographicBenefit(opp, profile);\n    const nameObj = window.i18n.getLocalizedSchemeName(opp);\n'''
replace_once(p, needle, replacement)

# Header demographic metadata.
needle = '''            <div style="display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 1.25rem; font-size: 0.875rem; color: var(--text-muted); border-top: 1px solid var(--border-color); padding-top: 0.85rem;">\n              <span>Scope: <strong>${window.i18n.getScopeLabel(opp.scope)}</strong></span>\n              <span>Target: <strong>${opp.target_beneficiary || 'Eligible Citizens'}</strong></span>\n            </div>\n'''
replacement = '''            <div style="display: flex; flex-wrap: wrap; gap: 0.65rem 1.25rem; margin-top: 1.25rem; font-size: 0.875rem; color: var(--text-muted); border-top: 1px solid var(--border-color); padding-top: 0.85rem;">\n              <span>Scope: <strong>${window.i18n.getScopeLabel(opp.scope)}</strong></span>\n              <span>Target: <strong>${opp.target_beneficiary || 'Eligible Citizens'}</strong></span>\n              <span>${window.i18n.get('lbl_gender')}: <strong>${this.formatEligibleGenders(opp)}</strong></span>\n              <span>${window.i18n.get('lbl_social_category')}: <strong>${this.formatEligibleCategories(opp)}</strong></span>\n              <span>${window.i18n.get('lbl_disability_eligibility')}: <strong>${this.formatDisabilityEligibility(opp)}</strong></span>\n            </div>\n            ${opp.demographic_eligibility_notes ? `\n              <div style="margin-top:0.75rem; font-size:0.8rem; color:#475569; background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:0.65rem 0.8rem;">\n                ${opp.demographic_eligibility_notes}\n              </div>\n            ` : ''}\n'''
replace_once(p, needle, replacement)

# Personalized demographic benefit after base benefit, only when a verified variant matches profile.
needle = '''              <div>\n                <h4 style="color: var(--primary-navy); margin-bottom: 0.3rem; font-size: 0.95rem;">${window.i18n.get('detail_benefits')}</h4>\n                <p style="color: var(--text-main); font-size: 0.925rem; line-height: 1.5;">${opp.benefit_summary || 'N/A'}</p>\n              </div>\n\n              <div>\n'''
replacement = '''              <div>\n                <h4 style="color: var(--primary-navy); margin-bottom: 0.3rem; font-size: 0.95rem;">${window.i18n.get('detail_benefits')}</h4>\n                <p style="color: var(--text-main); font-size: 0.925rem; line-height: 1.5;">${opp.benefit_summary || 'N/A'}</p>\n              </div>\n\n              ${personalizedDemographicBenefit ? `\n                <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-left:4px solid #138808; border-radius:10px; padding:0.9rem 1rem;">\n                  <h4 style="color:#166534; margin:0 0 0.35rem 0; font-size:0.95rem;">${window.i18n.get('detail_profile_specific_benefit')}</h4>\n                  <div style="font-size:0.78rem; color:#15803d; font-weight:700; margin-bottom:0.35rem;">${personalizedDemographicBenefit.label || ''}</div>\n                  <p style="color:#14532d; font-size:0.9rem; line-height:1.5; margin:0;">${personalizedDemographicBenefit.benefit_summary || ''}</p>\n                  ${personalizedDemographicBenefit.source_url ? `<a href="${personalizedDemographicBenefit.source_url}" target="_blank" rel="noopener noreferrer" style="display:inline-block; margin-top:0.5rem; color:#166534; font-size:0.8rem; font-weight:700;">${window.i18n.get('detail_verified_source')} ↗</a>` : ''}\n                </div>\n              ` : ''}\n\n              <div>\n'''
replace_once(p, needle, replacement)

# 4) i18n keys + counts.
p = ROOT / 'frontend/i18n.js'
text = p.read_text(encoding='utf-8')
text = text.replace('Search 100 official central and state schemes', 'Search 102 official central and state schemes', 1)
text = text.replace('100 அதிகாரப்பூர்வ மத்திய மற்றும் மாநில திட்டங்களைத் தேடி', '102 அதிகாரப்பூர்வ மத்திய மற்றும் மாநில திட்டங்களைத் தேடி', 1)
text = text.replace('100 आधिकारिक केंद्रीय और राज्य योजनाओं की खोज करें', '102 आधिकारिक केंद्रीय और राज्य योजनाओं की खोज करें', 1)
# Insert labels in each language after lbl_support first occurrence in each block using unique nearby strings.
text = text.replace('    lbl_support: "Support",\n', '''    lbl_support: "Support",\n    lbl_gender: "Gender",\n    lbl_social_category: "Social Category",\n    lbl_disability_eligibility: "Disability",\n    lbl_all_genders: "All genders",\n    lbl_all_social_categories: "All social categories",\n    lbl_any_disability_status: "Any disability status",\n    lbl_persons_with_disabilities: "Persons with disabilities",\n    detail_profile_specific_benefit: "Benefit for your profile",\n    detail_verified_source: "Verified official source",\n''', 1)
# Tamil support key exact occurrence
idx = text.find('    lbl_support: "ஆதரவு",')
if idx != -1:
    line_end = text.find('\n', idx) + 1
    text = text[:line_end] + '''    lbl_gender: "பாலினம்",\n    lbl_social_category: "சமூகப் பிரிவு",\n    lbl_disability_eligibility: "மாற்றுத்திறன் தகுதி",\n    lbl_all_genders: "அனைத்து பாலினங்களும்",\n    lbl_all_social_categories: "அனைத்து சமூகப் பிரிவுகளும்",\n    lbl_any_disability_status: "எந்த மாற்றுத்திறன் நிலையிலும்",\n    lbl_persons_with_disabilities: "மாற்றுத்திறனாளிகள்",\n    detail_profile_specific_benefit: "உங்கள் சுயவிவரத்திற்கான சிறப்பு பயன்",\n    detail_verified_source: "சரிபார்க்கப்பட்ட அதிகாரப்பூர்வ மூலம்",\n''' + text[line_end:]
# Hindi support key exact occurrence
idx = text.find('    lbl_support: "सहायता",')
if idx != -1:
    line_end = text.find('\n', idx) + 1
    text = text[:line_end] + '''    lbl_gender: "लिंग",\n    lbl_social_category: "सामाजिक श्रेणी",\n    lbl_disability_eligibility: "दिव्यांगता पात्रता",\n    lbl_all_genders: "सभी लिंग",\n    lbl_all_social_categories: "सभी सामाजिक श्रेणियां",\n    lbl_any_disability_status: "किसी भी दिव्यांगता स्थिति",\n    lbl_persons_with_disabilities: "दिव्यांग व्यक्ति",\n    detail_profile_specific_benefit: "आपकी प्रोफाइल के लिए विशेष लाभ",\n    detail_verified_source: "सत्यापित आधिकारिक स्रोत",\n''' + text[line_end:]
p.write_text(text, encoding='utf-8')

# 5) index static fallback counts.
p = ROOT / 'frontend/index.html'
text = p.read_text(encoding='utf-8')
text = text.replace('Search 100 official central and state schemes', 'Search 102 official central and state schemes')
text = text.replace('<div class="stat-val" id="statSchemes">100</div>', '<div class="stat-val" id="statSchemes">102</div>')
text = text.replace('<div class="stat-val" id="statRequirements">371</div>', '<div class="stat-val" id="statRequirements">379</div>')
text = text.replace('<div class="stat-val" id="statRelationships">522</div>', '<div class="stat-val" id="statRelationships">534</div>')
p.write_text(text, encoding='utf-8')

# 6) API catalogue limit so all 102 can be returned to Explore.
p = ROOT / 'server/app.py'
text = p.read_text(encoding='utf-8')
text = text.replace('limit: int = Query(20, ge=1, le=100)', 'limit: int = Query(20, ge=1, le=200)', 1)
p.write_text(text, encoding='utf-8')

# 7) Edge-case demographic display for historical Stand-Up India so flat arrays do not misstate the OR rule.
for rel in [
    'modules/M1_data/opportunity_master.json',
    'modules/M2_eligibility_graph/data/opportunity_master.json',
    'modules/M4_ranking_pathway/data/opportunity_master.json',
]:
    path = ROOT / rel
    data = json.loads(path.read_text(encoding='utf-8'))
    for opp in data:
        if opp.get('Opportunity_ID') == 'OPP035':
            opp['Gender_Eligibility_Display'] = 'Women; any gender for SC/ST applicants (historical eligibility)'
            opp['Social_Category_Eligibility_Display'] = 'SC / ST, or women from any social category (historical eligibility)'
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

# Ensure enriched pathway copy also carries display strings.
p = ROOT / 'modules/M1_data/pathway_reference_enriched.json'
if p.exists():
    data = json.loads(p.read_text(encoding='utf-8'))
    for item in data:
        # support both flattened opportunity and nested opportunity shapes
        candidates = [item]
        if isinstance(item, dict) and isinstance(item.get('opportunity'), dict):
            candidates.append(item['opportunity'])
        for opp in candidates:
            if opp.get('Opportunity_ID') == 'OPP035' or opp.get('opportunity_id') == 'OPP035':
                opp['Gender_Eligibility_Display'] = 'Women; any gender for SC/ST applicants (historical eligibility)'
                opp['Social_Category_Eligibility_Display'] = 'SC / ST, or women from any social category (historical eligibility)'
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

# 8) Adapter pass-through for optional display strings.
p = ROOT / 'server/adapters.py'
text = p.read_text(encoding='utf-8')
needle = '        "demographic_eligibility_notes": raw.get("Demographic_Eligibility_Notes", ""),\n'
if needle in text and 'gender_eligibility_display' not in text:
    text = text.replace(needle, needle + '        "gender_eligibility_display": raw.get("Gender_Eligibility_Display"),\n        "social_category_eligibility_display": raw.get("Social_Category_Eligibility_Display"),\n', 1)
p.write_text(text, encoding='utf-8')

print('Demographic/UI update applied.')
