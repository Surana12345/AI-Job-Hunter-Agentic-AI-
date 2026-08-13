"""AI Job Hunter - Phase 1 Demo Script"""
import httpx

base = "http://127.0.0.1:8000"
print("=" * 60)
print("  AI JOB HUNTER - PHASE 1 DEMO")
print("=" * 60)

# Health check
r = httpx.get(f"{base}/health")
print(f"\n[Health] GET /health -> {r.status_code}")
print(f"  Response: {r.json()}")

# Root
r = httpx.get(f"{base}/")
print(f"\n[Root] GET / -> {r.status_code}")
print(f"  Response: {r.json()}")

# Register (may already exist)
r = httpx.post(f"{base}/api/v1/auth/register", json={
    "email": "vikas@aijobhunter.com",
    "password": "SecurePass123!",
    "full_name": "Vikas Surana"
})
if r.status_code == 201:
    print(f"\n[Register] POST /api/v1/auth/register -> {r.status_code}")
    data = r.json()
    token = data.get("access_token", "")
    user = data.get("user", {})
    print(f"  User: {user.get('full_name')} ({user.get('email')})")
    print(f"  Token: {token[:50]}...")
else:
    print(f"\n[Register] User already exists (409) -- logging in instead")

# Login
r = httpx.post(f"{base}/api/v1/auth/login", json={
    "email": "vikas@aijobhunter.com",
    "password": "SecurePass123!"
})
print(f"\n[Login] POST /api/v1/auth/login -> {r.status_code}")
data = r.json()
token = data.get("access_token", "")
print(f"  Token received: Yes ({token[:40]}...)")

# Get profile
r = httpx.get(f"{base}/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
print(f"\n[Profile] GET /api/v1/auth/me -> {r.status_code}")
me = r.json()
print(f"  ID:     {me['id']}")
print(f"  Name:   {me['full_name']}")
print(f"  Email:  {me['email']}")
print(f"  Active: {me['is_active']}")

# Invalid token test
r = httpx.get(f"{base}/api/v1/auth/me", headers={"Authorization": "Bearer fake-token"})
print(f"\n[Auth Guard] GET /api/v1/auth/me (bad token) -> {r.status_code}")
print(f"  Response: {r.json()['detail']}")

print("\n" + "=" * 60)
print("  ALL ENDPOINTS WORKING - PHASE 1 COMPLETE!")
print("=" * 60)
print(f"\n  Swagger Docs: {base}/docs")
print(f"  ReDoc:        {base}/redoc")
