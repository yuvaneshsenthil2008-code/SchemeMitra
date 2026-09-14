/**
 * SchemeMitra — Comprehensive Trilingual UI Localization (English, Tamil, Hindi)
 * Prototype Identity & Educational Disclaimer Included
 * 
 * NOTE: Official M1 scheme names, department names, URLs, and canonical enum codes remain unchanged internally.
 * Display labels are localized for all SchemeMitra taxonomy sectors, support types, scopes, and UI elements.
 */

const translations = {
  en: {
    brand_name: "SchemeMitra",
    tagline: "AI-powered scheme matching for entrepreneurs",
    header_top_bar: "AI-powered scheme matching for entrepreneurs • Applications submitted on official government portals",

    nav_home: "Home",
    nav_explore: "Explore Schemes",
    nav_how_it_works: "How It Works",
    nav_set_profile: "Set Your Profile",
    nav_my_opportunities: "My Opportunities",
    nav_reset_profile: "Reset Profile",
    confirm_reset_title: "Reset your SchemeMitra profile?",
    confirm_reset_msg: "This will permanently clear:\n• your profile\n• completed actions\n• prepared documents\n• Goal Pathway progress\n\nOfficial scheme data will not be affected.",
    hero_title: "Empowering Indian Entrepreneurs with Transparent Opportunity Intelligence",
    hero_subtitle: "Search 100 official central and state schemes, discover verified requirements, and build your step-by-step pathway to success.",
    search_placeholder: "Search schemes by name, sector, benefit, or ID...",
    btn_search: "Search",
    btn_set_profile: "Set Your Profile",
    btn_speak_profile: "Speak to build your profile",
    btn_show_my_schemes: "Show My Schemes",
    btn_reset_confirm: "Reset Everything",
    btn_view_scheme_details: "View Scheme Details",
    btn_view_roadmap_steps: "View Roadmap Steps",
    btn_cancel: "Cancel",
    stat_schemes: "Official Schemes",
    stat_requirements: "Verified Requirements",
    stat_relationships: "Relationship Edges",
    stat_sectors: "Focus Sectors",
    sec_sectors_title: "Explore Opportunities by Sector",
    sec_sectors_sub: "Select a sector to browse verified government support programs",
    sec_how_title: "How SchemeMitra Helps You",
    sec_how_sub: "Discover, evaluate, and navigate government schemes tailored to your business goal",
    how_card1_title: "1. Tell Us About Yourself",
    how_card1_desc: "Share your location, background, business stage, interests and goals so SchemeMitra can understand which opportunities are relevant to you.",
    how_card2_title: "2. Find Opportunities That Fit You",
    how_card2_desc: "See opportunities ranked around your profile, understand why they may suit you, and identify any information or requirements you still need to complete.",
    how_card3_title: "3. See Your Opportunity Journey",
    how_card3_desc: "Explore how your profile, requirements, suitable opportunities and available support connect to your business goal through a personalized visual graph.",
    
    filters_title: "Filter Opportunities",
    filter_sector: "Primary Sector",
    filter_support: "Support Type",
    filter_stage: "Business Stage",
    filter_scope: "Scope",
    filter_all_sector: "All Sectors",
    filter_all_support: "All Support Types",
    filter_all_scope: "All Scopes",
    results_found: "Opportunities Found",
    lbl_schemes_available: "Schemes Available",
    lbl_scope: "Scope",
    lbl_support: "Support",
    btn_view_details: "View Details →",
    btn_apply_filters_close: "Apply Filters & Close",
    btn_filter_mobile: "⚙️ Filter Opportunities",
    quick_filter_placeholder: "Quick filter...",
    support_family_loan_credit: "Loan / Credit",
    support_family_subsidy_grant: "Subsidy / Grant",
    support_family_training: "Training & Skill Support",
    support_family_infrastructure: "Infrastructure & Equipment",
    support_family_market: "Market & Export Support",
    support_family_incubation: "Incubation & Mentorship",
    support_family_certification: "Certification",
    support_family_fellowship: "Fellowship",
    support_family_other: "Other Support",
    support_overlap_note: "A scheme may offer more than one type of support, so it can appear in multiple support categories.",
    match_scheme_name: "Matched scheme name",
    match_sector: "Matched sector",
    match_id: "Matched opportunity ID",
    related_match: "Related match",
    lbl_search: "Search",

    sort_by: "Sort By",
    sort_name: "Scheme Name",
    sort_sector: "Sector",
    badge_active: "ACTIVE",
    badge_needs_verification: "NEEDS VERIFICATION",
    badge_eligible: "ELIGIBLE",
    badge_potentially: "POTENTIALLY ELIGIBLE",
    badge_not_eligible: "NOT ELIGIBLE",
    
    tab_recommended: "Best Matches",
    tab_potentially: "More Information Needed",
    tab_pathway: "Opportunity Pathway",
    tab_graph: "Opportunity Graph",
    tab_verification: "Needs Verification",
    tab_application_guide: "Application Guide",
    
    detail_overview: "Overview",
    detail_benefits: "Benefits & Support",
    detail_eligibility: "Eligibility Summary",
    detail_documents: "Required Documents",
    detail_application: "Application Route",
    detail_official_url: "Official Source Link",
    detail_official_website: "Official Website",
    detail_lifecycle: "Lifecycle Status",
    confirm_reset_title: "Reset your SchemeMitra profile?",
    confirm_reset_msg: "This will permanently clear:\n• your profile\n• completed actions\n• prepared documents\n• Goal Pathway progress\n\nOfficial scheme data will not be affected.",
    voice_unsupported: "Browser Speech Recognition is unavailable in this environment. Please type your profile details below.",
    offline_title: "Backend Unavailable",
    offline_msg: "Unable to connect to the SchemeMitra server. Please check your connection and retry.",
    btn_retry: "Retry Connection",

    /* Profile Builder & Form Keys */
    profile_builder_sub: "Use your voice or answer in plain language to extract your canonical profile",
    tab_conversational: "Conversational / Voice Assistant",
    tab_structured_form: "Structured Form Input",
    voice_status_default: "Click the microphone button to start speaking, or type below.",
    voice_status_listening: "Listening... Speak now.",
    voice_status_done: "Recording complete. Click 'Extract Profile Fields' to proceed.",
    voice_status_silence: "Stopped after 3 seconds of silence. Review the transcript, then extract your profile.",
    tell_us_label: "Tell us about yourself & your business goal:",
    txt_message_placeholder: "Example: I am a 24-year-old female from Tamil Nadu with a degree wanting to start a food processing business with Rs 3 lakh income...",
    btn_extract_fields: "Extract Profile Fields",
    review_title: "Review & Confirm Your Extracted Profile",
    review_sub: "Review the fields extracted from your input. You can edit any field before saving.",
    btn_start_over: "Start Over",
    btn_edit_profile: "Edit Profile",
    basic_details: "Basic Details",
    financial_details: "Financial Details (₹)",
    business_info: "Business Info",
    lbl_age: "Age (Years)",
    lbl_gender: "Gender",
    lbl_category: "Category",
    lbl_state: "State",
    lbl_district: "District",
    lbl_income: "Annual Family Income",
    lbl_capital: "Available Own Capital",
    lbl_project_cost: "Estimated Project Cost",
    lbl_target_sector: "Target Sector",
    lbl_business_stage: "Business Stage",
    lbl_education: "Educational Qualification",
    lbl_education_field: "Field of Study / Trade",
    age_invalid: "Please enter a valid age between 1 and 120.",
    under18_title: "Personalized Scheme Matching for Under-18 Profile",
    under18_msg: "Most entrepreneurship opportunities in this catalogue are intended for adults. You can still explore schemes, but personalized matches will depend on each scheme's verified age requirements.",
    lbl_preferred_support: "Preferred Support Type",
    btn_save_confirm_profile: "Save & Confirm Profile",
    select_gender: "Select Gender",
    select_category: "Select Category",
    select_sector: "Select Sector",
    select_stage: "Select Stage",

    /* Dashboard & View Keys */
    no_profile_title: "No Profile Found",
    no_profile_msg: "Please set your profile to view personalized opportunity recommendations.",
    analyzing_title: "Analyzing Opportunities for Your Profile...",
    analyzing_sub: "Evaluating schemes for your profile criteria...",
    profile_summary_title: "Confirmed Profile",
    why_match_title: "Why You Match:",
    action_gaps_title: "Action Gaps Required:",
    action_gaps_sub: "Complete required prerequisites (e.g. Udyam Registration, DPR).",
    needs_verification_notice: "Verification Notice: These schemes are in historical or verification-required status.",
    pathway_sub: "Verified Sequence: Current State → Action Gaps → Prerequisite Requirements → Eligibility → Target Scheme",
    graph_title: "Opportunity Graph Visualization",
    graph_sub: "Network graph connecting verified prerequisite relationships.",
    graph_note: "Only verified prerequisite edges are shown.",
    guide_title: "Application Guide",
    guide_sub: "Step-by-step document submission & portal guide",
    guide_docs: "Required Documents",
    guide_channel: "Application Channel",
    guide_verification: "Verification & Tracking",
    nav_menu_title: "Navigation Menu",
    check_eligibility_cta: "Check My Eligibility for This Scheme",
    close: "Close",
    official_portal_notice: "SchemeMitra provides eligibility evaluation and preparation guidance. Final applications and approvals take place exclusively on official government portals.",
    btn_continue_official_portal: "Continue on Official Government Portal ↗",
    platform_positioning_disclaimer: "Note on Application Submission: SchemeMitra is a scheme discovery and guidance platform. We guide you through eligibility, prerequisites, and document preparation. SchemeMitra does not accept applications or grant approvals — final applications must be submitted directly on official government portals.",
    btn_apply: "Apply",
    btn_official_source: "Official Source ↗",
    apply_modal_title: "Apply for this Scheme",
    apply_modal_desc: "Applications for this scheme are submitted through the official government website. SchemeMitra provides discovery and guidance but does not process applications.",
    apply_modal_desc_fallback: "Applications for this scheme are submitted through the official government website. SchemeMitra provides discovery and guidance but does not process applications. Use the official scheme website below to view the latest application instructions and application route.",
    btn_visit_official_apply: "Visit Official Website to Apply ↗",
    btn_visit_official_scheme: "Visit Official Scheme Website ↗",
    apply_modal_no_url: "A verified official application link is not currently available in SchemeMitra.",

    btn_view_pathway_graph: "View Pathway & Graph",
    btn_view_pathway_gaps: "View Pathway & Gaps",
    node_target_opp: "Target Opp",
    node_req: "Req Node",
    node_support: "Support",
    btn_zoom_in: "🔍 +",
    btn_zoom_out: "🔍 -",
    btn_reset_zoom: "Reset Zoom",
    btn_clear_filters: "Clear Filters",

    no_profile_title: "Your Personalized Opportunities",
    no_profile_sub: "Complete your profile to discover schemes matched to your goals, location and eligibility.",
    no_profile_why_title: "Why create a profile?",
    no_profile_check1: "Find relevant schemes",
    no_profile_check2: "Understand your potential eligibility",
    no_profile_check3: "See missing requirements",
    no_profile_check4: "Get a personalized preparation roadmap",
    incomplete_profile_title: "Your Profile Needs Information",
    incomplete_profile_sub: "Complete the required core fields to view your personalized opportunities.",
    btn_complete_profile: "Complete Profile",
    btn_find_my_opportunities: "Find My Opportunities",
    core_gate_warning: "Complete the required core fields above to view personalized opportunities.",
    profile_readiness: "Profile Readiness",
    status_detected: "✓ Detected",
    status_confirmed: "✓ Confirmed",
    status_required: "Required",
    status_optional: "Optional / May improve matches",
    status_needed_some: "Needed for some schemes",
    status_please_confirm: "Please confirm",
    tab_roadmap: "Your Opportunity Graph",
    roadmap_title: "Your Opportunity Graph",
    roadmap_sub: "Visualizing your profile, matched opportunities, verified requirements, and benefits",

    /* Canonical M1 Sectors (EN) */
    sector_agri: "Agriculture & Allied",
    sector_food: "Food Processing & Agri Value Addition",
    sector_msme: "MSME & Manufacturing",
    sector_finance: "Finance & Credit",
    sector_startup: "Startup & Innovation",
    sector_skills: "Skills & Employment",
    sector_women: "Women & SHG Entrepreneurship",
    sector_social: "Social Empowerment & Inclusive Entrepreneurship",
    sector_handicrafts: "Handicrafts, Handloom & Artisan Economy",
    sector_export: "Export, Market Access & Business Growth",

    /* Support Types Display (EN) */
    sup_credit: "Loan / Credit",
    sup_subsidy: "Capital Subsidy",
    sup_grant: "Grant / Seed Funding",
    sup_training: "Training & Skill Support",
    sup_infrastructure: "Infrastructure & Equipment",
    sup_certification: "Certification",
    sup_credit_guarantee: "Credit Guarantee",
    sup_equipment_support: "Equipment Support",
    sup_export_support: "Export Support",
    sup_fellowship: "Fellowship",
    sup_incubation: "Incubation",
    sup_market_access: "Market Access",
    sup_mentorship: "Mentorship",
    sup_other_support: "Other Support",
    sup_skill_development: "Skill Development",

    /* Scopes Display (EN) */
    scope_central: "Central Govt",
    scope_state: "State Govt",

    /* Form Select Options Display (EN) */
    gender_male: "Male",
    gender_female: "Female",
    gender_trans: "Transgender",
    cat_general: "General",
    cat_obc: "OBC",
    cat_sc: "SC",
    cat_st: "ST",
    cat_minority: "Minority",
    stage_idea: "Idea",
    stage_startup: "Startup",
    stage_existing: "Existing Business"
  },

  ta: {
    brand_name: "SchemeMitra",
    tagline: "தொழில்முனைவோருக்கான AI ஆதரவு திட்ட பொருத்தம்",
    header_top_bar: "தொழில்முனைவோருக்கான AI ஆதரவு திட்ட பொருத்தம் • விண்ணப்பங்கள் அதிகாரப்பூர்வ அரசுத் தளங்களில் சமர்ப்பிக்கப்படுகின்றன",

    nav_home: "முகப்பு",
    nav_explore: "திட்டங்களை ஆராய்க",
    nav_how_it_works: "செயல்படும் முறை",
    nav_set_profile: "சுயவிவரத்தை அமைக்கவும்",
    nav_my_opportunities: "எனக்கான வாய்ப்புகள்",
    nav_reset_profile: "சுயவிவரத்தை மீட்டமைக்க",
    confirm_reset_title: "உங்கள் சுயவிவரத்தை மீட்டமைக்கவா?",
    confirm_reset_msg: "இது உங்கள் சேமிக்கப்பட்ட சுயவிவரத்தையும் தனிப்பயனாக்கப்பட்ட வாய்ப்புகளையும் நீக்கும்.",
    btn_view_scheme_details: "திட்டத்தின் விவரங்களைப் பார்க்க",
    btn_view_roadmap_steps: "வழிகாட்டி படிகளைப் பார்க்க",
    hero_title: "வெளிப்படையான வாய்ப்பு நுண்ணறிவுடன் இந்திய தொழில்முனைவோரை வலுப்படுத்துதல்",
    hero_subtitle: "100 அதிகாரப்பூர்வ மத்திய மற்றும் மாநில திட்டங்களைத் தேடி, சரிபார்க்கப்பட்ட தேவைகளைக் கண்டறிந்து, உங்கள் இலக்குக்கான வழியை உருவாக்குங்கள்.",
    search_placeholder: "திட்டத்தின் பெயர், துறை, பயன் அல்லது ஐடி மூலம் தேடவும்...",
    btn_search: "தேடுக",
    btn_set_profile: "சுயவிவரத்தை அமைக்கவும்",
    btn_speak_profile: "பேசி சுயவிவரத்தை உருவாக்கவும்",
    btn_show_my_schemes: "எனக்கான திட்டங்களைக் காட்டு",
    btn_reset_confirm: "மீட்டமைப்பை உறுதிப்படுத்து",
    btn_cancel: "ரத்து செய்",
    stat_schemes: "அதிகாரப்பூர்வ திட்டங்கள்",
    stat_requirements: "சரிபார்க்கப்பட்ட தகுதிகள்",
    stat_relationships: "தொடர்பு இணைப்புகள்",
    stat_sectors: "முக்கிய துறைகள்",
    sec_sectors_title: "துறை வாரியாக வாய்ப்புகளை ஆராய்க",
    sec_sectors_sub: "அரசு ஆதரவு திட்டங்களைப் பார்க்க ஒரு துறையைத் தேர்ந்தெடுக்கவும்",
    sec_how_title: "ஆப்பர்ச்சூனிட்டி OS உங்களுக்கு எவ்வாறு உதவுகிறது",
    sec_how_sub: "உங்கள் வணிக இலக்கிற்கு ஏற்ப அரசுத் திட்டங்களைக் கண்டறிந்து, மதிப்பீடு செய்து, வழிகாட்டலைப் பெறுங்கள்",
    how_card1_title: "1. உங்களைப் பற்றி எங்களிடம் கூறுங்கள்",
    how_card1_desc: "உங்கள் இருப்பிடம், பின்னணி, தொழில் நிலை, ஆர்வங்கள் மற்றும் இலக்குகளைப் பகிர்ந்து கொள்ளுங்கள், இதனால் ஆப்பர்ச்சூனிட்டி OS உங்களுக்குப் பொருத்தமான வாய்ப்புகளைப் புரிந்து கொள்ள முடியும்.",
    how_card2_title: "2. உங்களுக்குப் பொருத்தமான வாய்ப்புகளைக் கண்டறியவும்",
    how_card2_desc: "உங்கள் சுயவிவரத்தின் அடிப்படையில் வரிசைப்படுத்தப்பட்ட வாய்ப்புகளைப் பாருங்கள், அவை ஏன் உங்களுக்குப் பொருந்தக்கூடும் என்பதைப் புரிந்து கொள்ளுங்கள், மேலும் நீங்கள் பூர்த்தி செய்ய வேண்டிய தகவல்கள் அல்லது தேவைகளைக் கண்டறியவும்.",
    how_card3_title: "3. உங்கள் வாய்ப்புப் பயணத்தைப் பாருங்கள்",
    how_card3_desc: "உங்கள் சுயவிவரம், தேவைகள், பொருத்தமான வாய்ப்புகள் மற்றும் கிடைக்கக்கூடிய ஆதரவு ஆகியவை தனிப்பயனாக்கப்பட்ட காட்சி வரைபடம் மூலம் உங்கள் வணிக இலக்குடன் எவ்வாறு இணைகின்றன என்பதை ஆராயுங்கள்.",
    
    filters_title: "வாய்ப்புகளை வடிகட்டுக",
    filter_sector: "முதன்மை துறை",
    filter_support: "ஆதரவு வகை",
    filter_stage: "தொழில் நிலை",
    filter_scope: "அரசு வரம்பு",
    filter_all_sector: "அனைத்து துறைகளும்",
    filter_all_support: "அனைத்து ஆதரவு வகைகளும்",
    filter_all_scope: "அனைத்து வரம்புகளும்",
    results_found: "வாய்ப்புகள் கண்டறியப்பட்டன",
    lbl_schemes_available: "திட்டங்கள் உள்ளன",
    lbl_scope: "வரம்பு",
    lbl_support: "ஆதரவு",
    btn_view_details: "விவரங்களைப் பார்க்க →",
    btn_apply_filters_close: "வடிகட்டிகளைப் பயன்படுத்து & மூடு",
    btn_filter_mobile: "⚙️ வடிகட்டிகள்",
    quick_filter_placeholder: "விரைவு வடிகட்டி...",
    support_family_loan_credit: "கடன் / நிதி",
    support_family_subsidy_grant: "மானியம் / உதவித்தொகை",
    support_family_training: "பயிற்சி & திறன் ஆதரவு",
    support_family_infrastructure: "உள்கட்டமைப்பு & உபகரணங்கள்",
    support_family_market: "சந்தை & ஏற்றுமதி ஆதரவு",
    support_family_incubation: "இன்க்யூபேஷன் & வழிகாட்டுதல்",
    support_family_certification: "சான்றிதழ் ஆதரவு",
    support_family_fellowship: "ஃபெல்லோஷிப்",
    support_family_other: "பிற ஆதரவு",
    support_overlap_note: "ஒரு திட்டம் ஒன்றுக்கு மேற்பட்ட ஆதரவு வகைகளை வழங்கலாம்; அதனால் அது பல ஆதரவு பிரிவுகளில் தோன்றலாம்.",
    match_scheme_name: "திட்டப் பெயர் பொருந்தியது",
    match_sector: "துறை பொருந்தியது",
    match_id: "வாய்ப்பு அடையாளம் பொருந்தியது",
    related_match: "தொடர்புடைய பொருத்தம்",
    lbl_search: "தேடல்",

    sort_by: "வரிசைப்படுத்து",
    sort_name: "திட்டத்தின் பெயர்",
    sort_sector: "துறை",
    badge_active: "செயலில் உள்ளது",
    badge_needs_verification: "சரிபார்ப்பு தேவை",
    badge_eligible: "முழுத் தகுதி உள்ளது",
    badge_potentially: "சாத்தியமான தகுதி / இடைவெளிகள்",
    badge_not_eligible: "தகுதி இல்லை",
    
    tab_recommended: "பரிந்துரைக்கப்பட்டவை",
    tab_potentially: "சாத்தியமான தகுதி / இடைவெளிகள்",
    tab_pathway: "வாய்ப்பு பாதை",
    tab_graph: "வாய்ப்பு வரைபடம்",
    tab_verification: "சரிபார்ப்பு தேவை",
    tab_application_guide: "விண்ணப்ப வழிகாட்டி",
    
    detail_overview: "மேலோட்டம்",
    detail_benefits: "நன்மைகள் & ஆதரவு",
    detail_eligibility: "தகுதி சுருக்கம்",
    detail_documents: "தேவையான ஆவணங்கள்",
    detail_application: "விண்ணப்பிக்கும் முறை",
    detail_official_url: "அதிகாரப்பூர்வ தள இணைப்பு",
    detail_official_website: "அதிகாரப்பூர்வ இணையதளம்",
    detail_lifecycle: "நிலை நிலைமை",
    confirm_reset_title: "சுயவிவரத்தை மீட்டமைக்கவா?",
    confirm_reset_msg: "இது உங்கள் உள்ளூர் சுயவிவரத் தரவை அழித்து பொது உலாவு முறைக்குத் திரும்பும். நிச்சயமாகவா?",
    voice_unsupported: "உங்கள் உலாவியில் குரல் அங்கீகாரம் கிடைக்கவில்லை. கீழே தட்டச்சு செய்யவும்.",
    offline_title: "சேவையகம் கிடைக்கவில்லை",
    offline_msg: "ஆப்பர்ச்சூனிட்டி OS சேவையகத்துடன் இணைக்க முடியவில்லை.",
    btn_retry: "மீண்டும் முயல்க",

    /* Profile Builder & Form Keys (Tamil) */
    profile_builder_sub: "உங்கள் குரல் அல்லது எளிய உரையைப் பயன்படுத்தி சுயவிவரத்தைப் பெறவும்",
    tab_conversational: "உரையாடல் / குரல் உதவியாளர்",
    tab_structured_form: "படிவ உள்ளீடு",
    voice_status_default: "பேசத் தொடங்க மைக்கை அழுத்தவும், அல்லது கீழே தட்டச்சு செய்யவும்.",
    voice_status_listening: "கேட்கிறது... இப்போது பேசுங்கள்.",
    voice_status_done: "பதிவு முடிந்தது. 'சுயவிவரப் புலங்களைப் பிரித்தெடு' என்பதைக் கிளிக் செய்யவும்.",
    voice_status_silence: "3 விநாடிகள் பேச்சில்லாததால் பதிவு நிறுத்தப்பட்டது. உரையைச் சரிபார்த்து சுயவிவரத்தைப் பிரித்தெடுக்கவும்.",
    tell_us_label: "உங்களைப் பற்றியும் உங்கள் தொழில் இலக்கைப் பற்றியும் கூறுங்கள்:",
    txt_message_placeholder: "எடுத்துக்காட்டு: நான் தமிழ்நாட்டைச் சேர்ந்த 24 வயது பெண், உணவு பதப்படுத்தும் தொழிலைத் தொடங்க விரும்புகிறேன்...",
    btn_extract_fields: "சுயவிவரப் புலங்களைப் பிரித்தெடு",
    review_title: "பிரித்தெடுக்கப்பட்ட சுயவிவரத்தை மதிப்பாய்வு செய்க",
    review_sub: "சேமிப்பதற்கு முன் எந்தப் புலத்தையும் திருத்தலாம்.",
    btn_start_over: "மீண்டும் தொடங்குக",
    btn_edit_profile: "சுயவிவரத்தைத் திருத்து",
    basic_details: "அடிப்படை விவரங்கள்",
    financial_details: "நிதி விவரங்கள் (₹)",
    business_info: "வணிகத் தகவல்",
    lbl_age: "வயது (ஆண்டுகள்)",
    lbl_gender: "பாலினம்",
    lbl_category: "பிரிவு",
    lbl_state: "மாநிலம்",
    lbl_district: "மாவட்டம்",
    lbl_income: "ஆண்டு குடும்ப வருமானம்",
    lbl_capital: "சொந்த முதலீடு",
    lbl_project_cost: "மதிப்பிடப்பட்ட திட்டச் செலவு",
    lbl_target_sector: "இலக்குத் துறை",
    lbl_business_stage: "தொழில் நிலை",
    lbl_education: "கல்வித் தகுதி",
    lbl_education_field: "படிப்பு / தொழிற்துறை",
    age_invalid: "1 முதல் 120 வரை செல்லுபடியாகும் வயதை உள்ளிடவும்.",
    under18_title: "தனிப்பயன் தொழில்முனைவர் பொருத்தம் 18 வயதுக்கு மேற்பட்டவர்களுக்கு கிடைக்கும்.",
    under18_msg: "உங்கள் வயது சேமிக்கப்படும். ஆனால் 18 வயதிற்குக் குறைந்த சுயவிவரத்திற்கு SchemeMitra தொழில்முனைவர் திட்டங்களை பரிந்துரைக்காது. பொதுத் திட்டங்களை நீங்கள் இன்னும் ஆராயலாம்.",
    lbl_preferred_support: "விருப்பமான ஆதரவு வகை",
    btn_save_confirm_profile: "சேமித்து உறுதிப்படுத்து",
    select_gender: "பாலினத்தைத் தேர்ந்தெடுக்கவும்",
    select_category: "பிரிவைத் தேர்ந்தெடுக்கவும்",
    select_sector: "துறையைத் தேர்ந்தெடுக்கவும்",
    select_stage: "நிலையைத் தேர்ந்தெடுக்கவும்",

    /* Dashboard & View Keys (Tamil) */
    no_profile_title: "சுயவிவரம் கிடைக்கவில்லை",
    no_profile_msg: "தனிப்பயனாக்கப்பட்ட திட்டங்களைக் காண உங்கள் சுயவிவரத்தை அமைக்கவும்.",
    analyzing_title: "உங்கள் சுயவிவரத்திற்கான வாய்ப்புகள் பகுப்பாய்வு செய்யப்படுகின்றன...",
    analyzing_sub: "உங்கள் சுயவிவரத்திற்கான திட்டங்கள் மதிப்பீடு செய்யப்படுகின்றன...",
    profile_summary_title: "உறுதிப்படுத்தப்பட்ட சுயவிவரம்",
    why_match_title: "நீங்கள் பொருந்துவதற்கான காரணங்கள்:",
    action_gaps_title: "தேவையான நடவடிக்கை இடைவெளிகள்:",
    action_gaps_sub: "தேவையான முன்நிபந்தனைகளைப் பூர்த்தி செய்யவும் (எ.கா. உத்யாம் பதிவு, DPR).",
    needs_verification_notice: "சரிபார்ப்பு அறிவிப்பு: இத்திட்டங்கள் வரலாற்று ரீதியானவை அல்லது சரிபார்ப்பு தேவைப்படும் நிலையில் உள்ளன.",
    pathway_sub: "சரிபார்க்கப்பட்ட வரிசை: தற்போதைய நிலை → இடைவெளிகள் → முன்நிபந்தனைகள் → தகுதி → இலக்குத் திட்டம்",
    graph_title: "வாய்ப்பு வரைபடம்",
    graph_sub: "சரிபார்க்கப்பட்ட முன்நிபந்தனை தொடர்புகளைக் காட்டும் வரைபடம்.",
    graph_note: "சரிபார்க்கப்பட்ட இணைப்புகள் மட்டுமே காட்டப்படுகின்றன.",
    guide_title: "விண்ணப்ப வழிகாட்டி",
    guide_sub: "படிப்படியான ஆவணச் சமர்ப்பிப்பு & இணையதள வழிகாட்டி",
    guide_docs: "தேவையான ஆவணங்கள்",
    guide_channel: "விண்ணப்ப வழிமுறை",
    guide_verification: "சரிபார்ப்பு & கண்காணிப்பு",
    nav_menu_title: "வழிசெலுத்தல் மெனு",
    check_eligibility_cta: "இத்திட்டத்திற்கான எனது தகுதியைச் சரிபார்க்கவும்",
    close: "மூடு",
    official_portal_notice: "ஆப்பர்ச்சூனிட்டி OS தகுதி மதிப்பீடு மற்றும் வழிகாட்டலை மட்டுமே வழங்குகிறது. அதிகாரப்பூர்வ விண்ணப்பங்கள் மற்றும் ஒப்புதல்கள் அரசுத் தளங்களில் மட்டுமே நடைபெறும்.",
    btn_continue_official_portal: "அதிகாரப்பூர்வ அரசுத் தளத்திற்குச் செல்லவும் ↗",
    platform_positioning_disclaimer: "குறிப்பு: ஆப்பர்ச்சூனிட்டி OS என்பது திட்டக் கண்டுபிடிப்பு மற்றும் வழிகாட்டுதல் தளமாகும். அதிகாரப்பூர்வ விண்ணப்பங்கள் மற்றும் ஒப்புதல்கள் அரசுத் தளங்களில் மட்டுமே நடைபெறும்.",
    btn_apply: "விண்ணப்பிக்கவும்",
    btn_official_source: "அதிகாரப்பூர்வ தளம் ↗",
    apply_modal_title: "இத்திட்டத்திற்கு விண்ணப்பிக்கவும்",
    apply_modal_desc: "இத்திட்டத்திற்கான விண்ணப்பங்கள் அதிகாரப்பூர்வ அரசு இணையதளம் மூலம் சமர்ப்பிக்கப்படுகின்றன. ஆப்பர்ச்சூனிட்டி OS வழிகாட்டுதலை மட்டுமே வழங்குகிறது.",
    apply_modal_desc_fallback: "இத்திட்டத்திற்கான விண்ணப்பங்கள் அதிகாரப்பூர்வ அரசு இணையதளம் மூலம் சமர்ப்பிக்கப்படுகின்றன. சமீபத்திய விண்ணப்ப வழிகாட்டல்களைப் பார்க்க கீழே உள்ள அதிகாரப்பூர்வ இணையதளத்தைப் பயன்படுத்தவும்.",
    btn_visit_official_apply: "விண்ணப்பிக்க அதிகாரப்பூர்வ தளத்திற்குச் செல்லவும் ↗",
    btn_visit_official_scheme: "அதிகாரப்பூர்வ திட்ட இணையதளத்தைப் பார்க்கவும் ↗",
    apply_modal_no_url: "ஆப்பர்ச்சூனிட்டி OS இல் சரிபார்க்கப்பட்ட அதிகாரப்பூர்வ விண்ணப்ப இணைப்பு தற்போது கிடைக்கவில்லை.",

    btn_view_pathway_graph: "பாதை & வரைபடத்தைப் பார்க்க",
    btn_view_pathway_gaps: "பாதை & இடைவெளிகளைப் பார்க்க",
    node_target_opp: "இலக்குத் திட்டம்",
    node_req: "தேவை முனை",
    node_support: "ஆதரவு",
    btn_zoom_in: "🔍 +",
    btn_zoom_out: "🔍 -",
    btn_reset_zoom: "மீட்டமை",
    btn_clear_filters: "வடிகட்டிகளை அழி",

    no_profile_title: "உங்கள் தனிப்பயனாக்கப்பட்ட வாய்ப்புகள்",
    no_profile_sub: "உங்கள் இலக்குகள், இருப்பிடம் மற்றும் தகுதிக்கு ஏற்ப அரசுத் திட்டங்களைக் கண்டறிய உங்கள் சுயவிவரத்தைப் பூர்த்தி செய்யுங்கள்.",
    no_profile_why_title: "சுயவிவரத்தை ஏன் உருவாக்க வேண்டும்?",
    no_profile_check1: "பொருத்தமான திட்டங்களைக் கண்டறியவும்",
    no_profile_check2: "உங்கள் சாத்தியமான தகுதியைப் புரிந்து கொள்ளவும்",
    no_profile_check3: "தேவையான ஆவணங்கள்/தேவைகளைக் காணவும்",
    no_profile_check4: "தனிப்பயனாக்கப்பட்ட தயாரிப்பு வரைபடத்தைப் பெறவும்",
    incomplete_profile_title: "உங்கள் சுயவிவரம் முழுமையடையவில்லை",
    incomplete_profile_sub: "தனிப்பயனாக்கப்பட்ட வாய்ப்புகளைக் காண தேவையான கட்டாய புலங்களை நிரப்பவும்.",
    btn_complete_profile: "சுயவிவரத்தைப் பூர்த்தி செய்ய",
    btn_find_my_opportunities: "எனக்கான வாய்ப்புகளைக் கண்டறி",
    core_gate_warning: "தனிப்பயனாக்கப்பட்ட வாய்ப்புகளைப் பார்க்க மேலே உள்ள கட்டாய புலங்களை நிரப்பவும்.",
    profile_readiness: "சுயவிவரத் தயார்நிலை",
    status_detected: "✓ கண்டறியப்பட்டது",
    status_confirmed: "✓ உறுதி செய்யப்பட்டது",
    status_required: "கட்டாயம்",
    status_optional: "விருப்பத்தேர்வு / பொருத்தத்தை மேம்படுத்தலாம்",
    status_needed_some: "சில திட்டங்களுக்கு தேவைப்படலாம்",
    status_please_confirm: "தயவுசெய்து உறுதிப்படுத்தவும்",
    tab_roadmap: "உங்கள் வாய்ப்பு வரைபடம் (Opportunity Graph)",
    roadmap_title: "உங்கள் வாய்ப்பு வரைபடம் (Opportunity Graph)",
    roadmap_sub: "உங்கள் சுயவிவரம், பொருந்திய வாய்ப்புகள், சரிபார்க்கப்பட்ட தேவைகள் மற்றும் நன்மைகளை காட்சிப்படுத்துகிறது",

    /* Canonical M1 Sectors (Tamil) */
    sector_agri: "வேளாண்மை & சார்ந்த துறைகள்",
    sector_food: "உணவு பதப்படுத்துதல் & வேளாண் மதிப்பு கூட்டல்",
    sector_msme: "குறு, சிறு & நடுத்தர தொழில் (MSME) மற்றும் உற்பத்தி",
    sector_finance: "நிதி & கடன் உதவி",
    sector_startup: "ஸ்டார்ட்அப் & நத்தாக்கம்",
    sector_skills: "திறன் மேம்பாடு & வேலைவாய்ப்பு",
    sector_women: "மகளிர் & சுயஉதவிக் குழு தொழில்முனைவு",
    sector_social: "சமூக அதிகாரம் & உள்ளடக்கிய தொழில்முனைவு",
    sector_handicrafts: "கைவினைப்பொருட்கள், கைத்தறி & கைவினைஞர் பொருளாதாரம்",
    sector_export: "ஏற்றுமதி, சந்தை அணுகல் & வணிக வளர்ச்சி",

    /* Support Types Display (Tamil) */
    sup_credit: "கடன் / நிதி",
    sup_subsidy: "மூலதன மானியம்",
    sup_grant: "மானியம் / விதை நிதி",
    sup_training: "பயிற்சி & திறன் ஆதரவு",
    sup_infrastructure: "உள்கட்டமைப்பு & உபகரணங்கள்",
    sup_certification: "சான்றிதழ்",
    sup_credit_guarantee: "கடன் உத்தரவாதம்",
    sup_equipment_support: "உபகரணங்கள் உதவி",
    sup_export_support: "ஏற்றுமதி உதவி",
    sup_fellowship: "ஆராய்ச்சி நிதி / பெல்லோஷிப்",
    sup_incubation: "இன்குபேஷன் உதவி",
    sup_market_access: "சந்தை அணுகல்",
    sup_mentorship: "வழிகாட்டுதல்",
    sup_other_support: "இதர உதவிகள்",
    sup_skill_development: "திறன் மேம்பாடு",

    /* Scopes Display (Tamil) */
    scope_central: "மத்திய அரசு",
    scope_state: "மாநில அரசு",

    /* Form Select Options Display (Tamil) */
    gender_male: "ஆண்",
    gender_female: "பெண்",
    gender_trans: "திருநங்கை / திருநம்பி",
    cat_general: "பொது",
    cat_obc: "பிற்படுத்தப்பட்டோர் (OBC)",
    cat_sc: "ஆதிதிராவிடர் (SC)",
    cat_st: "பழங்குடியினர் (ST)",
    cat_minority: "பான்மையினர்",
    stage_idea: "யோசனை நிலை",
    stage_startup: "தொடக்க நிலை (ஸ்டார்ட்அப்)",
    stage_existing: "செயலில் உள்ள வணிகம்"
  },

  hi: {
    brand_name: "SchemeMitra",
    tagline: "उद्यमियों के लिए AI-संचालित योजना मिलान",
    header_top_bar: "उद्यमियों के लिए AI-संचालित योजना मिलान • आवेदन आधिकारिक सरकारी पोर्टल पर जमा किए जाते हैं",

    nav_home: "होम",
    nav_explore: "योजनाएं खोजें",
    nav_how_it_works: "यह कैसे काम करता है",
    nav_set_profile: "अपनी प्रोफाइल सेट करें",
    nav_my_opportunities: "मेरे अवसर",
    nav_reset_profile: "प्रोफाइल रीसेट करें",
    hero_title: "पारदर्शी अवसर बुद्धिमत्ता के साथ भारतीय उद्यमियों का सशक्तिकरण",
    hero_subtitle: "100 आधिकारिक केंद्रीय और राज्य योजनाओं की खोज करें, सत्यापित आवश्यकताओं को जानें और अपना चरणबद्ध मार्ग बनाएं।",
    search_placeholder: "योजना का नाम, क्षेत्र, लाभ या आईडी से खोजें...",
    btn_search: "खोजें",
    btn_set_profile: "अपनी प्रोफाइल सेट करें",
    btn_speak_profile: "बोलकर प्रोफाइल बनाएं",
    btn_show_my_schemes: "मेरी योजनाएं दिखाएं",
    btn_reset_confirm: "प्रोफाइल रीसेट करें",
    confirm_reset_title: "अपनी प्रोफाइल रीसेट करें?",
    confirm_reset_msg: "यह आपकी सहेजी गई प्रोफाइल और व्यक्तिगत अवसरों को साफ़ कर देगा।",
    btn_view_scheme_details: "योजना के विवरण देखें",
    btn_view_roadmap_steps: "रोडमैप के चरण देखें",
    btn_cancel: "रद्द करें",
    stat_schemes: "आधिकारिक योजनाएं",
    stat_requirements: "सत्यापित आवश्यकताएं",
    stat_relationships: "संबंध कड़ियां",
    stat_sectors: "प्रमुख क्षेत्र",
    sec_sectors_title: "क्षेत्र के अनुसार अवसर खोजें",
    sec_sectors_sub: "सरकारी सहायता कार्यक्रमों को देखने के लिए एक क्षेत्र चुनें",
    sec_how_title: "SchemeMitra आपकी कैसे मदद करता है",
    sec_how_sub: "अपने व्यावसायिक लक्ष्य के अनुरूप सरकारी योजनाओं की खोज करें, मूल्यांकन करें और सही मार्गदर्शन पाएं",
    how_card1_title: "1. अपने बारे में बताएं",
    how_card1_desc: "अपना स्थान, पृष्ठभूमि, व्यवसाय का चरण, रुचियां और लक्ष्य साझा करें ताकि SchemeMitra समझ सके कि कौन से अवसर आपके लिए प्रासंगिक हैं।",
    how_card2_title: "2. अपने अनुकूल अवसर खोजें",
    how_card2_desc: "अपनी प्रोफाइल के अनुसार रैंक किए गए अवसर देखें, समझें कि वे आपके लिए क्यों उपयुक्त हो सकते हैं, और आवश्यक जानकारी या आवश्यकताओं की पहचान करें।",
    how_card3_title: "3. अपनी अवसर यात्रा देखें",
    how_card3_desc: "देखें कि आपकी प्रोफाइल, आवश्यकताएं, उपयुक्त अवसर और उपलब्ध सहायता एक व्यक्तिगत विजुअल ग्राफ के माध्यम से आपके व्यावसायिक लक्ष्य से कैसे जुड़ते हैं।",
    
    filters_title: "अवसरों को फ़िल्टर करें",
    filter_sector: "प्राथमिक क्षेत्र",
    filter_support: "सहायता का प्रकार",
    filter_stage: "व्यवसाय चरण",
    filter_scope: "सरकारी दायरा",
    filter_all_sector: "सभी क्षेत्र",
    filter_all_support: "सभी सहायता प्रकार",
    filter_all_scope: "सभी दायरे",
    results_found: "अवसर मिले",
    lbl_schemes_available: "योजनाएं उपलब्ध हैं",
    lbl_scope: "दायरा",
    lbl_support: "सहायता",
    btn_view_details: "विवरण देखें →",
    btn_apply_filters_close: "फ़िल्टर लागू करें और बंद करें",
    btn_filter_mobile: "⚙️ फ़िल्टर करें",
    quick_filter_placeholder: "त्वरित फ़िल्टर...",
    support_family_loan_credit: "ऋण / क्रेडिट",
    support_family_subsidy_grant: "सब्सिडी / अनुदान",
    support_family_training: "प्रशिक्षण और कौशल सहायता",
    support_family_infrastructure: "अवसंरचना और उपकरण",
    support_family_market: "बाज़ार और निर्यात सहायता",
    support_family_incubation: "इनक्यूबेशन और मार्गदर्शन",
    support_family_certification: "प्रमाणन सहायता",
    support_family_fellowship: "फेलोशिप",
    support_family_other: "अन्य सहायता",
    support_overlap_note: "एक योजना एक से अधिक प्रकार की सहायता दे सकती है, इसलिए वह कई सहायता श्रेणियों में दिखाई दे सकती है।",
    match_scheme_name: "योजना नाम से मेल",
    match_sector: "क्षेत्र से मेल",
    match_id: "अवसर आईडी से मेल",
    related_match: "संबंधित परिणाम",
    lbl_search: "खोज",

    sort_by: "क्रमानुसार",
    sort_name: "योजना का नाम",
    sort_sector: "क्षेत्र",
    badge_active: "सक्रिय",
    badge_needs_verification: "सत्यापन आवश्यक",
    badge_eligible: "पूर्ण पात्र",
    badge_potentially: "संभावित पात्र / कमियां",
    badge_not_eligible: "पात्र नहीं",
    
    tab_recommended: "अनुशंसित",
    tab_potentially: "संभावित पात्र / कमियां",
    tab_pathway: "अवसर मार्ग",
    tab_graph: "अवसर ग्राफ",
    tab_verification: "सत्यापन आवश्यक",
    tab_application_guide: "आवेदन गाइड",
    
    detail_overview: "अवलोकन",
    detail_benefits: "लाभ एवं सहायता",
    detail_eligibility: "पात्रता का सारांश",
    detail_documents: "आवश्यक दस्तावेज",
    detail_application: "आवेदन का तरीका",
    detail_official_url: "आधिकारिक स्रोत लिंक",
    detail_official_website: "आधिकारिक वेबसाइट",
    detail_lifecycle: "जीवन चक्र स्थिति",
    confirm_reset_title: "प्रोफाइल रीसेट करें?",
    confirm_reset_msg: "यह आपके स्थानीय प्रोफाइल डेटा को हटा देगा और सार्वजनिक ब्राउज़िंग मोड में लौट जाएगा। क्या आप निश्चित हैं?",
    voice_unsupported: "ब्राउज़र भाषण पहचान इस वातावरण में उपलब्ध नहीं है। कृपया नीचे विवरण टाइप करें।",
    offline_title: "सर्वर अनुपलब्ध",
    offline_msg: "SchemeMitra सर्वर से कनेक्ट करने में असमर्थ।",
    btn_retry: "पुन: प्रयास करें",

    /* Profile Builder & Form Keys (Hindi) */
    profile_builder_sub: "अपनी प्रोफाइल निकालने के लिए अपनी आवाज का उपयोग करें या सामान्य भाषा में उत्तर दें",
    tab_conversational: "संवादात्मक / वॉयस असिस्टेंट",
    tab_structured_form: "संरचित फॉर्म इनपुट",
    voice_status_default: "बोलना शुरू करने के लिए माइक बटन दबाएं, या नीचे टाइप करें।",
    voice_status_listening: "सुन रहा है... अब बोलें।",
    voice_status_done: "रिकॉर्डिंग पूर्ण। आगे बढ़ने के लिए 'प्रोफाइल फ़ील्ड निकालें' पर क्लिक करें।",
    voice_status_silence: "3 सेकंड तक आवाज़ न मिलने पर रिकॉर्डिंग रोक दी गई। टेक्स्ट जाँचें, फिर प्रोफ़ाइल निकालें।",
    tell_us_label: "अपने और अपने व्यावसायिक लक्ष्य के बारे में बताएं:",
    txt_message_placeholder: "उदाहरण: मैं तमिलनाडु की 24 वर्षीय महिला हूं, स्नातक हूं और खाद्य प्रसंस्करण व्यवसाय शुरू करना चाहती हूं...",
    btn_extract_fields: "प्रोफाइल फ़ील्ड निकालें",
    review_title: "अपनी निकाली गई प्रोफाइल की समीक्षा और पुष्टि करें",
    review_sub: "सहेजने से पहले आप किसी भी क्षेत्र को संपादित कर सकते हैं।",
    btn_start_over: "पुन: प्रारंभ करें",
    btn_edit_profile: "प्रोफाइल संपादित करें",
    basic_details: "मूल विवरण",
    financial_details: "वित्तीय विवरण (₹)",
    business_info: "व्यवसाय जानकारी",
    lbl_age: "आयु (वर्ष)",
    lbl_gender: "लिंग",
    lbl_category: "वर्ग",
    lbl_state: "राज्य",
    lbl_district: "जिला",
    lbl_income: "वार्षिक पारिवारिक आय",
    lbl_capital: "उपलब्ध स्वयं की पूंजी",
    lbl_project_cost: "अनुमानित परियोजना लागत",
    lbl_target_sector: "लक्षित क्षेत्र",
    lbl_business_stage: "व्यवसाय चरण",
    lbl_education: "शैक्षणिक योग्यता",
    lbl_education_field: "अध्ययन / ट्रेड का क्षेत्र",
    age_invalid: "कृपया 1 से 120 के बीच सही आयु दर्ज करें।",
    under18_title: "व्यक्तिगत उद्यमी योजना मिलान 18 वर्ष और उससे अधिक आयु के लिए उपलब्ध है।",
    under18_msg: "आपकी आयु सहेजी जाएगी, लेकिन SchemeMitra 18 वर्ष से कम आयु वाले प्रोफ़ाइल को उद्यमिता योजनाएँ सुझाएगा नहीं। आप सार्वजनिक योजना सूची देख सकते हैं।",
    lbl_preferred_support: "पसंदीदा सहायता प्रकार",
    btn_save_confirm_profile: "सहेजें और पुष्टि करें",
    select_gender: "लिंग चुनें",
    select_category: "वर्ग चुनें",
    select_sector: "क्षेत्र चुनें",
    select_stage: "चरण चुनें",

    /* Dashboard & View Keys (Hindi) */
    no_profile_title: "कोई प्रोफाइल नहीं मिली",
    no_profile_msg: "कृपया व्यक्तिगत सिफारिशें देखने के लिए अपनी प्रोफाइल सेट करें।",
    analyzing_title: "आपकी प्रोफाइल के लिए अवसरों का विश्लेषण किया जा रहा है...",
    analyzing_sub: "आपकी प्रोफाइल के अनुसार योजनाओं का मूल्यांकन किया जा रहा है...",
    profile_summary_title: "पुष्टित प्रोफाइल",
    why_match_title: "आपके मेल खाने के कारण:",
    action_gaps_title: "आवश्यक कार्रवाई अंतर:",
    action_gaps_sub: "आवश्यक पूर्वापेक्षाएँ पूरी करें (जैसे उद्यम पंजीकरण, डीपीआर)।",
    needs_verification_notice: "सत्यापन सूचना: ये योजनाएं ऐतिहासिक या सत्यापन आवश्यक श्रेणी में हैं।",
    pathway_sub: "सत्यापित क्रम: वर्तमान स्थिति → अंतर → कार्रवाई → पात्रता → लक्ष्य योजना",
    graph_title: "अवसर ग्राफ विज़ुअलाइज़ेशन",
    graph_sub: "सत्यापित संबंधों को दर्शाने वाला नेटवर्क ग्राफ।",
    graph_note: "केवल सत्यापित संबंध ही दिखाए गए हैं।",
    guide_title: "आवेदन गाइड",
    guide_sub: "चरण-दर-चरण दस्तावेज जमा करने और पोर्टल गाइड",
    guide_docs: "आवश्यक दस्तावेज",
    guide_channel: "आवेदन चैनल",
    guide_verification: "सत्यापन और ट्रैकिंग",
    nav_menu_title: "नेविगेशन मेनू",
    check_eligibility_cta: "इस योजना के लिए मेरी पात्रता जांचें",
    close: "बंद करें",
    official_portal_notice: "SchemeMitra पात्रता मूल्यांकन और मार्गदर्शन प्रदान करता है। आधिकारिक आवेदन और स्वीकृतियां केवल सरकारी पोर्टल पर होती हैं।",
    btn_continue_official_portal: "आधिकारिक सरकारी पोर्टल पर आगे बढ़ें ↗",
    platform_positioning_disclaimer: "नोट: SchemeMitra एक योजना खोज और मार्गदर्शन प्लेटफॉर्म है। आधिकारिक आवेदन और स्वीकृतियां केवल सरकारी पोर्टल पर होती हैं।",
    btn_apply: "आवेदन करें",
    btn_official_source: "आधिकारिक स्रोत ↗",
    apply_modal_title: "इस योजना के लिए आवेदन करें",
    apply_modal_desc: "इस योजना के लिए आवेदन आधिकारिक सरकारी वेबसाइट के माध्यम से जमा किए जाते हैं। SchemeMitra केवल मार्गदर्शन प्रदान करता है।",
    apply_modal_desc_fallback: "इस योजना के लिए आवेदन आधिकारिक सरकारी वेबसाइट के माध्यम से जमा किए जाते हैं। नवीनतम आवेदन निर्देशों को देखने के लिए नीचे दी गई आधिकारिक वेबसाइट का उपयोग करें।",
    btn_visit_official_apply: "आवेदन करने के लिए आधिकारिक वेबसाइट पर जाएं ↗",
    btn_visit_official_scheme: "आधिकारिक योजना वेबसाइट पर जाएं ↗",
    apply_modal_no_url: "SchemeMitra में एक सत्यापित आधिकारिक आवेदन लिंक वर्तमान में उपलब्ध नहीं है।",

    btn_view_pathway_graph: "मार्ग और ग्राफ देखें",
    btn_view_pathway_gaps: "मार्ग और अंतर देखें",
    node_target_opp: "लक्ष्य योजना",
    node_req: "आवश्यकता नोड",
    node_support: "सहायता",
    btn_zoom_in: "🔍 +",
    btn_zoom_out: "🔍 -",
    btn_reset_zoom: "ज़ूम रीसेट",
    btn_clear_filters: "फ़िल्टर हटाएं",

    no_profile_title: "आपके व्यक्तिगत अवसर",
    no_profile_sub: "अपने लक्ष्यों, स्थान और पात्रता से मेल खाने वाली योजनाओं की खोज के लिए अपनी प्रोफ़ाइल पूरी करें।",
    no_profile_why_title: "प्रोफ़ाइल क्यों बनाएं?",
    no_profile_check1: "प्रासंगिक योजनाएं खोजें",
    no_profile_check2: "अपनी संभावित पात्रता समझें",
    no_profile_check3: "अधूरी आवश्यकताएं देखें",
    no_profile_check4: "व्यक्तिगत तैयारी रोडमैप प्राप्त करें",
    incomplete_profile_title: "आपकी प्रोफ़ाइल अधूरी है",
    incomplete_profile_sub: "अपने व्यक्तिगत अवसर देखने के लिए आवश्यक फ़ील्ड भरें।",
    btn_complete_profile: "प्रोफ़ाइल पूरी करें",
    btn_find_my_opportunities: "मेरे अवसर खोजें",
    core_gate_warning: "व्यक्तिगत अवसर देखने के लिए ऊपर दिए गए आवश्यक फ़ील्ड भरें।",
    profile_readiness: "प्रोफ़ाइल तैयारी",
    status_detected: "✓ पहचाना गया",
    status_confirmed: "✓ पुष्टीकृत",
    status_required: "आवश्यक",
    status_optional: "वैकल्पिक / मिलान सुधार सकता है",
    status_needed_some: "कुछ योजनाओं के लिए आवश्यक",
    status_please_confirm: "कृपया पुष्टि करें",
    tab_roadmap: "आपका अवसर ग्राफ (Opportunity Graph)",
    roadmap_title: "आपका अवसर ग्राफ (Opportunity Graph)",
    roadmap_sub: "आपकी प्रोफ़ाइल, मिलान किए गए अवसरों, सत्यापित आवश्यकताओं और लाभों का चित्रण",

    /* Canonical M1 Sectors (Hindi) */
    sector_agri: "कृषि एवं संबद्ध क्षेत्र",
    sector_food: "खाद्य प्रसंस्करण एवं कृषि मूल्य संवर्धन",
    sector_msme: "एमएसएमई (MSME) एवं विनिर्माण",
    sector_finance: "वित्त एवं ऋण सहायता",
    sector_startup: "स्टार्टअप एवं नवाचार",
    sector_skills: "कौशल एवं रोजगार",
    sector_women: "महिला एवं स्वयं सहायता समूह उद्यमिता",
    sector_social: "सामाजिक सशक्तिकरण एवं समावेशी उद्यमिता",
    sector_handicrafts: "हस्तशिल्प, हथकरघा एवं कारीगर अर्थव्यवस्था",
    sector_export: "निर्यात, बाजार पहुंच एवं व्यापार वृद्धि",

    /* Support Types Display (Hindi) */
    sup_credit: "ऋण / क्रेडिट",
    sup_subsidy: "कैपिटल सब्सिडी",
    sup_grant: "अनुदान / बीज पूंजी",
    sup_training: "प्रशिक्षण एवं कौशल सहायता",
    sup_infrastructure: "बुनियादी ढांचा एवं उपकरण",
    sup_certification: "प्रमाणन",
    sup_credit_guarantee: "ऋण गारंटी",
    sup_equipment_support: "उपकरण सहायता",
    sup_export_support: "निर्यात सहायता",
    sup_fellowship: "फेलोशिप / शोधवृत्ति",
    sup_incubation: "इन्क्यूबेशन सहायता",
    sup_market_access: "बाजार पहुंच",
    sup_mentorship: "मार्गदर्शन / मेंटरशिप",
    sup_other_support: "अन्य सहायता",
    sup_skill_development: "कौशल विकास",

    /* Scopes Display (Hindi) */
    scope_central: "केंद्रीय सरकार",
    scope_state: "राज्य सरकार",

    /* Form Select Options Display (Hindi) */
    gender_male: "पुरुष",
    gender_female: "महिला",
    gender_trans: "ट्रांसजेंडर",
    cat_general: "सामान्य",
    cat_obc: "ओबीसी (OBC)",
    cat_sc: "अनुसूचित जाति (SC)",
    cat_st: "अनुसूचित जनजाति (ST)",
    cat_minority: "अल्पसंख्यक",
    stage_idea: "विचार चरण",
    stage_startup: "स्टार्टअप चरण",
    stage_existing: "मौजूदा व्यवसाय"
  }
};

