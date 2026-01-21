# teacher_demo.py
import requests

print("👨‍🏫 TEACHER INTERACTIVE DEMO")
print("=" * 50)

print("\nWhat would you like to see?")
print("1. Real-time vehicle detection")
print("2. Traffic signal optimization")
print("3. Cambodia-specific scenarios")
print("4. Complete workflow")

choice = input("\nEnter choice (1-4): ")

if choice == "1":
    print("\n📷 Testing with different images...")
    images = ["test_traffic.jpg", "test_bus.jpg"]
    for img in images:
        print(f"\nProcessing {img}...")
        with open(img, 'rb') as f:
            response = requests.post('http://127.0.0.1:8000/api/detect/', files={'image': f})
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Detected {data.get('vehicles_detected', 0)} vehicles")
                print(f"⏱️  Time: {data.get('processing_time', 'N/A')}")

elif choice == "2":
    print("\n🚦 Testing different traffic scenarios...")
    
    scenarios = [
        ("Low Traffic", {"motorcycle": 3, "car": 2}),
        ("Medium Traffic", {"motorcycle": 8, "car": 6, "tuktuk": 3}),
        ("High Traffic", {"motorcycle": 15, "car": 10, "bus": 2, "truck": 2}),
        ("Motorcycle Heavy", {"motorcycle": 20, "car": 5, "tuktuk": 5})
    ]
    
    for name, counts in scenarios:
        print(f"\nScenario: {name}")
        print(f"Traffic: {counts}")
        
        data = {
            "lanes": [{
                "lane_id": 1,
                "direction": "test",
                "vehicle_counts": counts
            }]
        }
        
        response = requests.post('http://127.0.0.1:8000/api/optimize/', json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Congestion: {result['congestion_level']}")
            print(f"✅ Green time: {result['green_times'][0]['green_time']}s")

elif choice == "3":
    print("\n🇰🇭 Cambodia-Specific Features:")
    print("1. Motorcycle priority (+10s bonus for lanes with ≥5 motorcycles)")
    print("2. Tuktuk handling (1.5x weight in optimization)")
    print("3. Peak hour adjustments")
    print("4. Mixed traffic flow optimization")
    
    # Demonstrate motorcycle bonus
    print("\n🏍️ Demonstrating motorcycle bonus...")
    
    with_bonus = {"motorcycle": 6, "car": 3}
    without_bonus = {"car": 9}
    
    for name, counts in [("With Motorcycles", with_bonus), ("Cars Only", without_bonus)]:
        data = {"lanes": [{"lane_id": 1, "direction": "test", "vehicle_counts": counts}]}
        response = requests.post('http://127.0.0.1:8000/api/optimize/', json=data)
        if response.status_code == 200:
            result = response.json()
            green_time = result['green_times'][0]['green_time']
            bonus = result['green_times'][0].get('motorcycle_bonus', 0)
            print(f"{name}: {green_time}s (Bonus: {bonus}s)")

elif choice == "4":
    print("\n🚀 Running complete workflow...")
    import subprocess
    subprocess.run(["python", "test_complete_workflow.py"])

print("\n" + "=" * 50)
print("🎉 DEMONSTRATION COMPLETE!")