# traffic_simulation_demo.py
import pygame
import sys
import random
import requests
import json
import time
from datetime import datetime

class TrafficLightOptimizationDemo:
    """Interactive demo like the YouTube video but better"""
    
    def __init__(self):
        pygame.init()
        self.width = 1200
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("🇰🇭 Smart Traffic Optimizer - Live Demo")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.title_font = pygame.font.SysFont('Arial', 32, bold=True)
        
        # Colors
        self.colors = {
            'road': (50, 50, 50),
            'intersection': (40, 40, 40),
            'lane_marker': (255, 255, 200),
            'vehicle_motorcycle': (255, 100, 100),  # Red
            'vehicle_car': (100, 150, 255),         # Blue
            'vehicle_tuktuk': (255, 200, 50),       # Yellow
            'vehicle_bus': (100, 200, 100),         # Green
            'light_red': (255, 50, 50),
            'light_green': (50, 255, 50),
            'light_yellow': (255, 255, 50),
            'text': (255, 255, 255),
            'panel': (30, 40, 50)
        }
        
        # Simulation state
        self.vehicles = []
        self.traffic_lights = []
        self.optimization_results = None
        self.simulation_time = 0
        self.vehicles_passed = 0
        self.total_wait_time = 0
        
        # API connection
        self.api_base = "http://127.0.0.1:8000"
        
        # Initialize
        self.setup_intersection()
        self.spawn_initial_vehicles()
        self.load_optimization_data()
        
        # Statistics
        self.stats = {
            'total_vehicles': 0,
            'motorcycles': 0,
            'avg_wait_time': 0,
            'congestion': 'Low',
            'optimization_cycles': 0
        }
    
    def setup_intersection(self):
        """Setup a 4-way intersection"""
        # Define 4 lanes
        self.lanes = [
            # North (bottom to top)
            {
                'id': 1,
                'name': 'Northbound',
                'entry': (600, 750),
                'exit': (600, 50),
                'queue': [],
                'light_pos': (650, 400),
                'green_time': 30,
                'vehicle_counts': {'motorcycle': 0, 'car': 0, 'tuktuk': 0}
            },
            # South (top to bottom)
            {
                'id': 2,
                'name': 'Southbound',
                'entry': (600, 50),
                'exit': (600, 750),
                'queue': [],
                'light_pos': (550, 400),
                'green_time': 30,
                'vehicle_counts': {'motorcycle': 0, 'car': 0, 'tuktuk': 0}
            },
            # East (left to right)
            {
                'id': 3,
                'name': 'Eastbound',
                'entry': (50, 400),
                'exit': (1150, 400),
                'queue': [],
                'light_pos': (600, 350),
                'green_time': 30,
                'vehicle_counts': {'motorcycle': 0, 'car': 0, 'tuktuk': 0}
            },
            # West (right to left)
            {
                'id': 4,
                'name': 'Westbound',
                'entry': (1150, 400),
                'exit': (50, 400),
                'queue': [],
                'light_pos': (600, 450),
                'green_time': 30,
                'vehicle_counts': {'motorcycle': 0, 'car': 0, 'tuktuk': 0}
            }
        ]
        
        # Initialize traffic lights
        for lane in self.lanes:
            self.traffic_lights.append({
                'lane_id': lane['id'],
                'state': 'red',  # red, yellow, green
                'timer': 0,
                'position': lane['light_pos']
            })
    
    def spawn_initial_vehicles(self):
        """Spawn initial vehicles with Cambodian distribution"""
        vehicle_types = ['motorcycle'] * 52 + ['car'] * 25 + ['tuktuk'] * 15 + ['bus'] * 5 + ['truck'] * 3
        
        for _ in range(20):
            lane = random.choice(self.lanes)
            vehicle_type = random.choice(vehicle_types)
            self.spawn_vehicle(lane, vehicle_type)
    
    def spawn_vehicle(self, lane, vehicle_type):
        """Spawn a vehicle in a lane"""
        # Vehicle properties
        sizes = {
            'motorcycle': (4, 8),
            'car': (6, 12),
            'tuktuk': (5, 10),
            'bus': (8, 16),
            'truck': (10, 20)
        }
        
        width, height = sizes.get(vehicle_type, (6, 12))
        speed = random.uniform(1.5, 3.0)
        
        vehicle = {
            'id': len(self.vehicles),
            'type': vehicle_type,
            'lane_id': lane['id'],
            'x': lane['entry'][0],
            'y': lane['entry'][1],
            'width': width,
            'height': height,
            'speed': speed,
            'target_speed': speed,
            'waiting': False,
            'wait_time': 0,
            'color': self.get_vehicle_color(vehicle_type),
            'passed': False
        }
        
        self.vehicles.append(vehicle)
        lane['vehicle_counts'][vehicle_type] = lane['vehicle_counts'].get(vehicle_type, 0) + 1
        self.stats['total_vehicles'] += 1
        if vehicle_type == 'motorcycle':
            self.stats['motorcycles'] += 1
    
    def get_vehicle_color(self, vehicle_type):
        """Get color for vehicle type"""
        colors = {
            'motorcycle': self.colors['vehicle_motorcycle'],
            'car': self.colors['vehicle_car'],
            'tuktuk': self.colors['vehicle_tuktuk'],
            'bus': self.colors['vehicle_bus'],
            'truck': self.colors['vehicle_bus']
        }
        return colors.get(vehicle_type, (200, 200, 200))
    
    def load_optimization_data(self):
        """Load optimization data from your API"""
        try:
            # Prepare data for your optimization API
            lanes_data = []
            for lane in self.lanes:
                lanes_data.append({
                    'lane_id': lane['id'],
                    'direction': lane['name'],
                    'vehicle_counts': lane['vehicle_counts']
                })
            
            optimization_request = {
                'intersection_id': 'demo_intersection',
                'time_of_day': 'demo',
                'lanes': lanes_data
            }
            
            response = requests.post(
                f"{self.api_base}/api/optimize/",
                json=optimization_request,
                headers={'Content-Type': 'application/json'},
                timeout=3
            )
            
            if response.status_code == 200:
                self.optimization_results = response.json()
                print("✅ Loaded optimization from YOUR API!")
                
                # Update green times based on optimization
                if 'green_times' in self.optimization_results:
                    for opt_lane in self.optimization_results['green_times']:
                        lane_id = opt_lane['lane_id']
                        for lane in self.lanes:
                            if lane['id'] == lane_id:
                                lane['green_time'] = opt_lane['green_time']
                                break
                
                self.stats['optimization_cycles'] += 1
                
        except Exception as e:
            print(f"⚠️ Using simulated optimization: {e}")
            # Use simulated optimization if API fails
            self.optimization_results = {
                'congestion_level': 'Medium',
                'total_vehicles': self.stats['total_vehicles'],
                'motorcycle_percentage': (self.stats['motorcycles'] / max(1, self.stats['total_vehicles'])) * 100
            }
    
    def update_traffic_lights(self):
        """Update traffic light states based on optimization"""
        self.simulation_time += 1
        
        # Calculate which lane should have green light
        cycle_position = self.simulation_time % 120  # 120-frame cycle
        
        # Distribute green time based on optimization
        green_lane = 1  # Default
        if cycle_position < 30:
            green_lane = 1
        elif cycle_position < 60:
            green_lane = 2
        elif cycle_position < 90:
            green_lane = 3
        else:
            green_lane = 4
        
        # Update light states
        for light in self.traffic_lights:
            if light['lane_id'] == green_lane:
                light['state'] = 'green'
            else:
                light['state'] = 'red'
            light['timer'] += 1
    
    def update_vehicles(self):
        """Update all vehicle positions"""
        vehicles_to_remove = []
        
        for vehicle in self.vehicles:
            lane = self.lanes[vehicle['lane_id'] - 1]
            light_state = self.traffic_lights[vehicle['lane_id'] - 1]['state']
            
            # Calculate distance to intersection center
            distance_to_center = abs(vehicle['x'] - 600) + abs(vehicle['y'] - 400)
            
            # Check if vehicle should stop at red light
            if light_state == 'red' and distance_to_center < 100:
                vehicle['target_speed'] = max(0.1, vehicle['target_speed'] * 0.9)
                vehicle['waiting'] = True
                vehicle['wait_time'] += 1
                self.total_wait_time += 1
            else:
                vehicle['target_speed'] = min(vehicle['speed'], vehicle['target_speed'] * 1.05)
                vehicle['waiting'] = False
            
            # Smooth speed adjustment
            vehicle['speed'] += (vehicle['target_speed'] - vehicle['speed']) * 0.1
            
            # Move vehicle based on lane direction
            if lane['id'] == 1:  # North
                vehicle['y'] -= vehicle['speed']
                if vehicle['y'] < lane['exit'][1]:
                    vehicles_to_remove.append(vehicle)
                    self.vehicles_passed += 1
            elif lane['id'] == 2:  # South
                vehicle['y'] += vehicle['speed']
                if vehicle['y'] > lane['exit'][1]:
                    vehicles_to_remove.append(vehicle)
                    self.vehicles_passed += 1
            elif lane['id'] == 3:  # East
                vehicle['x'] += vehicle['speed']
                if vehicle['x'] > lane['exit'][0]:
                    vehicles_to_remove.append(vehicle)
                    self.vehicles_passed += 1
            else:  # West
                vehicle['x'] -= vehicle['speed']
                if vehicle['x'] < lane['exit'][0]:
                    vehicles_to_remove.append(vehicle)
                    self.vehicles_passed += 1
        
        # Remove vehicles that exited
        for vehicle in vehicles_to_remove:
            self.vehicles.remove(vehicle)
        
        # Spawn new vehicles occasionally
        if random.random() < 0.03 and len(self.vehicles) < 50:
            lane = random.choice(self.lanes)
            vehicle_types = ['motorcycle'] * 52 + ['car'] * 25 + ['tuktuk'] * 15
            vehicle_type = random.choice(vehicle_types)
            self.spawn_vehicle(lane, vehicle_type)
        
        # Update statistics
        self.update_statistics()
        
        # Re-optimize every 5 seconds (300 frames at 60 FPS)
        if self.simulation_time % 300 == 0:
            self.load_optimization_data()
    
    def update_statistics(self):
        """Update simulation statistics"""
        if len(self.vehicles) > 0:
            avg_wait = sum(v['wait_time'] for v in self.vehicles) / len(self.vehicles)
            self.stats['avg_wait_time'] = avg_wait / 60  # Convert to seconds
        
        # Update congestion level
        vehicle_count = len(self.vehicles)
        if vehicle_count > 35:
            self.stats['congestion'] = 'High'
        elif vehicle_count > 20:
            self.stats['congestion'] = 'Medium'
        else:
            self.stats['congestion'] = 'Low'
    
    def draw(self):
        """Draw everything on screen"""
        self.screen.fill((20, 30, 40))
        
        # Draw roads
        self.draw_roads()
        
        # Draw intersection
        pygame.draw.rect(self.screen, self.colors['intersection'], (550, 350, 100, 100))
        
        # Draw vehicles
        for vehicle in self.vehicles:
            pygame.draw.rect(self.screen, vehicle['color'],
                           (vehicle['x'] - vehicle['width']//2,
                            vehicle['y'] - vehicle['height']//2,
                            vehicle['width'], vehicle['height']))
            
            # Draw waiting indicator
            if vehicle['waiting']:
                pygame.draw.circle(self.screen, (255, 50, 50),
                                 (int(vehicle['x']), int(vehicle['y'] - vehicle['height']//2 - 5)), 3)
        
        # Draw traffic lights
        for light in self.traffic_lights:
            color = self.colors[f'light_{light["state"]}']
            pygame.draw.circle(self.screen, color, light['position'], 10)
            
            # Draw light state text
            state_text = self.font.render(light['state'][0].upper(), True, (255, 255, 255))
            self.screen.blit(state_text, (light['position'][0] - 5, light['position'][1] - 20))
        
        # Draw UI panels
        self.draw_ui_panels()
        
        # Draw title
        title = self.title_font.render("🇰🇭 Smart Traffic Optimizer - Live Simulation", True, self.colors['text'])
        self.screen.blit(title, (self.width//2 - title.get_width()//2, 10))
        
        pygame.display.flip()
    
    def draw_roads(self):
        """Draw the road network"""
        # Main vertical road
        pygame.draw.rect(self.screen, self.colors['road'], (550, 0, 100, self.height))
        # Main horizontal road
        pygame.draw.rect(self.screen, self.colors['road'], (0, 350, self.width, 100))
        
        # Lane markers
        for y in range(50, self.height, 40):
            pygame.draw.rect(self.screen, self.colors['lane_marker'], (595, y, 10, 20))
        
        for x in range(50, self.width, 40):
            pygame.draw.rect(self.screen, self.colors['lane_marker'], (x, 395, 20, 10))
    
    def draw_ui_panels(self):
        """Draw UI panels with statistics"""
        # Left panel: Real-time stats
        left_panel = pygame.Rect(20, 80, 350, 300)
        pygame.draw.rect(self.screen, self.colors['panel'], left_panel)
        pygame.draw.rect(self.screen, (50, 100, 150), left_panel, 3)
        
        stats_title = self.font.render("REAL-TIME STATISTICS", True, (100, 200, 255))
        self.screen.blit(stats_title, (left_panel.x + 10, left_panel.y + 10))
        
        stats = [
            f"Simulation Time: {self.simulation_time//60:02d}:{self.simulation_time%60:02d}",
            f"Total Vehicles: {len(self.vehicles)}",
            f"Vehicles Passed: {self.vehicles_passed}",
            f"Average Wait Time: {self.stats['avg_wait_time']:.1f}s",
            f"Congestion Level: {self.stats['congestion']}",
            "",
            "🇰🇭 CAMBODIA TRAFFIC:",
            f"Motorcycles: {self.stats['motorcycles']}",
            f"Motorcycle %: {(self.stats['motorcycles']/max(1,self.stats['total_vehicles'])*100):.1f}%"
        ]
        
        y_offset = 50
        for stat in stats:
            if "🇰🇭" in stat:
                text = self.font.render(stat, True, (255, 200, 100))
            else:
                text = self.font.render(stat, True, self.colors['text'])
            self.screen.blit(text, (left_panel.x + 10, left_panel.y + y_offset))
            y_offset += 30
        
        # Right panel: Optimization results
        right_panel = pygame.Rect(self.width - 370, 80, 350, 300)
        pygame.draw.rect(self.screen, self.colors['panel'], right_panel)
        pygame.draw.rect(self.screen, (150, 100, 50), right_panel, 3)
        
        opt_title = self.font.render("AI OPTIMIZATION RESULTS", True, (255, 200, 100))
        self.screen.blit(opt_title, (right_panel.x + 10, right_panel.y + 10))
        
        if self.optimization_results:
            opt_stats = [
                f"Optimization Cycles: {self.stats['optimization_cycles']}",
                f"Congestion: {self.optimization_results.get('congestion_level', 'N/A').upper()}",
                f"Total Vehicles: {self.optimization_results.get('total_vehicles', 0)}",
                f"Motorcycle %: {self.optimization_results.get('motorcycle_percentage', 0):.1f}%",
                "",
                "🚦 OPTIMIZED GREEN TIMES:"
            ]
            
            y_offset = 50
            for stat in opt_stats:
                text = self.font.render(stat, True, self.colors['text'])
                self.screen.blit(text, (right_panel.x + 10, right_panel.y + y_offset))
                y_offset += 30
            
            # Draw green time bars
            if 'green_times' in self.optimization_results:
                bar_y = right_panel.y + y_offset
                for opt_lane in self.optimization_results['green_times']:
                    lane_id = opt_lane['lane_id']
                    green_time = opt_lane['green_time']
                    
                    # Find lane name
                    lane_name = ""
                    for lane in self.lanes:
                        if lane['id'] == lane_id:
                            lane_name = lane['name']
                            break
                    
                    # Draw bar
                    bar_width = (green_time / 60) * 150
                    color = (100, 200, 100) if opt_lane.get('motorcycle_bonus') else (100, 150, 255)
                    pygame.draw.rect(self.screen, color,
                                   (right_panel.x + 10, bar_y, bar_width, 20))
                    
                    # Draw text
                    bar_text = self.font.render(f"{lane_name}: {green_time}s", True, self.colors['text'])
                    self.screen.blit(bar_text, (right_panel.x + bar_width + 15, bar_y))
                    
                    bar_y += 30
    
    def run(self):
        """Main simulation loop"""
        running = True
        
        print("\n" + "=" * 60)
        print("🎮 SMART TRAFFIC OPTIMIZER - INTERACTIVE DEMO")
        print("=" * 60)
        print("Controls:")
        print("  • SPACE: Pause/Resume simulation")
        print("  • R: Reset simulation")
        print("  • O: Run optimization using YOUR API")
        print("  • 1-4: Manually set green light")
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
                    elif event.key == pygame.K_o:
                        print("🔄 Running optimization using YOUR API...")
                        self.load_optimization_data()
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                        lane_idx = event.key - pygame.K_1
                        self.manual_green_light(lane_idx + 1)
                        print(f"🚦 Manual green light: Lane {lane_idx + 1}")
            
            if not paused:
                self.update_traffic_lights()
                self.update_vehicles()
                
                # Update window title with FPS
                fps = self.clock.get_fps()
                pygame.display.set_caption(
                    f"🇰🇭 Smart Traffic Optimizer - FPS: {fps:.1f} | Vehicles: {len(self.vehicles)} | Passed: {self.vehicles_passed}"
                )
            
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def reset_simulation(self):
        """Reset the simulation"""
        self.vehicles = []
        self.vehicles_passed = 0
        self.total_wait_time = 0
        self.simulation_time = 0
        self.stats = {
            'total_vehicles': 0,
            'motorcycles': 0,
            'avg_wait_time': 0,
            'congestion': 'Low',
            'optimization_cycles': 0
        }
        
        for lane in self.lanes:
            lane['vehicle_counts'] = {'motorcycle': 0, 'car': 0, 'tuktuk': 0}
        
        self.spawn_initial_vehicles()
        self.load_optimization_data()
    
    def manual_green_light(self, lane_id):
        """Manually set green light to specific lane"""
        for light in self.traffic_lights:
            if light['lane_id'] == lane_id:
                light['state'] = 'green'
            else:
                light['state'] = 'red'

# Simple version without API calls
class SimpleTrafficDemo:
    """Simple demo without API dependencies"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Traffic Light Optimization Demo")
        self.clock = pygame.time.Clock()
        
        self.vehicles = []
        self.lights = ['red', 'red', 'red', 'red']
        self.simulation_time = 0
        
    def run(self):
        """Run simple demo"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # Update simulation
            self.simulation_time += 1
            
            # Draw
            self.screen.fill((20, 30, 40))
            
            # Draw roads
            pygame.draw.rect(self.screen, (50, 50, 50), (350, 0, 100, 600))
            pygame.draw.rect(self.screen, (50, 50, 50), (0, 250, 800, 100))
            
            # Draw stats
            font = pygame.font.SysFont('Arial', 24)
            stats = font.render(f"Time: {self.simulation_time} | Vehicles: {len(self.vehicles)}", True, (255, 255, 255))
            self.screen.blit(stats, (20, 20))
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    print("Select demo mode:")
    print("1. Full AI-Optimized Simulation (Connects to YOUR API)")
    print("2. Simple Traffic Demo")
    
    choice = input("Enter choice (1-2): ").strip()
    
    try:
        if choice == "1":
            print("🚀 Starting full AI-optimized simulation...")
            print("📡 Connecting to YOUR API at: http://127.0.0.1:8000/")
            demo = TrafficLightOptimizationDemo()
            demo.run()
        else:
            print("🚗 Starting simple traffic demo...")
            demo = SimpleTrafficDemo()
            demo.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure Pygame is installed: pip install pygame")