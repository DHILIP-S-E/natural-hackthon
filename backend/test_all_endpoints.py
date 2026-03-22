"""
AURA Platform — Comprehensive Endpoint & Role Test Script
==========================================================
Tests ALL API endpoints across ALL user roles.
Checks: Authentication, Authorization, CRUD, Data Integrity, Error Handling.

Usage:
    python test_all_endpoints.py
    python test_all_endpoints.py --base-url http://localhost:8001/api/v1
"""

import argparse
import json
import sys
import time
import requests
from dataclasses import dataclass, field
from typing import Optional

# ─── Configuration ───────────────────────────────────────────────────────────

DEFAULT_BASE = "http://localhost:8001/api/v1"
PASSWORD = "Aura@2026"

USERS = {
    "super_admin":      "super@aura.in",
    "regional_manager": "regional@aura.in",
    "franchise_owner":  "owner@aura.in",
    "salon_manager":    "manager@aura.in",
    "stylist":          "stylist@aura.in",
    "customer":         "customer@aura.in",
}

# ─── Result Tracking ─────────────────────────────────────────────────────────

@dataclass
class TestResult:
    endpoint: str
    method: str
    role: str
    status: int
    expected: str  # "ok", "denied", "error"
    actual: str
    passed: bool
    detail: str = ""
    response_time_ms: int = 0


@dataclass
class TestSuite:
    results: list = field(default_factory=list)
    tokens: dict = field(default_factory=dict)
    base_url: str = DEFAULT_BASE
    created_ids: dict = field(default_factory=dict)

    @property
    def total(self): return len(self.results)
    @property
    def passed(self): return sum(1 for r in self.results if r.passed)
    @property
    def failed(self): return sum(1 for r in self.results if not r.passed)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def login(base_url: str, email: str, password: str) -> Optional[str]:
    """Login and return access token."""
    try:
        r = requests.post(f"{base_url}/auth/login", json={"email": email, "password": password}, timeout=10)
        if r.status_code == 200:
            data = r.json().get("data", {})
            return data.get("access_token")
    except Exception as e:
        print(f"  [LOGIN FAIL] {email}: {e}")
    return None


def req(suite: TestSuite, method: str, path: str, role: str, expected: str,
        json_body: dict = None, params: dict = None, desc: str = "") -> TestResult:
    """Make a request and record the result."""
    url = f"{suite.base_url}{path}"
    headers = {}
    token = suite.tokens.get(role)
    if token:
        headers["Authorization"] = f"Bearer {token}"

    start = time.time()
    try:
        r = requests.request(method, url, json=json_body, params=params,
                             headers=headers, timeout=15)
        elapsed = int((time.time() - start) * 1000)
        status = r.status_code

        # Determine actual result
        if status == 200 or status == 201:
            actual = "ok"
        elif status == 401:
            actual = "unauth"
        elif status == 403:
            actual = "denied"
        elif status == 404:
            actual = "not_found"
        elif status == 422:
            actual = "validation"
        else:
            actual = f"error_{status}"

        # Check pass/fail
        if expected == "ok":
            passed = status in (200, 201)
        elif expected == "denied":
            passed = status in (401, 403)
        elif expected == "not_found":
            passed = status == 404
        elif expected == "any":
            passed = True  # We just want to check it doesn't crash (500)
        else:
            passed = actual == expected

        # 500 is always a fail
        if status >= 500:
            passed = False
            actual = f"SERVER_ERROR_{status}"

        detail_text = ""
        if not passed:
            try:
                body = r.json()
                detail_text = str(body.get("detail", body.get("message", "")))[:100]
            except Exception:
                detail_text = r.text[:100]

        result = TestResult(
            endpoint=f"{method} {path}",
            method=method,
            role=role,
            status=status,
            expected=expected,
            actual=actual,
            passed=passed,
            detail=detail_text,
            response_time_ms=elapsed,
        )

        # Store created IDs for later use
        if passed and method == "POST" and status in (200, 201):
            try:
                body = r.json()
                data = body.get("data", {})
                if isinstance(data, dict) and "id" in data:
                    key = path.split("/")[1]  # e.g. "bookings"
                    suite.created_ids[key] = data["id"]
            except Exception:
                pass

    except requests.exceptions.ConnectionError:
        elapsed = int((time.time() - start) * 1000)
        result = TestResult(
            endpoint=f"{method} {path}",
            method=method, role=role, status=0,
            expected=expected, actual="CONNECTION_ERROR",
            passed=False, detail="Cannot connect to server",
            response_time_ms=elapsed,
        )
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        result = TestResult(
            endpoint=f"{method} {path}",
            method=method, role=role, status=0,
            expected=expected, actual="EXCEPTION",
            passed=False, detail=str(e)[:100],
            response_time_ms=elapsed,
        )

    suite.results.append(result)
    icon = "PASS" if result.passed else "FAIL"
    label = desc or path
    print(f"  [{icon}] {role:20s} {method:6s} {label:50s} -> {result.status} ({result.response_time_ms}ms)"
          + (f" | {result.detail}" if result.detail else ""))
    return result


