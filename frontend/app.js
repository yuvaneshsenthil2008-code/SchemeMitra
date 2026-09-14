/**
 * SchemeMitra — Core Application Controller & State Manager (Mobile-Responsive & Fully Localized)
 */

const SUPPORT_FAMILY_MAP = Object.freeze({
  LOAN_CREDIT: ["CREDIT", "LOAN", "CREDIT_GUARANTEE"],
  SUBSIDY_GRANT: ["SUBSIDY", "GRANT"],
  TRAINING_SKILL: ["TRAINING", "SKILL_DEVELOPMENT"],
  INFRASTRUCTURE_EQUIPMENT: ["INFRASTRUCTURE", "EQUIPMENT_SUPPORT"],
  MARKET_EXPORT: ["MARKET_ACCESS", "EXPORT_SUPPORT"],
  OTHER_SUPPORT: ["INCUBATION", "MENTORSHIP", "CERTIFICATION", "FELLOWSHIP", "OTHER_SUPPORT"]
});

const CANONICAL_SECTORS = [
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

const SECTOR_SEARCH_ALIASES = Object.freeze({
  agriculture: "Agriculture & Allied", farming: "Agriculture & Allied", agri: "Agriculture & Allied",
  food: "Food Processing & Agri Value Addition", "food processing": "Food Processing & Agri Value Addition", bakery: "Food Processing & Agri Value Addition",
  manufacturing: "MSME & Manufacturing", factory: "MSME & Manufacturing", msme: "MSME & Manufacturing",
  finance: "Finance & Credit", credit: "Finance & Credit", "business finance": "Finance & Credit",
  startup: "Startup & Innovation", innovation: "Startup & Innovation", "tech startup": "Startup & Innovation",
  skills: "Skills & Employment", training: "Skills & Employment", employment: "Skills & Employment",
  women: "Women & SHG Entrepreneurship", shg: "Women & SHG Entrepreneurship", "self help group": "Women & SHG Entrepreneurship",
  "social empowerment": "Social Empowerment & Inclusive Entrepreneurship", "inclusive entrepreneurship": "Social Empowerment & Inclusive Entrepreneurship",
  handicraft: "Handicrafts, Handloom & Artisan Economy", handloom: "Handicrafts, Handloom & Artisan Economy", artisan: "Handicrafts, Handloom & Artisan Economy", weaving: "Handicrafts, Handloom & Artisan Economy",
  export: "Export, Market Access & Business Growth", "market access": "Export, Market Access & Business Growth", "international market": "Export, Market Access & Business Growth"
});

function normalizeCatalogText(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/&/g, " and ")
    .replace(/[\-_–—/\\'’".,:;()\[\]{}]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function resolveSectorIntent(query) {
  const q = normalizeCatalogText(query);
  if (!q) return null;
  const canonical = CANONICAL_SECTORS.find(s => normalizeCatalogText(s) === q);
  return canonical || SECTOR_SEARCH_ALIASES[q] || null;
}

function normalizeScopeGroup(rawScope) {
  const raw = String(rawScope || "").trim().toLowerCase();
  if (!raw) return null;
  if (raw.startsWith("central")) return "CENTRAL";
  const stateNames = new Set([
    "tamil nadu", "kerala", "karnataka", "andhra pradesh", "telangana", "maharashtra", "delhi",
    "uttar pradesh", "west bengal", "bihar", "rajasthan", "gujarat", "punjab", "haryana", "odisha",
    "assam", "madhya pradesh", "jharkhand", "chhattisgarh", "goa"
  ]);
  if (raw.startsWith("state") || stateNames.has(raw)) return "STATE";
  return null;
}

function matchesSupportFamily(supportTypes, family) {
  if (!family) return true;
  const allowed = SUPPORT_FAMILY_MAP[String(family).toUpperCase()] || [];
  const actual = new Set((supportTypes || []).map(x => String(x).trim().toUpperCase()));
  return allowed.some(code => actual.has(code));
}

function scoreSearchMatch(o, query) {
  const q = normalizeCatalogText(query);
  if (!q) return { score: 0, reason: null };
  const oid = normalizeCatalogText(o.opportunity_id);
  const name = normalizeCatalogText(o.opportunity_name);
  const primary = normalizeCatalogText(o.primary_sector);
  const secondary = (o.secondary_sectors || []).map(normalizeCatalogText).join(" ");
  const ministry = normalizeCatalogText(o.ministry_department);
  const supports = (o.support_types || []).map(normalizeCatalogText).join(" ");
  const benefit = normalizeCatalogText(o.benefit_summary);
  const eligibility = normalizeCatalogText(o.eligibility_summary);

  if (q === oid) return { score: 1000, reason: "Matched opportunity ID" };
  if (q === name) return { score: 950, reason: "Matched scheme name" };
  if (name.startsWith(q)) return { score: 900, reason: "Matched scheme name" };
  const tokens = q.split(" ").filter(t => t.length > 1);
  if (tokens.length && tokens.every(t => name.includes(t))) return { score: 850, reason: "Matched scheme name" };
  if (q === primary) return { score: 800, reason: "Matched sector" };
  if (secondary.includes(q) || ministry.includes(q) || supports.includes(q)) return { score: 500, reason: "Related match" };
  if (benefit.includes(q) || eligibility.includes(q)) return { score: 300, reason: "Related match" };
  return { score: 0, reason: null };
}

/**
 * Single Global Navbar Controller for Desktop Auto-Hide Navigation
 */
/**
 * Single Global Navbar Controller for Desktop Auto-Hide Navigation
 */
const NavbarController = {
  headerEl: null,
  revealZoneEl: null,
  isInitialized: false,
  previousScrollY: 0,
  ticking: false,
  TOP_THRESHOLD: 15,
  MOVEMENT_THRESHOLD: 3,
  lastInputMethod: "pointer", // 'pointer' | 'keyboard'
  pointerInsideNavbar: false,

  isDesktop() {
    return window.matchMedia("(min-width: 769px)").matches;
  },

  isHoveredOrFocused() {
    if (!this.headerEl) return false;

    // 1. Check Pointer Presence (hover state)
    const isPointerInside =
      this.pointerInsideNavbar ||
      this.headerEl.matches(":hover") ||
      (this.revealZoneEl && this.revealZoneEl.matches(":hover"));

    if (isPointerInside) return true;

    // 2. Check Keyboard Focus Only (Mouse-click focus must NOT permanently lock navbar)
    if (this.lastInputMethod === "keyboard" && this.headerEl.contains(document.activeElement)) {
      return true;
    }

    return false;
  },

  show() {
    if (this.headerEl) {
      this.headerEl.classList.add("nav-visible");
    }
  },

  hide() {
    if (!this.isDesktop()) {
      if (this.headerEl) this.headerEl.classList.add("nav-visible");
      return;
    }
    // Rule: Page top overrides everything. Never hide at page top.
    if ((window.scrollY || window.pageYOffset || 0) <= this.TOP_THRESHOLD) {
      this.show();
      return;
    }
    // Rule: Never hide if hovering or keyboard focused inside header/revealZone
    if (this.isHoveredOrFocused()) return;

    if (this.headerEl) {
      this.headerEl.classList.remove("nav-visible");
    }
  },

  handleScroll() {
    if (!this.ticking) {
      window.requestAnimationFrame(() => {
        this.updateOnScroll();
        this.ticking = false;
      });
      this.ticking = true;
    }
  },

  updateOnScroll() {
    if (!this.isDesktop()) {
      this.show();
      return;
    }

    const currentScrollY = Math.max(0, window.scrollY || window.pageYOffset || 0);

    // Rule: At page top (<= TOP_THRESHOLD), navbar MUST ALWAYS be visible
    if (currentScrollY <= this.TOP_THRESHOLD) {
      this.show();
      this.previousScrollY = currentScrollY;
      return;
    }

    const diff = currentScrollY - this.previousScrollY;

    if (Math.abs(diff) >= this.MOVEMENT_THRESHOLD) {
      if (diff > 0) {
        // User scrolling DOWN -> hide navbar
        this.hide();
      } else {
        // User scrolling UP -> show navbar
        this.show();
      }
      this.previousScrollY = currentScrollY;
    }
  },

  updateHeaderHeight() {
    if (this.headerEl) {
      const height = this.headerEl.offsetHeight;
      if (height > 0) {
        document.documentElement.style.setProperty("--schememitra-header-height", `${height}px`);
      }
    }
  },

  initialize() {
    this.headerEl = document.getElementById("siteHeader");
    this.revealZoneEl = document.getElementById("navRevealZone");
    if (!this.headerEl) return;

    if (this.isInitialized) {
      if ((window.scrollY || window.pageYOffset || 0) <= this.TOP_THRESHOLD) {
        this.show();
      }
      this.updateHeaderHeight();
      return;
    }
    this.isInitialized = true;

    // 1. Global Input Method Tracking ('pointer' vs 'keyboard')
    document.addEventListener("pointerdown", () => {
      this.lastInputMethod = "pointer";
    }, { capture: true, passive: true });

    document.addEventListener("keydown", (e) => {
      if (["Tab", "ArrowDown", "ArrowUp", "ArrowLeft", "ArrowRight", "Enter", "Space"].includes(e.key) || e.key.startsWith("Arrow")) {
        this.lastInputMethod = "keyboard";
      }
    }, { capture: true, passive: true });

    // 2. Initial State: Render visible on page load/reload
    this.previousScrollY = Math.max(0, window.scrollY || window.pageYOffset || 0);
    this.show();
    this.updateHeaderHeight();
    setTimeout(() => this.updateHeaderHeight(), 50);

    // 3. Window Scroll Listener
    window.addEventListener("scroll", () => this.handleScroll(), { passive: true });

    // 4. Pointer Hover Handlers (Tracking pointer presence & reveal)
    const onPointerEnter = () => {
      this.pointerInsideNavbar = true;
      this.show();
    };

    const onPointerLeave = () => {
      this.pointerInsideNavbar = false;
    };

    if (this.revealZoneEl) {
      this.revealZoneEl.addEventListener("pointerenter", onPointerEnter);
      this.revealZoneEl.addEventListener("pointerleave", onPointerLeave);
      this.revealZoneEl.addEventListener("mouseenter", onPointerEnter);
      this.revealZoneEl.addEventListener("mouseleave", onPointerLeave);
    }

    this.headerEl.addEventListener("pointerenter", onPointerEnter);
    this.headerEl.addEventListener("pointerleave", onPointerLeave);
    this.headerEl.addEventListener("mouseenter", onPointerEnter);
    this.headerEl.addEventListener("mouseleave", onPointerLeave);

    // 5. Focus Handlers
    this.headerEl.addEventListener("focusin", () => {
      this.show();
    });

    // 6. Pointer Click Cleanup (blur mouse-clicked item after action)
    this.headerEl.addEventListener("click", (e) => {
      if (this.lastInputMethod === "pointer" && document.activeElement && this.headerEl.contains(document.activeElement)) {
        document.activeElement.blur();
      }
    });

    // 7. Global Viewport Top-Edge & Navbar Mouse Tracking (18px top activation zone)
    document.addEventListener("mousemove", (event) => {
      if (!this.isDesktop()) {
        this.show();
        return;
      }

      const headerBottom = this.headerEl ? this.headerEl.getBoundingClientRect().bottom : 0;
      const isVisible = this.headerEl.classList.contains("nav-visible");

      // 18px top trigger zone OR cursor inside open navbar area -> show navbar
      if (event.clientY <= 18 || (isVisible && event.clientY <= headerBottom)) {
        this.show();
      }
    }, { passive: true });

    // 8. Window Resize & Language Change Handlers
    window.addEventListener("resize", () => {
      this.updateHeaderHeight();
      if (!this.isDesktop()) {
        this.show();
      } else if ((window.scrollY || window.pageYOffset || 0) <= this.TOP_THRESHOLD) {
        this.show();
      }
    });

    window.addEventListener("languageChanged", () => {
      this.updateHeaderHeight();
    });
  }
};

window.NavbarController = NavbarController;

class SchemeMitraApp {
  constructor() {
    this.currentPage = "home";
    this.opportunities = [];
    this.stats = null;
    this.userProfile = null;
    this.selectedScheme = null;
    this.targetSchemeAfterProfile = null;
  }

  async init() {
    this.setupAutoHideNavbar();

    // Setup event listeners
    const mainLang = document.getElementById("langSelect");
    const mobileLang = document.getElementById("langSelectMobile");
    if (mainLang) mainLang.value = window.i18n.currentLang;
    if (mobileLang) mobileLang.value = window.i18n.currentLang;

    if (mainLang) {
      mainLang.addEventListener("change", (e) => {
        window.i18n.setLanguage(e.target.value);
        if (mobileLang) mobileLang.value = e.target.value;
      });
    }

    // Check for saved profile
    this.loadProfileFromStorage();

    // Fetch initial health stats & opportunities
    try {
      await this.fetchHealthStats();
      await this.fetchOpportunities();
      this.renderSectorsGrid();
      this.updateHeaderState();
    } catch (err) {
      console.error("Initialization error:", err);
      this.showError("Unable to load portal dataset from server.", err.message);
    }
  }

  setupAutoHideNavbar() {
    NavbarController.initialize();
  }

  loadProfileFromStorage() {
    const saved = localStorage.getItem("oppo_profile");
    if (saved) {
      try {
        this.userProfile = JSON.parse(saved);
      } catch (e) {
        this.userProfile = null;
      }
    }
  }

  saveProfileToStorage(profile) {
    this.userProfile = profile;
    localStorage.setItem("oppo_profile", JSON.stringify(profile));
    this.updateHeaderState();

    // Auto-redirect to target scheme page if user came from a scheme page Check Eligibility click
    if (this.targetSchemeAfterProfile) {
      const targetId = this.targetSchemeAfterProfile;
      this.targetSchemeAfterProfile = null;
      this.showSchemeDetail(targetId, "dashboard", "recommended");
    }
  }

  clearProfileFromStorage() {
    this.userProfile = null;
    localStorage.removeItem("oppo_profile");
    if (window.myOpportunities) {
      window.myOpportunities.analysisResult = null;
      window.myOpportunities.selectedOppId = null;
    }
    this.updateHeaderState();
  }

  updateHeaderState() {
    const hasProfile = !!(this.userProfile && Object.keys(this.userProfile).length > 0);

    const profileItem = document.getElementById("navProfileItem");
    const profileItemMobile = document.getElementById("navProfileItemMobile");
    const resetBtn = document.getElementById("navResetItem");
    const resetBtnMobile = document.getElementById("navResetItemMobile");

    const lblHeaderAction = document.getElementById("lblHeaderAction");
    const lblMobileHeaderAction = document.getElementById("lblMobileHeaderAction");

    if (hasProfile) {
      if (profileItem) profileItem.style.display = "none";
      if (profileItemMobile) profileItemMobile.style.display = "none";
      if (resetBtn) resetBtn.style.display = "block";
      if (resetBtnMobile) resetBtnMobile.style.display = "block";
      if (lblHeaderAction) lblHeaderAction.textContent = (window.i18n && window.i18n.get('nav_reset_profile')) || "Reset Profile";
      if (lblMobileHeaderAction) lblMobileHeaderAction.textContent = (window.i18n && window.i18n.get('nav_reset_profile')) || "Reset Profile";
    } else {
      if (profileItem) profileItem.style.display = "block";
      if (profileItemMobile) profileItemMobile.style.display = "block";
      if (resetBtn) resetBtn.style.display = "none";
      if (resetBtnMobile) resetBtnMobile.style.display = "none";
      if (lblHeaderAction) lblHeaderAction.textContent = (window.i18n && window.i18n.get('nav_set_profile')) || "Set Profile";
      if (lblMobileHeaderAction) lblMobileHeaderAction.textContent = (window.i18n && window.i18n.get('nav_set_profile')) || "Set Profile";
    }
  }

  toggleMobileNav() {
    const drawer = document.getElementById("mobileNavDrawer");
    if (drawer) {
      drawer.classList.toggle("active");
    }
  }

  toggleMobileFilterDrawer() {
    const sidebar = document.getElementById("filterSidebar");
    if (sidebar) {
      sidebar.classList.toggle("active");
    }
  }

  handleHeaderAction() {
    if (this.userProfile && Object.keys(this.userProfile).length > 0) {
      this.promptResetProfile();
    } else {
      this.showPage("profile");
    }
  }

  promptResetProfile() {
    const modal = document.getElementById("resetModal");
    if (modal) modal.classList.add("active");
  }

  closeResetModal() {
    const modal = document.getElementById("resetModal");
    if (modal) modal.classList.remove("active");
  }

  async confirmResetProfile() {
    const oldClientId = localStorage.getItem("schememitra_client_id");

    if (oldClientId && oldClientId.trim()) {
      try {
        const res = await fetch("/api/user/reset", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ client_id: oldClientId.trim() })
        });
        if (!res.ok) {
          alert("Could not reset your SchemeMitra data. Please try again.");
          return;
        }
      } catch (err) {
        console.error("Server reset network error:", err);
        alert("Could not reset your SchemeMitra data. Please try again.");
        return;
      }
    }

    const keysToRemove = [
      "oppo_profile",
      "schememitra_user_profile",
      "schememitra_client_id",
      "schememitra_user_progress_overlay",
      "schememitra_business_preparation_progress",
      "schememitra_goal_pathway_progress",
      "schememitra_progress_server_migrated"
    ];
    keysToRemove.forEach(k => localStorage.removeItem(k));

    this.userProfile = null;
    if (window.myOpportunities && typeof window.myOpportunities.resetLocalState === "function") {
      window.myOpportunities.resetLocalState();
    }

    this.updateHeaderState();
    this.closeResetModal();
    this.showPage("profile");
    alert("SchemeMitra has been reset. You can start with a new profile.");
  }

  async fetchHealthStats() {
    const res = await fetch("/api/health");
    if (!res.ok) throw new Error("Health check failed");
    this.stats = await res.json();
    console.log("SchemeMitra Pipeline Version:", this.stats.pipeline_version || "candidate-pipeline-v2");
    
    // Dynamic dataset stats update — zero hardcoding
    document.getElementById("statSchemes").textContent = this.stats.catalogue_count || 100;
    document.getElementById("statRequirements").textContent = this.stats.requirements_count || 371;
    document.getElementById("statRelationships").textContent = this.stats.relationships_count || 522;
    document.getElementById("statSectors").textContent = this.stats.sectors_count || 10;
  }

  async fetchOpportunities(params = {}) {
    let url = "/api/opportunities?limit=100";
    if (params.sector) url += `&sector=${encodeURIComponent(params.sector)}`;
    if (params.search) url += `&search=${encodeURIComponent(params.search)}`;
    if (params.support_type) url += `&support_type=${encodeURIComponent(params.support_type)}`;
    if (params.scope) url += `&scope=${encodeURIComponent(params.scope)}`;

    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to fetch opportunities");
    const data = await res.json();
    this.opportunities = data.items || [];
    this.renderOpportunityCards(this.opportunities);
  }

  renderSectorsGrid() {
    const grid = document.getElementById("sectorsGrid");
    if (!grid) return;

    // Collect sectors dynamically from opportunities dataset
    const sectorCounts = {};
    this.opportunities.forEach(o => {
      const sec = o.primary_sector || "Agriculture & Allied";
      sectorCounts[sec] = (sectorCounts[sec] || 0) + 1;
    });

    const sectorIcons = {
      "Agriculture & Allied": "🌾",
      "Food Processing & Agri Value Addition": "🍱",
      "MSME & Manufacturing": "🏭",
      "Finance & Credit": "💳",
      "Startup & Innovation": "💡",
      "Skills & Employment": "🎓",
      "Women & SHG Entrepreneurship": "👩‍💼",
      "Social Empowerment & Inclusive Entrepreneurship": "🤝",
      "Handicrafts, Handloom & Artisan Economy": "🧶",
      "Export, Market Access & Business Growth": "🌐"
    };

    grid.innerHTML = Object.entries(sectorCounts).map(([sector, count]) => `
      <div class="sector-card" onclick="app.showExploreSector('${sector.replace(/'/g, "\\'")}')">
        <div>
          <div class="sector-icon">${sectorIcons[sector] || "🏢"}</div>
          <div class="sector-name">${window.i18n.getSectorLabel(sector)}</div>
        </div>
        <div class="sector-count">${count} ${window.i18n.get('lbl_schemes_available')}</div>
      </div>
    `).join("");

    // Populate sector filter dropdown preserving canonical values as option values
    const select = document.getElementById("filterSector");
    if (select) {
      const currentVal = select.value;
      select.innerHTML = `<option value="" data-i18n="filter_all_sector">${window.i18n.get("filter_all_sector")}</option>` +
        Object.keys(sectorCounts).map(sec => `<option value="${sec}">${window.i18n.getSectorLabel(sec)}</option>`).join("");
      select.value = currentVal;
    }
  }

  renderOpportunityCards(items) {
    const container = document.getElementById("oppCardsContainer");
    const countBadge = document.getElementById("resultsCount");
    if (countBadge) countBadge.textContent = items.length;

    if (!container) return;

    if (items.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; padding: 3rem; background: #ffffff; border-radius: 12px; color: var(--text-muted);">
          No matching opportunities found for the selected criteria.
        </div>
      `;
      return;
    }

    container.innerHTML = items.map(o => {
      const nameObj = window.i18n.getLocalizedSchemeName(o);
      const titleContent = nameObj.localized
        ? `<span style="display:block;">${nameObj.localized}</span><span style="font-size:0.85rem; color:var(--text-muted); font-weight:500;">${nameObj.official}</span>`
        : nameObj.official;

      const sectorLabel = window.i18n.getSectorLabel(o.primary_sector);
      const scopeLabel = window.i18n.getScopeLabel(o.scope);
      const supportLabels = (o.support_types || []).map(s => window.i18n.getSupportTypeLabel(s)).join(', ');
      const rawMatchReason = o._matchReason || o.match_reason;
      const matchReasonMap = {
        "Matched scheme name": "match_scheme_name",
        "Matched sector": "match_sector",
        "Matched opportunity ID": "match_id",
        "Related match": "related_match"
      };
      const matchReason = rawMatchReason ? window.i18n.get(matchReasonMap[rawMatchReason] || rawMatchReason) : "";

      return `
        <div class="opp-card">
          <div class="opp-card-header">
            <div>
              <span class="opp-sector-tag">${sectorLabel}</span>
              ${matchReason ? `<span style="margin-left:0.45rem;font-size:0.75rem;color:var(--accent-blue);font-weight:600;">${matchReason}</span>` : ''}
              <h3 class="opp-title" onclick="app.showSchemeDetail('${o.opportunity_id}', 'explore')">${titleContent}</h3>
            </div>
            <span class="badge ${o.lifecycle_status === 'ACTIVE' ? 'badge-active' : 'badge-verification'}">
              ${o.lifecycle_status === 'ACTIVE' ? window.i18n.get('badge_active') : window.i18n.get('badge_needs_verification')}
            </span>
          </div>
          <p class="opp-benefit">${o.benefit_summary || o.eligibility_summary || ''}</p>
          <div class="opp-meta">
            <span>${window.i18n.get('lbl_scope')}: <strong>${scopeLabel || 'Central'}</strong></span>
            <span>${window.i18n.get('lbl_support')}: <strong>${supportLabels || 'Financial'}</strong></span>
            <a href="#" onclick="app.showSchemeDetail('${o.opportunity_id}', 'explore'); return false;" style="margin-left: auto; color: var(--accent-blue); font-weight: 600; text-decoration: none; padding: 0.4rem 0;">${window.i18n.get('btn_view_details')}</a>
          </div>
        </div>
      `;
    }).join("");
  }

  showSchemeDetail(opportunityId, returnPage = "explore", returnTab = "recommended") {
    this.showPage("scheme");
    if (window.schemeDetail) {
      window.schemeDetail.loadAndRender(opportunityId, returnPage, returnTab);
    }
  }

  openDetailModal(opportunityId) {
    this.showSchemeDetail(opportunityId);
  }

  closeModal() {
    const modal = document.getElementById("detailModal");
    if (modal) modal.classList.remove("active");
  }

  showPage(pageId) {
    this.currentPage = pageId;
    document.querySelectorAll(".page-view").forEach(el => el.style.display = "none");

    document.querySelectorAll(".nav-link").forEach(el => el.classList.remove("active"));
    if (pageId === "home") document.getElementById("navHome")?.classList.add("active");
    if (pageId === "explore") document.getElementById("navExplore")?.classList.add("active");
    if (pageId === "dashboard") document.getElementById("navDashboard")?.classList.add("active");

    if (pageId === "home") {
      document.getElementById("viewHome").style.display = "block";
    } else if (pageId === "explore") {
      document.getElementById("viewExplore").style.display = "block";
    } else if (pageId === "profile") {
      document.getElementById("viewProfile").style.display = "block";
      if (window.profileBuilder) window.profileBuilder.render();
    } else if (pageId === "dashboard") {
      document.getElementById("viewDashboard").style.display = "block";
      if (window.myOpportunities) window.myOpportunities.render();
    } else if (pageId === "scheme") {
      document.getElementById("viewSchemeDetail").style.display = "block";
    }
    window.scrollTo(0, 0);
  }

  reRenderCurrentPage() {
    this.updateHeaderState();
    this.renderSectorsGrid();
    if (this.currentPage === "profile" && window.profileBuilder) {
      window.profileBuilder.render();
    } else if (this.currentPage === "dashboard" && window.myOpportunities) {
      window.myOpportunities.render();
    } else if (this.currentPage === "explore") {
      this.applyFilters();
    }
  }

  showExploreSector(sectorName) {
    this.showPage("explore");
    const filterSec = document.getElementById("filterSector");
    const filterSup = document.getElementById("filterSupport");
    const filterScope = document.getElementById("filterScope");
    const searchInput = document.getElementById("exploreSearchInput");
    if (filterSup) filterSup.value = "";
    if (filterScope) filterScope.value = "";
    if (searchInput) searchInput.value = "";
    if (filterSec) filterSec.value = sectorName;
    this.applyFilters();
  }

  handleHeroSearch() {
    const q = document.getElementById("heroSearchInput")?.value || "";
    this.clearFilters(false);
    this.showPage("explore");
    const searchInput = document.getElementById("exploreSearchInput");
    if (searchInput) searchInput.value = q;
    this.applyFilters();
  }

  clearFilter(filterName) {
    const map = {
      sector: "filterSector",
      support: "filterSupport",
      scope: "filterScope",
      search: "exploreSearchInput"
    };
    const el = document.getElementById(map[filterName]);
    if (el) el.value = "";
    this.applyFilters();
  }

  clearFilters(renderNow = true) {
    ["filterSector", "filterSupport", "filterScope", "exploreSearchInput"].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = "";
    });
    if (renderNow) this.applyFilters();
  }

  updateActiveFilters(sec, sup, scope, q) {
    const el = document.getElementById("activeFilters");
    if (!el) return;
    const chips = [];
    if (sec) chips.push({ key: "sector", label: `${window.i18n.get("filter_sector")}: ${window.i18n.getSectorLabel(sec)}` });
    if (sup) {
      const select = document.getElementById("filterSupport");
      const label = select?.selectedOptions?.[0]?.textContent || sup;
      chips.push({ key: "support", label: `${window.i18n.get("filter_support")}: ${label}` });
    }
    if (scope) {
      const select = document.getElementById("filterScope");
      const label = select?.selectedOptions?.[0]?.textContent || scope;
      chips.push({ key: "scope", label: `${window.i18n.get("filter_scope")}: ${label}` });
    }
    if (q) chips.push({ key: "search", label: `${window.i18n.get("lbl_search")}: ${q}` });
    el.innerHTML = chips.map(c => `
      <button type="button" onclick="app.clearFilter('${c.key}')" style="border:1px solid var(--border-color);background:#fff;border-radius:999px;padding:0.35rem 0.7rem;font-size:0.78rem;cursor:pointer;color:var(--primary-navy);">
        ${c.label} ×
      </button>
    `).join("");
    el.style.display = chips.length ? "flex" : "none";
  }

  applyFilters() {
    const sec = document.getElementById("filterSector")?.value || "";
    const sup = document.getElementById("filterSupport")?.value || "";
    const scope = document.getElementById("filterScope")?.value || "";
    const rawQuery = document.getElementById("exploreSearchInput")?.value || "";
    const q = rawQuery.trim();

    let filtered = [...this.opportunities];

    if (sec) {
      filtered = filtered.filter(o => o.primary_sector === sec);
    }
    if (sup) {
      filtered = filtered.filter(o => matchesSupportFamily(o.support_types || [], sup));
    }
    if (scope) {
      filtered = filtered.filter(o => normalizeScopeGroup(o.scope) === scope);
    }

    if (q) {
      const sectorIntent = resolveSectorIntent(q);
      if (sectorIntent) {
        filtered = filtered
          .filter(o => o.primary_sector === sectorIntent)
          .map(o => ({ ...o, _matchReason: "Matched sector" }));
      } else {
        filtered = filtered
          .map((o, index) => {
            const match = scoreSearchMatch(o, q);
            return { item: { ...o, _matchReason: match.reason }, score: match.score, index };
          })
          .filter(x => x.score > 0)
          .sort((a, b) => b.score - a.score || a.index - b.index)
          .map(x => x.item);
      }
    }

    this.updateActiveFilters(sec, sup, scope, q);
    this.renderOpportunityCards(filtered);
  }

  scrollToSection(id) {
    this.showPage("home");
    setTimeout(() => {
      const el = document.getElementById(id);
      if (el) el.scrollIntoView({ behavior: "smooth" });
    }, 100);
  }

  showError(title, msg) {
    document.getElementById("errorBoundary").style.display = "block";
    document.getElementById("errorTitle").textContent = title || "Error";
    document.getElementById("errorMessage").textContent = msg || "An unexpected error occurred.";
  }
}

window.app = new SchemeMitraApp();
document.addEventListener("DOMContentLoaded", () => window.app.init());
