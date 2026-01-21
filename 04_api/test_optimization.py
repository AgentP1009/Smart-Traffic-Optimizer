# test_optimization.py
import requests
import json

def test_traffic_optimization():
    """Test the new traffic optimization endpoint"""
    
    print("🧪 Testing Traffic Optimization API")
    print("=" * 60)
    
    # Test data for Cambodian intersection
    test_data = {
        "intersection_id": "phnom_penh_central_market",
        "time_of_day": "morning_peak",
        "lanes": [
            {
                "lane_id": 1,
                "direction": "northbound",
                "vehicle_counts": {
                    "motorcycle": 12,
                    "car": 4,
                    "tuktuk": 3,
                    "bicycle": 2
                }
            },
            {
                "lane_id": 2,
                "direction": "southbound",
                "vehicle_counts": {
                    "motorcycle": 8,
                    "car": 6,
                    "bus": 1
                }
            },
            {
                "lane_id": 3,
                "direction": "eastbound",
                "vehicle_counts": {
                    "motorcycle": 6,
                    "car": 3,
                    "tuktuk": 2
                }
            },
            {
                "lane_id": 4,
                "direction": "westbound",
                "vehicle_counts": {
                    "motorcycle": 10,
                    "car": 2,
                    "truck": 1
                }
            }
        ]
    }
    
    url = "http://127.0.0.1:8000/api/optimize/"
    
    try:
        # Test GET first
        print("1. Testing GET request (should show API info)...")
        response = requests.get(url)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Message: {data.get('message', 'No message')}")
            print(f"   Description: {data.get('description', 'No description')}")
        
        # Test POST with optimization data
        print("\n2. Testing POST request with traffic data...")
        response = requests.post(
            url,
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ {result['message']}")
            print(f"📍 Intersection: {result['intersection_id']}")
            print(f"⏰ Time: {result['time_of_day']}")
            print(f"🚦 Congestion Level: {result['congestion_level'].upper()}")
            print(f"📊 Total Vehicles: {result['total_vehicles']}")
            print(f"🏍️ Motorcycles: {result['total_motorcycles']} ({result['motorcycle_percentage']}%)")
            
            print("\n" + "=" * 50)
            print("OPTIMIZED GREEN TIMES:")
            print("=" * 50)
            
            for lane in result['green_times']:
                bonus_info = f" (+{lane['motorcycle_bonus']}s 🏍️ bonus)" if lane.get('motorcycle_bonus') else ""
                print(f"\nLane {lane['lane_id']} ({lane['direction']}):")
                print(f"  ⏱️  Green Time: {lane['green_time']} seconds{bonus_info}")
                print(f"  📈 Allocation: {lane['allocation_percent']}%")
                print(f"  🚗 Vehicle Summary: {lane['vehicle_summary']}")
            
            print("\n" + "=" * 50)
            print("💡 RECOMMENDATIONS:")
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"  {i}. {rec}")
            
            # Save results
            with open('optimization_test_results.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Results saved to: optimization_test_results.json")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running!")
        print("Run: python manage.py runserver")
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")

def test_all_endpoints():
    """Test all API endpoints"""
    
    print("\n🔍 Testing All API Endpoints")
    print("=" * 40)
    
    endpoints = [
        ("http://127.0.0.1:8000/", "API Root"),
        ("http://127.0.0.1:8000/api/detect/", "Vehicle Detection"),
        ("http://127.0.0.1:8000/api/optimize/", "Traffic Optimization"),
        ("http://127.0.0.1:8000/api/live/start/", "Live Detection Start"),
        ("http://127.0.0.1:8000/api/models/", "AI Models")
    ]
    
    for url, name in endpoints:
        try:
            response = requests.get(url)
            print(f"{name}:")
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if 'message' in data:
                    print(f"  Message: {data['message']}")
            print()
        except Exception as e:
            print(f"{name}: Error - {e}\n")

if __name__ == "__main__":
    print("🚀 SMART TRAFFIC OPTIMIZER - OPTIMIZATION TEST")
    print("=" * 60)
    
    # Test all endpoints
    test_all_endpoints()
    
    # Test optimization specifically
    test_traffic_optimization()
    
    print("\n" + "=" * 60)
    print("🎉 TEST COMPLETED!")
    print("\nNext steps:")
    print("1. Check optimization_test_results.json")
    print("2. Implement the optimization function in views.py")
    print("3. Test with real detection data")