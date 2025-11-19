# optimization_engine.py
from datetime import datetime

class TrafficOptimizer:
    def __init__(self):
        self.optimization_history = []
    
    def calculate_optimal_green_time(self, intersection_data):
        base_green_time = 30  # seconds
        
        # Factor 1: Vehicle count
        vehicle_factor = intersection_data['vehicle_count'] / 50
        
        # Factor 2: Congestion level
        congestion_factors = {
            'low': 0.8,
            'medium': 1.0, 
            'high': 1.3,
            'severe': 1.6
        }
        congestion_factor = congestion_factors.get(
            intersection_data['congestion_level'], 1.0
        )
        
        # Factor 3: Time of day
        current_hour = datetime.now().hour
        if current_hour in [7, 8, 9, 16, 17, 18]:
            time_factor = 1.2
        else:
            time_factor = 0.9
        
        # Calculate optimal green time
        optimal_green = base_green_time * vehicle_factor * congestion_factor * time_factor
        optimal_green = max(10, min(60, optimal_green))
        
        return round(optimal_green)
    
    def optimize_intersection(self, intersection_id, current_traffic):
        optimal_green = self.calculate_optimal_green_time(current_traffic)
        
        optimization_result = {
            'intersection_id': intersection_id,
            'timestamp': datetime.now().isoformat(),
            'current_vehicle_count': current_traffic['vehicle_count'],
            'current_congestion': current_traffic['congestion_level'],
            'recommended_green_time': optimal_green,
            'optimization_reason': self.get_optimization_reason(current_traffic, optimal_green)
        }
        
        self.optimization_history.append(optimization_result)
        return optimization_result
    
    def get_optimization_reason(self, traffic_data, green_time):
        reasons = []
        
        if traffic_data['vehicle_count'] > 40:
            reasons.append('high vehicle volume')
        if traffic_data['congestion_level'] in ['high', 'severe']:
            reasons.append('congestion detected')
        if datetime.now().hour in [7, 8, 9, 16, 17, 18]:
            reasons.append('rush hour adjustment')
            
        return ' + '.join(reasons) if reasons else 'normal traffic conditions'

if __name__ == '__main__':
    # Test the optimizer
    optimizer = TrafficOptimizer()
    test_traffic = {
        'vehicle_count': 45,
        'congestion_level': 'high'
    }
    result = optimizer.optimize_intersection('test_intersection', test_traffic)
    print('Optimization Result:', result)
