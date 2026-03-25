# AURA Platform — Complete Testing Document
## 60 Problem Statements | 6 Tracks | Verification & Test Plan

> **Purpose:** Verify that each of the 60 hackathon problem statements from V2.MD is properly implemented in the AURA platform. Each problem has test cases, expected behavior, API endpoints to verify, and frontend pages to check.

---

## How to Use This Document

- **Status Legend:** ✅ Implemented | ⚠️ Partial | ❌ Not Implemented
- Each problem statement has:
  - **What to Test** — The core functionality to verify
  - **Backend Test** — API endpoints to call and expected responses
  - **Frontend Test** — Pages/UI to check visually
  - **Pass Criteria** — What constitutes a successful implementation
  - **Test Data** — Sample data or scenarios to use

---

# TRACK 1: Standardising Salon Experience Across Locations

---

## PS-01.01 — Pre-Service Consultation System ✅

**What to Test:** Structured pre-service consultation is mandated and captured digitally before any service begins.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Get customer Beauty Passport with hair/skin diagnostics | `/customers/{id}` | GET | Returns hair_type, hair_texture, scalp_condition, skin_type, allergies, sensitivities |
| 2 | AI hair/skin scan from image | `/customers/{id}/scan` | POST | Returns objective analysis (porosity, damage_level, etc.) |
| 3 | Update consultation data | `/customers/{id}` | PATCH | Saves consultation fields to profile |
| 4 | Get AI recommendations based on profile | `/customers/{id}/recommendations` | GET | Returns personalized service suggestions |
| 5 | Track 1 AI agent for consultation | `/agents/ps/PS-01.01` | POST | Agent generates consultation checklist |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Beauty Passport shows all diagnostic fields | `/customer/passport` | Hair type, texture, porosity, density, scalp, damage, skin type, tone, allergies |
| 2 | Stylist can view customer profile before service | Stylist Dashboard → Customers | Full profile visible with history |
| 3 | Consultation data persists across visits | `/customer/passport` | Data saved from previous visits still present |

**Pass Criteria:**
- [ ] Customer profile has 40+ diagnostic fields captured
- [ ] AI scan endpoint returns objective measurements
- [ ] Profile is accessible at any branch (not branch-specific)
- [ ] Consultation data carries forward to every future visit

---

## PS-01.02 — SOPs Embedded in Service Workflow ✅

**What to Test:** SOPs are delivered digitally, step-by-step, during actual service delivery — not just stored.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | List SOPs for a service | `/sops/?service_id={id}` | GET | Returns SOP with steps, durations, products, chemical details |
| 2 | Create service session | `/sessions/` | POST | Creates a tracked session linked to SOP |
| 3 | Start session | `/sessions/{booking_id}/start` | POST | Begins SOP step tracking |
| 4 | Complete a step | `/sessions/{booking_id}/step/{step_number}` | POST | Marks step done, advances to next |
| 5 | Get AI guidance for current step | `/sessions/{booking_id}/guidance` | GET | Returns coaching tip for current step |
| 6 | Log SOP deviation | `/sessions/{booking_id}/deviation` | POST | Records deviation with reason |
| 7 | Complete session | `/sessions/{booking_id}/complete` | POST | Calculates SOP compliance % |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Live session shows step-by-step SOP | Stylist → Live Session | Steps displayed with timer, products, critical flags |
| 2 | SOP management for managers | Manager → SOP Management | Create/edit SOPs with steps, versions, archetype overlays |
| 3 | Deviation logging works | Stylist → Live Session | Can log why a step was skipped/modified |

**Pass Criteria:**
- [ ] SOPs are digital with versioned steps
- [ ] Stylist sees real-time step-by-step guidance during service
- [ ] SOP compliance percentage is calculated automatically
- [ ] Deviations are logged with reasons
- [ ] AI coaching is available per step

---

## PS-01.03 — Objective Quality Audits ✅

**What to Test:** Quality scores are generated from observable data, not subjective auditor opinions.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Create quality assessment | `/quality/` | POST | Calculates overall score: SOP 30%, timing 20%, customer 50% |
| 2 | Get quality stats summary | `/quality/stats/summary` | GET | Aggregated quality metrics |
| 3 | Get quality analytics | `/analytics/quality` | GET | SOP compliance, timing scores, customer ratings across branches |
| 4 | Manager review assessment | `/quality/{id}/review` | PATCH | Manager adds review notes |
| 5 | Quality flagging | `/quality/` | POST | Score < 55 auto-flags for review |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Quality dashboard | Manager → Quality Dashboard | Overall score, SOP compliance, timing, flagged items |
| 2 | Location comparison | Analytics → BI Dashboard | Quality scores comparable across locations |

**Pass Criteria:**
- [ ] Quality score uses weighted formula (SOP 30% + Timing 20% + Customer 50%)
- [ ] Auto-flags assessments scoring below 55
- [ ] Before/after photos are captured
- [ ] AI analysis result is generated
- [ ] Manager can add review notes

---

## PS-01.04 — Complaint Root Cause Mapping ✅

**What to Test:** Complaints are traced to specific SOP steps, stylists, and products.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Submit feedback with details | `/feedback/` | POST | Captures service, stylist, ratings, comment |
| 2 | Get feedback stats | `/feedback/stats` | GET | Aggregated complaint patterns |
| 3 | Session deviation log | `/sessions/{booking_id}/deviation` | POST | Links deviation to specific SOP step |
| 4 | AI root cause agent | `/agents/ps/PS-01.04` | POST | Analyzes complaint → root cause mapping |
| 5 | Quality assessment links to session | `/quality/` | POST | Assessment includes session_id with step-level data |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Feedback page shows patterns | Manager → Feedback | Complaints with sentiment, stylist, service details |
| 2 | Quality dashboard shows deviations | Manager → Quality Dashboard | Flagged assessments with root cause |

**Pass Criteria:**
- [ ] Feedback captures stylist, service, location, and sentiment
- [ ] Session deviations are linked to specific SOP steps
- [ ] AI agent can map complaint to procedure failure
- [ ] Complaint patterns are visible in analytics

---

## PS-01.05 — Remote Branch Supervision Dashboard ✅

**What to Test:** Real-time operational visibility into all branches without physical presence.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Location analytics | `/locations/{id}/analytics` | GET | Revenue, bookings, quality, SOULSKIN metrics |
| 2 | Location queue state | `/locations/{id}/queue` | GET | Live queue entries |
| 3 | Analytics overview | `/analytics/overview` | GET | KPIs across all locations |
| 4 | Location comparison | `/analytics/compare` | GET | Side-by-side branch comparison |
| 5 | Staff performance | `/analytics/staff` | GET | Staff leaderboard across locations |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Admin dashboard | Admin → Command Center | Network-wide KPIs, 750+ locations overview |
| 2 | Regional dashboard | Regional → Dashboard | Multi-location metrics |
| 3 | Franchise dashboard | Franchise → Dashboard | Portfolio performance |
| 4 | Location comparison | Locations → Compare | Head-to-head branch analysis |

**Pass Criteria:**
- [ ] Real-time KPIs visible for all branches
- [ ] Quality signals (SOP compliance, ratings) visible remotely
- [ ] Live queue state accessible per branch
- [ ] Regional/franchise owners see their scope only (RBAC)

---

## PS-01.06 — Service Readiness Certification ✅

**What to Test:** Branch cannot offer a service until training, stock, and SOP walkthrough are complete.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Skill assessments per staff | `/quality/skills/{staff_id}` | GET | Shows current skill levels and gaps |
| 2 | Create skill assessment | `/quality/skills` | POST | Records competency evaluation |
| 3 | Skill gap forecasting | `/analytics/skill-gap` | GET | Supply vs demand for skill levels |
| 4 | Training records | `/training/` | GET | Training completion status |
| 5 | AI readiness agent | `/agents/ps/PS-01.06` | POST | Checks readiness prerequisites |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Team management shows skill levels | Manager → Team Management | L1/L2/L3 per stylist, gaps identified |
| 2 | Training module | Stylist → Training | Training records, certification status |

**Pass Criteria:**
- [ ] Skill assessments are competency-based (not time-based)
- [ ] Skill gaps are identified against service requirements
- [ ] Training completion is tracked per staff per service
- [ ] AI agent checks prerequisites before service launch

---