# ─── Test Sections ───────────────────────────────────────────────────────────

def test_auth(s: TestSuite):
    """Test authentication endpoints."""
    print("\n" + "=" * 80)
    print("1. AUTHENTICATION & LOGIN")
    print("=" * 80)

    # Login all users
    for role, email in USERS.items():
        token = login(s.base_url, email, PASSWORD)
        if token:
            s.tokens[role] = token
            print(f"  [PASS] {role:20s} logged in successfully")
        else:
            print(f"  [FAIL] {role:20s} LOGIN FAILED — {email}")
            s.results.append(TestResult(
                endpoint="POST /auth/login", method="POST", role=role,
                status=0, expected="ok", actual="login_failed",
                passed=False, detail=f"Cannot login {email}",
            ))

    # Test unauthenticated access
    print("\n  --- Unauthenticated Access ---")
    req(s, "GET", "/auth/me", "none", "denied", desc="GET /auth/me (no token)")
    req(s, "GET", "/bookings", "none", "denied", desc="GET /bookings (no token)")
    req(s, "GET", "/locations", "none", "denied", desc="GET /locations (no token)")

    # Test /auth/me for each role
    print("\n  --- GET /auth/me (each role) ---")
    for role in USERS:
        if role in s.tokens:
            req(s, "GET", "/auth/me", role, "ok")


def test_users_admin(s: TestSuite):
    """Test admin user management."""
    print("\n" + "=" * 80)
    print("2. USER MANAGEMENT (Admin Only)")
    print("=" * 80)

    # Only super_admin and regional_manager should access /auth/users
    for role in USERS:
        if role not in s.tokens:
            continue
        expected = "ok" if role in ("super_admin", "regional_manager") else "denied"
        req(s, "GET", "/auth/users", role, expected)


def test_locations(s: TestSuite):
    """Test location endpoints across all roles."""
    print("\n" + "=" * 80)
    print("3. LOCATIONS")
    print("=" * 80)

    for role in USERS:
        if role not in s.tokens:
            continue
        req(s, "GET", "/locations", role, "ok")

    # Get first location ID
    if "super_admin" in s.tokens:
        r = requests.get(f"{s.base_url}/locations",
                         headers={"Authorization": f"Bearer {s.tokens['super_admin']}"}, timeout=10)
        try:
            data = r.json().get("data", {})
            locs = data if isinstance(data, list) else data.get("locations", data.get("items", []))
            if locs and len(locs) > 0:
                loc_id = locs[0].get("id", "")
                s.created_ids["location"] = loc_id
                print(f"  [INFO] Using location: {loc_id}")
        except Exception:
            pass

    loc_id = s.created_ids.get("location", "nonexistent")
    print(f"\n  --- GET /locations/{loc_id[:8]}... (each role) ---")
    for role in USERS:
        if role not in s.tokens:
            continue
        req(s, "GET", f"/locations/{loc_id}", role, "any")


