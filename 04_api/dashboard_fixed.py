# dashboard_fixed.py
import json
import matplotlib.pyplot as plt

def visualize_optimization_results():
    """Create visualizations without emoji issues"""
    
    try:
        with open('complete_workflow_results.json', 'r') as f:
            data = json.load(f)
        
        opt_results = data['optimization_results']
        green_times = opt_results['green_times']
        
        # Use simpler titles without emojis
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Smart Traffic Optimizer - Results Visualization', fontsize=16, fontweight='bold')
        
        # Plot 1: Green Time Distribution
        ax1 = axes[0, 0]
        lanes = [f"Lane {g['lane_id']}" for g in green_times]
        times = [g['green_time'] for g in green_times]
        
        bars = ax1.bar(lanes, times, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
        ax1.set_title('Green Time Allocation per Lane', fontweight='bold')
        ax1.set_ylabel('Green Time (seconds)')
        ax1.set_xlabel('Lanes')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{int(height)}s', ha='center', va='bottom')
        
        # Plot 2: Vehicle Distribution
        ax2 = axes[0, 1]
        vehicle_counts = {}
        for lane in data['intersection_data']['lanes']:
            for vehicle, count in lane['vehicle_counts'].items():
                vehicle_counts[vehicle] = vehicle_counts.get(vehicle, 0) + count
        
        vehicles = list(vehicle_counts.keys())
        counts = list(vehicle_counts.values())
        
        colors = ['#FF9999', '#66B3FF', '#99FF99', '#FFCC99', '#FFD700']
        wedges, texts, autotexts = ax2.pie(counts, labels=vehicles, autopct='%1.1f%%', 
                                           colors=colors[:len(vehicles)])
        ax2.set_title('Vehicle Distribution', fontweight='bold')
        
        # Plot 3: Motorcycle Percentage
        ax3 = axes[1, 0]
        motorcycle_pct = opt_results['motorcycle_percentage']
        other_pct = 100 - motorcycle_pct
        
        labels = ['Motorcycles', 'Other Vehicles']
        sizes = [motorcycle_pct, other_pct]
        colors = ['#FF6B6B', '#4ECDC4']
        
        ax3.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax3.set_title(f'Motorcycle Percentage: {motorcycle_pct}%', fontweight='bold')
        
        # Plot 4: Optimization Metrics
        ax4 = axes[1, 1]
        metrics = [
            opt_results['total_vehicles'],
            opt_results['motorcycle_percentage'],
            len(green_times),
            sum(times)/len(times)
        ]
        metric_names = ['Total Vehicles', 'Motorcycle %', 'Lanes', 'Avg Green Time']
        
        bars2 = ax4.bar(range(len(metrics)), metrics, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
        ax4.set_title('Optimization Metrics', fontweight='bold')
        ax4.set_xticks(range(len(metrics)))
        ax4.set_xticklabels(metric_names, rotation=45)
        
        # Add value labels
        for bar, value in zip(bars2, metrics):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{value:.1f}', ha='center', va='bottom')
        
        # Add note without emojis
        plt.figtext(0.5, 0.01, 
                   'Optimized for Cambodian Traffic Patterns (Motorcycle Priority)',
                   ha='center', fontsize=10, style='italic', bbox=dict(boxstyle="round,pad=0.3", 
                   facecolor="yellow", alpha=0.2))
        
        plt.tight_layout()
        plt.savefig('optimization_charts.png', dpi=150, bbox_inches='tight')
        plt.show()
        
        print("✅ Visualization saved as: optimization_charts.png")
        
    except FileNotFoundError:
        print("❌ Results file not found. Run complete workflow test first.")
    except Exception as e:
        print(f"❌ Visualization error: {e}")

if __name__ == "__main__":
    visualize_optimization_results()