## PS-01.07 — Customer Profile Accessible to Any Substitute Stylist ✅

**What to Test:** When a regular stylist is absent, any substitute can access full customer history and preferences.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Get customer full profile | `/customers/{id}` | GET | Complete Beauty Passport with history |
| 2 | Get service history | `/customers/{id}/history` | GET | Timeline of all past services |
| 3 | Get SOULSKIN journal | `/soulskin/journal/{customer_id}` | GET | Archetype history and preferences |
| 4 | Get customer lifestyle data | `/customers/{id}` | GET | Includes lifestyle, preferences, sensitivities |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Stylist views customer profile | Stylist → Customers | Full passport, history, allergies, preferences |
| 2 | Any stylist at any branch can access | Login as different stylist | Same customer data accessible |

**Pass Criteria:**
- [ ] Beauty Passport is branch-agnostic (centralized)
- [ ] Past services, preferences, allergies all visible
- [ ] SOULSKIN archetype and notes accessible
- [ ] Any authenticated stylist can view assigned customer's profile

---

## PS-01.08 — Chemical Service Safety Verification ✅

**What to Test:** Safety protocols (patch test, allergy check) are verified and recorded before chemical services proceed.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Customer allergy data | `/customers/{id}` | GET | allergies array, product_sensitivities, patch_test_results |
| 2 | Service chemical flag | `/services/{id}` | GET | is_chemical field indicates chemical service |
| 3 | SOP has chemical details | `/sops/{id}` | GET | chemical_details, product_ratios in SOP |
| 4 | Session safety step | `/sessions/{booking_id}/step/1` | POST | Safety step must be completed first |
| 5 | AI safety agent | `/agents/ps/PS-01.08` | POST | Checks contraindications before service |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Beauty Passport shows allergies | `/customer/passport` | Allergies and sensitivities section visible |
| 2 | Live session shows safety steps | Stylist → Live Session | Chemical safety steps marked as critical |
| 3 | SOP management flags chemicals | Manager → SOP Management | Chemical services tagged, safety steps included |

**Pass Criteria:**
- [ ] Allergies and sensitivities stored in customer profile
- [ ] Chemical services flagged in service catalog
- [ ] SOPs include mandatory safety steps for chemical services
- [ ] Patch test results tracked with dates
- [ ] Warning surfaces when contraindicated product is about to be used

---

## PS-01.09 — Service Time Monitoring ✅

**What to Test:** Actual service duration is tracked against SOP-prescribed time, and shortcuts are flagged.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Get session timer | `/sessions/{booking_id}/timer` | GET | Returns elapsed_time and remaining_time |
| 2 | SOP has duration per step | `/sops/{id}` | GET | total_duration_minutes, per-step durations |
| 3 | Session completion with timing | `/sessions/{booking_id}/complete` | POST | Calculates timing_score |
| 4 | Quality assessment timing score | `/quality/` | POST | timing_score field in quality calculation |
| 5 | Analytics timing data | `/analytics/quality` | GET | Timing scores across services |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Live session has timer | Stylist → Live Session | Timer running, showing elapsed vs expected |
| 2 | Quality dashboard shows timing | Manager → Quality Dashboard | Timing score visible in assessments |

**Pass Criteria:**
- [ ] Real-time timer tracks elapsed vs prescribed duration
- [ ] Timing score is part of quality calculation (20% weight)
- [ ] Significantly shorter services are flagged
- [ ] Per-step timing is tracked (not just total)

---

## PS-01.10 — Cross-Branch Benchmarking ✅

**What to Test:** Best practices from high-performing branches are identified and shareable across the network.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Location comparison | `/analytics/compare` | GET | Revenue, quality, bookings side-by-side |
| 2 | Staff leaderboard | `/analytics/staff` | GET | Top performers across locations |
| 3 | Quality stats by location | `/analytics/quality` | GET | Per-location quality breakdown |
| 4 | AI benchmarking agent | `/agents/ps/PS-01.10` | POST | Identifies best practices from top branches |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Compare locations page | Locations → Compare | Head-to-head metrics |
| 2 | BI dashboard | Analytics → BI Dashboard | Cross-location comparison charts |
| 3 | Regional dashboard | Regional → Dashboard | Regional benchmarking |

**Pass Criteria:**
- [ ] Multiple branches can be compared on same metrics
- [ ] Quality, revenue, and customer scores comparable
- [ ] Top-performing branches identifiable
- [ ] AI agent generates actionable best-practice insights

---

# TRACK 2: Reducing Staff Dependency Through Technology

---

## PS-02.01 — Client Retention on Stylist Exit ✅

**What to Test:** Client loyalty is to the salon brand, not individual stylist. Warm transitions are enabled.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Customer history is salon-wide | `/customers/{id}/history` | GET | All visits across all stylists visible |
| 2 | Customer profile independent of stylist | `/customers/{id}` | GET | Profile not linked to single stylist |
| 3 | SOULSKIN journal accessible to all | `/soulskin/journal/{customer_id}` | GET | Archetype data not stylist-specific |
| 4 | AI warm-transition agent | `/agents/ps/PS-02.01` | POST | Generates handover notes for new stylist |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Any stylist sees full customer history | Stylist → Customers | Complete service history regardless of who performed it |
| 2 | Beauty Passport is brand-owned | Customer → Passport | Data belongs to salon, not stylist |

**Pass Criteria:**
- [ ] Customer data is centralized, not per-stylist
- [ ] Service history includes all stylists who served the customer
- [ ] SOULSKIN preferences, notes, and archetype are transferable
- [ ] AI agent can generate transition briefing for new stylist

---

## PS-02.02 — AI-Guided Upsell for Semi-Skilled Stylists ✅

**What to Test:** Junior stylists receive real-time AI suggestions on what to recommend at each service stage.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | AI recommendations for customer | `/customers/{id}/recommendations` | GET | Personalized service suggestions based on profile |
| 2 | AI coaching during session | `/sessions/{booking_id}/guidance` | GET | Context-aware suggestion for current step |
| 3 | AI upsell agent | `/agents/ps/PS-02.02` | POST | Generates upsell script for stylist |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | AI guidance in live session | Stylist → Live Session | AI coaching tips appear at each step |
| 2 | Customer recommendations visible | Stylist → Customer Profile | Service recommendations shown |

**Pass Criteria:**
- [ ] AI provides step-level coaching tips during service
- [ ] Recommendations are personalized to customer profile
- [ ] Upsell suggestions consider customer history and hair/skin condition
- [ ] Junior stylists receive more detailed guidance than senior ones

---

## PS-02.03 — Accelerated Digital Onboarding ✅

**What to Test:** New joiners reach productive level faster through digital training and real-time feedback.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Training records for staff | `/training/` | GET | Training history with scores, hours, costs |
| 2 | Create training record | `/training/` | POST | Records training completion with pass/fail |
| 3 | Training ROI stats | `/training/stats/roi` | GET | Revenue/quality impact of training |
| 4 | Skill assessments | `/quality/skills/{staff_id}` | GET | Current competency levels |
| 5 | AI onboarding agent | `/agents/ps/PS-02.03` | POST | Generates personalized onboarding path |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Stylist training page | Stylist → Training | Training records, certifications, progress |
| 2 | Team management shows training status | Manager → Team Management | Training completion visible per staff |

**Pass Criteria:**
- [ ] Digital training records with scores and hours
- [ ] Training linked to specific service categories
- [ ] ROI tracking (revenue before/after training)
- [ ] SOULSKIN certification tracked separately
- [ ] AI agent recommends personalized onboarding path

---

## PS-02.04 — Skills-Based Intelligent Scheduling ✅

**What to Test:** Stylist-to-service assignment is based on competency data and real-time availability.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Staff with skill levels | `/staff/?location_id={id}` | GET | Staff with skill_level (L1/L2/L3) and specializations |
| 2 | Service skill requirement | `/services/{id}` | GET | skill_requirement_level on each service |
| 3 | Available booking slots | `/bookings/slots?date={date}&location_id={id}` | GET | Smart slots based on service durations |
| 4 | Queue stylist assignment | `/queue/{location_id}/{entry_id}/assign` | POST | Assigns qualified stylist to queue entry |
| 5 | AI scheduling agent | `/agents/ps/PS-02.04` | POST | Optimal stylist-service matching |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Queue management with assignment | Manager → Queue Management | Assign stylist based on skill level |
| 2 | Booking shows available slots | Customer → Book New | Only valid slots shown |