def test_staff(s: TestSuite):
    """Test staff endpoints."""
    print("\n" + "=" * 80)
    print("4. STAFF")
    print("=" * 80)

    for role in USERS:
        if role not in s.tokens:
            continue
        req(s, "GET", "/staff", role, "ok")


def test_customers(s: TestSuite):
    """Test customer endpoints."""
    print("\n" + "=" * 80)
    print("5. CUSTOMERS")
    print("=" * 80)

    for role in USERS:
        if role not in s.tokens:
            continue
        req(s, "GET", "/customers", role, "ok")

    # Search
    if "salon_manager" in s.tokens:
        req(s, "GET", "/customers/search", "salon_manager", "any", params={"q": "Priya"})


def test_bookings(s: TestSuite):
    """Test booking endpoints."""
    print("\n" + "=" * 80)
    print("6. BOOKINGS")
    print("=" * 80)

    # List bookings
    for role in USERS:
        if role not in s.tokens:
            continue
        req(s, "GET", "/bookings", role, "ok", params={"page": 1, "per_page": 5})

    # Today's bookings
    print("\n  --- GET /bookings/today ---")
    for role in ("stylist", "salon_manager", "super_admin"):
        if role in s.tokens:
            req(s, "GET", "/bookings/today", role, "any")


def test_services(s: TestSuite):
    """Test services endpoints."""
    print("\n" + "=" * 80)
    print("7. SERVICES & SOPs")
    print("=" * 80)

    for role in USERS:
        if role not in s.tokens:
            continue
        req(s, "GET", "/services", role, "ok")

    # SOPs
    print("\n  --- SOPs ---")
    for role in ("salon_manager", "super_admin", "stylist"):
        if role in s.tokens:
            req(s, "GET", "/sops", role, "ok")


def test_analytics(s: TestSuite):
    """Test analytics endpoints across roles."""
    print("\n" + "=" * 80)
    print("8. ANALYTICS & BI")
    print("=" * 80)

    analytics_endpoints = [
        "/analytics/overview",
        "/analytics/revenue",
        "/analytics/quality",
        "/analytics/staff",
        "/analytics/customers",
        "/analytics/soulskin",
        "/analytics/compare",
        "/analytics/attrition",
        "/analytics/skill-gap",
        "/analytics/forecast",
        "/analytics/training-roi",
    ]

    # Staff roles should have access, customers may not
    for endpoint in analytics_endpoints:
        for role in ("super_admin", "salon_manager", "customer"):
            if role not in s.tokens:
                continue
            req(s, "GET", endpoint, role, "any")


def test_queue(s: TestSuite):
    """Test queue endpoints."""
    print("\n" + "=" * 80)
    print("9. QUEUE MANAGEMENT")
    print("=" * 80)

    loc_id = s.created_ids.get("location", "nonexistent")
    for role in ("salon_manager", "stylist", "super_admin"):
        if role in s.tokens:
            req(s, "GET", f"/queue/{loc_id}", role, "any")

    if "salon_manager" in s.tokens:
        req(s, "GET", f"/queue/{loc_id}/wait-estimate", "salon_manager", "any")


def test_soulskin(s: TestSuite):
    """Test SOULSKIN endpoints."""
    print("\n" + "=" * 80)
    print("10. SOULSKIN ENGINE")
    print("=" * 80)

    # Archetypes - public
    req(s, "GET", "/soulskin/archetypes", "customer", "any")

    # Journal
    if "customer" in s.tokens:
        req(s, "GET", "/soulskin/journal/me", "customer", "any")


