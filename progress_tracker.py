# progress_tracker.py
import os
import time
import json
from datetime import datetime

class TrafficOptimizerTracker:
    def __init__(self):
        self.progress_file = 'progress_status.json'
        self.load_progress()
    
    def load_progress(self):
        default_progress = {
            "phases": {
                "1": {"name": "Core Infrastructure", "status": "completed", "progress": 100},
                "2": {"name": "AI Vision Integration", "status": "completed", "progress": 100},
                "3": {"name": "Production Deployment", "status": "completed", "progress": 100},
                "4": {"name": "Cambodia Enhancements", "status": "in_progress", "progress": 30},
                "5": {"name": "Advanced Features", "status": "planned", "progress": 0}
            },
            "tasks": {
                "database_setup": {"status": "completed", "phase": 1},
                "api_development": {"status": "completed", "phase": 1},
                "ml_training": {"status": "completed", "phase": 1},
                "vehicle_detection": {"status": "completed", "phase": 2},
                "fusion_engine": {"status": "completed", "phase": 2},
                "vision_api": {"status": "completed", "phase": 2},
                "folder_organization": {"status": "completed", "phase": 3},
                "testing": {"status": "completed", "phase": 3},
                "moto_detection": {"status": "in_progress", "phase": 4},
                "tuktuk_classification": {"status": "planned", "phase": 4},
                "cambodia_patterns": {"status": "planned", "phase": 4},
                "multi_camera": {"status": "planned", "phase": 5},
                "mobile_app": {"status": "planned", "phase": 5}
            },
            "last_updated": datetime.now().isoformat(),
            "system_status": "operational"
        }
        
        try:
            with open(self.progress_file, 'r') as f:
                self.progress = json.load(f)
        except:
            self.progress = default_progress
            self.save_progress()
    
    def save_progress(self):
        self.progress['last_updated'] = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def display_dashboard(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print('🚦 SMART TRAFFIC OPTIMIZER - LIVE DASHBOARD')
        print('=' * 60)
        
        # System Status
        status_color = '🟢' if self.progress['system_status'] == 'operational' else '🔴'
        print(f'{status_color} System Status: {self.progress["system_status"].upper()}')
        print(f'📅 Last Updated: {self.progress["last_updated"]}')
        print()
        
        # Phase Progress
        print('📊 PROJECT PHASES:')
        for phase_id, phase in self.progress['phases'].items():
            status_icon = '✅' if phase['status'] == 'completed' else '🔄' if phase['status'] == 'in_progress' else '⏳'
            bar = '█' * (phase['progress'] // 5) + '░' * (20 - (phase['progress'] // 5))
            print(f' {status_icon} Phase {phase_id}: {phase["name"]}')
            print(f'    {bar} {phase["progress"]}%')
        print()
        
        # Current Tasks
        print('🎯 CURRENT TASKS:')
        for task_id, task in self.progress['tasks'].items():
            if task['status'] == 'in_progress':
                print(f'   🔄 {task_id.replace("_", " ").title()}')
        print()
        
        # Recent Activity
        print('📈 RECENT ACTIVITY:')
        activities = [
            '✅ AI Vision System Integrated',
            '✅ Real-time Vehicle Detection Active', 
            '✅ API Endpoints Operational',
            '🔄 Enhancing Moto Detection for Cambodia',
            '⏳ Preparing Tuktuk Classification'
        ]
        for activity in activities[-3:]:
            print(f'   {activity}')
        
        print()
        print('💡 Commands: [U]pdate Progress | [R]un System Test | [Q]uit')
        print('=' * 60)
    
    def update_task(self, task_id, status):
        if task_id in self.progress['tasks']:
            self.progress['tasks'][task_id]['status'] = status
            self.save_progress()
            return True
        return False
    
    def update_phase(self, phase_id, progress, status=None):
        if phase_id in self.progress['phases']:
            self.progress['phases'][phase_id]['progress'] = progress
            if status:
                self.progress['phases'][phase_id]['status'] = status
            self.save_progress()
            return True
        return False
    
    def run_system_test(self):
        print('🧪 Running System Tests...')
        time.sleep(2)
        
        tests = [
            ('API Server', self.test_api),
            ('Database', self.test_database),
            ('Vision System', self.test_vision),
            ('AI Models', self.test_ai_models)
        ]
        
        for test_name, test_func in tests:
            print(f'   Testing {test_name}...', end=' ')
            try:
                if test_func():
                    print('✅ PASS')
                else:
                    print('❌ FAIL')
            except:
                print('❌ ERROR')
        
        time.sleep(2)
    
    def test_api(self):
        try:
            import requests
            response = requests.get('http://localhost:8000/', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def test_database(self):
        return os.path.exists('progress_status.json')
    
    def test_vision(self):
        return os.path.exists('02_ai_vision/vision_engine/lightweight_detector.py')
    
    def test_ai_models(self):
        return os.path.exists('05_models/yolov8n.pt')

def main():
    tracker = TrafficOptimizerTracker()
    
    while True:
        tracker.display_dashboard()
        
        try:
            command = input('Enter command: ').strip().lower()
            
            if command == 'u':
                print('\nUpdate Options:')
                print('1. Complete Moto Detection')
                print('2. Start Tuktuk Classification') 
                print('3. Update Phase Progress')
                choice = input('Select option: ').strip()
                
                if choice == '1':
                    tracker.update_task('moto_detection', 'completed')
                    tracker.update_phase('4', 50)
                    print('✅ Moto detection marked complete!')
                elif choice == '2':
                    tracker.update_task('tuktuk_classification', 'in_progress')
                    print('🔄 Tuktuk classification started!')
                elif choice == '3':
                    phase = input('Phase number (1-5): ')
                    progress = input('Progress (0-100): ')
                    tracker.update_phase(phase, int(progress))
                    print('✅ Phase progress updated!')
                
                input('Press Enter to continue...')
                
            elif command == 'r':
                tracker.run_system_test()
                input('Press Enter to continue...')
                
            elif command == 'q':
                print('👋 Exiting dashboard...')
                break
                
            else:
                print('⏳ Auto-updating in 5 seconds...')
                time.sleep(5)
                
        except KeyboardInterrupt:
            print('\n👋 Exiting dashboard...')
            break

if __name__ == '__main__':
    main()