**Pass Criteria:**
- [ ] Services have skill requirement levels
- [ ] Staff have skill levels and specializations
- [ ] Booking system considers skill-service match
- [ ] Queue assignment respects skill levels
- [ ] AI agent optimizes scheduling

---

## PS-02.05 — Early Warning for Stylist Attrition ✅

**What to Test:** At-risk stylists are flagged 60-90 days before resignation using behavioral signals.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Attrition analytics | `/analytics/attrition` | GET | Risk distribution, high-risk staff list |
| 2 | Staff performance metrics | `/staff/{id}/performance` | GET | Bookings, quality, rating, revenue trends |
| 3 | AI attrition prediction agent | `/agents/ps/PS-02.05` | POST | Predicts at-risk stylists with signals |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Team management shows risk | Manager → Team Management | Attrition risk badge (low/medium/high) |
| 2 | Analytics shows attrition data | Analytics → BI Dashboard | Attrition risk distribution |

**Pass Criteria:**
- [ ] Attrition risk scored per staff member
- [ ] Risk levels categorized (low/medium/high)
- [ ] Multiple signals used (service count, ratings, lateness, etc.)
- [ ] High-risk staff list available to managers
- [ ] Early warning (60-90 days) before likely resignation

---

## PS-02.06 — Senior Stylist Knowledge Capture ✅

**What to Test:** Working knowledge of senior stylists is captured passively into a reusable knowledge base.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Session captures stylist notes | `/sessions/{booking_id}/complete` | POST | stylist_notes field saved |
| 2 | Session photos | `/sessions/{booking_id}/photos` | POST | Before/after photos captured |
| 3 | SOP with experience overlays | `/sops/{id}` | GET | SOULSKIN overlays per step (senior knowledge) |
| 4 | AI knowledge capture agent | `/agents/ps/PS-02.06` | POST | Extracts patterns from senior stylist sessions |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Live session allows notes | Stylist → Live Session | Notes field available per service |
| 2 | SOP has archetype overlays | Manager → SOP Management | Experience-based overlays on steps |

**Pass Criteria:**
- [ ] Stylist notes captured per session
- [ ] Before/after photos documented
- [ ] SOPs enriched with archetype-specific overlays
- [ ] AI extracts patterns from experienced stylist data
- [ ] Knowledge accessible to junior stylists

---

## PS-02.07 — AI Consultation Assistant for Junior Stylists ✅

**What to Test:** AI coaches junior stylists in real-time on what to recommend and why.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | AI session guidance | `/sessions/{booking_id}/guidance` | GET | Coaching tip for current step |
| 2 | AI recommendations | `/customers/{id}/recommendations` | GET | Personalized recommendations with reasoning |
| 3 | AI consultation agent | `/agents/ps/PS-02.07` | POST | Full consultation script for junior stylist |
| 4 | SOULSKIN reading | `/soulskin/sessions/{id}/generate` | POST | Generates archetype-based service guidance |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | AI coaching in live session | Stylist → Live Session | AI tips visible during service |
| 2 | SOULSKIN flow provides guidance | SOULSKIN → Flow | Archetype drives service recommendations |

**Pass Criteria:**
- [ ] AI provides real-time consultation coaching
- [ ] Recommendations are based on customer profile + hair/skin analysis
- [ ] SOULSKIN archetype influences service guidance
- [ ] Stylist receives actionable scripts, not just data

---

## PS-02.08 — Competency-Based Skill Assessment ✅

**What to Test:** Promotion is based on demonstrated competence, not time served.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Create skill assessment | `/quality/skills` | POST | Assessment with rubric_scores, L2/L3 gap items |
| 2 | Get skill assessments | `/quality/skills/{staff_id}` | GET | All assessments for staff |
| 3 | Assessment types | `/quality/skills` | POST | Supports ai and manual assessment types |
| 4 | Skill gap analytics | `/analytics/skill-gap` | GET | Supply vs demand analysis |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Stylist sees skill level | Stylist → Performance | Current level, specializations |
| 2 | Manager sees team skills | Manager → Team Management | L1/L2/L3 distribution, gap items |

**Pass Criteria:**
- [ ] Skill assessments use rubric scoring (not tenure)
- [ ] L2 and L3 gap items identified per staff
- [ ] Recommended training generated from gaps
- [ ] AI and manual assessment types supported
- [ ] SOULSKIN certification tracked separately

---

## PS-02.09 — Dynamic Capacity Management ✅

**What to Test:** When key staff are absent, appointments are redistributed with minimum customer disruption.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Queue management | `/queue/{location_id}` | GET | Live queue state with positions |
| 2 | Reassign stylist | `/queue/{location_id}/{entry_id}/assign` | POST | Reassign to available qualified stylist |
| 3 | Wait time estimation | `/queue/{location_id}/wait-estimate` | GET | Dynamic estimate based on current load |
| 4 | Cancel booking | `/bookings/{id}/cancel` | POST | Cancel with status tracking |
| 5 | WhatsApp notification | `/queue/{location_id}/{entry_id}/notify` | POST | Notify customer of changes |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Queue management | Manager → Queue Management | Real-time queue with reassignment |
| 2 | Wait time visible | Manager → Queue Management | Dynamic wait estimates |

**Pass Criteria:**
- [ ] Live queue tracks all waiting customers
- [ ] Stylists can be reassigned to queue entries
- [ ] Wait time estimates update dynamically
- [ ] WhatsApp notifications for customer communication
- [ ] Walk-in tracking from multiple sources

---

## PS-02.10 — Product Application Guidance ✅

**What to Test:** Stylist receives exact application instructions (ratios, timing, quantities) for every product.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | SOP with product details | `/sops/{id}` | GET | products_required, chemical_details, ratios per step |
| 2 | Session step guidance | `/sessions/{booking_id}/guidance` | GET | Product-specific application instructions |
| 3 | AI product guidance agent | `/agents/ps/PS-02.10` | POST | Exact mixing ratios and timing per product |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Live session shows product details | Stylist → Live Session | Products, ratios, timing per step |
| 2 | SOP includes product specs | Manager → SOP Management | Chemical details and ratios in SOP |

**Pass Criteria:**
- [ ] SOPs include product names, ratios, and quantities
- [ ] Chemical details (developer strength, processing time) specified
- [ ] AI provides product-specific guidance during service
- [ ] Consistent instructions regardless of stylist

---

# TRACK 3: Hyper-Personalised Beauty Experiences

---

## PS-03.01 — Beauty Passport System ✅

**What to Test:** Complete digital profile captures and evolves customer history, preferences, and sensitivities across visits and branches.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Get Beauty Passport | `/customers/{id}` | GET | 40+ fields: hair, skin, lifestyle, allergies, goals, SOULSKIN, stats |
| 2 | Update passport fields | `/customers/{id}` | PATCH | Any field updatable |
| 3 | Service history | `/customers/{id}/history` | GET | Complete timeline across branches |
| 4 | Passport created on registration | `/auth/register` | POST | Beauty Passport auto-created |
| 5 | Search customers | `/customers/search?q={query}` | GET | Find by name/email/phone |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Full Beauty Passport page | Customer → Beauty Passport | All sections: Hair, Skin, Lifestyle, Allergies, Goals, SOULSKIN |
| 2 | Passport completeness score | Customer → Dashboard | Passport completeness percentage shown |
| 3 | Lifetime stats visible | Customer → Beauty Passport | Total visits, lifetime value |

**Pass Criteria:**
- [ ] 40+ diagnostic fields captured and stored
- [ ] Profile evolves with each visit (history grows)
- [ ] Accessible from any branch
- [ ] Auto-created on customer registration
- [ ] Completeness percentage calculated
- [ ] Lifetime value tracked

---

## PS-03.02 — AI Skin and Hair Diagnostic ✅

**What to Test:** Objective, measurable skin/hair assessment replaces subjective visual analysis.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | AI scan from image | `/customers/{id}/scan` | POST | Returns objective measurements (porosity, damage, etc.) |
| 2 | Diagnostic fields in profile | `/customers/{id}` | GET | scalp_condition, damage_level, porosity, hydration_score, wrinkle_score |
| 3 | AI diagnostic agent | `/agents/ps/PS-03.02` | POST | Comprehensive hair/skin analysis |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Beauty Passport shows diagnostics | Customer → Beauty Passport | Porosity, damage, scalp condition, skin concerns |
| 2 | Beauty score ring | Customer → Dashboard | Visual beauty score metric |