class I18nManager {
  constructor() {
    this.currentLang = localStorage.getItem("oppo_lang") || "en";
  }

  setLanguage(lang) {
    if (translations[lang]) {
      this.currentLang = lang;
      localStorage.setItem("oppo_lang", lang);
      this.applyTranslations();
      window.dispatchEvent(new CustomEvent("languageChanged", { detail: { lang } }));
    }
  }

  get(key) {
    return (translations[this.currentLang] && translations[this.currentLang][key]) || translations.en[key] || key;
  }

  /**
   * Translates exact canonical M1 sector values into localized display labels.
   */
  getSectorLabel(canonicalSector) {
    if (!canonicalSector) return "";
    const map = {
      "Agriculture & Allied": "sector_agri",
      "Food Processing & Agri Value Addition": "sector_food",
      "MSME & Manufacturing": "sector_msme",
      "Finance & Credit": "sector_finance",
      "Startup & Innovation": "sector_startup",
      "Skills & Employment": "sector_skills",
      "Women & SHG Entrepreneurship": "sector_women",
      "Social Empowerment & Inclusive Entrepreneurship": "sector_social",
      "Handicrafts, Handloom & Artisan Economy": "sector_handicrafts",
      "Export, Market Access & Business Growth": "sector_export"
    };

    const key = map[canonicalSector];
    return key ? this.get(key) : canonicalSector;
  }

