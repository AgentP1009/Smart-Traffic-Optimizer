# ultimate_visualization.py
import pygame
import sys
import math
import random
import requests
import json
from datetime import datetime

# Initialize Pygame
pygame.init()

# Colors
BACKGROUND = (20, 30, 40)
ROAD_COLOR = (50, 50, 50)
LANE_MARKER = (255, 255, 255)
TEXT_COLOR = (255, 255, 255)
VEHICLE_COLORS = {
    'motorcycle': (255, 100, 100),  # Red
    'car': (100, 150, 255),         # Blue
    'tuktuk': (255, 200, 50),       # Yellow
    'bus': (100, 200, 100),         # Green
    'truck': (180, 100, 200),       # Purple
    'bicycle': (255, 150, 50)       # Orange
}

class TrafficSimulator2D:
    """Amazing 2D traffic visualization for teacher demonstration"""
    
    def __init__(self, width=1200, height=800):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("🇰🇭 Smart Traffic Optimizer - Real-Time Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 20)
        self.title_font = pygame.font.SysFont('Arial', 32, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 16)
        
        # Simulation data
        self.vehicles = []
        self.traffic_lights = []
        self.optimization_data = None
        self.detection_data = None
        self.simulation_time = 0
        self.green_times = [30, 30, 30, 30]  # Default green times
        self.current_green = 0  # Which lane has green light
        self.light_timer = 0
        
        # Statistics
        self.vehicles_passed = 0
        self.avg_wait_time = 0
        self.congestion_level = "Low"
        
        # Initialize intersection
        self.setup_intersection()
        self.spawn_initial_vehicles()
        
        # Try to load real optimization data
        self.load_real_data()
    
    def load_real_data(self):
        """Try to load real optimization data from API"""
        try:
            # Try to get optimization data
            test_data = {
                "lanes": [
                    {"lane_id": 1, "direction": "North", "vehicle_counts": {"motorcycle": 8, "car": 3}},
                    {"lane_id": 2, "direction": "South", "vehicle_counts": {"motorcycle": 5, "car": 4}},
                    {"lane_id": 3, "direction": "East", "vehicle_counts": {"motorcycle": 6, "car": 2}},
                    {"lane_id": 4, "direction": "West", "vehicle_counts": {"motorcycle": 10, "car": 3}}
                ]
            }
            
            response = requests.post(
                "http://127.0.0.1:8000/api/optimize/",
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=2
            )
            
            if response.status_code == 200:
                self.optimization_data = response.json()
                print("✅ Loaded real optimization data from API!")
                
                # Update green times based on real optimization
                if 'green_times' in self.optimization_data:
                    self.green_times = [lane['green_time'] for lane in self.optimization_data['green_times']]
                    print(f"🚦 Real green times: {self.green_times}")
        
        except:
            print("⚠️ Using simulated data (API not available)")
    
    def setup_intersection(self):
        """Setup the 4-way intersection"""
        # Define lanes (x, y, width, height, direction)
        self.lanes = [
            # Northbound (bottom to top)
            {"rect": pygame.Rect(550, 600, 100, 200), "direction": "north", "entry": (600, 800), "exit": (600, 0)},
            # Southbound (top to bottom)
            {"rect": pygame.Rect(550, 0, 100, 200), "direction": "south", "entry": (600, -100), "exit": (600, 800)},
            # Eastbound (left to right)
            {"rect": pygame.Rect(0, 350, 200, 100), "direction": "east", "entry": (-100, 400), "exit": (1200, 400)},
            # Westbound (right to left)
            {"rect": pygame.Rect(1000, 350, 200, 100), "direction": "west", "entry": (1300, 400), "exit": (-100, 400)}
        ]
        
        # Traffic lights at each lane
        for i, lane in enumerate(self.lanes):
            if lane["direction"] == "north":
                light_pos = (lane["rect"].x + lane["rect"].width + 10, lane["rect"].y + 50)
            elif lane["direction"] == "south":
                light_pos = (lane["rect"].x - 30, lane["rect"].y + lane["rect"].height - 50)
            elif lane["direction"] == "east":
                light_pos = (lane["rect"].x + lane["rect"].width - 50, lane["rect"].y - 30)
            else:  # west
                light_pos = (lane["rect"].x + 50, lane["rect"].y + lane["rect"].height + 10)
            
            self.traffic_lights.append({
                "lane": i,
                "position": light_pos,
                "state": "red",  # red, yellow, green
                "timer": 0
            })
    
    def spawn_initial_vehicles(self):
        """Spawn initial vehicles with Cambodian distribution"""
        vehicle_types = ['motorcycle'] * 52 + ['car'] * 25 + ['tuktuk'] * 15 + ['bus'] * 5 + ['truck'] * 3
        
        for _ in range(20):
            lane_idx = random.randint(0, 3)
            vehicle_type = random.choice(vehicle_types)
            self.spawn_vehicle(lane_idx, vehicle_type)
    
    def spawn_vehicle(self, lane_idx, vehicle_type):
        """Spawn a vehicle in a specific lane"""
        lane = self.lanes[lane_idx]
        
        # Vehicle properties based on type
        sizes = {
            'motorcycle': (15, 8),
            'car': (25, 12),
            'tuktuk': (20, 10),
            'bus': (35, 15),
            'truck': (40, 18),
            'bicycle': (12, 6)
        }
        
        width, height = sizes.get(vehicle_type, (20, 10))
        speed = random.uniform(1.0, 3.0)  # Slower for larger vehicles
        
        # Position vehicle at entry point
        if lane["direction"] == "north":
            x = lane["rect"].x + lane["rect"].width // 2 + random.randint(-20, 20)
            y = lane["entry"][1]
        elif lane["direction"] == "south":
            x = lane["rect"].x + lane["rect"].width // 2 + random.randint(-20, 20)
            y = lane["entry"][1]
        elif lane["direction"] == "east":
            x = lane["entry"][0]
            y = lane["rect"].y + lane["rect"].height // 2 + random.randint(-20, 20)
        else:  # west
            x = lane["entry"][0]
            y = lane["rect"].y + lane["rect"].height // 2 + random.randint(-20, 20)
        
        self.vehicles.append({
            "id": len(self.vehicles),
            "type": vehicle_type,
            "lane": lane_idx,
            "direction": lane["direction"],
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "speed": speed,
            "target_speed": speed,
            "waiting": False,
            "wait_time": 0,
            "color": VEHICLE_COLORS.get(vehicle_type, (200, 200, 200))
        })
    
    def update_traffic_lights(self):
        """Update traffic light states based on optimization"""
        self.light_timer += 1
        
        # Cycle through lanes based on green times
        total_cycle = sum(self.green_times) + len(self.green_times) * 3  # 3 seconds yellow each
        
        cycle_time = self.light_timer % (total_cycle * 60)  # Convert to frames (60 fps)
        
        # Calculate which lane should have green light
        accumulated_time = 0
        new_green = 0
        
        for i, green_time in enumerate(self.green_times):
            lane_cycle = green_time * 60  # Green time in frames
            if accumulated_time <= cycle_time < accumulated_time + lane_cycle:
                new_green = i
                # Set light states
                for j, light in enumerate(self.traffic_lights):
                    if j == i:
                        light["state"] = "green"
                    else:
                        light["state"] = "red"
                break
            accumulated_time += lane_cycle + 3 * 60  # Add yellow time
        
        if new_green != self.current_green:
            self.current_green = new_green
        
        # Update light timers
        for light in self.traffic_lights:
            light["timer"] += 1
    
    def update_vehicles(self):
        """Update all vehicle positions"""
        vehicles_to_remove = []
        
        for vehicle in self.vehicles:
            lane = self.lanes[vehicle["lane"]]
            light = self.traffic_lights[vehicle["lane"]]
            
            # Check if vehicle should stop at red light
            distance_to_intersection = self.get_distance_to_intersection(vehicle)
            
            if light["state"] == "red" and distance_to_intersection < 100:
                # Slow down for red light
                vehicle["target_speed"] = max(0.1, vehicle["target_speed"] * 0.95)
                vehicle["waiting"] = True
                vehicle["wait_time"] += 1
            else:
                # Accelerate to normal speed
                vehicle["target_speed"] = min(vehicle["speed"], vehicle["target_speed"] * 1.05)
                vehicle["waiting"] = False
            
            # Smooth speed adjustment
            vehicle["speed"] += (vehicle["target_speed"] - vehicle["speed"]) * 0.1
            
            # Move vehicle based on direction
            if vehicle["direction"] == "north":
                vehicle["y"] -= vehicle["speed"]
                if vehicle["y"] < -50:
                    vehicles_to_remove.append(vehicle)
                    self.vehicles_passed += 1
            elif vehicle["direction"] == "south":
                vehicle["y"] += vehicle["speed"]
                if vehicle["y"] > 850:
                    vehicles_to_remove.append(vehicle)
                    self.vehicles_passed += 1
            elif vehicle["direction"] == "east":
                vehicle["x"] += vehicle["speed"]
                if vehicle["x"] > 1250:
                    vehicles_to_remove.append(vehicle)
                    self.vehicles_passed += 1
            else:  # west
                vehicle["x"] -= vehicle["speed"]
                if vehicle["x"] < -50:
                    vehicles_to_remove.append(vehicle)
                    self.vehicles_passed += 1
        
        # Remove vehicles that exited
        for vehicle in vehicles_to_remove:
            self.vehicles.remove(vehicle)
        
        # Spawn new vehicles occasionally
        if random.random() < 0.05 and len(self.vehicles) < 40:
            lane_idx = random.randint(0, 3)
            vehicle_types = ['motorcycle'] * 52 + ['car'] * 25 + ['tuktuk'] * 15 + ['bus'] * 5 + ['truck'] * 3
            vehicle_type = random.choice(vehicle_types)
            self.spawn_vehicle(lane_idx, vehicle_type)
        
        # Update congestion level
        self.update_congestion()
    
    def get_distance_to_intersection(self, vehicle):
        """Calculate vehicle's distance to intersection center"""
        center_x, center_y = 600, 400  # Intersection center
        
        if vehicle["direction"] == "north":
            return abs(vehicle["y"] - center_y)
        elif vehicle["direction"] == "south":
            return abs(vehicle["y"] - center_y)
        elif vehicle["direction"] == "east":
            return abs(vehicle["x"] - center_x)
        else:  # west
            return abs(vehicle["x"] - center_x)
    
    def update_congestion(self):
        """Update congestion level based on traffic"""
        total_vehicles = len(self.vehicles)
        total_wait_time = sum(v["wait_time"] for v in self.vehicles)
        
        if total_vehicles > 0:
            self.avg_wait_time = total_wait_time / total_vehicles / 60  # Convert to seconds
        
        if total_vehicles > 30:
            self.congestion_level = "High"
        elif total_vehicles > 20:
            self.congestion_level = "Medium"
        else:
            self.congestion_level = "Low"
    
    def draw(self):
        """Draw everything on screen"""
        self.screen.fill(BACKGROUND)
        
        # Draw roads
        for lane in self.lanes:
            pygame.draw.rect(self.screen, ROAD_COLOR, lane["rect"])
            # Draw lane markers
            if lane["direction"] in ["north", "south"]:
                for y in range(lane["rect"].y, lane["rect"].y + lane["rect"].height, 40):
                    pygame.draw.rect(self.screen, LANE_MARKER, 
                                   (lane["rect"].x + lane["rect"].width//2 - 2, y, 4, 20))
            else:
                for x in range(lane["rect"].x, lane["rect"].x + lane["rect"].width, 40):
                    pygame.draw.rect(self.screen, LANE_MARKER,
                                   (x, lane["rect"].y + lane["rect"].height//2 - 2, 20, 4))
        
        # Draw intersection
        intersection_rect = pygame.Rect(500, 300, 200, 200)
        pygame.draw.rect(self.screen, (40, 40, 40), intersection_rect)
        
        # Draw vehicles
        for vehicle in self.vehicles:
            # Draw vehicle body
            pygame.draw.rect(self.screen, vehicle["color"],
                           (vehicle["x"] - vehicle["width"]//2,
                            vehicle["y"] - vehicle["height"]//2,
                            vehicle["width"], vehicle["height"]))
            
            # Draw vehicle type indicator
            type_text = self.small_font.render(vehicle["type"][0].upper(), True, (255, 255, 255))
            self.screen.blit(type_text, (vehicle["x"] - 5, vehicle["y"] - 8))
            
            # Draw waiting indicator if stopped
            if vehicle["waiting"]:
                pygame.draw.circle(self.screen, (255, 0, 0),
                                 (int(vehicle["x"]), int(vehicle["y"] - vehicle["height"]//2 - 10)), 3)
        
        # Draw traffic lights
        for light in self.traffic_lights:
            # Draw light pole
            pygame.draw.rect(self.screen, (100, 100, 100),
                           (light["position"][0] - 5, light["position"][1] - 30, 10, 40))
            
            # Draw lights
            colors = {"red": (255, 0, 0), "yellow": (255, 255, 0), "green": (0, 255, 0)}
            light_color = colors.get(light["state"], (100, 100, 100))
            
            pygame.draw.circle(self.screen, light_color,
                             (int(light["position"][0]), int(light["position"][1])), 8)
            
            # Draw light state text
            state_text = self.small_font.render(light["state"][0].upper(), True, (255, 255, 255))
            self.screen.blit(state_text, (light["position"][0] - 5, light["position"][1] - 20))
        
        # Draw statistics panel
        self.draw_statistics_panel()
        
        # Draw optimization info if available
        self.draw_optimization_info()
        
        # Draw title
        title = self.title_font.render("🇰🇭 Smart Traffic Optimizer - Cambodia Simulation", True, TEXT_COLOR)
        self.screen.blit(title, (self.width//2 - title.get_width()//2, 10))
        
        pygame.display.flip()
    
    def draw_statistics_panel(self):
        """Draw statistics panel on the right side"""
        panel_rect = pygame.Rect(self.width - 300, 50, 280, 300)
        pygame.draw.rect(self.screen, (30, 40, 50), panel_rect)
        pygame.draw.rect(self.screen, (50, 100, 150), panel_rect, 2)
        
        # Panel title
        panel_title = self.font.render("REAL-TIME STATISTICS", True, (100, 200, 255))
        self.screen.blit(panel_title, (panel_rect.x + 10, panel_rect.y + 10))
        
        stats = [
            f"Simulation Time: {self.simulation_time // 60:02d}:{self.simulation_time % 60:02d}",
            f"Total Vehicles: {len(self.vehicles)}",
            f"Vehicles Passed: {self.vehicles_passed}",
            f"Congestion Level: {self.congestion_level}",
            f"Avg Wait Time: {self.avg_wait_time:.1f}s",
            "",
            "🇰🇭 CAMBODIA TRAFFIC:",
            f"• Motorcycles: {sum(1 for v in self.vehicles if v['type'] == 'motorcycle')}",
            f"• Cars: {sum(1 for v in self.vehicles if v['type'] == 'car')}",
            f"• Tuktuks: {sum(1 for v in self.vehicles if v['type'] == 'tuktuk')}",
            f"• Buses/Trucks: {sum(1 for v in self.vehicles if v['type'] in ['bus', 'truck'])}"
        ]
        
        y_offset = 50
        for stat in stats:
            if "🇰🇭" in stat:
                text = self.small_font.render(stat, True, (255, 200, 100))
            else:
                text = self.small_font.render(stat, True, TEXT_COLOR)
            self.screen.blit(text, (panel_rect.x + 10, panel_rect.y + y_offset))
            y_offset += 25
    
    def draw_optimization_info(self):
        """Draw optimization information"""
        if self.optimization_data:
            panel_rect = pygame.Rect(10, 400, 350, 200)
            pygame.draw.rect(self.screen, (30, 40, 50), panel_rect)
            pygame.draw.rect(self.screen, (150, 100, 50), panel_rect, 2)
            
            title = self.font.render("AI OPTIMIZATION RESULTS", True, (255, 200, 100))
            self.screen.blit(title, (panel_rect.x + 10, panel_rect.y + 10))
            
            info = [
                f"Congestion: {self.optimization_data.get('congestion_level', 'N/A').upper()}",
                f"Total Vehicles: {self.optimization_data.get('total_vehicles', 0)}",
                f"Motorcycles: {self.optimization_data.get('total_motorcycles', 0)}",
                "",
                "🚦 OPTIMIZED GREEN TIMES:"
            ]
            
            y_offset = 50
            for line in info:
                text = self.small_font.render(line, True, TEXT_COLOR)
                self.screen.blit(text, (panel_rect.x + 10, panel_rect.y + y_offset))
                y_offset += 25
            
            # Draw green time bars
            if 'green_times' in self.optimization_data:
                bar_x = panel_rect.x + 10
                bar_y = panel_rect.y + y_offset
                bar_height = 15
                
                for i, lane in enumerate(self.optimization_data['green_times'][:4]):
                    green_time = lane['green_time']
                    max_green = 60
                    bar_width = (green_time / max_green) * 200
                    
                    # Draw bar
                    color = (100, 200, 100) if lane.get('motorcycle_bonus') else (100, 150, 255)
                    pygame.draw.rect(self.screen, color,
                                   (bar_x, bar_y, bar_width, bar_height))
                    
                    # Draw text
                    time_text = self.small_font.render(f"L{i+1}: {green_time}s", True, TEXT_COLOR)
                    self.screen.blit(time_text, (bar_x + bar_width + 5, bar_y - 2))
                    
                    bar_y += 25
    
    def run(self):
        """Main simulation loop"""
        running = True
        
        print("\n" + "=" * 60)
        print("🇰🇭 SMART TRAFFIC OPTIMIZER - REAL-TIME SIMULATION")
        print("=" * 60)
        print("Controls:")
        print("  • SPACE: Pause/Resume simulation")
        print("  • R: Reset simulation")
        print("  • 1-4: Manually set green light to lane 1-4")
        print("  • ESC: Exit simulation")
        print("=" * 60)
        
        paused = False
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                        print(f"⏸️  Simulation {'paused' if paused else 'resumed'}")
                    elif event.key == pygame.K_r:
                        self.reset_simulation()
                        print("🔄 Simulation reset")
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                        lane_idx = event.key - pygame.K_1
                        self.manual_green_light(lane_idx)
                        print(f"🚦 Manual green light: Lane {lane_idx + 1}")
            
            if not paused:
                # Update simulation
                self.update_traffic_lights()
                self.update_vehicles()
                self.simulation_time += 1
                
                # Update FPS in window title
                fps = self.clock.get_fps()
                pygame.display.set_caption(
                    f"🇰🇭 Smart Traffic Optimizer - FPS: {fps:.1f} | Vehicles: {len(self.vehicles)} | Congestion: {self.congestion_level}"
                )
            
            # Draw everything
            self.draw()
            
            # Control frame rate
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def reset_simulation(self):
        """Reset the simulation"""
        self.vehicles = []
        self.vehicles_passed = 0
        self.avg_wait_time = 0
        self.simulation_time = 0
        self.light_timer = 0
        self.spawn_initial_vehicles()
    
    def manual_green_light(self, lane_idx):
        """Manually set green light to specific lane"""
        for i, light in enumerate(self.traffic_lights):
            if i == lane_idx:
                light["state"] = "green"
            else:
                light["state"] = "red"
        self.current_green = lane_idx
        self.light_timer = 0

# Simple version without real API calls (for backup)
class SimpleTrafficSimulator:
    """Simple traffic simulator without API dependencies"""
    
    def __init__(self):
        self.width = 1000
        self.height = 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Traffic Simulation - Cambodia")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Simple intersection
        self.roads = [
            pygame.Rect(400, 0, 200, 700),  # Vertical
            pygame.Rect(0, 300, 1000, 100)   # Horizontal
        ]
        
        self.vehicles = []
        self.spawn_timer = 0
        
    def spawn_vehicle(self):
        """Spawn a vehicle"""
        vehicle_types = ['motorcycle', 'car', 'tuktuk', 'bus']
        colors = [(255, 100, 100), (100, 150, 255), (255, 200, 50), (100, 200, 100)]
        
        vtype = random.choice(vehicle_types)
        color = colors[vehicle_types.index(vtype)]
        
        self.vehicles.append({
            'x': random.randint(0, self.width),
            'y': random.randint(0, self.height),
            'speed': random.uniform(1, 3),
            'color': color,
            'type': vtype,
            'direction': random.choice(['left', 'right', 'up', 'down'])
        })
    
    def run(self):
        """Run simple simulator"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            # Spawn vehicles
            self.spawn_timer += 1
            if self.spawn_timer > 30 and len(self.vehicles) < 30:
                self.spawn_vehicle()
                self.spawn_timer = 0
            
            # Update vehicles
            for v in self.vehicles:
                if v['direction'] == 'left':
                    v['x'] -= v['speed']
                elif v['direction'] == 'right':
                    v['x'] += v['speed']
                elif v['direction'] == 'up':
                    v['y'] -= v['speed']
                else:
                    v['y'] += v['speed']
                
                # Remove if out of bounds
                if v['x'] < -50 or v['x'] > self.width + 50 or v['y'] < -50 or v['y'] > self.height + 50:
                    self.vehicles.remove(v)
            
            # Draw
            self.screen.fill((20, 30, 40))
            
            # Draw roads
            for road in self.roads:
                pygame.draw.rect(self.screen, (50, 50, 50), road)
                pygame.draw.rect(self.screen, (100, 100, 100), road, 2)
            
            # Draw vehicles
            for v in self.vehicles:
                pygame.draw.circle(self.screen, v['color'], (int(v['x']), int(v['y'])), 10)
                # Draw type indicator
                font = pygame.font.SysFont('Arial', 12)
                text = font.render(v['type'][0].upper(), True, (255, 255, 255))
                self.screen.blit(text, (v['x'] - 4, v['y'] - 6))
            
            # Draw stats
            font = pygame.font.SysFont('Arial', 24)
            stats = font.render(f"Vehicles: {len(self.vehicles)} | Cambodia Traffic Sim", True, (255, 255, 255))
            self.screen.blit(stats, (20, 20))
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

# Main execution
if __name__ == "__main__":
    print("Select visualization mode:")
    print("1. Full AI-Optimized Simulation (Requires API)")
    print("2. Simple Traffic Visualization")
    print("3. Exit")
    
    choice = input("Enter choice (1-3): ").strip()
    
    try:
        if choice == "1":
            print("🚀 Starting Full AI-Optimized Simulation...")
            simulator = TrafficSimulator2D()
            simulator.run()
        elif choice == "2":
            print("🚗 Starting Simple Traffic Visualization...")
            simulator = SimpleTrafficSimulator()
            simulator.run()
        else:
            print("Goodbye!")
    except pygame.error as e:
        print(f"❌ Pygame error: {e}")
        print("Make sure you have a display available or try the simple version.")
    except Exception as e:
        print(f"❌ Error: {e}")