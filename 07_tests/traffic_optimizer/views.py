# traffic_optimizer/views.py - Add this function
@api_view(['POST'])
def optimize_traffic_signal(request):
    """
    Calculate optimal green time based on vehicle counts
    Expected input: {"lane_data": [{"lane_id": 1, "vehicles": {"car": 2, "motorcycle": 5, "tuktuk": 1}}, ...]}
    """
    try:
        data = request.data
        lane_data = data.get('lane_data', [])
        
        if not lane_data:
            return Response({"error": "No lane data provided"}, status=400)
        
        # Calculate total vehicles per lane
        lane_totals = []
        for lane in lane_data:
            lane_id = lane.get('lane_id')
            vehicles = lane.get('vehicles', {})
            total = sum(vehicles.values())
            lane_totals.append({
                "lane_id": lane_id,
                "total_vehicles": total,
                "vehicle_breakdown": vehicles
            })
        
        # Simple optimization algorithm (you can improve this)
        total_all_lanes = sum(item['total_vehicles'] for item in lane_totals)
        
        if total_all_lanes == 0:
            # No traffic - use minimum green time
            green_times = [{"lane_id": item['lane_id'], "green_time": 15} for item in lane_totals]
        else:
            # Proportional allocation with minimum 15s and maximum 60s
            green_times = []
            for item in lane_totals:
                proportion = item['total_vehicles'] / total_all_lanes
                green_time = max(15, min(60, int(proportion * 120)))  # 120s cycle
                green_times.append({
                    "lane_id": item['lane_id'],
                    "green_time": green_time,
                    "allocation_percentage": round(proportion * 100, 1)
                })
        
        # Prioritize lanes with more motorcycles (Cambodia-specific)
        for i, item in enumerate(lane_totals):
            motorcycles = item['vehicle_breakdown'].get('motorcycle', 0)
            if motorcycles > 5:  # If many motorcycles, add bonus time
                green_times[i]['green_time'] = min(70, green_times[i]['green_time'] + 10)
                green_times[i]['motorcycle_bonus'] = True
        
        return Response({
            "success": True,
            "message": "Traffic signal optimization calculated",
            "cycle_duration": 120,  # 2-minute cycle
            "optimization_method": "proportional_with_motorcycle_priority",
            "green_times": green_times,
            "summary": {
                "total_vehicles": total_all_lanes,
                "lanes_optimized": len(lane_totals),
                "average_green_time": sum(g['green_time'] for g in green_times) / len(green_times)
            }
        })
        
    except Exception as e:
        return Response({"error": str(e)}, status=500)