  /**
   * Translates support type codes / strings into localized display labels.
   */
  getSupportTypeLabel(canonicalType) {
    if (!canonicalType) return "";
    const raw = String(canonicalType).toUpperCase();

    if (raw.includes("CREDIT_GUARANTEE")) return this.get("sup_credit_guarantee");
    if (raw.includes("CREDIT") || raw.includes("LOAN")) return this.get("sup_credit");
    if (raw.includes("SUBSIDY")) return this.get("sup_subsidy");
    if (raw.includes("GRANT")) return this.get("sup_grant");
    if (raw.includes("TRAINING") || raw.includes("SKILL")) return this.get("sup_training");
    if (raw.includes("INFRASTRUCTURE") || raw.includes("EQUIPMENT")) return this.get("sup_infrastructure");
    if (raw.includes("CERTIFICATION")) return this.get("sup_certification");
    if (raw.includes("EXPORT")) return this.get("sup_export_support");
    if (raw.includes("FELLOWSHIP")) return this.get("sup_fellowship");
    if (raw.includes("INCUBATION")) return this.get("sup_incubation");
    if (raw.includes("MARKET")) return this.get("sup_market_access");
    if (raw.includes("MENTORSHIP")) return this.get("sup_mentorship");

    return canonicalType;
  }

  /**
   * Translates scope strings into localized display labels.
   */
  getScopeLabel(canonicalScope) {
    if (!canonicalScope) return "";
    const s = String(canonicalScope).toLowerCase();
    if (s.includes("central")) return this.get("scope_central");
    if (s.includes("state")) return this.get("scope_state");
    return canonicalScope;
  }

