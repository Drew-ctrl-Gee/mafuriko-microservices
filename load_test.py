"""
MafurikoAI - Load Testing
Tests system scalability under simulated load
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
        return {
            "success": r.status_code == 200,
            "response_time": time.time() - start,
            "status_code": r.status_code
        }
    except Exception as e:
        return {"success": False, "response_time": time.time() - start, "error": str(e)}


def test_prediction():
    """Test ML prediction endpoint"""
    start = time.time()
    try:
        r = requests.post(f"{BASE_URL}/api/predict", 
            json={
                "road": "Thika Road",
                "location": "Nairobi",
                "weather": {
                    "rainfall_mm": 45,
                    "humidity_percent": 78,
                    "temperature_c": 23
                }
            }, 
            timeout=10
        )
        return {
            "success": r.status_code == 200,
            "response_time": time.time() - start,
            "status_code": r.status_code
        }
    except Exception as e:
        return {"success": False, "response_time": time.time() - start, "error": str(e)}


def test_weather():
    """Test weather endpoint"""
    start = time.time()
    try:
        r = requests.get(f"{BASE_URL}/api/weather/Nairobi", timeout=5)
        return {
            "success": r.status_code == 200,
            "response_time": time.time() - start,
            "status_code": r.status_code
        }
    except Exception as e:
        return {"success": False, "response_time": time.time() - start, "error": str(e)}


def test_chatbot():
    """Test chatbot endpoint"""
    start = time.time()
    try:
        r = requests.post(f"{BASE_URL}/api/chat",
            json={
                "message": "Is Thika Road safe?",
                "location": "Nairobi"
            },
            timeout=10
        )
        return {
            "success": r.status_code == 200,
            "response_time": time.time() - start,
            "status_code": r.status_code
        }
    except Exception as e:
        return {"success": False, "response_time": time.time() - start, "error": str(e)}


def run_load_test(test_func, num_requests, concurrent_users, test_name):
    """Run load test with concurrent users"""
    print(f"\n🧪 {test_name}")
    print(f"📊 Requests: {num_requests} | Concurrent Users: {concurrent_users}")
    print("=" * 60)
    
    start_time = time.time()
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = [executor.submit(test_func) for _ in range(num_requests)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    
    total_time = time.time() - start_time
    
    # Analyze results
    successful = sum(1 for r in results if r.get("success"))
    failed = num_requests - successful
    response_times = [r["response_time"] for r in results if r.get("success")]
    
    if response_times:
        avg_time = mean(response_times) * 1000  # ms
        med_time = median(response_times) * 1000
        min_time = min(response_times) * 1000
        max_time = max(response_times) * 1000
    else:
        avg_time = med_time = min_time = max_time = 0
    
    requests_per_second = num_requests / total_time
    success_rate = (successful / num_requests) * 100
    
    print(f"✅ Successful:        {successful}/{num_requests}")
    print(f"❌ Failed:            {failed}/{num_requests}")
    print(f"📈 Success Rate:      {success_rate:.2f}%")
    print(f"⚡ Requests/second:   {requests_per_second:.2f}")
    print(f"⏱️  Total time:        {total_time:.2f}s")
    print(f"\n📊 Response Times:")
    print(f"   Average: {avg_time:.2f}ms")
    print(f"   Median:  {med_time:.2f}ms")
    print(f"   Min:     {min_time:.2f}ms")
    print(f"   Max:     {max_time:.2f}ms")
    
    return {
        "test_name": test_name,
        "total_requests": num_requests,
        "concurrent_users": concurrent_users,
        "successful": successful,
        "failed": failed,
        "success_rate": success_rate,
        "requests_per_second": requests_per_second,
        "total_time": total_time,
        "avg_response_ms": avg_time,
        "median_response_ms": med_time,
        "min_response_ms": min_time,
        "max_response_ms": max_time
    }


def main():
    print("=" * 60)
    print("🚀 MAFURIKO AI - LOAD TESTING")
    print("=" * 60)
    
    all_results = []
    
    # Test 1: Health checks
    all_results.append(run_load_test(test_health, 100, 10, "TEST 1: Health Check Endpoint"))
    
    # Test 2: Weather
    all_results.append(run_load_test(test_weather, 50, 10, "TEST 2: Weather Service"))
    
    # Test 3: ML Predictions
    all_results.append(run_load_test(test_prediction, 100, 20, "TEST 3: ML Predictions (Real Model)"))
    
    # Test 4: Chatbot
    all_results.append(run_load_test(test_chatbot, 50, 10, "TEST 4: Chatbot Service"))
    
    # Test 5: Stress test
    all_results.append(run_load_test(test_prediction, 500, 50, "TEST 5: STRESS TEST - 500 predictions"))
    
    # Save results
    with open('load_test_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 LOAD TEST SUMMARY")
    print("=" * 60)
    
    for result in all_results:
        print(f"\n{result['test_name']}")
        print(f"   Success Rate: {result['success_rate']:.1f}%")
        print(f"   Avg Response: {result['avg_response_ms']:.2f}ms")
        print(f"   Throughput:   {result['requests_per_second']:.2f} req/s")
    
    print("\n💾 Results saved to load_test_results.json")


if __name__ == "__main__":
    main()