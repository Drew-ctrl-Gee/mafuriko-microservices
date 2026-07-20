"""
MafurikoAI - Load Testing Script
Tests all microservices under simulated load
Milestone 5: System scalability testing
"""
import requests
import time
import concurrent.futures
from statistics import mean, median
import json

BASE_URL = "http://localhost:5000"


def test_health():
    """Test health endpoint"""
    start = time.time()
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        return {"success": r.status_code == 200, "time": time.time() - start, "status": r.status_code}
    except Exception as e:
        return {"success": False, "time": time.time() - start, "error": str(e)}


def test_weather():
    """Test weather service"""
    start = time.time()
    try:
        r = requests.get(f"{BASE_URL}/api/weather/Nairobi", timeout=10)
        return {"success": r.status_code == 200, "time": time.time() - start}
    except:
        return {"success": False, "time": time.time() - start}


def test_prediction():
    """Test ML prediction"""
    start = time.time()
    try:
        r = requests.post(f"{BASE_URL}/api/predict",
            json={
                "road": "Thika Road",
                "location": "Nairobi",
                "weather": {"rainfall_mm": 45, "humidity_percent": 78, "temperature_c": 23}
            },
            timeout=10
        )
        return {"success": r.status_code == 200, "time": time.time() - start}
    except:
        return {"success": False, "time": time.time() - start}


def test_chat():
    """Test chatbot"""
    start = time.time()
    try:
        r = requests.post(f"{BASE_URL}/api/chat",
            json={"message": "Is Thika Road safe?", "location": "Nairobi"},
            timeout=10
        )
        return {"success": r.status_code == 200, "time": time.time() - start}
    except:
        return {"success": False, "time": time.time() - start}


def test_signup():
    """Test signup"""
    start = time.time()
    try:
        import random
        r = requests.post(f"{BASE_URL}/api/auth/signup",
            json={
                "username": f"user_{random.randint(1000, 9999)}",
                "email": f"test{random.randint(1000, 9999)}@test.com",
                "password": "password123",
                "location": "Nairobi"
            },
            timeout=10
        )
        return {"success": r.status_code == 200, "time": time.time() - start}
    except:
        return {"success": False, "time": time.time() - start}


def run_test(test_func, num_requests, concurrent, name):
    """Run load test with concurrent users"""
    print(f"\n{'=' * 65}")
    print(f"🧪 {name}")
    print(f"📊 Requests: {num_requests} | Concurrent Users: {concurrent}")
    print('=' * 65)
    
    start = time.time()
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent) as executor:
        futures = [executor.submit(test_func) for _ in range(num_requests)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    
    total_time = time.time() - start
    successful = sum(1 for r in results if r.get("success"))
    failed = num_requests - successful
    times = [r["time"] for r in results if r.get("success")]
    
    if times:
        avg_time = mean(times) * 1000
        med_time = median(times) * 1000
        min_time = min(times) * 1000
        max_time = max(times) * 1000
        rps = num_requests / total_time
        success_rate = (successful / num_requests) * 100
        
        print(f"✅ Successful:      {successful}/{num_requests} ({success_rate:.1f}%)")
        print(f"❌ Failed:          {failed}/{num_requests}")
        print(f"⚡ Requests/second: {rps:.2f}")
        print(f"⏱️  Total time:      {total_time:.2f}s")
        print(f"📊 Response Times:")
        print(f"   Average: {avg_time:.2f}ms")
        print(f"   Median:  {med_time:.2f}ms")
        print(f"   Min:     {min_time:.2f}ms")
        print(f"   Max:     {max_time:.2f}ms")
        
        return {
            "test_name": name,
            "total_requests": num_requests,
            "concurrent_users": concurrent,
            "successful": successful,
            "failed": failed,
            "success_rate": success_rate,
            "requests_per_second": rps,
            "total_time_seconds": total_time,
            "avg_response_ms": avg_time,
            "median_response_ms": med_time,
            "min_response_ms": min_time,
            "max_response_ms": max_time
        }
    else:
        print("❌ All requests failed!")
        return None


def main():
    print("\n" + "=" * 65)
    print("🚀 MAFURIKO AI - COMPREHENSIVE LOAD TESTING")
    print("Milestone 5: System Scalability & Reliability")
    print("=" * 65)
    
    all_results = []
    
    # Test 1: Health check
    result = run_test(test_health, 100, 10, "TEST 1: Health Endpoint (Light Load)")
    if result: all_results.append(result)
    
    # Test 2: Weather
    result = run_test(test_weather, 50, 10, "TEST 2: Weather Service (Medium Load)")
    if result: all_results.append(result)
    
    # Test 3: ML Predictions
    result = run_test(test_prediction, 100, 20, "TEST 3: ML Predictions (High Load)")
    if result: all_results.append(result)
    
    # Test 4: Chatbot
    result = run_test(test_chat, 50, 10, "TEST 4: Chatbot Service (Medium Load)")
    if result: all_results.append(result)
    
    # Test 5: Signup
    result = run_test(test_signup, 30, 5, "TEST 5: User Signup (Light Load)")
    if result: all_results.append(result)
    
    # Test 6: STRESS TEST
    result = run_test(test_prediction, 500, 50, "TEST 6: STRESS TEST - 500 predictions/50 users")
    if result: all_results.append(result)
    
    # Save results
    with open('load_test_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Summary
    print("\n" + "=" * 65)
    print("📊 FINAL LOAD TEST SUMMARY")
    print("=" * 65)
    
    for r in all_results:
        status = "✅" if r["success_rate"] >= 95 else "⚠️" if r["success_rate"] >= 80 else "❌"
        print(f"\n{status} {r['test_name']}")
        print(f"   Success Rate:  {r['success_rate']:.1f}%")
        print(f"   Avg Response:  {r['avg_response_ms']:.2f}ms")
        print(f"   Throughput:    {r['requests_per_second']:.2f} req/s")
    
    print("\n" + "=" * 65)
    print("💾 Results saved to: load_test_results.json")
    print("✅ Load testing complete!")
    print("=" * 65)


if __name__ == "__main__":
    main()