  /**
   * Returns localized scheme name object: { localized: string|null, official: string }
   * Official scheme name remains primary unless a verified localized field exists in data.
   */
  getLocalizedSchemeName(opp) {
    if (!opp) return { localized: null, official: "" };
    const official = opp.opportunity_name || opp.name || opp.Opportunity_Name || "";
    
    // Check for verified localized name fields in record if present
    const langKey = `opportunity_name_${this.currentLang}`;
    const nameKey = `name_${this.currentLang}`;
    const localized = opp[langKey] || opp[nameKey] || opp.localized_name || null;

    if (localized && localized !== official) {
      return { localized, official };
    }
    return { localized: null, official };
  }

  applyTranslations() {
    document.querySelectorAll("[data-i18n]").forEach(el => {
      const key = el.getAttribute("data-i18n");
      const text = this.get(key);
      if (el.tagName === "INPUT" && (el.type === "text" || el.type === "search")) {
        el.placeholder = text;
      } else if (el.tagName === "TEXTAREA") {
        el.placeholder = text;
      } else {
        el.textContent = text;
      }
    });

    // Re-render active page to immediately update dynamically inserted content
    if (window.app && window.app.reRenderCurrentPage) {
      window.app.reRenderCurrentPage();
    }
  }
}

window.i18n = new I18nManager();