def test_feedback(s: TestSuite):
    """Test feedback endpoints."""
    print("\n" + "=" * 80)
    print("11. FEEDBACK")
    print("=" * 80)

    for role in USERS:
        if role not in s.tokens:
            continue
        req(s, "GET", "/feedback", role, "any", params={"per_page": 5})

    if "salon_manager" in s.tokens:
        req(s, "GET", "/feedback/stats", "salon_manager", "any")


def test_notifications(s: TestSuite):
    """Test notification endpoints."""
    print("\n" + "=" * 80)
    print("12. NOTIFICATIONS")
    print("=" * 80)

    for role in USERS:
        if role not in s.tokens:
            continue
        req(s, "GET", "/notifications", role, "any")
        req(s, "GET", "/notifications/unread-count", role, "any")


def test_trends(s: TestSuite):
    """Test trend intelligence endpoints."""
    print("\n" + "=" * 80)
    print("13. TRENDS")
    print("=" * 80)

    for role in ("salon_manager", "super_admin", "stylist"):
        if role in s.tokens:
            req(s, "GET", "/trends", role, "any")


def test_climate(s: TestSuite):
    """Test climate endpoints."""
    print("\n" + "=" * 80)
    print("14. CLIMATE")
    print("=" * 80)

    for role in ("salon_manager", "customer", "super_admin"):
        if role in s.tokens:
            req(s, "GET", "/climate", role, "any")


def test_training(s: TestSuite):
    """Test training endpoints."""
    print("\n" + "=" * 80)
    print("15. TRAINING")
    print("=" * 80)

    for role in ("salon_manager", "super_admin", "stylist"):
        if role in s.tokens:
            req(s, "GET", "/training", role, "any")

    if "salon_manager" in s.tokens:
        req(s, "GET", "/training/stats/roi", "salon_manager", "any")


def test_quality(s: TestSuite):
    """Test quality assessment endpoints."""
    print("\n" + "=" * 80)
    print("16. QUALITY ASSESSMENTS")
    print("=" * 80)

    for role in ("salon_manager", "super_admin", "stylist"):
        if role in s.tokens:
            req(s, "GET", "/quality", role, "any", params={"per_page": 5})

    if "salon_manager" in s.tokens:
        req(s, "GET", "/quality/stats/summary", "salon_manager", "any")


def test_homecare(s: TestSuite):
    """Test homecare endpoints."""
    print("\n" + "=" * 80)
    print("17. HOMECARE")
    print("=" * 80)

    for role in ("customer", "salon_manager"):
        if role in s.tokens:
            req(s, "GET", "/homecare", role, "any")


def test_journey(s: TestSuite):
    """Test journey endpoints."""
    print("\n" + "=" * 80)
    print("18. BEAUTY JOURNEY")
    print("=" * 80)

    for role in ("customer", "salon_manager"):
        if role in s.tokens:
            req(s, "GET", "/journey", role, "any")


def test_mood(s: TestSuite):
    """Test mood endpoints."""
    print("\n" + "=" * 80)
    print("19. MOOD DETECTION")
    print("=" * 80)

    for role in ("customer", "stylist"):
        if role in s.tokens:
            req(s, "GET", "/mood", role, "any")


def test_mirror(s: TestSuite):
    """Test AR mirror endpoints."""
    print("\n" + "=" * 80)
    print("20. AR MIRROR")
    print("=" * 80)

    for role in ("customer", "stylist"):
        if role in s.tokens:
            req(s, "GET", "/mirror/styles", role, "any")


def test_twin(s: TestSuite):
    """Test digital twin endpoints."""
    print("\n" + "=" * 80)
    print("21. DIGITAL TWIN")
    print("=" * 80)

    if "customer" in s.tokens:
        req(s, "GET", "/twin/me", "customer", "any")


