# text_demo.py
import time
import random

def text_traffic_simulation():
    """Simple text-based traffic simulation"""
    
    print("\n" + "=" * 60)
    print("🇰🇭 SMART TRAFFIC OPTIMIZER - TEXT SIMULATION")
    print("=" * 60)
    
    lanes = [
        {"name": "North to Center", "vehicles": 8, "motorcycles": 5},
        {"name": "South to Riverside", "vehicles": 6, "motorcycles": 3},
        {"name": "East to AEON Mall", "vehicles": 7, "motorcycles": 4},
        {"name": "West to Airport", "vehicles": 10, "motorcycles": 7}
    ]
    
    for second in range(1, 31):  # 30-second simulation
        print(f"\n⏱️  Second {second}:")
        
        # Show lane status
        for lane in lanes:
            vehicles = lane["vehicles"]
            motorcycles = lane["motorcycles"]
            wait_time = random.randint(1, vehicles * 2)
            
            # Simple "traffic" visualization
            traffic_bar = "🚗" * min(vehicles, 5) + "🏍️" * min(motorcycles, 5)
            if vehicles > 5 or motorcycles > 5:
                traffic_bar += f"...({vehicles} vehicles)"
            
            print(f"  {lane['name']:20} {traffic_bar} Wait: {wait_time}s")
        
        # Simulate traffic light changes
        if second % 5 == 0:
            green_lane = (second // 5) % 4
            print(f"\n  🚦 GREEN LIGHT: {lanes[green_lane]['name']}")
            
            # Reduce vehicles in green lane
            if lanes[green_lane]["vehicles"] > 0:
                lanes[green_lane]["vehicles"] -= random.randint(1, 3)
                lanes[green_lane]["motorcycles"] = max(0, lanes[green_lane]["motorcycles"] - random.randint(0, 2))
        
        # Add new vehicles
        if random.random() < 0.3:
            new_lane = random.randint(0, 3)
            lanes[new_lane]["vehicles"] += random.randint(1, 3)
            if random.random() < 0.6:  # 60% chance new vehicle is motorcycle (Cambodia!)
                lanes[new_lane]["motorcycles"] += 1
        
        time.sleep(0.5)  # Slow down for viewing
    
    print("\n" + "=" * 60)
    print("📊 SIMULATION COMPLETE - FINAL STATISTICS:")
    total_vehicles = sum(l["vehicles"] for l in lanes)
    total_motorcycles = sum(l["motorcycles"] for l in lanes)
    print(f"  Total vehicles: {total_vehicles}")
    print(f"  Motorcycles: {total_motorcycles} ({total_motorcycles/total_vehicles*100:.1f}%)")
    print(f"  🇰🇭 Typical Cambodian traffic: 52% motorcycles")
    print("=" * 60)

if __name__ == "__main__":
    text_traffic_simulation()