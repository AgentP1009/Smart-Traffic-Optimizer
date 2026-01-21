# live_demo.py
import cv2
import requests
import time
import json
from datetime import datetime

def live_webcam_detection():
    """Real-time traffic monitoring using webcam"""
    
    print("🎥 LIVE TRAFFIC MONITORING DEMONSTRATION")
    print("=" * 60)
    print("Point your webcam at:")
    print("1. Toy vehicles (cars, motorcycles)")
    print("2. Phone showing traffic videos")
    print("3. Printed traffic images")
    print("=" * 60)
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Webcam not available. Using simulated mode...")
        return simulated_demo()
    
    print("✅ Webcam connected! Starting live monitoring...")
    print("Press 'q' to quit, 's' to save snapshot")
    
    frame_count = 0
    detection_results = []
    
    while True:
        # Capture frame
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Process every 5th frame for performance
        if frame_count % 5 == 0:
            # Save frame temporarily
            temp_file = "temp_frame.jpg"
            cv2.imwrite(temp_file, frame)
            
            # Send to API for detection
            try:
                with open(temp_file, 'rb') as img:
                    files = {'image': img}
                    response = requests.post('http://127.0.0.1:8000/api/detect/', files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('success'):
                        vehicles = data.get('vehicles_detected', 0)
                        detections = data.get('detections', [])
                        
                        # Display results on frame
                        cv2.putText(frame, f"Vehicles: {vehicles}", (10, 30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        
                        # Count by type
                        counts = {}
                        for det in detections:
                            v_type = det.get('vehicle', 'unknown')
                            counts[v_type] = counts.get(v_type, 0) + 1
                        
                        y_pos = 70
                        for v_type, count in counts.items():
                            cv2.putText(frame, f"{v_type}: {count}", (10, y_pos), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                            y_pos += 30
                        
                        # Store for optimization
                        detection_results.append({
                            'timestamp': datetime.now().strftime("%H:%M:%S"),
                            'counts': counts,
                            'total': vehicles
                        })
                        
                        print(f"\r📊 Live: {vehicles} vehicles detected", end="")
                        
            except Exception as e:
                print(f"\n⚠️ Detection error: {e}")
        
        # Display frame
        cv2.imshow('Smart Traffic Optimizer - Live Demo', frame)
        
        # Check for key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Save snapshot
            filename = f"snapshot_{datetime.now().strftime('%H%M%S')}.jpg"
            cv2.imwrite(filename, frame)
            print(f"\n💾 Saved snapshot: {filename}")
        elif key == ord('o'):
            # Run optimization on collected data
            run_optimization(detection_results)
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    # Final summary
    print("\n\n📈 DEMO SUMMARY:")
    print("-" * 40)
    print(f"Frames processed: {frame_count}")
    print(f"Detection cycles: {len(detection_results)}")
    
    if detection_results:
        total_vehicles = sum(r['total'] for r in detection_results)
        print(f"Total vehicles detected: {total_vehicles}")
        
        # Save data for later analysis
        with open('live_demo_data.json', 'w') as f:
            json.dump(detection_results, f, indent=2)
        print(f"💾 Data saved to: live_demo_data.json")
        
        # Run final optimization
        run_optimization(detection_results)

def run_optimization(detection_results):
    """Run optimization based on collected data"""
    
    if not detection_results:
        print("❌ No data for optimization")
        return
    
    print("\n⚡ RUNNING TRAFFIC OPTIMIZATION...")
    
    # Aggregate data from all detections
    total_counts = {}
    for result in detection_results[-10:]:  # Last 10 detections
        for v_type, count in result['counts'].items():
            total_counts[v_type] = total_counts.get(v_type, 0) + count
    
    # Create lane data (simulating 4 lanes)
    lane_data = {
        "intersection_id": "live_demo_intersection",
        "time_of_day": "current",
        "lanes": [
            {
                "lane_id": 1,
                "direction": "northbound",
                "vehicle_counts": distribute_vehicles(total_counts, 1, 4)
            },
            {
                "lane_id": 2,
                "direction": "southbound",
                "vehicle_counts": distribute_vehicles(total_counts, 2, 4)
            },
            {
                "lane_id": 3,
                "direction": "eastbound",
                "vehicle_counts": distribute_vehicles(total_counts, 3, 4)
            },
            {
                "lane_id": 4,
                "direction": "westbound",
                "vehicle_counts": distribute_vehicles(total_counts, 4, 4)
            }
        ]
    }
    
    # Send to optimization API
    try:
        response = requests.post(
            'http://127.0.0.1:8000/api/optimize/',
            json=lane_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ OPTIMIZATION RESULTS:")
            print(f"Congestion level: {result['congestion_level'].upper()}")
            print(f"Total vehicles: {result['total_vehicles']}")
            print(f"Motorcycle %: {result['motorcycle_percentage']}%")
            
            # Show green times
            print("\n🚦 OPTIMIZED GREEN TIMES:")
            for lane in result['green_times']:
                bonus = f" (+{lane['motorcycle_bonus']}s 🏍️)" if lane.get('motorcycle_bonus') else ""
                print(f"Lane {lane['lane_id']}: {lane['green_time']}s{bonus}")
            
            # Save results
            with open('live_optimization_results.json', 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Results saved to: live_optimization_results.json")
            
    except Exception as e:
        print(f"❌ Optimization error: {e}")

def distribute_vehicles(total_counts, lane_num, total_lanes):
    """Distribute vehicles across lanes"""
    lane_counts = {}
    for v_type, total in total_counts.items():
        # Simple distribution: each lane gets roughly equal
        base = total // total_lanes
        extra = 1 if lane_num <= total % total_lanes else 0
        lane_counts[v_type] = base + extra
    return lane_counts

def simulated_demo():
    """Fallback demo if webcam not available"""
    
    print("📱 SIMULATED LIVE DEMO MODE")
    print("=" * 60)
    
    # Simulate traffic scenarios
    scenarios = [
        {"name": "Morning Peak", "counts": {"motorcycle": 12, "car": 6, "tuktuk": 4}},
        {"name": "School Zone", "counts": {"motorcycle": 8, "car": 4, "bicycle": 6}},
        {"name": "Highway", "counts": {"car": 10, "truck": 3, "bus": 2}},
        {"name": "Market Area", "counts": {"motorcycle": 15, "tuktuk": 5, "car": 3}}
    ]
    
    for i, scenario in enumerate(scenarios):
        print(f"\nScenario {i+1}: {scenario['name']}")
        print(f"Traffic: {scenario['counts']}")
        
        # Create lane data
        lane_data = {
            "intersection_id": f"demo_{scenario['name'].lower().replace(' ', '_')}",
            "time_of_day": "peak_hours",
            "lanes": [
                {
                    "lane_id": 1,
                    "direction": "north_south",
                    "vehicle_counts": scenario['counts']
                },
                {
                    "lane_id": 2,
                    "direction": "east_west",
                    "vehicle_counts": {k: max(1, v//2) for k, v in scenario['counts'].items()}
                }
            ]
        }
        
        # Run optimization
        try:
            response = requests.post(
                'http://127.0.0.1:8000/api/optimize/',
                json=lane_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  🚦 Congestion: {result['congestion_level'].upper()}")
                print(f"  ⏱️  Green times: {[l['green_time'] for l in result['green_times']]}s")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        time.sleep(2)  # Pause between scenarios
    
    print("\n" + "=" * 60)
    print("🎉 SIMULATION COMPLETE!")

if __name__ == "__main__":
    # Check if API is running
    try:
        response = requests.get('http://127.0.0.1:8000/', timeout=2)
        if response.status_code == 200:
            print("✅ API is running!")
            live_webcam_detection()
        else:
            print("❌ API not responding")
            simulated_demo()
    except:
        print("⚠️ Could not connect to API. Starting simulated demo...")
        simulated_demo()# live_demo.py
import cv2
import requests
import time
import json
from datetime import datetime

def live_webcam_detection():
    """Real-time traffic monitoring using webcam"""
    
    print("🎥 LIVE TRAFFIC MONITORING DEMONSTRATION")
    print("=" * 60)
    print("Point your webcam at:")
    print("1. Toy vehicles (cars, motorcycles)")
    print("2. Phone showing traffic videos")
    print("3. Printed traffic images")
    print("=" * 60)
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Webcam not available. Using simulated mode...")
        return simulated_demo()
    
    print("✅ Webcam connected! Starting live monitoring...")
    print("Press 'q' to quit, 's' to save snapshot")
    
    frame_count = 0
    detection_results = []
    
    while True:
        # Capture frame
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Process every 5th frame for performance
        if frame_count % 5 == 0:
            # Save frame temporarily
            temp_file = "temp_frame.jpg"
            cv2.imwrite(temp_file, frame)
            
            # Send to API for detection
            try:
                with open(temp_file, 'rb') as img:
                    files = {'image': img}
                    response = requests.post('http://127.0.0.1:8000/api/detect/', files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('success'):
                        vehicles = data.get('vehicles_detected', 0)
                        detections = data.get('detections', [])
                        
                        # Display results on frame
                        cv2.putText(frame, f"Vehicles: {vehicles}", (10, 30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        
                        # Count by type
                        counts = {}
                        for det in detections:
                            v_type = det.get('vehicle', 'unknown')
                            counts[v_type] = counts.get(v_type, 0) + 1
                        
                        y_pos = 70
                        for v_type, count in counts.items():
                            cv2.putText(frame, f"{v_type}: {count}", (10, y_pos), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                            y_pos += 30
                        
                        # Store for optimization
                        detection_results.append({
                            'timestamp': datetime.now().strftime("%H:%M:%S"),
                            'counts': counts,
                            'total': vehicles
                        })
                        
                        print(f"\r📊 Live: {vehicles} vehicles detected", end="")
                        
            except Exception as e:
                print(f"\n⚠️ Detection error: {e}")
        
        # Display frame
        cv2.imshow('Smart Traffic Optimizer - Live Demo', frame)
        
        # Check for key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Save snapshot
            filename = f"snapshot_{datetime.now().strftime('%H%M%S')}.jpg"
            cv2.imwrite(filename, frame)
            print(f"\n💾 Saved snapshot: {filename}")
        elif key == ord('o'):
            # Run optimization on collected data
            run_optimization(detection_results)
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    # Final summary
    print("\n\n📈 DEMO SUMMARY:")
    print("-" * 40)
    print(f"Frames processed: {frame_count}")
    print(f"Detection cycles: {len(detection_results)}")
    
    if detection_results:
        total_vehicles = sum(r['total'] for r in detection_results)
        print(f"Total vehicles detected: {total_vehicles}")
        
        # Save data for later analysis
        with open('live_demo_data.json', 'w') as f:
            json.dump(detection_results, f, indent=2)
        print(f"💾 Data saved to: live_demo_data.json")
        
        # Run final optimization
        run_optimization(detection_results)

def run_optimization(detection_results):
    """Run optimization based on collected data"""
    
    if not detection_results:
        print("❌ No data for optimization")
        return
    
    print("\n⚡ RUNNING TRAFFIC OPTIMIZATION...")
    
    # Aggregate data from all detections
    total_counts = {}
    for result in detection_results[-10:]:  # Last 10 detections
        for v_type, count in result['counts'].items():
            total_counts[v_type] = total_counts.get(v_type, 0) + count
    
    # Create lane data (simulating 4 lanes)
    lane_data = {
        "intersection_id": "live_demo_intersection",
        "time_of_day": "current",
        "lanes": [
            {
                "lane_id": 1,
                "direction": "northbound",
                "vehicle_counts": distribute_vehicles(total_counts, 1, 4)
            },
            {
                "lane_id": 2,
                "direction": "southbound",
                "vehicle_counts": distribute_vehicles(total_counts, 2, 4)
            },
            {
                "lane_id": 3,
                "direction": "eastbound",
                "vehicle_counts": distribute_vehicles(total_counts, 3, 4)
            },
            {
                "lane_id": 4,
                "direction": "westbound",
                "vehicle_counts": distribute_vehicles(total_counts, 4, 4)
            }
        ]
    }
    
    # Send to optimization API
    try:
        response = requests.post(
            'http://127.0.0.1:8000/api/optimize/',
            json=lane_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ OPTIMIZATION RESULTS:")
            print(f"Congestion level: {result['congestion_level'].upper()}")
            print(f"Total vehicles: {result['total_vehicles']}")
            print(f"Motorcycle %: {result['motorcycle_percentage']}%")
            
            # Show green times
            print("\n🚦 OPTIMIZED GREEN TIMES:")
            for lane in result['green_times']:
                bonus = f" (+{lane['motorcycle_bonus']}s 🏍️)" if lane.get('motorcycle_bonus') else ""
                print(f"Lane {lane['lane_id']}: {lane['green_time']}s{bonus}")
            
            # Save results
            with open('live_optimization_results.json', 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Results saved to: live_optimization_results.json")
            
    except Exception as e:
        print(f"❌ Optimization error: {e}")

def distribute_vehicles(total_counts, lane_num, total_lanes):
    """Distribute vehicles across lanes"""
    lane_counts = {}
    for v_type, total in total_counts.items():
        # Simple distribution: each lane gets roughly equal
        base = total // total_lanes
        extra = 1 if lane_num <= total % total_lanes else 0
        lane_counts[v_type] = base + extra
    return lane_counts

def simulated_demo():
    """Fallback demo if webcam not available"""
    
    print("📱 SIMULATED LIVE DEMO MODE")
    print("=" * 60)
    
    # Simulate traffic scenarios
    scenarios = [
        {"name": "Morning Peak", "counts": {"motorcycle": 12, "car": 6, "tuktuk": 4}},
        {"name": "School Zone", "counts": {"motorcycle": 8, "car": 4, "bicycle": 6}},
        {"name": "Highway", "counts": {"car": 10, "truck": 3, "bus": 2}},
        {"name": "Market Area", "counts": {"motorcycle": 15, "tuktuk": 5, "car": 3}}
    ]
    
    for i, scenario in enumerate(scenarios):
        print(f"\nScenario {i+1}: {scenario['name']}")
        print(f"Traffic: {scenario['counts']}")
        
        # Create lane data
        lane_data = {
            "intersection_id": f"demo_{scenario['name'].lower().replace(' ', '_')}",
            "time_of_day": "peak_hours",
            "lanes": [
                {
                    "lane_id": 1,
                    "direction": "north_south",
                    "vehicle_counts": scenario['counts']
                },
                {
                    "lane_id": 2,
                    "direction": "east_west",
                    "vehicle_counts": {k: max(1, v//2) for k, v in scenario['counts'].items()}
                }
            ]
        }
        
        # Run optimization
        try:
            response = requests.post(
                'http://127.0.0.1:8000/api/optimize/',
                json=lane_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  🚦 Congestion: {result['congestion_level'].upper()}")
                print(f"  ⏱️  Green times: {[l['green_time'] for l in result['green_times']]}s")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        time.sleep(2)  # Pause between scenarios
    
    print("\n" + "=" * 60)
    print("🎉 SIMULATION COMPLETE!")

if __name__ == "__main__":
    # Check if API is running
    try:
        response = requests.get('http://127.0.0.1:8000/', timeout=2)
        if response.status_code == 200:
            print("✅ API is running!")
            live_webcam_detection()
        else:
            print("❌ API not responding")
            simulated_demo()
    except:
        print("⚠️ Could not connect to API. Starting simulated demo...")
        simulated_demo()