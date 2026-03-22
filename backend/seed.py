"""AURA Seed Data — Demo data for all 6 roles, 5 locations, 12 services, bookings, SOULSKIN sessions."""
import asyncio
from datetime import datetime, timedelta, timezone, date
from app.database import engine, async_session_factory, Base
from app.models import *
from app.utils.security import hash_password
from app.utils.helpers import generate_booking_number

PASSWORD = hash_password("Aura@2026")


async def seed():
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        # ═══ USERS ═══
        users_data = [
            {"email": "super@aura.in", "role": UserRole.SUPER_ADMIN, "first_name": "Rajesh", "last_name": "Kumar"},
            {"email": "regional@aura.in", "role": UserRole.REGIONAL_MANAGER, "first_name": "Lakshmi", "last_name": "Nair"},
            {"email": "owner@aura.in", "role": UserRole.FRANCHISE_OWNER, "first_name": "Arun", "last_name": "Venkatesh"},
            {"email": "manager@aura.in", "role": UserRole.SALON_MANAGER, "first_name": "Deepa", "last_name": "Ramesh"},
            {"email": "stylist@aura.in", "role": UserRole.STYLIST, "first_name": "Meena", "last_name": "Sundaram"},
            {"email": "customer@aura.in", "role": UserRole.CUSTOMER, "first_name": "Priya", "last_name": "Sharma"},
            {"email": "customer2@aura.in", "role": UserRole.CUSTOMER, "first_name": "Ananya", "last_name": "Iyer"},
            {"email": "customer3@aura.in", "role": UserRole.CUSTOMER, "first_name": "Kavitha", "last_name": "Rajan"},
        ]

        users = []
        for u in users_data:
            user = User(
                email=u["email"], phone=f"+91{hash(u['email']) % 9000000000 + 1000000000}",
                password_hash=PASSWORD, role=u["role"],
                first_name=u["first_name"], last_name=u["last_name"],
                is_active=True, is_verified=True,
            )
            db.add(user)
            users.append(user)
        await db.flush()

        super_admin, regional, owner, manager_user, stylist_user, cust1, cust2, cust3 = users

        # ═══ LOCATIONS ═══
        locations_data = [
            {"name": "Naturals Anna Nagar", "code": "NAT-TN-001", "city": "Chennai", "state": "Tamil Nadu", "region": "South India",
             "address": "123 Anna Nagar 2nd Street, Chennai 600040", "seating_capacity": 12, "latitude": 13.0827, "longitude": 80.2707},
            {"name": "Naturals T.Nagar", "code": "NAT-TN-002", "city": "Chennai", "state": "Tamil Nadu", "region": "South India",
             "address": "45 Usman Road, T.Nagar, Chennai 600017", "seating_capacity": 8},
            {"name": "Naturals Koramangala", "code": "NAT-KA-001", "city": "Bangalore", "state": "Karnataka", "region": "South India",
             "address": "78 5th Block, Koramangala, Bangalore 560095", "seating_capacity": 10},
            {"name": "Naturals Bandra", "code": "NAT-MH-001", "city": "Mumbai", "state": "Maharashtra", "region": "West India",
             "address": "23 Hill Road, Bandra West, Mumbai 400050", "seating_capacity": 15},
            {"name": "Naturals CP", "code": "NAT-DL-001", "city": "Delhi", "state": "Delhi", "region": "North India",
             "address": "Block A, Connaught Place, New Delhi 110001", "seating_capacity": 10},
        ]

        locs = []
        for ld in locations_data:
            loc = Location(
                **ld, franchise_owner_id=owner.id, manager_id=manager_user.id,
                is_active=True, soulskin_enabled=True, smart_mirror_enabled=True,
                monthly_revenue_target=500000,
                operating_hours={"mon": {"open": "09:00", "close": "20:00"}, "tue": {"open": "09:00", "close": "20:00"},
                                 "wed": {"open": "09:00", "close": "20:00"}, "thu": {"open": "09:00", "close": "20:00"},
                                 "fri": {"open": "09:00", "close": "20:00"}, "sat": {"open": "09:00", "close": "21:00"},
                                 "sun": {"open": "10:00", "close": "19:00"}},
            )
            db.add(loc)
            locs.append(loc)
        await db.flush()

        anna_nagar = locs[0]

        # ═══ STAFF PROFILES ═══
        stylist_profile = StaffProfile(
            user_id=stylist_user.id, location_id=anna_nagar.id, employee_id="NAT-EMP-001",
            designation="Senior Stylist", specializations=["hair_color", "bridal", "keratin"],
            skill_level=SkillLevel.L2, years_experience=5.0, bio="Award-winning colorist with SOULSKIN certification.",
            is_available=True, soulskin_certified=True, current_rating=4.7, total_services_done=1247,
            total_revenue_generated=3750000, languages_spoken=["english", "tamil", "hindi"],
            attrition_risk_score=0.15, attrition_risk_label=AttritionRisk.LOW,
        )
        db.add(stylist_profile)

        manager_profile = StaffProfile(
            user_id=manager_user.id, location_id=anna_nagar.id, employee_id="NAT-EMP-002",
            designation="Salon Manager", skill_level=SkillLevel.L3, years_experience=8.0,
            is_available=True, soulskin_certified=True, current_rating=4.9,
        )
        db.add(manager_profile)
        await db.flush()

        # ═══ CUSTOMER PROFILES (Beauty Passports) ═══
        cust_profiles = []
        customers_data = [
            {"user_id": cust1.id, "beauty_score": 78, "hair_type": "wavy", "hair_texture": "medium", "hair_porosity": "high",
             "hair_density": "thick", "scalp_condition": "normal", "hair_damage_level": 3, "current_hair_color": "dark_brown",
             "skin_type": "combination", "skin_tone": "medium", "undertone": "warm", "primary_skin_concerns": ["pigmentation", "dullness"],
             "city": "Chennai", "dominant_archetype": "bloom", "total_visits": 24, "lifetime_value": 48000,
             "known_allergies": ["PPD"], "stress_level": "medium", "diet_type": "vegetarian"},
            {"user_id": cust2.id, "beauty_score": 65, "hair_type": "straight", "hair_texture": "fine",
             "skin_type": "oily", "skin_tone": "fair", "undertone": "cool",
             "city": "Chennai", "dominant_archetype": "storm", "total_visits": 8, "lifetime_value": 12000},
            {"user_id": cust3.id, "beauty_score": 82, "hair_type": "curly", "hair_texture": "coarse",
             "skin_type": "dry", "skin_tone": "dusky", "undertone": "warm",
             "city": "Chennai", "dominant_archetype": "phoenix", "total_visits": 15, "lifetime_value": 32000},
        ]

        for cd in customers_data:
            cp = CustomerProfile(preferred_location_id=anna_nagar.id, preferred_stylist_id=stylist_profile.id,
                                 passport_completeness=75, **cd)
            db.add(cp)
            cust_profiles.append(cp)
        await db.flush()

        # ═══ SERVICES ═══
        services_data = [
            {"name": "Hair Cut", "category": "hair", "duration_minutes": 30, "base_price": 500, "skill_required": SkillLevel.L1},
            {"name": "Hair Color", "category": "hair", "duration_minutes": 90, "base_price": 2500, "is_chemical": True, "skill_required": SkillLevel.L2},
            {"name": "Balayage", "category": "hair", "duration_minutes": 120, "base_price": 5000, "is_chemical": True, "skill_required": SkillLevel.L2, "tags": ["trending", "premium"]},
            {"name": "Keratin Treatment", "category": "hair", "duration_minutes": 150, "base_price": 6000, "is_chemical": True, "skill_required": SkillLevel.L2, "tags": ["premium"]},
            {"name": "Bridal Makeup", "category": "makeup", "duration_minutes": 120, "base_price": 15000, "skill_required": SkillLevel.L3, "tags": ["bridal", "premium"]},
            {"name": "Deep Cleansing Facial", "category": "skin", "duration_minutes": 60, "base_price": 1500, "skill_required": SkillLevel.L1},
            {"name": "Scalp Treatment", "category": "hair", "duration_minutes": 45, "base_price": 1200, "skill_required": SkillLevel.L1},
            {"name": "Manicure", "category": "nail", "duration_minutes": 30, "base_price": 600, "skill_required": SkillLevel.L1},
            {"name": "Pedicure", "category": "nail", "duration_minutes": 45, "base_price": 800, "skill_required": SkillLevel.L1},
            {"name": "Eyebrow Threading", "category": "hair", "duration_minutes": 15, "base_price": 100, "skill_required": SkillLevel.L1},
            {"name": "Head Massage", "category": "wellness", "duration_minutes": 30, "base_price": 500, "skill_required": SkillLevel.L1},
            {"name": "Glass Skin Facial", "category": "skin", "duration_minutes": 75, "base_price": 3500, "skill_required": SkillLevel.L2, "tags": ["trending"], "ar_preview_available": True},
        ]

        svc_list = []
        for sd in services_data:
            svc = Service(short_description=f"Premium {sd['name']} service", **sd)
            db.add(svc)
            svc_list.append(svc)
        await db.flush()

        # ═══ SOPs (Hair Color & Balayage detailed) ═══
        hair_color_sop = SOP(
            service_id=svc_list[1].id, title="Hair Color SOP", version="1.0",
            total_duration_minutes=90, chemicals_involved=True,
            chemical_ratios={"developer": 1, "color_cream": 1.5},
            products_required=["developer", "color_cream", "gloves", "foil", "toner"],
            steps=[
                {"step_number": 1, "title": {"en": "Consultation", "ta": "ஆலோசனை"}, "instructions": {"en": "Assess hair condition, check allergy history, discuss desired outcome."}, "duration_minutes": 10, "critical": True, "warning": "Check allergy profile before proceeding", "timer_required": False},
                {"step_number": 2, "title": {"en": "Strand Test", "ta": "நிலை சோதனை"}, "instructions": {"en": "Perform strand test on small section. Wait for result."}, "duration_minutes": 5, "critical": True, "timer_required": True, "timer_seconds": 300},
                {"step_number": 3, "title": {"en": "Mix Color", "ta": "கலர் கலவை"}, "instructions": {"en": "Mix developer and color cream at 1:1.5 ratio."}, "duration_minutes": 5, "products_required": ["developer", "color_cream"]},
                {"step_number": 4, "title": {"en": "Section & Apply", "ta": "பிரிவு & பூச்சு"}, "instructions": {"en": "Section hair into quadrants. Apply from roots to mid-lengths."}, "duration_minutes": 25},
                {"step_number": 5, "title": {"en": "Processing Time", "ta": "செயலாக்க நேரம்"}, "instructions": {"en": "Allow color to develop. Check every 10 minutes."}, "duration_minutes": 30, "timer_required": True, "timer_seconds": 1800, "critical": True},
                {"step_number": 6, "title": {"en": "Rinse & Tone", "ta": "கழுவி & டோன்"}, "instructions": {"en": "Rinse thoroughly. Apply toner if needed."}, "duration_minutes": 10, "products_required": ["toner"]},
                {"step_number": 7, "title": {"en": "Style & Finish", "ta": "பாணி & முடிவு"}, "instructions": {"en": "Blow dry and style. Showcase final result."}, "duration_minutes": 5},
            ],
            soulskin_overlays={
                "phoenix": {"overall_note": "Bold and decisive — client wants transformation speed. Be confident in your technique."},
                "storm": {"overall_note": "Slow and grounding — take extra time on scalp massage at rinse. Minimal conversation."},
                "moon": {"overall_note": "Silent or soft music preferred. Gentle approach. Do not rush."},
                "bloom": {"overall_note": "Celebrate with client — this is a happy occasion. Share excitement about the colour."},
                "river": {"overall_note": "Transition energy — acknowledge the change they're going through."},
            },
            created_by=manager_user.id,
        )
        db.add(hair_color_sop)
        await db.flush()

        # Link SOP to service
        svc_list[1].sop_id = hair_color_sop.id

        # ═══ TREND SIGNALS ═══
        trends = [
            TrendSignal(trend_name="Cherry Mocha Hair", slug="cherry-mocha-hair", description="Rich cherry-brown with warm mocha undertones",
                       service_category="hair", applicable_cities=["Chennai", "Bangalore", "Mumbai"],
                       overall_signal_strength=8.5, social_media_score=9.0, search_trend_score=7.5,
                       booking_demand_score=8.0, trajectory=TrendTrajectory.GROWING, longevity_label=TrendLongevity.TREND,
                       confidence_level=0.85, is_active=True, celebrity_trigger="Deepika Padukone debuted cherry mocha highlights"),
            TrendSignal(trend_name="Glass Skin Facial", slug="glass-skin-facial", description="K-beauty inspired skin treatment for glass-like luminous finish",
                       service_category="skin", applicable_cities=["Chennai", "Bangalore", "Mumbai", "Delhi"],
                       overall_signal_strength=9.2, social_media_score=9.5, search_trend_score=9.0,
                       trajectory=TrendTrajectory.PEAK, longevity_label=TrendLongevity.MOVEMENT,
                       confidence_level=0.92, is_active=True, climate_correlation={"season": "monsoon", "notes": "Glass skin surges in humidity"}),
            TrendSignal(trend_name="Curtain Bangs", slug="curtain-bangs", description="Soft, face-framing bangs with center part",
                       service_category="hair", applicable_cities=["Chennai", "Bangalore"],
                       overall_signal_strength=7.8, trajectory=TrendTrajectory.GROWING, longevity_label=TrendLongevity.TREND,
                       confidence_level=0.78, is_active=True),
        ]
        for t in trends:
            db.add(t)

        # ═══ CLIMATE RECOMMENDATIONS ═══
        climates = [
            ClimateRecommendation(city="Chennai", date_for=date.today(), temperature_celsius=34.0, humidity_pct=78.0,
                                  uv_index=9.2, aqi=142, weather_condition="sunny", is_alert=True,
                                  hair_recommendations={"alerts": ["High humidity — avoid keratin services"], "home_care_tip": "Apply anti-frizz serum before stepping out"},
                                  skin_recommendations={"alerts": ["UV 9.2 — recommend SPF 50"], "home_care_tip": "Double SPF. Reapply every 2 hours."},
                                  general_advisory="High UV and humidity day. Recommend protective treatments."),
            ClimateRecommendation(city="Bangalore", date_for=date.today(), temperature_celsius=28.0, humidity_pct=55.0,
                                  uv_index=6.5, aqi=85, weather_condition="cloudy",
                                  hair_recommendations={"alerts": [], "home_care_tip": "Good hair day — moderate conditions"},
                                  skin_recommendations={"alerts": [], "home_care_tip": "Light moisturizer sufficient"},
                                  general_advisory="Moderate conditions. All services suitable."),
        ]
        for c in climates:
            db.add(c)

        # ═══ SOULSKIN DEMO SESSIONS ═══
        soulskin_sessions = [
            SoulskinSession(
                customer_id=cust_profiles[0].id, stylist_id=stylist_profile.id, location_id=anna_nagar.id,
                question_1_song="Kesariya", question_2_colour="Gold", question_3_word="Free",
                archetype="bloom", soul_reading="You are in full bloom. Something new is opening inside you — a celebration, a beginning, a joy that has been waiting.",
                archetype_reason="Gold and freedom — the energy of Bloom. You're ready to celebrate who you're becoming.",
                service_protocol={"primary_treatment": "Balayage with honey highlights", "why_this_treatment": "Bloom needs warmth and light"},
                stylist_script={"opening": "Gold — what a beautiful choice. Let's make that energy visible.", "closing": "Look at that glow. That's the Bloom in you."},
                session_completed=True, customer_reaction="loved_it",
            ),
            SoulskinSession(
                customer_id=cust_profiles[1].id, stylist_id=stylist_profile.id, location_id=anna_nagar.id,
                question_1_song="Numb", question_2_colour="Grey", question_3_word="Peace",
                archetype="storm", soul_reading="You carry weight today. Tension, change, or turbulence. You need grounding, not stimulation.",
                archetype_reason="Grey and peace — the Storm archetype seeks calm after chaos.",
                stylist_script={"opening": "Let's make this chair your safe space today.", "closing": "You came in carrying a storm. You're leaving lighter."},
                session_completed=True, customer_reaction="loved_it",
            ),
            SoulskinSession(
                customer_id=cust_profiles[2].id, stylist_id=stylist_profile.id, location_id=anna_nagar.id,
                question_1_song="Phir Le Aya Dil", question_2_colour="Red", question_3_word="Bold",
                archetype="phoenix", soul_reading="You are standing at the edge of something ending. You are not afraid of the fire. You are ready to rise.",
                archetype_reason="Red and bold — pure Phoenix. Transformation through fire.",
                stylist_script={"opening": "Red. Bold. You know exactly what you want.", "closing": "That's not just colour. That's courage made visible."},
                session_completed=True, customer_reaction="loved_it",
            ),
        ]
        for ss in soulskin_sessions:
            db.add(ss)
        await db.flush()

        # ═══ BOOKINGS (sample) ═══
        now = datetime.now(timezone.utc)
        for i in range(20):
            days_ago = i * 4
            booking = Booking(
                booking_number=generate_booking_number(),
                customer_id=cust_profiles[i % 3].id,
                location_id=anna_nagar.id,
                stylist_id=stylist_profile.id,
                service_id=svc_list[i % len(svc_list)].id,
                status=BookingStatus.COMPLETED if i > 2 else BookingStatus.CONFIRMED,
                scheduled_at=now - timedelta(days=days_ago),
                base_price=float(svc_list[i % len(svc_list)].base_price),
                final_price=float(svc_list[i % len(svc_list)].base_price),
                source=BookingSource.APP,
                payment_status=PaymentStatus.PAID if i > 2 else PaymentStatus.PENDING,
                payment_method=PaymentMethod.UPI if i % 2 == 0 else PaymentMethod.CARD,
                soulskin_session_id=soulskin_sessions[i % 3].id if i < 6 else None,
            )
            db.add(booking)
        await db.flush()

        # ═══ FEEDBACK (sample) ═══
        for i in range(10):
            fb = CustomerFeedback(
                customer_id=cust_profiles[i % 3].id, stylist_id=stylist_profile.id,
                location_id=anna_nagar.id, service_id=svc_list[i % len(svc_list)].id,
                overall_rating=4 + (i % 2), service_rating=4 + (i % 2), stylist_rating=5,
                soulskin_experience_rating=5 if i < 5 else None,
                would_recommend=True, comment=f"Amazing experience! Visit #{i+1}",
                sentiment=Sentiment.POSITIVE, sentiment_score=0.92,
                source=FeedbackSource.APP, is_verified=True,
            )
            db.add(fb)

        # ═══ TRAINING RECORDS ═══
        trainings = [
            TrainingRecord(staff_id=stylist_profile.id, training_name="Advanced Hair Color Masterclass",
                          training_type=TrainingType.CLASSROOM, service_category="hair",
                          provider="Naturals Academy", hours_completed=16, cost_to_company=5000,
                          passed=True, score=92, includes_soulskin=False,
                          revenue_before=280000, revenue_after=350000, quality_score_before=78, quality_score_after=88),
            TrainingRecord(staff_id=stylist_profile.id, training_name="SOULSKIN Emotional Intelligence Certification",
                          training_type=TrainingType.CLASSROOM, service_category="emotional_intelligence",
                          provider="AURA Academy", hours_completed=8, cost_to_company=3000,
                          passed=True, score=95, includes_soulskin=True,
                          revenue_before=350000, revenue_after=420000, quality_score_before=88, quality_score_after=93),
            TrainingRecord(staff_id=stylist_profile.id, training_name="Bridal Makeup Intensive",
                          training_type=TrainingType.EXTERNAL_WORKSHOP, service_category="makeup",
                          provider="Bobbi Brown India", hours_completed=24, cost_to_company=15000,
                          passed=True, score=88),
        ]
        for tr in trainings:
            db.add(tr)

        # ═══ SERVICE SESSIONS ═══
        # Get the first few completed bookings for sessions
        from sqlalchemy import select
        booking_result = await db.execute(
            select(Booking).where(Booking.status == BookingStatus.COMPLETED).limit(5)
        )
        completed_bookings = booking_result.scalars().all()

        sessions_created = []
        for i, bk in enumerate(completed_bookings):
            session = ServiceSession(
                booking_id=bk.id, sop_id=hair_color_sop.id if i < 2 else None,
                sop_version="1.0", status=SessionStatus.COMPLETED,
                steps_total=7, current_step=7,
                steps_completed=[1, 2, 3, 4, 5, 6, 7],
                started_at=bk.scheduled_at, completed_at=bk.scheduled_at + timedelta(hours=1, minutes=30),
                quality_score=85 + (i * 2), sop_compliance_pct=90 + i,
                soulskin_active=i < 3, archetype_applied=["bloom", "storm", "phoenix"][i % 3] if i < 3 else None,
                products_used={"developer": "30vol", "color_cream": "6.1 dark ash blonde"},
            )
            db.add(session)
            sessions_created.append(session)
        await db.flush()

        # ═══ QUALITY ASSESSMENTS ═══
        for i, bk in enumerate(completed_bookings):
            sop_score = 85 + (i * 3)
            timing_score = 80 + (i * 4)
            cust_rating = 4 + (1 if i % 2 == 0 else 0)
            overall = sop_score * 0.30 + timing_score * 0.20 + (cust_rating * 20) * 0.50
            qa = QualityAssessment(
                booking_id=bk.id, session_id=sessions_created[i].id if i < len(sessions_created) else None,
                stylist_id=stylist_profile.id, location_id=anna_nagar.id,
                service_id=bk.service_id,
                sop_compliance_score=sop_score, timing_score=timing_score,
                customer_rating=cust_rating, overall_score=round(overall, 2),
                soulskin_alignment_score=88.0 if i < 3 else None,
                is_flagged=overall < 55,
                ai_feedback=f"Good technique. SOP compliance at {sop_score}%. Customer satisfaction high.",
                reviewed_by_manager=i < 3,
            )
            db.add(qa)

        # ═══ SKILL ASSESSMENTS ═══
        skill_assessments = [
            SkillAssessment(
                staff_id=stylist_profile.id, assessed_by=manager_user.id,
                assessment_type=AssessmentType.MANAGER, service_category="hair",
                skill_area="color_technique", current_level=SkillLevel.L2, score=88.0,
                rubric_scores={"technique": 90, "speed": 85, "consultation": 92, "product_knowledge": 88, "customer_handling": 90},
                l2_gap_items=[], l3_gap_items=["Advanced balayage certification", "50+ keratin treatments"],
                recommended_training=["Advanced Balayage Workshop", "Keratin Specialist Program"],
                soulskin_certified=True,
            ),
            SkillAssessment(
                staff_id=stylist_profile.id, assessed_by=manager_user.id,
                assessment_type=AssessmentType.AI, service_category="skin",
                skill_area="facial_technique", current_level=SkillLevel.L1, score=72.0,
                rubric_scores={"technique": 70, "speed": 75, "consultation": 78, "product_knowledge": 68},
                recommended_training=["Advanced Facial Techniques", "Skin Analysis Certification"],
            ),
        ]
        for sa in skill_assessments:
            db.add(sa)

        # ═══ MOOD DETECTIONS ═══
        moods = [
            MoodDetection(customer_id=cust_profiles[0].id, detected_emotion="happy", emotion_confidence=0.87,
                         energy_level="high", recommended_archetype="bloom",
                         service_adjustment="Customer in great mood — celebrate with vibrant styles",
                         consent_given=True, captured_at=now - timedelta(days=5)),
            MoodDetection(customer_id=cust_profiles[1].id, detected_emotion="stressed", emotion_confidence=0.72,
                         energy_level="low", secondary_emotion="tired",
                         recommended_archetype="storm",
                         service_adjustment="Consider extra scalp massage. Gentle approach recommended.",
                         do_not_recommend=["loud_environment", "chemical_treatments"],
                         consent_given=True, captured_at=now - timedelta(days=10)),
            MoodDetection(customer_id=cust_profiles[2].id, detected_emotion="excited", emotion_confidence=0.91,
                         energy_level="high", recommended_archetype="phoenix",
                         service_adjustment="Customer excited for transformation — bold choices welcome",
                         consent_given=True, captured_at=now - timedelta(days=3)),
        ]
        for m in moods:
            db.add(m)

        # ═══ DIGITAL BEAUTY TWINS ═══
        twins = [
            DigitalBeautyTwin(
                customer_id=cust_profiles[0].id, consent_given=True, consent_date=now - timedelta(days=30),
                is_active=True, skin_timeline=[
                    {"date": (now - timedelta(days=60)).strftime("%Y-%m-%d"), "skin_score": 68, "acne_level": 2, "hydration": "normal"},
                    {"date": (now - timedelta(days=30)).strftime("%Y-%m-%d"), "skin_score": 72, "acne_level": 1, "hydration": "normal"},
                    {"date": now.strftime("%Y-%m-%d"), "skin_score": 78, "acne_level": 1, "hydration": "well-hydrated"},
                ],
                future_simulations=[{
                    "simulation_id": "sim_001", "weeks_ahead": 12,
                    "predicted_state": {"skin_score": 85, "acne_level": 0, "pigmentation_level": 1},
                    "treatment_plan_assumed": ["monthly_facial", "daily_spf", "weekly_mask"],
                }],
                hairstyle_tryons=[
                    {"tryon_id": "tryon_001", "style_name": "Bob with curtain bangs", "color_applied": "warm copper", "customer_reacted": "loved"},
                    {"tryon_id": "tryon_002", "style_name": "Layered waves", "color_applied": "honey highlights", "customer_reacted": "saved"},
                ],
            ),
            DigitalBeautyTwin(
                customer_id=cust_profiles[2].id, consent_given=True, consent_date=now - timedelta(days=15),
                is_active=True, skin_timeline=[
                    {"date": now.strftime("%Y-%m-%d"), "skin_score": 82, "acne_level": 0, "hydration": "well-hydrated"},
                ],
            ),
        ]
        for tw in twins:
            db.add(tw)

        # ═══ AR MIRROR SESSIONS ═══
        ar_sessions = [
            ARMirrorSession(
                customer_id=cust_profiles[0].id, location_id=anna_nagar.id,
                initiated_by=MirrorInitiator.CUSTOMER, session_type=MirrorSessionType.HAIR_COLOR,
                tryons=[
                    {"sequence": 1, "type": "hair_color", "value": "warm_copper_balayage", "duration_seconds": 45, "customer_reaction": "positive", "saved": True},
                    {"sequence": 2, "type": "hair_color", "value": "ash_blonde", "duration_seconds": 30, "customer_reaction": "neutral", "saved": False},
                ],
                final_selection={"type": "hair_color", "value": "warm_copper_balayage"},
                climate_recommendations={"uv_index": 9.2, "recommendation": "UV-protective gloss finish recommended"},
                session_duration_secs=180, booking_created_after=True,
            ),
            ARMirrorSession(
                customer_id=cust_profiles[0].id, location_id=anna_nagar.id,
                initiated_by=MirrorInitiator.STYLIST, session_type=MirrorSessionType.HAIRSTYLE,
                tryons=[
                    {"sequence": 1, "type": "hairstyle", "value": "curtain_bangs", "duration_seconds": 60, "customer_reaction": "positive", "saved": True},
                ],
                session_duration_secs=120,
            ),
        ]
        for ar in ar_sessions:
            db.add(ar)

        # ═══ BEAUTY JOURNEY PLANS ═══
        journey = BeautyJourneyPlan(
            customer_id=cust_profiles[0].id, plan_duration_weeks=12,
            primary_goal="Reduce hair damage and improve skin radiance",
            generated_at=now - timedelta(days=14),
            milestones=[
                {"week": 1, "milestone": "Start recovery phase", "salon_visit": {"recommended_service": "Deep Protein Treatment", "estimated_cost": 1500},
                 "home_care": ["Apply coconut oil mask twice weekly", "Avoid heat styling"], "expected_outcome": "Reduced breakage by 20%"},
                {"week": 4, "milestone": "Deep treatment phase", "salon_visit": {"recommended_service": "Scalp Treatment + Facial", "estimated_cost": 2700},
                 "home_care": ["Weekly protein mask", "Daily SPF"], "expected_outcome": "Visible texture improvement"},
                {"week": 8, "milestone": "Strengthening phase", "salon_visit": {"recommended_service": "Keratin + Glass Skin Facial", "estimated_cost": 9500},
                 "home_care": ["Bond repair shampoo", "Weekly exfoliation"], "expected_outcome": "Significant damage reduction"},
                {"week": 12, "milestone": "Maintenance & celebrate", "salon_visit": {"recommended_service": "Balayage + Maintenance Facial", "estimated_cost": 6500},
                 "home_care": ["Continue balanced routine"], "expected_outcome": "Goal achieved: 70% damage reduction, natural shine restored"},
            ],
            expected_outcomes={"week_4": "Visible reduction in hair fall", "week_8": "Smoother texture, balanced scalp", "week_12": "Target achieved"},
            estimated_total_cost=20200, ai_notes="Personalized 12-week journey for damage repair and skin radiance.",
        )
        db.add(journey)

        # ═══ HOMECARE PLANS ═══
        homecare = HomecarePlan(
            customer_id=cust_profiles[0].id, soulskin_archetype="bloom",
            generated_at=now - timedelta(days=7), plan_duration_weeks=4,
            hair_routine={"daily": "Sulfate-free shampoo, leave-in conditioner", "weekly": "Deep conditioning mask with argan oil", "monthly": "Protein treatment at home"},
            skin_routine={"daily": "Cleanser + Vitamin C serum + SPF 50", "weekly": "Gentle exfoliation + hydrating mask", "monthly": "Professional facial recommended"},
            climate_adjustments={"high_uv": "Reapply SPF every 2 hours", "high_humidity": "Use anti-frizz serum before going out"},
            archetype_rituals={"bloom": "Begin each morning with gratitude journaling + gentle scalp massage to activate growth energy"},
            product_recommendations=[
                {"product_name": "Olaplex No. 3", "usage": "Weekly", "reason": "Bond repair for damaged hair", "estimated_price": 2800},
                {"product_name": "La Roche-Posay SPF 50", "usage": "Daily", "reason": "UV protection", "estimated_price": 1200},
            ],
            dos=["Stay hydrated (8+ glasses daily)", "Use silk pillowcase", "Apply hair oil 30min before wash"],
            donts=["Avoid heat styling without protectant", "No chemical treatments for 2 weeks", "Don't skip SPF even on cloudy days"],
            next_visit_recommendation="Deep Protein Treatment in 3 weeks",
            ai_notes="Bloom archetype homecare — nurturing routine with self-celebration rituals.",
        )
        db.add(homecare)

        # ═══ NOTIFICATIONS ═══
        notifications = [
            Notification(user_id=cust1.id, notification_type="booking_reminder", title="Upcoming Appointment",
                        body="Your appointment at Naturals Anna Nagar is tomorrow at 10:00 AM",
                        channel=NotificationChannel.IN_APP, priority=NotificationPriority.NORMAL,
                        sent_at=now - timedelta(hours=2)),
            Notification(user_id=cust1.id, notification_type="journey_milestone", title="Journey Milestone",
                        body="This week: recommended Deep Protein Treatment. Book now!",
                        channel=NotificationChannel.IN_APP, priority=NotificationPriority.NORMAL,
                        sent_at=now - timedelta(days=1)),
            Notification(user_id=stylist_user.id, notification_type="quality_flag", title="Quality Alert",
                        body="Session quality score below threshold (52%). Review required.",
                        channel=NotificationChannel.IN_APP, priority=NotificationPriority.HIGH,
                        sent_at=now - timedelta(days=2)),
            Notification(user_id=manager_user.id, notification_type="trend_alert", title="New Trend Detected",
                        body="Glass Skin Facial is trending in Chennai. Consider increasing inventory.",
                        channel=NotificationChannel.IN_APP, priority=NotificationPriority.NORMAL,
                        sent_at=now - timedelta(days=3)),
            Notification(user_id=manager_user.id, notification_type="climate_alert", title="High UV Alert",
                        body="UV Index 9.2 in Chennai today. Recommend UV-protective services to all customers.",
                        channel=NotificationChannel.IN_APP, priority=NotificationPriority.HIGH, is_read=True,
                        sent_at=now - timedelta(hours=6)),
            Notification(user_id=manager_user.id, notification_type="attrition_risk", title="Staff Attrition Risk",
                        body="1 staff member has HIGH attrition risk. Review immediately.",
                        channel=NotificationChannel.IN_APP, priority=NotificationPriority.URGENT,
                        sent_at=now - timedelta(days=1)),
        ]
        for n in notifications:
            db.add(n)

        # ═══ SMART QUEUE ENTRIES ═══
        queue_entries = [
            SmartQueueEntry(
                location_id=anna_nagar.id, customer_name="Walk-in Ravi", customer_phone="+919876543210",
                service_id=svc_list[0].id, status=QueueStatus.WAITING,
                position_in_queue=1, estimated_wait_mins=15,
                walk_in_source=WalkInSource.IN_PERSON, joined_queue_at=now - timedelta(minutes=20),
            ),
            SmartQueueEntry(
                location_id=anna_nagar.id, customer_name="Walk-in Sita", customer_phone="+919876543211",
                service_id=svc_list[5].id, status=QueueStatus.WAITING,
                position_in_queue=2, estimated_wait_mins=30,
                walk_in_source=WalkInSource.WHATSAPP, joined_queue_at=now - timedelta(minutes=10),
            ),
            SmartQueueEntry(
                location_id=anna_nagar.id, customer_id=cust_profiles[0].id,
                customer_name="Priya Sharma", customer_phone="+919876543212",
                service_id=svc_list[1].id, preferred_stylist_id=stylist_profile.id,
                status=QueueStatus.ASSIGNED, position_in_queue=3, estimated_wait_mins=45,
                walk_in_source=WalkInSource.APP_CHECKIN, joined_queue_at=now - timedelta(minutes=5),
                assigned_at=now - timedelta(minutes=2),
            ),
        ]
        for qe in queue_entries:
            db.add(qe)

        # ═══ ADDITIONAL CLIMATE DATA (Mumbai, Delhi) ═══
        extra_climates = [
            ClimateRecommendation(city="Mumbai", date_for=date.today(), temperature_celsius=32.0, humidity_pct=82.0,
                                  uv_index=7.8, aqi=168, weather_condition="hazy", is_alert=False,
                                  hair_recommendations={"alerts": ["High humidity — anti-frizz products recommended"], "home_care_tip": "Use oil-based serum"},
                                  skin_recommendations={"alerts": ["AQI 168 — consider pollution protection"], "home_care_tip": "Double cleanse in the evening"},
                                  general_advisory="Humid with moderate pollution. Anti-frizz and cleansing focus."),
            ClimateRecommendation(city="Delhi", date_for=date.today(), temperature_celsius=38.0, humidity_pct=35.0,
                                  uv_index=10.5, aqi=245, weather_condition="sunny", is_alert=True,
                                  hair_recommendations={"alerts": ["Extreme UV — avoid outdoor chemical processing"], "home_care_tip": "Wear a hat and use UV spray"},
                                  skin_recommendations={"alerts": ["AQI 245 CRITICAL — pollution alert", "UV 10.5 — maximum protection needed"],
                                                        "home_care_tip": "SPF 50 mandatory. Antioxidant serum recommended."},
                                  general_advisory="CRITICAL: Extreme UV and hazardous AQI. Minimize outdoor exposure."),
        ]
        for ec in extra_climates:
            db.add(ec)

        await db.commit()
        print("✅ AURA seed data loaded successfully!")
        print(f"   📍 {len(locs)} locations")
        print(f"   👥 {len(users)} users (password: Aura@2026)")
        print(f"   💇 {len(svc_list)} services")
        print(f"   🔮 {len(soulskin_sessions)} SOULSKIN sessions")
        print(f"   📊 20 bookings, 10 feedback, 3 training records")
        print(f"   🌤️ Climate data for 4 cities")
        print(f"   📈 3 trend signals")
        print(f"   ⭐ {len(completed_bookings)} quality assessments + {len(sessions_created)} service sessions")
        print(f"   🧠 {len(moods)} mood detections + {len(twins)} digital twins")
        print(f"   🪞 {len(ar_sessions)} AR mirror sessions")
        print(f"   📋 1 beauty journey plan + 1 homecare plan")
        print(f"   🔔 {len(notifications)} notifications")
        print(f"   🚶 {len(queue_entries)} queue entries")
        print(f"   📝 {len(skill_assessments)} skill assessments")


if __name__ == "__main__":
    asyncio.run(seed())
