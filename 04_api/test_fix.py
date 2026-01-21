# test_fix.py
import requests

def test_all_endpoints():
    base_url = "http://127.0.0.1:8000"
    
    endpoints = [
        ("/", "Home/API Root"),
        ("/api/detect/", "Vehicle Detection"),
        ("/api/optimize/", "Traffic Optimization"),  # NEW
        ("/api/ai-models/", "AI Models"),
        ("/api/live-detection/start/", "Live Detection Start"),
        ("/stats/", "Statistics")
    ]
    
    print("🔍 Testing Updated API Endpoints")
    print("=" * 60)
    
    for endpoint, name in endpoints:
        try:
            url = base_url + endpoint
            print(f"\n{name} ({endpoint}):")
            
            if endpoint == "/api/optimize/":
                # Test GET first
                response = requests.get(url)
                print(f"  GET Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"  Message: {data.get('message', 'No message')}")
            else:
                response = requests.get(url)
                print(f"  Status: {response.status_code}")
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if 'message' in data:
                            print(f"  Message: {data['message']}")
                    except:
                        pass
        except Exception as e:
            print(f"  Error: {e}")

def test_optimization_post():
    """Test POST to optimization endpoint"""
    print("\n🧪 Testing Optimization POST Request")
    print("=" * 50)
    
    test_data = {
        "lanes": [
            {
                "lane_id": 1,
                "direction": "northbound",
                "vehicle_counts": {"motorcycle": 8, "car": 3, "tuktuk": 2}
            },
            {
                "lane_id": 2,
                "direction": "southbound",
                "vehicle_counts": {"motorcycle": 5, "car": 4, "bus": 1}
            }
        ],
        "intersection_id": "test_intersection",
        "time_of_day": "peak_hours"
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/optimize/",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"POST Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('message')}")
            print(f"📊 Total vehicles: {result.get('total_vehicles')}")
            print(f"🚦 Green times calculated: {len(result.get('green_times', []))}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    print("🚀 SMART TRAFFIC OPTIMIZER - URL FIX TEST")
    print("=" * 60)
    
    test_all_endpoints()
    test_optimization_post()
    
    print("\n" + "=" * 60)
    print("🎉 TEST COMPLETED!")