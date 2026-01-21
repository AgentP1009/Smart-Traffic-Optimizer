# simple_dashboard.py
import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image, ImageTk
import io
import json

class TrafficDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Traffic Optimizer - Live Dashboard")
        self.root.geometry("1200x700")
        
        # API URL
        self.api_url = "http://127.0.0.1:8000"
        
        self.setup_ui()
        self.update_dashboard()
    
    def setup_ui(self):
        # Create frames
        left_frame = tk.Frame(self.root, width=400, bg='#f0f0f0')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_frame = tk.Frame(self.root, width=800, bg='white')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Left panel - Controls
        tk.Label(left_frame, text="🚦 SMART TRAFFIC OPTIMIZER", 
                font=('Arial', 16, 'bold'), bg='#f0f0f0').pack(pady=20)
        
        # System Status
        status_frame = tk.LabelFrame(left_frame, text="System Status", padx=10, pady=10)
        status_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.status_labels = {}
        statuses = [
            ("API Server", "Checking..."),
            ("AI Model", "Checking..."),
            ("Database", "Checking..."),
            ("Live Feed", "Checking...")
        ]
        
        for name, value in statuses:
            frame = tk.Frame(status_frame)
            frame.pack(fill=tk.X, pady=2)
            tk.Label(frame, text=f"{name}:", width=15, anchor='w').pack(side=tk.LEFT)
            self.status_labels[name] = tk.Label(frame, text=value, fg='gray')
            self.status_labels[name].pack(side=tk.LEFT)
        
        # Quick Actions
        action_frame = tk.LabelFrame(left_frame, text="Quick Actions", padx=10, pady=10)
        action_frame.pack(pady=10, padx=10, fill=tk.X)
        
        buttons = [
            ("📷 Test Detection", self.test_detection),
            ("⚡ Run Optimization", self.run_optimization),
            ("📊 View Statistics", self.view_stats),
            ("🎥 Start Live Feed", self.start_live),
            ("📈 Generate Report", self.generate_report)
        ]
        
        for text, command in buttons:
            tk.Button(action_frame, text=text, command=command, 
                     bg='#4CAF50', fg='white', height=2).pack(fill=tk.X, pady=5)
        
        # Traffic Scenarios
        scenario_frame = tk.LabelFrame(left_frame, text="Test Scenarios", padx=10, pady=10)
        scenario_frame.pack(pady=10, padx=10, fill=tk.X)
        
        scenarios = [
            ("Morning Peak", {"motorcycle": 15, "car": 8, "tuktuk": 5}),
            ("School Zone", {"motorcycle": 10, "bicycle": 8, "car": 4}),
            ("Market Area", {"motorcycle": 20, "tuktuk": 10, "car": 5}),
            ("Highway", {"car": 12, "truck": 4, "bus": 3})
        ]
        
        for name, traffic in scenarios:
            btn = tk.Button(scenario_frame, text=name, 
                           command=lambda t=traffic: self.run_scenario(t))
            btn.pack(fill=tk.X, pady=2)
        
        # Right panel - Results Display
        self.result_text = tk.Text(right_frame, height=20, width=70, font=('Courier', 10))
        self.result_text.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        # Image display
        self.image_label = tk.Label(right_frame)
        self.image_label.pack(pady=10)
    
    def update_dashboard(self):
        # Update system status
        try:
            response = requests.get(f"{self.api_url}/", timeout=2)
            if response.status_code == 200:
                self.status_labels["API Server"].config(text="✅ Online", fg='green')
            else:
                self.status_labels["API Server"].config(text="❌ Offline", fg='red')
        except:
            self.status_labels["API Server"].config(text="❌ Offline", fg='red')
        
        # Schedule next update
        self.root.after(5000, self.update_dashboard)
    
    def test_detection(self):
        try:
            with open('test_traffic.jpg', 'rb') as img:
                files = {'image': img}
                response = requests.post(f"{self.api_url}/api/detect/", files=files)
            
            if response.status_code == 200:
                data = response.json()
                self.display_result("Vehicle Detection Results", data)
                
                # Load and display image
                img = Image.open('test_traffic.jpg')
                img.thumbnail((400, 300))
                photo = ImageTk.PhotoImage(img)
                self.image_label.config(image=photo)
                self.image_label.image = photo
                
            else:
                messagebox.showerror("Error", f"Detection failed: {response.status_code}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Detection error: {e}")
    
    def run_optimization(self):
        # Sample traffic data
        traffic_data = {
            "intersection_id": "dashboard_demo",
            "time_of_day": "current",
            "lanes": [
                {
                    "lane_id": 1,
                    "direction": "northbound",
                    "vehicle_counts": {"motorcycle": 8, "car": 4, "tuktuk": 3}
                },
                {
                    "lane_id": 2,
                    "direction": "southbound",
                    "vehicle_counts": {"motorcycle": 6, "car": 5, "bus": 2}
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/api/optimize/",
                json=traffic_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.display_result("Traffic Optimization Results", data)
            else:
                messagebox.showerror("Error", f"Optimization failed: {response.status_code}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Optimization error: {e}")
    
    def run_scenario(self, traffic_counts):
        scenario_data = {
            "intersection_id": "scenario_test",
            "time_of_day": "peak_hours",
            "lanes": [
                {
                    "lane_id": 1,
                    "direction": "main_road",
                    "vehicle_counts": traffic_counts
                },
                {
                    "lane_id": 2,
                    "direction": "side_road",
                    "vehicle_counts": {k: max(1, v//2) for k, v in traffic_counts.items()}
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/api/optimize/",
                json=scenario_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.display_result(f"Scenario Results", data)
            else:
                messagebox.showerror("Error", f"Scenario failed: {response.status_code}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Scenario error: {e}")
    
    def view_stats(self):
        try:
            response = requests.get(f"{self.api_url}/stats/")
            if response.status_code == 200:
                data = response.json()
                self.display_result("System Statistics", data)
            else:
                messagebox.showerror("Error", f"Stats failed: {response.status_code}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Stats error: {e}")
    
    def start_live(self):
        messagebox.showinfo("Live Feed", "Starting live camera feed...\nRun: python live_demo.py")
    
    def generate_report(self):
        try:
            # Generate a simple report
            report = "SMART TRAFFIC OPTIMIZER - DASHBOARD REPORT\n"
            report += "=" * 50 + "\n\n"
            report += f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            # Add system status
            report += "SYSTEM STATUS:\n"
            for name, label in self.status_labels.items():
                report += f"  {name}: {label.cget('text')}\n"
            
            # Save report
            with open('dashboard_report.txt', 'w') as f:
                f.write(report)
            
            messagebox.showinfo("Report Generated", "Report saved as: dashboard_report.txt")
        
        except Exception as e:
            messagebox.showerror("Error", f"Report error: {e}")
    
    def display_result(self, title, data):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"{title}\n")
        self.result_text.insert(tk.END, "=" * 50 + "\n\n")
        
        # Format JSON nicely
        formatted = json.dumps(data, indent=2)
        self.result_text.insert(tk.END, formatted)

if __name__ == "__main__":
    import time
    root = tk.Tk()
    app = TrafficDashboard(root)
    root.mainloop()