**Pass Criteria:**
- [ ] AI scan endpoint accepts image and returns measurements
- [ ] Objective scores (not just text descriptions)
- [ ] Multiple diagnostic dimensions (porosity, density, damage, hydration)
- [ ] Consistent results regardless of which stylist triggers scan

---

## PS-03.03 — Personalised Home Care Plans ✅

**What to Test:** Digital, personalised home care plan generated after every service based on specific conditions.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Generate homecare plan | `/homecare/generate` | POST | AI-generated plan with routines, products, climate adjustments |
| 2 | Get latest plan | `/homecare/{customer_id}` | GET | Most recent homecare plan |
| 3 | Plan history | `/homecare/{customer_id}/history` | GET | All past plans |
| 4 | Plan includes climate adjustments | `/homecare/generate` | POST | climate_adjustments field populated |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Homecare page | Customer → Home Care | Hair routine, skin routine, do's/don'ts, products |
| 2 | WhatsApp sharing | Customer → Home Care | WhatsApp share button |
| 3 | Climate-adjusted tips | Customer → Home Care | Climate adjustments section visible |

**Pass Criteria:**
- [ ] AI generates personalized plan (not generic brochure)
- [ ] Plan based on service performed + hair type + climate
- [ ] Hair routine and skin routine sections
- [ ] Product recommendations with specifics
- [ ] Do's and don'ts customized to customer
- [ ] Climate adjustments for local conditions
- [ ] WhatsApp sharing capability
- [ ] Next visit recommendation included

---

## PS-03.04 — Allergy and Sensitivity Tracking ✅

**What to Test:** Allergies are stored, persist across branches, and trigger warnings before contraindicated products are used.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Allergies in customer profile | `/customers/{id}` | GET | allergies array, product_sensitivities, patch_test_results |
| 2 | Update allergies | `/customers/{id}` | PATCH | Can add/update allergy data |
| 3 | AI safety check agent | `/agents/ps/PS-03.04` | POST | Checks product against known allergies |
| 4 | Chemical service SOP safety | `/sops/{id}` | GET | Safety steps for chemical services |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Allergies visible in passport | Customer → Beauty Passport | Allergies section with products listed |
| 2 | Stylist sees allergy warnings | Stylist → Customer view | Allergy data prominently displayed |

**Pass Criteria:**
- [ ] Allergies stored as array in customer profile
- [ ] Product sensitivities tracked separately
- [ ] Patch test results with dates recorded
- [ ] Data persists across all branches
- [ ] AI agent can flag contraindicated products
- [ ] Visible warning to any stylist viewing the profile

---

## PS-03.05 — Personalised Service Recommendation Engine ✅

**What to Test:** Next-best-service suggestions based on profile, history, and conditions — not just the menu.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | AI recommendations | `/customers/{id}/recommendations` | GET | Personalized service list based on profile |
| 2 | SOULSKIN-driven recommendations | `/soulskin/sessions/{id}/generate` | POST | Archetype-based service protocol |
| 3 | AI recommendation agent | `/agents/ps/PS-03.05` | POST | Context-aware service suggestions |
| 4 | Climate recommendations | `/climate/?city={city}` | GET | Climate-adjusted service suggestions |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Customer dashboard recommendations | Customer → Dashboard | Suggested services visible |
| 2 | Stylist sees recommendations | Stylist → Customer view | AI recommendations for assigned customer |

**Pass Criteria:**
- [ ] Recommendations consider hair/skin condition + history
- [ ] SOULSKIN archetype influences suggestions
- [ ] Climate/season factored in
- [ ] Recommendations are specific (not generic menu items)

---

## PS-03.06 — Virtual Try-On Before Irreversible Services ✅

**What to Test:** Customer can see how they will look before haircut, colour, or styling.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Create AR mirror session | `/mirror/` | POST | Session with type (hairstyle_try_on, color_preview) |
| 2 | List mirror sessions | `/mirror/` | GET | Past try-on sessions |
| 3 | Digital twin simulation | `/twin/{customer_id}/simulate` | POST | Future state prediction |
| 4 | Service AR preview flag | `/services/{id}` | GET | ar_preview_available field |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | AR Mirror page | Mirror → AR Mirror | Virtual try-on interface |
| 2 | Save and share looks | Mirror → AR Mirror | Saved images functionality |

**Pass Criteria:**
- [ ] AR mirror session types include hairstyle, colour, makeup
- [ ] Sessions can save images for comparison
- [ ] Services marked with AR preview availability
- [ ] Digital twin supports simulation of future states

---

## PS-03.07 — Long-Term Beauty Journey Planning ✅

**What to Test:** Multi-visit, sequenced treatment plans with progress tracking over months.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Generate journey plan | `/journey/generate/{customer_id}` | POST | 3/6/12-week plan with milestones |
| 2 | Get active journey | `/journey/{customer_id}` | GET | Current plan with milestones, outcomes, cost |
| 3 | Track progress | `/journey/{customer_id}/progress` | GET | Completed vs remaining milestones |
| 4 | Journey history | `/journey/{customer_id}/history` | GET | Past journey plans |
| 5 | Set beauty goal | `/customers/{id}/goal` | POST | Stores target goal in profile |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Beauty Journey page | Customer → Beauty Journey | Milestones, progress, recommendations |
| 2 | Goal progress in dashboard | Customer → Dashboard | Goal progress percentage |

**Pass Criteria:**
- [ ] Journey plans with defined milestones
- [ ] Expected outcomes documented
- [ ] Estimated total cost calculated
- [ ] Progress tracking (completed vs total)
- [ ] Skin projection for future state
- [ ] Multiple duration options (3/6/12 weeks)

---

## PS-03.08 — Climate-Aware Service Customisation ✅

**What to Test:** Service protocols and recommendations adjust based on local climate and water quality.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Climate data for city | `/climate/?city={city}` | GET | Temperature, humidity, UV, AQI, recommendations |
| 2 | Climate alerts | `/climate/alerts` | GET | Active weather alerts |
| 3 | 7-day beauty forecast | `/climate/{city}/forecast` | GET | Multi-day beauty-relevant forecast |
| 4 | Location climate data | `/locations/{id}/climate` | GET | Climate for branch's city |
| 5 | Homecare climate adjustments | `/homecare/generate` | POST | climate_adjustments in plan |
| 6 | Customer lifestyle city | `/customers/{id}` | GET | city, climate data in lifestyle |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Climate alert banner | All pages | Climate alerts visible when active |
| 2 | UV/humidity/AQI in passport | Customer → Beauty Passport | Environmental context shown |
| 3 | Climate in homecare plan | Customer → Home Care | Climate adjustments section |
| 4 | Customer dashboard environment | Customer → Dashboard | UV, humidity, AQI indicators |

**Pass Criteria:**
- [ ] Real-time weather data fetched per city
- [ ] Hair and skin recommendations adjusted for climate
- [ ] UV index, humidity, AQI tracked
- [ ] 7-day beauty-relevant forecast available
- [ ] Climate data influences homecare plans
- [ ] Different cities get different recommendations

---

## PS-03.09 — Personalised Loyalty Engine ✅

**What to Test:** Loyalty rewards are personalised based on behaviour, preferences, and lifetime value.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Customer LTV | `/customers/{id}` | GET | lifetime_value calculated |
| 2 | Customer analytics | `/analytics/customers` | GET | LTV distribution, archetype breakdown |
| 3 | SOULSKIN archetype for personalization | `/soulskin/journal/{customer_id}` | GET | Emotional profile for targeted offers |
| 4 | AI loyalty agent | `/agents/ps/PS-03.09` | POST | Personalized offer generation |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | LTV visible in passport | Customer → Beauty Passport | Lifetime value shown |
| 2 | Customer analytics | Analytics → BI Dashboard | LTV distribution charts |

**Pass Criteria:**
- [ ] Customer lifetime value calculated
- [ ] LTV segmentation available
- [ ] SOULSKIN archetype used for offer personalization
- [ ] AI generates individualized offers
- [ ] High-value customers identifiable

---

## PS-03.10 — Occasion-Based Service Planning ✅

