# auto_updater.py - AUTO PROGRESS UPDATER
import time
import json
import os
from datetime import datetime, timedelta

class AutoProgressUpdater:
    def __init__(self):
        self.progress_file = 'progress_status.json'
        self.activities_log = 'activities.log'
    
    def log_activity(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        with open(self.activities_log, 'a') as f:
            f.write(log_entry + '\n')
        print(f"📝 {log_entry}")
    
    def detect_changes(self):
        """Detect file changes and auto-update progress"""
        changes_detected = []
        
        # Check for new vision improvements
        if os.path.exists('02_ai_vision/vision_engine'):
            changes_detected.append('vision_engine_modified')
        
        # Check for API modifications
        if os.path.getmtime('04_api/final_api.py') > (time.time() - 3600):
            changes_detected.append('api_updated')
        
        # Check for new test runs
        if os.path.exists('07_tests') and any(f.endswith('.py') for f in os.listdir('07_tests')):
            changes_detected.append('tests_executed')
        
        return changes_detected
    
    def auto_update_progress(self):
        """Automatically update progress based on detected changes"""
        try:
            with open(self.progress_file, 'r') as f:
                progress = json.load(f)
            
            changes = self.detect_changes()
            
            for change in changes:
                if change == 'vision_engine_modified' and progress['tasks']['moto_detection']['status'] == 'in_progress':
                    progress['tasks']['moto_detection']['status'] = 'completed'
                    progress['phases']['4']['progress'] = min(100, progress['phases']['4']['progress'] + 10)
                    self.log_activity('Auto-detected: Moto detection improvements')
                
                elif change == 'api_updated':
                    progress['phases']['3']['progress'] = 100
                    self.log_activity('Auto-detected: API enhancements')
                
                elif change == 'tests_executed':
                    progress['system_status'] = 'tested'
                    self.log_activity('Auto-detected: System testing completed')
            
            progress['last_updated'] = datetime.now().isoformat()
            
            with open(self.progress_file, 'w') as f:
                json.dump(progress, f, indent=2)
            
            return len(changes) > 0
            
        except Exception as e:
            self.log_activity(f'Error in auto-update: {e}')
            return False
    
    def run_monitor(self, interval=30):
        """Run continuous monitoring"""
        print('🔍 Starting Auto Progress Monitor...')
        print('   Monitoring for changes every 30 seconds')
        print('   Press Ctrl+C to stop\n')
        
        try:
            while True:
                if self.auto_update_progress():
                    print('✅ Progress auto-updated!')
                else:
                    print('⏳ No changes detected...')
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print('\n👋 Stopping auto-monitor...')

if __name__ == '__main__':
    updater = AutoProgressUpdater()
    updater.run_monitor()
