# In your views.py, add:
@api_view(['POST'])
def optimize_traffic(request):
    """
    Receive vehicle counts and return optimal green time
    Expected JSON: {"lane_counts": {"lane1": {"car": 5, "motorcycle": 10}, ...}}
    """
    data = request.data
    lane_counts = data.get('lane_counts', {})
    
    # Your optimization logic here
    green_times = calculate_green_times(lane_counts)
    
    return Response({
        "message": "Traffic optimization calculated",
        "green_times": green_times,
        "total_vehicles": sum(sum(lane.values()) for lane in lane_counts.values())
    })