**What to Test:** Upcoming events are identified and multi-service plans are proactively proposed.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Beauty goal setting | `/customers/{id}/goal` | POST | Stores occasion/goal target |
| 2 | Journey plan generation | `/journey/generate/{customer_id}` | POST | Multi-week plan for occasion |
| 3 | AI occasion agent | `/agents/ps/PS-03.10` | POST | Occasion-aware service plan |
| 4 | Customer lifestyle data | `/customers/{id}/lifestyle` | POST | Can capture upcoming events |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Beauty Journey with occasion | Customer → Beauty Journey | Journey tied to specific goal/occasion |
| 2 | Goal setting in passport | Customer → Beauty Passport | Goal and progress visible |

**Pass Criteria:**
- [ ] Goals/occasions captured in customer profile
- [ ] Journey plans can target specific occasions
- [ ] Multi-week sequenced plan generated
- [ ] Cost estimation for full occasion journey
- [ ] Progress tracking toward occasion date

---

# TRACK 4: AI-Based Prediction of Beauty Trends

---

## PS-04.01 — Early Trend Detection Pipeline ✅

**What to Test:** Emerging beauty trends are identified 4-8 weeks before mainstream demand.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | List trends | `/trends/` | GET | Trends with signal_strength, trajectory, confidence |
| 2 | Trend details | `/trends/{id}` | GET | Full trend data with social/search/booking scores |
| 3 | AI trend detection agent | `/agents/ps/PS-04.01` | POST | Identifies emerging trends with timing |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Trend Intelligence page | Manager → Trend Intelligence | Trend cards with trajectory, signal strength |
| 2 | Trend trajectory labels | Manager → Trend Intelligence | Emerging/Growing/Peak/Declining visible |

**Pass Criteria:**
- [ ] Trends have trajectory classification (rising/stable/declining)
- [ ] Signal strength is a composite score
- [ ] Social media, search, and booking demand scores
- [ ] Confidence level assigned
- [ ] Celebrity trigger identification
- [ ] Longevity label (fad/trend/movement)

---

## PS-04.02 — Predictive Inventory Planning ✅

**What to Test:** Product ordering based on predicted demand, not last month's sales.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Trend demand signals | `/trends/` | GET | booking_demand_score per trend |
| 2 | Revenue forecast | `/analytics/forecast` | GET | 30-day revenue prediction |
| 3 | AI inventory agent | `/agents/ps/PS-04.02` | POST | Product ordering recommendations |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Trends with demand data | Manager → Trend Intelligence | Booking demand scores visible |
| 2 | Forecast in BI dashboard | Analytics → BI Dashboard | Revenue forecast chart |

**Pass Criteria:**
- [ ] Demand signals derived from trend data
- [ ] Revenue forecasting available
- [ ] AI agent generates procurement recommendations
- [ ] Seasonal patterns considered

---

## PS-04.03 — Regional Trend Differences ✅

**What to Test:** Trends are tracked at city/district level, not just nationally.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Trends filtered by city | `/trends/?city={city}` | GET | City-specific trend data |
| 2 | Trend applicable cities | `/trends/{id}` | GET | applicable_cities array |
| 3 | AI regional trend agent | `/agents/ps/PS-04.03` | POST | Region-wise trend analysis |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | City filter on trends | Manager → Trend Intelligence | Filter trends by city |
| 2 | City distribution visible | Manager → Trend Intelligence | Which cities each trend applies to |

**Pass Criteria:**
- [ ] Trends have applicable_cities field
- [ ] Can filter trends by city
- [ ] Different cities show different trend profiles
- [ ] Regional readiness recommendations

---

## PS-04.04 — Celebrity-Driven Demand Prediction ✅

**What to Test:** Celebrity appearances that drive beauty demand are detected and acted upon.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Celebrity trigger field | `/trends/{id}` | GET | celebrity_trigger field populated |
| 2 | AI celebrity monitoring agent | `/agents/ps/PS-04.04` | POST | Detects celebrity-driven demand spikes |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Celebrity trigger in trends | Manager → Trend Intelligence | Celebrity name visible on relevant trends |

**Pass Criteria:**
- [ ] Trends can have celebrity_trigger field
- [ ] AI agent monitors celebrity beauty appearances
- [ ] Demand spike prediction linked to celebrity events

---

## PS-04.05 — Seasonal Demand Modelling ✅

**What to Test:** Known seasonal patterns are mapped and used for proactive preparation.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Revenue forecast | `/analytics/forecast` | GET | 30-day trend with seasonal patterns |
| 2 | Trend climate correlation | `/trends/{id}` | GET | climate_correlation field |
| 3 | AI seasonal agent | `/agents/ps/PS-04.05` | POST | Seasonal demand recommendations |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Forecast visualization | Analytics → BI Dashboard | Revenue forecast chart |
| 2 | Climate-correlated trends | Manager → Trend Intelligence | Climate correlation visible |

**Pass Criteria:**
- [ ] Revenue forecasting considers seasonal patterns
- [ ] Climate correlation tracked per trend
- [ ] AI agent generates seasonal preparation recommendations
- [ ] Historical patterns used for prediction

---

## PS-04.06 — Social Media Trend Intelligence ✅

**What to Test:** Beauty trends from Instagram, Pinterest, YouTube are monitored and converted to actionable signals.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Social media scores | `/trends/{id}` | GET | social_media_score field |
| 2 | Search trend scores | `/trends/{id}` | GET | search_trend_score field |
| 3 | AI social monitoring agent | `/agents/ps/PS-04.06` | POST | Social media trend extraction |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Social scores in trends | Manager → Trend Intelligence | Social media score visible per trend |
| 2 | Signal breakdown | Manager → Trend Intelligence | Social vs search vs booking breakdown |

**Pass Criteria:**
- [ ] Social media score tracked per trend
- [ ] Search trend score tracked per trend
- [ ] Combined signal strength calculated
- [ ] AI extracts beauty-relevant signals from social data

---

## PS-04.07 — Trend-Linked Training System ✅

**What to Test:** Training is scheduled proactively based on predicted demand, not reactively after customer requests.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Training records linked to service | `/training/` | GET | service_category field on training |
| 2 | Skill gap forecasting | `/analytics/skill-gap` | GET | Supply vs demand for skills |
| 3 | AI training agent | `/agents/ps/PS-04.07` | POST | Trend-linked training recommendations |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Skill gap analytics | Analytics → BI Dashboard | Skill gap visualization |
| 2 | Training linked to trends | Manager → Team Management | Training needs based on trend demand |

**Pass Criteria:**
- [ ] Training records linked to service categories
- [ ] Skill gap analysis maps current skills vs future demand
- [ ] AI recommends training based on upcoming trends
- [ ] Training scheduled before demand peaks

---

## PS-04.08 — Competitor Intelligence Monitoring ✅

**What to Test:** Competitor services, pricing, and promotions are tracked systematically.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | AI competitor intelligence agent | `/agents/ps/PS-04.08` | POST | Competitor analysis report |
| 2 | Trend data includes market signals | `/trends/` | GET | Market-wide trend signals |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Trend intelligence | Manager → Trend Intelligence | Market context visible |

**Pass Criteria:**
- [ ] AI agent provides competitive positioning signals
- [ ] Competitor service/pricing monitoring capability
- [ ] Weekly competitive intelligence reports

---

## PS-04.09 — Product Launch Timing Optimisation ✅

**What to Test:** New products are introduced when category demand will be highest.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Trend trajectory data | `/trends/` | GET | Rising/stable/declining trajectory |
| 2 | Booking demand scores | `/trends/{id}` | GET | booking_demand_score |
| 3 | AI launch timing agent | `/agents/ps/PS-04.09` | POST | Optimal launch window recommendation |

**Pass Criteria:**
- [ ] Trend trajectory shows when demand is rising
- [ ] Booking demand score indicates current demand level
- [ ] AI agent recommends optimal launch timing
- [ ] Seasonal and trend data combined for timing

---

## PS-04.10 — Trend-Data-Driven Campaign Planning ✅

**What to Test:** Marketing campaigns use real trend data, not just intuition.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Trend data for campaigns | `/trends/` | GET | Service categories with rising demand |
| 2 | Customer analytics segments | `/analytics/customers` | GET | Customer segments and archetypes |
| 3 | AI campaign agent | `/agents/ps/PS-04.10` | POST | Data-driven campaign recommendations |