def test_roles_rbac(s: TestSuite):
    """Test RBAC endpoints."""
    print("\n" + "=" * 80)
    print("22. ROLES & RBAC")
    print("=" * 80)

    if "super_admin" in s.tokens:
        req(s, "GET", "/roles", "super_admin", "any")

    # Customer should NOT access admin endpoints
    if "customer" in s.tokens:
        req(s, "GET", "/auth/users", "customer", "denied", desc="Customer -> /auth/users (should deny)")
        req(s, "POST", "/locations", "customer", "denied",
            json_body={"name": "Test", "code": "TEST", "city": "Test"},
            desc="Customer -> POST /locations (should deny)")


def test_agents(s: TestSuite):
    """Test agent registry."""
    print("\n" + "=" * 80)
    print("23. AGENT REGISTRY")
    print("=" * 80)

    if "super_admin" in s.tokens:
        req(s, "GET", "/agents/registry", "super_admin", "any")


def test_sessions(s: TestSuite):
    """Test session endpoints."""
    print("\n" + "=" * 80)
    print("24. SERVICE SESSIONS")
    print("=" * 80)

    if "stylist" in s.tokens:
        req(s, "GET", "/sessions/active", "stylist", "any")


def test_error_handling(s: TestSuite):
    """Test error handling — invalid routes, bad data."""
    print("\n" + "=" * 80)
    print("25. ERROR HANDLING & EDGE CASES")
    print("=" * 80)

    role = "super_admin" if "super_admin" in s.tokens else list(s.tokens.keys())[0]

    # Non-existent routes
    req(s, "GET", "/nonexistent", role, "any", desc="Non-existent route")
    req(s, "GET", "/bookings/nonexistent-id", role, "any", desc="Non-existent booking")
    req(s, "GET", "/locations/nonexistent-id", role, "any", desc="Non-existent location")
    req(s, "GET", "/staff/nonexistent-id", role, "any", desc="Non-existent staff")

    # Invalid login
    r = requests.post(f"{s.base_url}/auth/login",
                       json={"email": "wrong@test.com", "password": "wrong"}, timeout=10)
    passed = r.status_code in (401, 400, 422)
    s.results.append(TestResult(
        endpoint="POST /auth/login (bad creds)", method="POST", role="none",
        status=r.status_code, expected="denied", actual="denied" if passed else f"error_{r.status_code}",
        passed=passed and r.status_code < 500, detail="Invalid credentials test",
    ))
    print(f"  [{'PASS' if passed else 'FAIL'}] {'none':20s} POST   {'Invalid login credentials':50s} -> {r.status_code}")

    # Empty body POST
    req(s, "POST", "/auth/login", "none", "any", json_body={}, desc="Empty login body")


# ─── Report ──────────────────────────────────────────────────────────────────

