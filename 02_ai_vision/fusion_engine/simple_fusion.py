from datetime import datetime

class SimpleFusionEngine:
    def fuse_data(self, vision_data, existing_traffic_data):
        '''Combine camera data with existing PostgreSQL data'''
        # Get current time for time-based adjustments
        current_hour = datetime.now().hour
        is_rush_hour = current_hour in [7, 8, 9, 16, 17, 18]
        
        # Base green time from your existing system
        base_green = existing_traffic_data.get('current_green_time', 30)
        
        # Simple vision-based adjustments
        vision_adjustment = self._calculate_vision_adjustment(vision_data)
        
        # Time-based adjustment
        time_factor = 1.2 if is_rush_hour else 0.9
        
        # Calculate new green time
        new_green_time = base_green * vision_adjustment * time_factor
        new_green_time = max(10, min(60, new_green_time))
        
        return {
            'recommended_green_time': round(new_green_time),
            'adjustment_reason': self._explain_adjustment(vision_data, is_rush_hour),
            'confidence': 'High - Real-time visual confirmation',
            'vision_data_used': vision_data,
            'previous_green_time': base_green
        }
    
    def _calculate_vision_adjustment(self, vision_data):
        '''Simple rules instead of complex ML'''
        vehicle_count = vision_data['vehicle_count']
        congestion = vision_data['congestion_level']
        
        # Simple adjustment rules
        if congestion == 'High' or vehicle_count > 15:
            return 1.4  # 40% longer green time
        elif congestion == 'Medium' or vehicle_count > 8:
            return 1.2  # 20% longer
        elif congestion == 'Low' and vehicle_count < 3:
            return 0.7  # 30% shorter
        else:
            return 1.0  # No change
    
    def _explain_adjustment(self, vision_data, is_rush_hour):
        reasons = []
        
        if vision_data['vehicle_count'] > 15:
            reasons.append(f'High traffic ({vision_data['vehicle_count']} vehicles)')
        elif vision_data['vehicle_count'] < 3:
            reasons.append(f'Light traffic ({vision_data['vehicle_count']} vehicles)')
            
        if is_rush_hour:
            reasons.append('Rush hour adjustment')
            
        return ' + '.join(reasons) if reasons else 'Normal traffic conditions'

# Test function
def test_fusion():
    fusion = SimpleFusionEngine()
    vision_data = {'vehicle_count': 10, 'congestion_level': 'Medium'}
    existing_data = {'current_green_time': 30}
    result = fusion.fuse_data(vision_data, existing_data)
    print('🔄 Fusion Test Result:', result)
    return result

if __name__ == '__main__':
    test_fusion()
