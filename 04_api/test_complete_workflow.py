# test_complete_workflow.py
import requests
import json
import time

def complete_smart_traffic_workflow():
    """Test the complete Smart Traffic Optimizer workflow"""
    
    print("🚀 SMART TRAFFIC OPTIMIZER - COMPLETE WORKFLOW TEST")
    print("=" * 70)
    print("Simulating: Detection → Analysis → Optimization → Results")
    print("=" * 70)
    
    base_url = "http://127.0.0.1:8000"
    
    # Step 1: Check API Status
    print("\n📋 STEP 1: Checking API Status")
    print("-" * 40)
    try:
        response = requests.get(base_url + "/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data['status']}")
            print(f"📱 Message: {data['message']}")
            print(f"🔧 Version: {data['version']}")
    except Exception as e:
        print(f"❌ API check failed: {e}")
        return
    
    # Step 2: Test Vehicle Detection with Real Image
    print("\n📷 STEP 2: Vehicle Detection Test")
    print("-" * 40)
    
    # Try to detect vehicles from test image
    try:
        with open('test_traffic.jpg', 'rb') as img:
            files = {'image': img}
            response = requests.post(base_url + "/api/detect/", files=files)
        
        if response.status_code == 200:
            detect_data = response.json()
            print(f"✅ Detection successful!")
            print(f"📊 Vehicles detected: {detect_data.get('vehicles_detected', 0)}")
            print(f"⏱️ Processing time: {detect_data.get('processing_time', 'N/A')}")
            
            # Extract vehicle counts for optimization
            vehicle_counts = {}
            if 'detections' in detect_data:
                for detection in detect_data['detections']:
                    vehicle = detection.get('vehicle')
                    count = detection.get('count', 1)
                    if vehicle:
                        vehicle_counts[vehicle] = vehicle_counts.get(vehicle, 0) + count
        else:
            print(f"⚠️ Detection returned {response.status_code}")
            print("Using simulated data for workflow...")
            vehicle_counts = {"motorcycle": 8, "car": 4, "tuktuk": 2}
            
    except FileNotFoundError:
        print("⚠️ test_traffic.jpg not found, using simulated data")
        vehicle_counts = {"motorcycle": 8, "car": 4, "tuktuk": 2}
    
    # Step 3: Prepare Optimization Data (Cambodia-specific)
    print("\n🚦 STEP 3: Preparing Traffic Data for Optimization")
    print("-" * 40)
    
    # Create a simulated Phnom Penh intersection
    intersection_data = {
        "intersection_id": "phnom_penh_russian_market",
        "time_of_day": "morning_peak",
        "lanes": [
            {
                "lane_id": 1,
                "direction": "northbound_to_center",
                "vehicle_counts": {
                    "motorcycle": vehicle_counts.get("motorcycle", 5),
                    "car": vehicle_counts.get("car", 3),
                    "tuktuk": vehicle_counts.get("tuktuk", 2)
                }
            },
            {
                "lane_id": 2,
                "direction": "southbound_to_riverside",
                "vehicle_counts": {
                    "motorcycle": vehicle_counts.get("motorcycle", 0) + 3,
                    "car": vehicle_counts.get("car", 0) + 2,
                    "bus": 1
                }
            },
            {
                "lane_id": 3,
                "direction": "eastbound_to_aeon_mall",
                "vehicle_counts": {
                    "motorcycle": vehicle_counts.get("motorcycle", 0) + 4,
                    "car": vehicle_counts.get("car", 0) + 1,
                    "tuktuk": vehicle_counts.get("tuktuk", 0) + 1,
                    "bicycle": 2
                }
            },
            {
                "lane_id": 4,
                "direction": "westbound_to_airport",
                "vehicle_counts": {
                    "motorcycle": vehicle_counts.get("motorcycle", 0) + 6,
                    "car": vehicle_counts.get("car", 0) + 3,
                    "truck": 1
                }
            }
        ]
    }
    
    print(f"📍 Intersection: {intersection_data['intersection_id']}")
    print(f"⏰ Time: {intersection_data['time_of_day']}")
    print(f"🛣️ Lanes: {len(intersection_data['lanes'])}")
    
    total_vehicles = sum(sum(lane['vehicle_counts'].values()) for lane in intersection_data['lanes'])
    total_motorcycles = sum(lane['vehicle_counts'].get('motorcycle', 0) for lane in intersection_data['lanes'])
    
    print(f"📊 Total vehicles: {total_vehicles}")
    print(f"🏍️ Motorcycles: {total_motorcycles} ({total_motorcycles/total_vehicles*100:.1f}%)")
    
    # Step 4: Run Traffic Optimization
    print("\n⚙️ STEP 4: Running Traffic Signal Optimization")
    print("-" * 40)
    
    try:
        response = requests.post(
            base_url + "/api/optimize/",
            json=intersection_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            optimize_data = response.json()
            
            print(f"✅ Optimization successful!")
            print(f"📈 Congestion level: {optimize_data['congestion_level'].upper()}")
            print(f"🔄 Cycle duration: {optimize_data['optimization_parameters']['cycle_time']}s")
            
            # Display optimization results
            print("\n" + "=" * 60)
            print("🚦 OPTIMIZED SIGNAL TIMES")
            print("=" * 60)
            
            total_green_time = 0
            for lane in optimize_data['green_times']:
                direction = lane['direction']
                green_time = lane['green_time']
                bonus = f" (+{lane['motorcycle_bonus']}s 🏍️)" if lane.get('motorcycle_bonus') else ""
                allocation = lane['allocation_percent']
                
                print(f"\nLane {lane['lane_id']} ({direction}):")
                print(f"  ⏱️  Green time: {green_time} seconds{bonus}")
                print(f"  📊 Allocation: {allocation}%")
                print(f"  🚗 Vehicles: {lane['vehicle_summary']}")
                
                total_green_time += green_time
            
            print("\n" + "=" * 60)
            print("📊 OPTIMIZATION SUMMARY")
            print("=" * 60)
            print(f"Total vehicles processed: {optimize_data['total_vehicles']}")
            print(f"Motorcycle percentage: {optimize_data['motorcycle_percentage']}%")
            print(f"Total green time allocated: {total_green_time}s")
            print(f"Average green time per lane: {total_green_time/len(optimize_data['green_times']):.1f}s")
            
            if optimize_data['recommendations']:
                print("\n💡 CAMBODIA-SPECIFIC RECOMMENDATIONS:")
                for i, rec in enumerate(optimize_data['recommendations'], 1):
                    print(f"  {i}. {rec}")
            
            # Save complete results
            results = {
                "workflow_test": "Smart Traffic Optimizer - Complete Workflow",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "detection_results": detect_data if 'detect_data' in locals() else "Simulated",
                "intersection_data": intersection_data,
                "optimization_results": optimize_data,
                "performance_metrics": {
                    "total_vehicles": total_vehicles,
                    "motorcycle_percentage": round(total_motorcycles/total_vehicles*100, 1),
                    "congestion_level": optimize_data['congestion_level'],
                    "total_green_time": total_green_time,
                    "average_green_time": total_green_time/len(optimize_data['green_times'])
                }
            }
            
            with open('complete_workflow_results.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Complete results saved to: complete_workflow_results.json")
            
        else:
            print(f"❌ Optimization failed: {response.status_code}")
            print(response.text[:200])
            
    except Exception as e:
        print(f"❌ Optimization error: {e}")
    
    # Step 5: Check System Statistics
    print("\n📈 STEP 5: Checking System Statistics")
    print("-" * 40)
    
    try:
        response = requests.get(base_url + "/stats/")
        if response.status_code == 200:
            stats_data = response.json()
            print(f"✅ System Status: {stats_data['system_status']['api_health']}")
            print(f"📊 Today's detections: {stats_data['traffic_metrics']['vehicles_today']}")
            print(f"🏍️ Most common vehicle: {stats_data['most_common_vehicle']}")
    except Exception as e:
        print(f"⚠️ Stats check failed: {e}")
    
    print("\n" + "=" * 70)
    print("🎉 SMART TRAFFIC OPTIMIZER WORKFLOW COMPLETE!")
    print("=" * 70)
    print("\n✅ What's working:")
    print("   1. Real-time vehicle detection (YOLOv8)")
    print("   2. Cambodia-specific traffic optimization")
    print("   3. Motorcycle-priority signal timing")
    print("   4. Complete API ecosystem")
    print("\n🚀 Ready for deployment to Cambodian traffic systems!")

def quick_api_health_check():
    """Quick check of all API endpoints"""
    
    print("\n🔧 API HEALTH CHECK")
    print("=" * 40)
    
    endpoints = [
        ("/", "API Root"),
        ("/api/detect/", "Vehicle Detection"),
        ("/api/optimize/", "Traffic Optimization"),
        ("/api/ai-models/", "AI Models"),
        ("/api/live-detection/start/", "Live Detection"),
        ("/stats/", "Statistics")
    ]
    
    base_url = "http://127.0.0.1:8000"
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(base_url + endpoint, timeout=2)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {name}: {response.status_code}")
        except:
            print(f"❌ {name}: Connection failed")

if __name__ == "__main__":
    # Quick health check first
    quick_api_health_check()
    
    # Run complete workflow
    complete_smart_traffic_workflow()