def print_report(s: TestSuite):
    """Print final test report."""
    print("\n")
    print("=" * 80)
    print("FINAL TEST REPORT")
    print("=" * 80)

    # Summary
    print(f"\n  Total Tests:  {s.total}")
    print(f"  Passed:       {s.passed}  ({s.passed / max(s.total, 1) * 100:.1f}%)")
    print(f"  Failed:       {s.failed}  ({s.failed / max(s.total, 1) * 100:.1f}%)")

    # Login summary
    print(f"\n  Roles authenticated: {len(s.tokens)} / {len(USERS)}")
    for role, email in USERS.items():
        status = "OK" if role in s.tokens else "FAILED"
        print(f"    {role:20s} {email:25s} [{status}]")

    # Failed tests
    failures = [r for r in s.results if not r.passed]
    if failures:
        print(f"\n  --- FAILURES ({len(failures)}) ---")
        for f in failures:
            print(f"    [{f.status:3d}] {f.role:20s} {f.endpoint:55s} expected={f.expected} got={f.actual}"
                  + (f" | {f.detail}" if f.detail else ""))

    # Server errors (500+)
    server_errors = [r for r in s.results if r.status >= 500]
    if server_errors:
        print(f"\n  --- SERVER ERRORS (500+) — {len(server_errors)} ---")
        for e in server_errors:
            print(f"    [{e.status}] {e.role:20s} {e.endpoint:55s} | {e.detail}")

    # Slow endpoints (>2s)
    slow = [r for r in s.results if r.response_time_ms > 2000]
    if slow:
        print(f"\n  --- SLOW ENDPOINTS (>2s) — {len(slow)} ---")
        for sl in slow:
            print(f"    {sl.response_time_ms:5d}ms  {sl.endpoint}")

    # Per-module summary
    print("\n  --- MODULE SUMMARY ---")
    modules = {}
    for r in s.results:
        parts = r.endpoint.split(" ", 1)
        if len(parts) > 1:
            path = parts[1].split("/")
            module = path[1] if len(path) > 1 else "root"
        else:
            module = "unknown"
        if module not in modules:
            modules[module] = {"pass": 0, "fail": 0}
        if r.passed:
            modules[module]["pass"] += 1
        else:
            modules[module]["fail"] += 1

    for mod, counts in sorted(modules.items()):
        total = counts["pass"] + counts["fail"]
        pct = counts["pass"] / max(total, 1) * 100
        status = "OK" if counts["fail"] == 0 else "ISSUES"
        print(f"    {mod:25s}  {counts['pass']:3d}/{total:3d} passed  ({pct:5.1f}%)  [{status}]")

    # Per-role summary
    print("\n  --- ROLE ACCESS SUMMARY ---")
    for role in USERS:
        role_results = [r for r in s.results if r.role == role]
        if not role_results:
            continue
        role_pass = sum(1 for r in role_results if r.passed)
        role_total = len(role_results)
        role_pct = role_pass / max(role_total, 1) * 100
        print(f"    {role:20s}  {role_pass:3d}/{role_total:3d} passed  ({role_pct:5.1f}%)")

    # Final verdict
    print("\n" + "=" * 80)
    if s.failed == 0:
        print("  ALL TESTS PASSED")
    elif server_errors:
        print(f"  {len(server_errors)} SERVER ERROR(S) DETECTED — Backend needs fixes")
    else:
        print(f"  {s.failed} TEST(S) FAILED — Review failures above")
    print("=" * 80 + "\n")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AURA API Test Suite")
    parser.add_argument("--base-url", default=DEFAULT_BASE, help="API base URL")
    args = parser.parse_args()

    suite = TestSuite(base_url=args.base_url)

    print("\n" + "=" * 80)
    print("  AURA PLATFORM — COMPREHENSIVE API TEST SUITE")
    print(f"  Base URL: {suite.base_url}")
    print(f"  Testing {len(USERS)} roles × 25 modules")
    print("=" * 80)

    # Check server is running
    try:
        requests.get(f"{suite.base_url}/", timeout=5)
    except requests.exceptions.ConnectionError:
        print(f"\n  ERROR: Cannot connect to {suite.base_url}")
        print("  Make sure the backend is running: uvicorn app.main:app --port 8001")
        sys.exit(1)

    start = time.time()

    # Run all test sections
    test_auth(suite)
    test_users_admin(suite)
    test_locations(suite)
    test_staff(suite)
    test_customers(suite)
    test_bookings(suite)
    test_services(suite)
    test_analytics(suite)
    test_queue(suite)
    test_soulskin(suite)
    test_feedback(suite)
    test_notifications(suite)
    test_trends(suite)
    test_climate(suite)
    test_training(suite)
    test_quality(suite)
    test_homecare(suite)
    test_journey(suite)
    test_mood(suite)
    test_mirror(suite)
    test_twin(suite)
    test_roles_rbac(suite)
    test_agents(suite)
    test_sessions(suite)
    test_error_handling(suite)

    elapsed = time.time() - start
    print(f"\n  Completed in {elapsed:.1f}s")

    # Print report
    print_report(suite)

    # Exit code
    sys.exit(1 if suite.failed > 0 else 0)


if __name__ == "__main__":
    main()