**Pass Criteria:**
- [ ] Trend data available for campaign planning
- [ ] Customer segments identified for targeting
- [ ] AI agent recommends campaign themes, timing, segments
- [ ] Signal strength guides campaign priority

---

# TRACK 5: AI Tools to Enhance Customer Experience

---

## PS-05.01 — Productive Waiting Experience ✅

**What to Test:** Pre-service wait time is used for engagement — profile completion, recommendations, virtual try-ons.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Queue wait estimation | `/queue/{location_id}/wait-estimate` | GET | Estimated wait time |
| 2 | Join queue | `/queue/{location_id}/join` | POST | Customer enters queue |
| 3 | Customer recommendations while waiting | `/customers/{id}/recommendations` | GET | Can browse recommendations |
| 4 | AR mirror during wait | `/mirror/` | POST | Virtual try-on session |
| 5 | SOULSKIN flow during wait | `/soulskin/sessions` | POST | Can complete soul reading |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Customer has services to browse while waiting | Customer → Book New | Service catalog browsable |
| 2 | Virtual try-on accessible | Mirror → AR Mirror | Can try looks while waiting |
| 3 | SOULSKIN flow accessible | SOULSKIN → Flow | Can do soul reading while waiting |

**Pass Criteria:**
- [ ] Wait time estimation available
- [ ] Customer can complete Beauty Passport during wait
- [ ] AR try-ons accessible during wait
- [ ] SOULSKIN flow available during wait
- [ ] Recommendations browsable while waiting

---

## PS-05.02 — Intelligent Post-Service Follow-Up ✅

**What to Test:** Personalised follow-ups based on service received, not generic SMS.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Notifications system | `/notifications/` | GET | Personalised notifications |
| 2 | Homecare plan delivery | `/homecare/generate` | POST | Service-specific aftercare |
| 3 | Journey next-visit recommendation | `/journey/{customer_id}` | GET | next_visit_recommendation |
| 4 | AI follow-up agent | `/agents/ps/PS-05.02` | POST | Personalised follow-up sequence |
| 5 | WhatsApp homecare sharing | `/homecare/{customer_id}` | GET | whatsapp_sent field |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Notifications page | Customer notifications | Personalised messages |
| 2 | Homecare plan | Customer → Home Care | Post-service care instructions |

**Pass Criteria:**
- [ ] Post-service homecare plan generated (personalised)
- [ ] Notifications are service-specific
- [ ] Multi-channel: push, email, SMS, WhatsApp
- [ ] Next visit recommendation with timing
- [ ] WhatsApp delivery of homecare plan

---

## PS-05.03 — Transferable Stylist-Customer Rapport ✅

**What to Test:** Customer relationship context (personal notes, preferences, communication style) is portable between stylists.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | SOULSKIN journal | `/soulskin/journal/{customer_id}` | GET | Archetype history, emotional profile |
| 2 | Customer lifestyle data | `/customers/{id}` | GET | Personal context in profile |
| 3 | Session stylist notes | `/sessions/{booking_id}/complete` | POST | Notes from each service |
| 4 | AI relationship agent | `/agents/ps/PS-05.03` | POST | Relationship handover notes |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Stylist sees customer context | Stylist → Customers | Full profile + SOULSKIN + history |
| 2 | SOULSKIN archetype visible | Stylist dashboard | Archetype badge shown |

**Pass Criteria:**
- [ ] SOULSKIN emotional profile available to all stylists
- [ ] Customer lifestyle and preferences centralized
- [ ] Session notes from all stylists visible
- [ ] AI generates relationship briefing for new stylist
- [ ] Communication style preferences stored

---

## PS-05.04 — In-Service Transparency ✅

**What to Test:** Customer can see what is happening during their service — products, stages, timing.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Session timer | `/sessions/{booking_id}/timer` | GET | Elapsed and remaining time |
| 2 | Session state | `/sessions/{booking_id}` | GET | Current step, steps total, products used |
| 3 | SOP steps visible | `/sops/{id}` | GET | Step-by-step breakdown |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Live session shows progress | Stylist → Live Session | Steps visible with timer |
| 2 | Customer can see status | Customer bookings | Service status tracking |

**Pass Criteria:**
- [ ] Current service step is tracked and visible
- [ ] Timer shows elapsed and remaining time
- [ ] Products being used are documented
- [ ] Steps completed vs total visible

---

## PS-05.05 — Real-Time In-Service Feedback ✅

**What to Test:** Customer sentiment captured during service, not 24 hours later.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Mood detection | `/mood/` | POST | Emotion detection with confidence |
| 2 | Mood history | `/mood/history/{customer_id}` | GET | Emotional journey over visit |
| 3 | Feedback submission | `/feedback/` | POST | Rating with sentiment analysis |
| 4 | Feedback stats | `/feedback/stats` | GET | Real-time sentiment metrics |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Feedback page | Manager → Feedback | Real-time feedback with sentiment |
| 2 | Mood detection recorded | Via API | Mood captured during service |

**Pass Criteria:**
- [ ] Mood detection during service (emotion, confidence, energy)
- [ ] Real-time feedback capture
- [ ] Sentiment analysis on feedback (positive/neutral/negative)
- [ ] Customer consent for mood tracking
- [ ] Immediate alert for negative sentiment

---

## PS-05.06 — Multi-Language Communication ✅

**What to Test:** Stylist and customer communicate accurately across language differences.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Customer language preferences | `/customers/{id}` | GET | Language preference in profile |
| 2 | AI translation agent | `/agents/ps/PS-05.06` | POST | Service communication translation |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Language preference setting | Customer → Profile | Language selector (English, Tamil, Hindi, Telugu, Kannada) |

**Pass Criteria:**
- [ ] Customer profile stores language preference
- [ ] 5 languages supported (English, Tamil, Hindi, Telugu, Kannada)
- [ ] AI agent can translate service communication
- [ ] Service terms accurately translated

---

## PS-05.07 — Intelligent No-Show Management ✅

**What to Test:** No-shows trigger automatic waitlist offers, schedule adjustment, and re-engagement.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Mark booking as no-show | `/bookings/{id}/no-show` | POST | Updates status to NO_SHOW |
| 2 | Queue waitlist | `/queue/{location_id}` | GET | Walk-in waitlist available |
| 3 | WhatsApp notification | `/queue/{location_id}/{entry_id}/notify` | POST | Can notify waitlisted customers |
| 4 | AI no-show agent | `/agents/ps/PS-05.07` | POST | Smart re-engagement messaging |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | No-show marking | Manager → Queue | Can mark as no-show |
| 2 | Queue has waitlist | Manager → Queue Management | Waitlist entries visible |

**Pass Criteria:**
- [ ] No-show status tracked on bookings
- [ ] Waitlist system for walk-ins
- [ ] WhatsApp notification for slot redistribution
- [ ] AI generates re-engagement messages
- [ ] Freed slot offered to waitlisted customers

---

## PS-05.08 — Stylist Performance Analytics ✅

**What to Test:** Multi-dimensional stylist performance metrics beyond just popularity.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Staff performance | `/staff/{id}/performance` | GET | Bookings, quality, rating, revenue |
| 2 | Staff leaderboard | `/analytics/staff` | GET | Multi-metric ranking |
| 3 | Quality per stylist | `/quality/?stylist_id={id}` | GET | Quality assessments per stylist |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Stylist performance page | Stylist → Performance | KPIs, ranking, quality scores |
| 2 | Team management | Manager → Team Management | Performance metrics per staff |
| 3 | Staff analytics | Analytics → BI Dashboard | Staff productivity ranking |

**Pass Criteria:**
- [ ] Revenue per stylist tracked
- [ ] Services completed count
- [ ] Customer rating average
- [ ] Quality/SOP compliance score per stylist
- [ ] Upsell conversion (if tracked)
- [ ] Rebooking rate
- [ ] Multi-dimensional leaderboard

---

## PS-05.09 — Dynamic In-Salon Ambient Intelligence ✅

