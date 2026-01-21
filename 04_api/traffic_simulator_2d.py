# traffic_simulator_2d.py
import pygame
import requests
import random
import json
import threading
import time
from datetime import datetime

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🚦 Smart Traffic Optimizer - 2D Simulation")

# Colors
BACKGROUND = (40, 44, 52)
ROAD_COLOR = (60, 63, 65)
LANE_COLOR = (100, 100, 100)
WHITE = (255, 255, 255)
GREEN = (76, 175, 80)
RED = (244, 67, 54)
YELLOW = (255, 235, 59)
BLUE = (33, 150, 243)
ORANGE = (255, 152, 0)
PURPLE = (156, 39, 176)

# Vehicle colors by type
VEHICLE_COLORS = {
    "motorcycle": (255, 193, 7),   # Yellow
    "car": (33, 150, 243),         # Blue
    "tuktuk": (233, 30, 99),       # Pink
    "bus": (0, 150, 136),          # Teal
    "truck": (121, 85, 72),        # Brown
    "bicycle": (139, 195, 74)      # Light green
}

class Intersection:
    def __init__(self, x, y, width, height, lanes=4):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.lanes = lanes
        
        # Lane definitions
        self.lane_data = []
        self.green_times = [30, 30, 30, 30]  # Default 30s each
        self.current_green = 0
        self.signal_timer = 0
        self.signal_state = "green"  # green, yellow, red
        
        # Vehicle queues per lane
        self.vehicle_queues = [[] for _ in range(lanes)]
        self.vehicle_counts = {vtype: 0 for vtype in VEHICLE_COLORS.keys()}
        
        # API data
        self.api_url = "http://127.0.0.1:8000"
        self.last_optimization = None
        self.optimization_results = None
        
    def draw(self, screen):
        # Draw intersection roads
        pygame.draw.rect(screen, ROAD_COLOR, 
                        (self.x - self.width//2, self.y - self.height//2, 
                         self.width, self.height))
        
        # Draw lane dividers
        for i in range(1, self.lanes//2 + 1):
            # Horizontal lanes
            lane_y = self.y - self.height//2 + (i * self.height//(self.lanes//2 + 1))
            pygame.draw.line(screen, LANE_COLOR, 
                           (self.x - self.width//2, lane_y),
                           (self.x + self.width//2, lane_y), 2)
            
            # Vertical lanes
            lane_x = self.x - self.width//2 + (i * self.width//(self.lanes//2 + 1))
            pygame.draw.line(screen, LANE_COLOR,
                           (lane_x, self.y - self.height//2),
                           (lane_x, self.y + self.height//2), 2)
        
        # Draw traffic lights
        self.draw_traffic_lights(screen)
        
        # Draw vehicles in queues
        self.draw_vehicle_queues(screen)
        
    def draw_traffic_lights(self, screen):
        # Positions for traffic lights (N, S, E, W)
        positions = [
            (self.x, self.y - self.height//2 - 30),  # North
            (self.x, self.y + self.height//2 + 30),  # South
            (self.x + self.width//2 + 30, self.y),  # East
            (self.x - self.width//2 - 30, self.y)   # West
        ]
        
        for i, (x, y) in enumerate(positions):
            # Draw light housing
            pygame.draw.rect(screen, (50, 50, 50), (x-15, y-40, 30, 80))
            
            # Draw lights (red, yellow, green)
            colors = [RED, YELLOW, GREEN]
            light_y = y - 30
            
            for j, color in enumerate(colors):
                # Determine if this light should be on
                light_on = False
                if i == self.current_green:
                    if self.signal_state == "green" and j == 2:  # Green light
                        light_on = True
                    elif self.signal_state == "yellow" and j == 1:  # Yellow light
                        light_on = True
                elif self.signal_state != "green" or i != self.current_green:
                    if j == 0:  # Red light for other directions
                        light_on = True
                
                # Draw light
                light_color = color if light_on else (color[0]//4, color[1]//4, color[2]//4)
                pygame.draw.circle(screen, light_color, (x, light_y + j*20), 8)
            
            # Draw lane number
            font = pygame.font.Font(None, 24)
            text = font.render(f"L{i+1}", True, WHITE)
            screen.blit(text, (x-8, y+35))
            
            # Draw green time if this is current green lane
            if i == self.current_green:
                time_font = pygame.font.Font(None, 28)
                time_text = time_font.render(f"{self.green_times[i]}s", True, GREEN)
                screen.blit(time_text, (x-15, y-70))
    
    def draw_vehicle_queues(self, screen):
        # Draw vehicles waiting at each lane
        for lane_idx, vehicles in enumerate(self.vehicle_queues):
            if lane_idx == 0:  # North lane
                base_x = self.x
                base_y = self.y - self.height//2 - 20
                for i, vehicle in enumerate(vehicles[:5]):  # Show first 5
                    color = VEHICLE_COLORS.get(vehicle["type"], WHITE)
                    pygame.draw.rect(screen, color, 
                                    (base_x - 15 + i*10, base_y - 20, 10, 20))
                    
            elif lane_idx == 1:  # South lane
                base_x = self.x
                base_y = self.y + self.height//2 + 20
                for i, vehicle in enumerate(vehicles[:5]):
                    color = VEHICLE_COLORS.get(vehicle["type"], WHITE)
                    pygame.draw.rect(screen, color,
                                    (base_x - 15 + i*10, base_y, 10, 20))
                    
            elif lane_idx == 2:  # East lane
                base_x = self.x + self.width//2 + 20
                base_y = self.y
                for i, vehicle in enumerate(vehicles[:5]):
                    color = VEHICLE_COLORS.get(vehicle["type"], WHITE)
                    pygame.draw.rect(screen, color,
                                    (base_x, base_y - 15 + i*10, 20, 10))
                    
            elif lane_idx == 3:  # West lane
                base_x = self.x - self.width//2 - 20
                base_y = self.y
                for i, vehicle in enumerate(vehicles[:5]):
                    color = VEHICLE_COLORS.get(vehicle["type"], WHITE)
                    pygame.draw.rect(screen, color,
                                    (base_x - 20, base_y - 15 + i*10, 20, 10))

class Vehicle:
    def __init__(self, vehicle_type, start_pos, target_lane):
        self.type = vehicle_type
        self.x, self.y = start_pos
        self.target_lane = target_lane
        self.speed = random.uniform(1.0, 3.0)
        self.color = VEHICLE_COLORS.get(vehicle_type, WHITE)
        self.size = self.get_size()
        self.waiting_time = 0
        
    def get_size(self):
        # Different sizes for different vehicles
        sizes = {
            "motorcycle": (15, 8),
            "car": (25, 12),
            "tuktuk": (20, 10),
            "bus": (35, 15),
            "truck": (30, 15),
            "bicycle": (12, 6)
        }
        return sizes.get(self.type, (20, 10))
    
    def move(self, intersection):
        # Move towards intersection
        target_x, target_y = intersection.x, intersection.y
        
        # Adjust target based on lane
        if self.target_lane == 0:  # North
            target_y = intersection.y - intersection.height//2 - 50
        elif self.target_lane == 1:  # South
            target_y = intersection.y + intersection.height//2 + 50
        elif self.target_lane == 2:  # East
            target_x = intersection.x + intersection.width//2 + 50
        elif self.target_lane == 3:  # West
            target_x = intersection.x - intersection.width//2 - 50
        
        # Move towards target
        dx = target_x - self.x
        dy = target_y - self.y
        dist = (dx**2 + dy**2)**0.5
        
        if dist > self.speed:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
        else:
            # Reached intersection - add to queue
            self.x, self.y = target_x, target_y
            self.waiting_time += 1
            
            # Check if we can cross (green light for our lane)
            if (intersection.current_green == self.target_lane and 
                intersection.signal_state == "green"):
                return "crossing"
            else:
                return "waiting"
        
        return "moving"
    
    def draw(self, screen):
        width, height = self.size
        pygame.draw.rect(screen, self.color, 
                        (self.x - width//2, self.y - height//2, width, height))
        
        # Draw vehicle type icon
        font = pygame.font.Font(None, 20)
        icons = {
            "motorcycle": "🏍️",
            "car": "🚗",
            "tuktuk": "🛺",
            "bus": "🚌",
            "truck": "🚚",
            "bicycle": "🚲"
        }
        icon = icons.get(self.type, "🚗")
        text = font.render(icon, True, WHITE)
        screen.blit(text, (self.x - 8, self.y - 8))

class TrafficSimulator:
    def __init__(self):
        self.intersection = Intersection(WIDTH//2, HEIGHT//2, 200, 200)
        self.vehicles = []
        self.spawn_timer = 0
        self.spawn_interval = 60  # Frames between spawns
        
        # Statistics
        self.total_vehicles = 0
        self.vehicles_crossed = 0
        self.average_wait_time = 0
        self.congestion_level = "Low"
        
        # API thread for optimization
        self.optimization_thread = None
        self.running = True
        self.optimization_interval = 300  # Optimize every 300 frames (~10 seconds)
        self.optimization_counter = 0
        
        # Fonts
        self.title_font = pygame.font.Font(None, 36)
        self.stats_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # Start API monitoring thread
        self.start_api_thread()
    
    def start_api_thread(self):
        """Start background thread for API optimization"""
        def api_monitor():
            while self.running:
                time.sleep(5)  # Check every 5 seconds
                self.optimize_traffic()
        
        self.api_thread = threading.Thread(target=api_monitor)
        self.api_thread.daemon = True
        self.api_thread.start()
    
    def spawn_vehicle(self):
        """Spawn a random vehicle approaching the intersection"""
        vehicle_types = list(VEHICLE_COLORS.keys())
        vehicle_type = random.choice(vehicle_types)
        
        # Choose random lane (0: N, 1: S, 2: E, 3: W)
        lane = random.randint(0, 3)
        
        # Set starting position based on lane
        if lane == 0:  # North
            start_pos = (self.intersection.x + random.randint(-50, 50), 
                        self.intersection.y - 300)
        elif lane == 1:  # South
            start_pos = (self.intersection.x + random.randint(-50, 50), 
                        self.intersection.y + 300)
        elif lane == 2:  # East
            start_pos = (self.intersection.x + 300, 
                        self.intersection.y + random.randint(-50, 50))
        else:  # West
            start_pos = (self.intersection.x - 300, 
                        self.intersection.y + random.randint(-50, 50))
        
        vehicle = Vehicle(vehicle_type, start_pos, lane)
        self.vehicles.append(vehicle)
        self.total_vehicles += 1
        
        # Update vehicle counts
        self.intersection.vehicle_counts[vehicle_type] += 1
        
        # Add to appropriate queue
        self.intersection.vehicle_queues[lane].append({
            "type": vehicle_type,
            "waiting": 0
        })
    
    def optimize_traffic(self):
        """Call optimization API with current traffic data"""
        try:
            # Prepare lane data from current queues
            lane_data = []
            directions = ["northbound", "southbound", "eastbound", "westbound"]
            
            for i in range(4):
                # Count vehicles by type in this lane's queue
                vehicle_counts = {}
                for vehicle in self.intersection.vehicle_queues[i]:
                    v_type = vehicle["type"]
                    vehicle_counts[v_type] = vehicle_counts.get(v_type, 0) + 1
                
                lane_data.append({
                    "lane_id": i + 1,
                    "direction": directions[i],
                    "vehicle_counts": vehicle_counts
                })
            
            # Prepare API request
            request_data = {
                "intersection_id": "2d_simulation",
                "time_of_day": "simulation",
                "lanes": lane_data
            }
            
            # Call optimization API
            response = requests.post(
                f"{self.intersection.api_url}/api/optimize/",
                json=request_data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                self.intersection.optimization_results = result
                self.intersection.last_optimization = datetime.now()
                
                # Update green times
                for lane in result.get('green_times', []):
                    lane_idx = lane['lane_id'] - 1
                    if 0 <= lane_idx < 4:
                        self.intersection.green_times[lane_idx] = lane['green_time']
                
                # Update congestion level
                self.congestion_level = result.get('congestion_level', 'Low').upper()
                
                print(f"✅ Optimization updated: {self.congestion_level} traffic")
                
        except Exception as e:
            print(f"⚠️ Optimization error: {e}")
    
    def update(self):
        """Update simulation state"""
        # Spawn new vehicles
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_vehicle()
            self.spawn_timer = 0
            
            # Adjust spawn rate based on congestion
            if self.congestion_level == "HIGH":
                self.spawn_interval = max(20, self.spawn_interval - 10)
            elif self.congestion_level == "LOW":
                self.spawn_interval = min(100, self.spawn_interval + 5)
        
        # Update traffic signals
        self.intersection.signal_timer += 1
        current_green_time = self.intersection.green_times[self.intersection.current_green]
        
        if self.intersection.signal_state == "green":
            if self.intersection.signal_timer >= current_green_time * 10:  # Convert seconds to frames
                self.intersection.signal_state = "yellow"
                self.intersection.signal_timer = 0
        elif self.intersection.signal_state == "yellow":
            if self.intersection.signal_timer >= 50:  # 5 seconds yellow
                self.intersection.signal_state = "red"
                self.intersection.signal_timer = 0
        else:  # red
            if self.intersection.signal_timer >= 20:  # 2 seconds all red
                self.intersection.signal_state = "green"
                self.intersection.current_green = (self.intersection.current_green + 1) % 4
                self.intersection.signal_timer = 0
        
        # Update vehicles
        vehicles_to_remove = []
        
        for i, vehicle in enumerate(self.vehicles):
            status = vehicle.move(self.intersection)
            
            if status == "crossing":
                # Vehicle is crossing - remove it after a delay
                if vehicle.waiting_time > 20:  # Crossed intersection
                    vehicles_to_remove.append(i)
                    self.vehicles_crossed += 1
                    
                    # Remove from queue
                    for queue in self.intersection.vehicle_queues[vehicle.target_lane]:
                        if queue.get("type") == vehicle.type:
                            self.intersection.vehicle_queues[vehicle.target_lane].remove(queue)
                            self.intersection.vehicle_counts[vehicle.type] = max(
                                0, self.intersection.vehicle_counts[vehicle.type] - 1)
                            break
        
        # Remove vehicles that have crossed
        for i in reversed(vehicles_to_remove):
            self.vehicles.pop(i)
        
        # Periodically optimize traffic
        self.optimization_counter += 1
        if self.optimization_counter >= self.optimization_interval:
            self.optimize_traffic()
            self.optimization_counter = 0
        
        # Update average wait time
        if self.vehicles_crossed > 0:
            total_wait = sum(v.waiting_time for v in self.vehicles)
            self.average_wait_time = total_wait / len(self.vehicles) if self.vehicles else 0
    
    def draw(self, screen):
        """Draw everything"""
        # Clear screen
        screen.fill(BACKGROUND)
        
        # Draw intersection
        self.intersection.draw(screen)
        
        # Draw vehicles
        for vehicle in self.vehicles:
            vehicle.draw(screen)
        
        # Draw UI panels
        self.draw_stats_panel(screen)
        self.draw_control_panel(screen)
        self.draw_optimization_panel(screen)
    
    def draw_stats_panel(self, screen):
        """Draw statistics panel"""
        panel_x, panel_y = 20, 20
        panel_width, panel_height = 350, 200
        
        # Panel background
        pygame.draw.rect(screen, (30, 30, 40), 
                        (panel_x, panel_y, panel_width, panel_height), 
                        border_radius=10)
        pygame.draw.rect(screen, (60, 60, 80), 
                        (panel_x, panel_y, panel_width, panel_height), 
                        2, border_radius=10)
        
        # Title
        title = self.title_font.render("📊 Traffic Statistics", True, WHITE)
        screen.blit(title, (panel_x + 10, panel_y + 10))
        
        # Statistics
        stats_y = panel_y + 50
        stats = [
            f"Total Vehicles: {self.total_vehicles}",
            f"Vehicles Waiting: {len(self.vehicles)}",
            f"Crossed: {self.vehicles_crossed}",
            f"Avg Wait Time: {self.average_wait_time:.1f}s",
            f"Congestion: {self.congestion_level}",
            f"Spawn Rate: {self.spawn_interval} frames"
        ]
        
        for i, stat in enumerate(stats):
            text = self.stats_font.render(stat, True, WHITE)
            screen.blit(text, (panel_x + 20, stats_y + i * 25))
    
    def draw_control_panel(self, screen):
        """Draw control panel"""
        panel_x, panel_y = 20, 240
        panel_width, panel_height = 350, 150
        
        # Panel background
        pygame.draw.rect(screen, (30, 30, 40), 
                        (panel_x, panel_y, panel_width, panel_height), 
                        border_radius=10)
        pygame.draw.rect(screen, (60, 60, 80), 
                        (panel_x, panel_y, panel_width, panel_height), 
                        2, border_radius=10)
        
        # Title
        title = self.title_font.render("🎮 Controls", True, WHITE)
        screen.blit(title, (panel_x + 10, panel_y + 10))
        
        # Control instructions
        controls = [
            "SPACE: Spawn vehicle",
            "O: Run optimization",
            "+/-: Adjust spawn rate",
            "R: Reset simulation"
        ]
        
        for i, control in enumerate(controls):
            text = self.stats_font.render(control, True, WHITE)
            screen.blit(text, (panel_x + 20, panel_y + 50 + i * 25))
    
    def draw_optimization_panel(self, screen):
        """Draw optimization results panel"""
        if not self.intersection.optimization_results:
            return
        
        panel_x, panel_y = WIDTH - 370, 20
        panel_width, panel_height = 350, 300
        
        # Panel background
        pygame.draw.rect(screen, (30, 30, 40), 
                        (panel_x, panel_y, panel_width, panel_height), 
                        border_radius=10)
        pygame.draw.rect(screen, (60, 60, 80), 
                        (panel_x, panel_y, panel_width, panel_height), 
                        2, border_radius=10)
        
        # Title
        title = self.title_font.render("⚡ Optimization", True, WHITE)
        screen.blit(title, (panel_x + 10, panel_y + 10))
        
        # Last optimization time
        if self.intersection.last_optimization:
            time_str = self.intersection.last_optimization.strftime("%H:%M:%S")
            time_text = self.small_font.render(f"Last: {time_str}", True, YELLOW)
            screen.blit(time_text, (panel_x + 20, panel_y + 50))
        
        # Green times
        y_pos = panel_y + 80
        for i, green_time in enumerate(self.intersection.green_times):
            direction = ["North", "South", "East", "West"][i]
            color = GREEN if i == self.intersection.current_green else WHITE
            
            text = self.stats_font.render(f"Lane {i+1} ({direction}): {green_time}s", 
                                         True, color)
            screen.blit(text, (panel_x + 20, y_pos))
            y_pos += 25
        
        # Vehicle counts
        y_pos += 10
        count_text = self.stats_font.render("Vehicle Counts:", True, WHITE)
        screen.blit(count_text, (panel_x + 20, y_pos))
        y_pos += 25
        
        for vtype, count in self.intersection.vehicle_counts.items():
            if count > 0:
                color = VEHICLE_COLORS.get(vtype, WHITE)
                text = self.small_font.render(f"{vtype}: {count}", True, color)
                screen.blit(text, (panel_x + 40, y_pos))
                y_pos += 20
    
    def handle_event(self, event):
        """Handle user input events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Spawn a vehicle
                self.spawn_vehicle()
            
            elif event.key == pygame.K_o:
                # Run optimization
                self.optimize_traffic()
            
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                # Increase spawn rate (fewer frames between spawns)
                self.spawn_interval = max(10, self.spawn_interval - 10)
            
            elif event.key == pygame.K_MINUS:
                # Decrease spawn rate
                self.spawn_interval = min(200, self.spawn_interval + 10)
            
            elif event.key == pygame.K_r:
                # Reset simulation
                self.__init__()
    
    def run(self):
        """Main simulation loop"""
        clock = pygame.time.Clock()
        
        print("🚀 Starting 2D Traffic Simulator...")
        print("Controls:")
        print("  SPACE: Spawn vehicle")
        print("  O: Run optimization")
        print("  +/-: Adjust spawn rate")
        print("  R: Reset simulation")
        print("  ESC: Exit")
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        self.handle_event(event)
            
            # Update simulation
            self.update()
            
            # Draw everything
            self.draw(screen)
            
            # Update display
            pygame.display.flip()
            
            # Cap at 60 FPS
            clock.tick(60)
        
        self.running = False
        pygame.quit()

def main():
    # Check if API is running
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=2)
        if response.status_code == 200:
            print("✅ API connected successfully!")
        else:
            print("⚠️ API returned status:", response.status_code)
    except:
        print("⚠️ Could not connect to API. Running in offline mode...")
    
    # Start simulation
    simulator = TrafficSimulator()
    simulator.run()

if __name__ == "__main__":
    main()