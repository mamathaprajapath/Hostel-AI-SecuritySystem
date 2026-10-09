import sys
import os

# Add root folder to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from backend.main import app
from database.seed_data import seed_database

def test_full_pipeline():
    print("=== Testing System Initialization & Endpoints ===")
    seed_database()
    
    client = TestClient(app)

    # 1. Test Dashboard API
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200
    stats = res.json()
    print("[TEST PASSED] Dashboard Stats Endpoint:", stats)

    # 2. Test Residents API
    res = client.get("/api/residents")
    assert res.status_code == 200
    residents = res.json()
    print(f"[TEST PASSED] Residents List Endpoint: Found {len(residents)} residents")

    # 3. Test Parents API
    res = client.get("/api/parents")
    assert res.status_code == 200
    parents = res.json()
    print(f"[TEST PASSED] Parents List Endpoint: Found {len(parents)} parents")

    # 4. Test Outing Requests API
    res = client.get("/api/outing/requests")
    assert res.status_code == 200
    print("[TEST PASSED] Outing Requests Endpoint OK")

    # 5. Test Access Logs API
    res = client.get("/api/access/logs")
    assert res.status_code == 200
    print("[TEST PASSED] Access Logs Endpoint OK")

    # 6. Test Unknown Events API
    res = client.get("/api/unknown/events")
    assert res.status_code == 200
    print("[TEST PASSED] Unknown Events Endpoint OK")

    # 7. Test Camera Status API
    res = client.get("/api/camera/status")
    assert res.status_code == 200
    print("[TEST PASSED] Camera Status Endpoint OK")

    print("=== ALL API & DB INTEGRATION TESTS PASSED CLEANLY! ===")

if __name__ == "__main__":
    test_full_pipeline()