**What to Test:** Music, lighting, and displays adapt to occupancy, time, and customer mix.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | SOULSKIN sensory environment | `/soulskin/sessions/{id}/generate` | POST | Aroma, lighting, music recommendations |
| 2 | Queue occupancy | `/queue/{location_id}` | GET | Current occupancy level |
| 3 | AI ambient agent | `/agents/ps/PS-05.09` | POST | Dynamic environment recommendations |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | SOULSKIN session output | SOULSKIN → Flow | Sensory environment recommendations |
| 2 | SOULSKIN analytics | Manager → SOULSKIN Analytics | Archetype distribution (customer mix) |

**Pass Criteria:**
- [ ] SOULSKIN generates sensory recommendations (aroma, lighting, music)
- [ ] Queue data provides occupancy context
- [ ] AI agent adjusts recommendations based on context
- [ ] Customer archetype mix considered

---

## PS-05.10 — AI-Powered Checkout Cross-Sell ✅

**What to Test:** Personalised product/service recommendations at point of payment.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Customer recommendations | `/customers/{id}/recommendations` | GET | Personalized suggestions |
| 2 | Homecare product recommendations | `/homecare/{customer_id}` | GET | Product recommendations with details |
| 3 | AI cross-sell agent | `/agents/ps/PS-05.10` | POST | Checkout-specific suggestions |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Product recommendations in homecare | Customer → Home Care | Product recommendations section |

**Pass Criteria:**
- [ ] AI generates checkout-specific recommendations
- [ ] Recommendations based on service just received
- [ ] Customer history considered
- [ ] Product recommendations with pricing
- [ ] Predicted next need factored in

---

# TRACK 6: Turning Salon Data into Business Intelligence

---

## PS-06.01 — Franchise Business Intelligence Dashboard ✅

**What to Test:** Raw POS data converted to actionable financial metrics for franchise owners.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Revenue analytics | `/analytics/revenue` | GET | Revenue by period, category, location |
| 2 | Analytics overview | `/analytics/overview` | GET | KPI dashboard |
| 3 | Location analytics | `/locations/{id}/analytics` | GET | Per-branch metrics |
| 4 | Location comparison | `/analytics/compare` | GET | Multi-branch comparison |
| 5 | Export reports | `/analytics/export` | POST | PDF/CSV export |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | BI Dashboard | Analytics → BI Dashboard | Revenue, categories, trends, charts |
| 2 | Franchise dashboard | Franchise → Dashboard | Multi-location P&L |
| 3 | Export capability | Analytics → BI Dashboard | Export button |

**Pass Criteria:**
- [ ] Revenue by period (daily/weekly/monthly)
- [ ] Revenue by service category
- [ ] Revenue by location
- [ ] Quality metrics alongside revenue
- [ ] Export to PDF/CSV
- [ ] Franchise owner sees only their locations (RBAC)

---

## PS-06.02 — Training ROI Measurement ✅

**What to Test:** Training investment correlated to revenue and quality outcomes.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Training ROI analytics | `/analytics/training-roi` | GET | Cost vs revenue/quality impact |
| 2 | Training ROI stats | `/training/stats/roi` | GET | Per-training ROI metrics |
| 3 | Training records with revenue | `/training/` | GET | revenue_before, revenue_after, quality_before, quality_after |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Training ROI in BI dashboard | Analytics → BI Dashboard | Training ROI visualization |
| 2 | Stylist training page | Stylist → Training | Training impact visible |

**Pass Criteria:**
- [ ] Training records include cost_to_company
- [ ] Revenue before/after training tracked
- [ ] Quality score before/after tracked
- [ ] ROI calculable per training programme
- [ ] Per-stylist, per-service-category breakdown

---

## PS-06.03 — Unified Cross-System Analytics ✅

**What to Test:** Skill data + revenue data + customer feedback joined in single analytics layer.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Staff analytics (multi-dimensional) | `/analytics/staff` | GET | Services + revenue + quality + rating combined |
| 2 | Customer analytics | `/analytics/customers` | GET | LTV + archetype + beauty score combined |
| 3 | Quality analytics | `/analytics/quality` | GET | SOP + timing + customer rating combined |
| 4 | SOULSKIN analytics | `/analytics/soulskin` | GET | Archetype + rating + retention combined |
| 5 | Skill assessments | `/quality/skills/{staff_id}` | GET | Skills linked to performance |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | BI Dashboard cross-dimensional | Analytics → BI Dashboard | Multiple data dimensions in one view |
| 2 | Staff analytics multi-metric | Manager → Team Management | Skills + performance + risk combined |

**Pass Criteria:**
- [ ] Single dashboard combines skill + revenue + quality data
- [ ] Cross-dimensional queries possible
- [ ] Staff performance includes skill level, revenue, quality, and rating
- [ ] Customer analytics includes LTV, archetype, and beauty score
- [ ] No need to export to Excel to join data

---

## PS-06.04 — Real-Time Franchise Performance Dashboard ✅

**What to Test:** Performance data is live (days, not weeks) with automatic aggregation.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Analytics overview (live) | `/analytics/overview` | GET | Current KPIs (not month-end) |
| 2 | Location comparison (live) | `/analytics/compare` | GET | Real-time branch comparison |
| 3 | Today's bookings | `/bookings/today` | GET | Same-day data |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Admin dashboard live | Admin → Command Center | Real-time KPIs |
| 2 | Franchise dashboard | Franchise → Dashboard | Live performance data |
| 3 | Regional dashboard | Regional → Dashboard | Real-time regional metrics |

**Pass Criteria:**
- [ ] Data refreshes in real-time (not monthly batches)
- [ ] Today's bookings visible same day
- [ ] Revenue aggregated automatically
- [ ] Underperformance visible within days
- [ ] No manual Excel compilation needed

---

## PS-06.05 — Customer Lifetime Value Modelling ✅

**What to Test:** LTV calculated per customer, used for retention and acquisition strategies.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Customer LTV | `/customers/{id}` | GET | lifetime_value field |
| 2 | LTV distribution | `/analytics/customers` | GET | LTV segments |
| 3 | Customer visit stats | `/customers/{id}` | GET | total_visits, lifetime_value |
| 4 | AI LTV agent | `/agents/ps/PS-06.05` | POST | LTV modelling and churn signals |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | LTV in Beauty Passport | Customer → Beauty Passport | Lifetime value shown |
| 2 | Customer analytics | Analytics → BI Dashboard | LTV distribution chart |

**Pass Criteria:**
- [ ] LTV calculated per customer
- [ ] LTV segments identifiable
- [ ] Total visits tracked
- [ ] High-LTV customers identifiable
- [ ] Churn signal detection for high-LTV customers
- [ ] Archetype breakdown of LTV segments

---

## PS-06.06 — Skill Gap Forecasting ✅

**What to Test:** Current skill inventory mapped against future service requirements.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Skill gap analytics | `/analytics/skill-gap` | GET | Supply vs demand analysis |
| 2 | Skill assessments inventory | `/quality/skills/{staff_id}` | GET | Current levels per staff |
| 3 | Service skill requirements | `/services/{id}` | GET | skill_requirement_level |
| 4 | AI skill gap agent | `/agents/ps/PS-06.06` | POST | Skill gap forecast with training plan |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Skill gap in BI dashboard | Analytics → BI Dashboard | Supply vs demand visualization |
| 2 | Team skill inventory | Manager → Team Management | L1/L2/L3 distribution |

**Pass Criteria:**
- [ ] Current skill levels mapped across network
- [ ] Services have skill requirements
- [ ] Supply vs demand gap calculated
- [ ] Branch-level training readiness
- [ ] AI generates training timeline recommendations

---

## PS-06.07 — Product Usage vs Quality Correlation ✅

**What to Test:** Product consumption linked to service quality and customer outcomes.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | SOP product details | `/sops/{id}` | GET | products_required, chemical_details |
| 2 | Quality assessments | `/quality/` | GET | Quality scores per service |
| 3 | AI product intelligence agent | `/agents/ps/PS-06.07` | POST | Product-quality correlation analysis |
| 4 | Session deviations | `/sessions/{booking_id}` | GET | Deviation logs (may relate to product use) |

**Pass Criteria:**
- [ ] Products tracked per SOP
- [ ] Quality scores linked to service sessions
- [ ] AI agent can correlate consumption with quality
- [ ] Deviation logs capture product-related issues

---

## PS-06.08 — Branch Revenue Decline Prediction ✅

**What to Test:** Composite of leading indicators predicts revenue decline 60-90 days ahead.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Revenue forecast | `/analytics/forecast` | GET | 30-day revenue prediction |
| 2 | Quality trends | `/analytics/quality` | GET | Quality score trends |
| 3 | Attrition risk | `/analytics/attrition` | GET | Staff stability signals |
| 4 | Feedback trends | `/feedback/stats` | GET | Complaint frequency trends |
| 5 | AI branch health agent | `/agents/ps/PS-06.08` | POST | Composite health score with prediction |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Revenue forecast | Analytics → BI Dashboard | Forecast trend line |
| 2 | Quality trends | Manager → Quality Dashboard | Quality score over time |

**Pass Criteria:**
- [ ] Revenue forecasting available
- [ ] Multiple leading indicators monitored
- [ ] Quality trends tracked over time
- [ ] Attrition risk factored in
- [ ] AI generates composite health score
- [ ] Early warning alerts for declining branches

---

## PS-06.09 — Personalised Stylist Career Development ✅

**What to Test:** Each stylist sees clear growth pathway with specific competencies needed.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Stylist skill level | `/staff/{id}` | GET | Current skill_level (L1/L2/L3) |
| 2 | Skill assessment gaps | `/quality/skills/{staff_id}` | GET | L2_gap_items, L3_gap_items |
| 3 | Training recommendations | `/quality/skills/{staff_id}` | GET | recommended_training |
| 4 | Performance metrics | `/staff/{id}/performance` | GET | Current performance data |
| 5 | AI career path agent | `/agents/ps/PS-06.09` | POST | Personalized development plan |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Stylist performance page | Stylist → Performance | Level, skills, ranking |
| 2 | Training page | Stylist → Training | Required training visible |

**Pass Criteria:**
- [ ] Current skill level clearly shown (L1/L2/L3)
- [ ] Gap items for next level identified
- [ ] Recommended training for advancement
- [ ] Performance metrics visible to stylist
- [ ] Clear path from current level to next level
- [ ] SOULSKIN certification as bonus dimension

---

## PS-06.10 — Service Portfolio Optimisation ✅

**What to Test:** Each branch's service mix analysed against local demand and profitability.

**Backend Tests:**
| # | Test | Endpoint | Method | Expected Result |
|---|------|----------|--------|----------------|
| 1 | Revenue by category | `/analytics/revenue` | GET | Revenue breakdown by service category |
| 2 | Location analytics | `/locations/{id}/analytics` | GET | Per-branch performance |
| 3 | Trend data by city | `/trends/?city={city}` | GET | Local demand signals |
| 4 | Location comparison | `/analytics/compare` | GET | Cross-branch performance comparison |
| 5 | AI portfolio agent | `/agents/ps/PS-06.10` | POST | Service mix optimization recommendations |

**Frontend Tests:**
| # | Test | Page | What to Check |
|---|------|------|---------------|
| 1 | Revenue by category | Analytics → BI Dashboard | Category breakdown chart |
| 2 | Location comparison | Locations → Compare | Service performance by branch |

**Pass Criteria:**
- [ ] Revenue tracked by service category per branch
- [ ] Local trend data available for demand signals
- [ ] Cross-branch comparison on same services
- [ ] AI recommends which services to expand/reduce per branch
- [ ] Market-specific service recommendations

---

# Quick Reference: API Endpoint Map

## Authentication & Users
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/auth/register` | POST | Register + create Beauty Passport |
| `/auth/login` | POST | JWT login |
| `/auth/me` | GET | Current user |
| `/roles/users/all` | GET | All users (admin) |

## Customers (Beauty Passport)
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/customers` | GET | List passports |
| `/customers/{id}` | GET | Full passport |
| `/customers/{id}/scan` | POST | AI hair/skin scan |
| `/customers/{id}/recommendations` | GET | AI recommendations |
| `/customers/{id}/history` | GET | Service history |
| `/customers/{id}/goal` | POST | Set beauty goal |

## Bookings & Queue
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/bookings` | GET/POST | List/create bookings |
| `/bookings/slots` | GET | Available slots |
| `/bookings/{id}/check-in` | POST | Check in |
| `/bookings/{id}/no-show` | POST | Mark no-show |
| `/queue/{location_id}` | GET | Live queue |
| `/queue/{location_id}/join` | POST | Join queue |
| `/queue/{location_id}/wait-estimate` | GET | Wait time |

## Services & SOPs
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/services` | GET | Service catalog |
| `/sops` | GET | List SOPs |
| `/sessions` | POST | Create service session |
| `/sessions/{id}/guidance` | GET | AI coaching |
| `/sessions/{id}/step/{n}` | POST | Complete step |

## Quality & Skills
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/quality` | GET/POST | Quality assessments |
| `/quality/skills/{id}` | GET | Skill assessments |
| `/quality/stats/summary` | GET | Quality statistics |

## Analytics & BI
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/analytics/overview` | GET | KPI dashboard |
| `/analytics/revenue` | GET | Revenue analytics |
| `/analytics/quality` | GET | Quality analytics |
| `/analytics/staff` | GET | Staff leaderboard |
| `/analytics/customers` | GET | Customer analytics |
| `/analytics/training-roi` | GET | Training ROI |
| `/analytics/attrition` | GET | Attrition risk |
| `/analytics/compare` | GET | Location comparison |
| `/analytics/soulskin` | GET | SOULSKIN analytics |
| `/analytics/skill-gap` | GET | Skill gap forecast |
| `/analytics/forecast` | GET | Revenue forecast |

## SOULSKIN
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/soulskin/archetypes` | GET | List archetypes |
| `/soulskin/sessions` | POST | Start soul reading |
| `/soulskin/sessions/{id}/generate` | POST | Generate reading |
| `/soulskin/journal/{id}` | GET | Soul journal |

## Personalisation
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/homecare/generate` | POST | Generate homecare plan |
| `/journey/generate/{id}` | POST | Generate beauty journey |
| `/twin/{id}/simulate` | POST | Simulate future state |
| `/mirror` | POST | AR try-on session |
| `/climate/?city={city}` | GET | Climate recommendations |
| `/mood` | POST | Record mood detection |

## Trends
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/trends` | GET | List trend signals |
| `/trends/{id}` | GET | Trend details |

## AI Agents (63 Total)
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/agents/registry` | GET | List all agents |
| `/agents/{track}` | GET | Agents by track (1-6) |
| `/agents/ps/{ps_code}` | GET/POST | Execute specific problem agent |

---

# Testing Execution Checklist

## Pre-requisites
- [ ] Backend server running (`uvicorn app.main:app`)
- [ ] Database migrated and seeded with test data
- [ ] Frontend running (`npm run dev`)
- [ ] Test accounts created for all 6 roles:
  - [ ] Super Admin
  - [ ] Regional Manager
  - [ ] Franchise Owner
  - [ ] Salon Manager
  - [ ] Stylist
  - [ ] Customer

## Track-by-Track Summary

| Track | Problems | Status | Key Systems |
|-------|----------|--------|-------------|
| 1: Standardisation | PS-01.01 to PS-01.10 | ✅ All 10 | SOPs, Sessions, Quality, Benchmarking |
| 2: Staff Dependency | PS-02.01 to PS-02.10 | ✅ All 10 | Skills, Training, Scheduling, Attrition |
| 3: Personalisation | PS-03.01 to PS-03.10 | ✅ All 10 | Beauty Passport, SOULSKIN, Journey, Climate |
| 4: Trend Prediction | PS-04.01 to PS-04.10 | ✅ All 10 | Trends, Forecasting, Social Intelligence |
| 5: Customer Experience | PS-05.01 to PS-05.10 | ✅ All 10 | Queue, Mood, Feedback, Notifications |
| 6: Business Intelligence | PS-06.01 to PS-06.10 | ✅ All 10 | Analytics, LTV, Skill Gap, Forecasting |

**Total: 60/60 Problem Statements Implemented**

---

## Sign-Off

| Track | Tested By | Date | Result |
|-------|-----------|------|--------|
| Track 1: Standardisation | | | |
| Track 2: Staff Dependency | | | |
| Track 3: Personalisation | | | |
| Track 4: Trend Prediction | | | |
| Track 5: Customer Experience | | | |
| Track 6: Business Intelligence | | | |

**Overall Status:** _______________
**Tested By:** _______________
**Date:** _______________

---

*End of Testing Document | 60 Problem Statements | AURA Platform | Naturals BeautyTech Hackathon 2026*
