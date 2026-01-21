# cctv_demo.py
import cv2
import requests
import time

def cctv_live_demo(rtsp_url=None):
    """Demo with IP camera or video file"""
    
    print("📡 CCTV/IP CAMERA DEMONSTRATION")
    print("=" * 60)
    
    # Use RTSP URL or video file
    if rtsp_url:
        print(f"Connecting to: {rtsp_url}")
        cap = cv2.VideoCapture(rtsp_url)
    else:
        print("Using sample traffic video")
        # Download a sample video or use existing
        video_path = "traffic_sample.mp4"
        cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("❌ Could not open video source")
        return
    
    print("✅ Video source connected!")
    print("Press 'q' to quit, 'space' to pause")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Resize for display
        frame = cv2.resize(frame, (800, 600))
        
        # Display instructions
        cv2.putText(frame, "Smart Traffic Optimizer - Live CCTV", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, "Press 'd' for detection, 'o' for optimization", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow('CCTV Traffic Monitoring', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('d'):
            # Run detection on current frame
            temp_file = "cctv_snapshot.jpg"
            cv2.imwrite(temp_file, frame)
            
            try:
                with open(temp_file, 'rb') as img:
                    files = {'image': img}
                    response = requests.post('http://127.0.0.1:8000/api/detect/', files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        vehicles = data.get('vehicles_detected', 0)
                        print(f"📊 Detection: {vehicles} vehicles")
                        
                        # Show on frame
                        cv2.putText(frame, f"DETECTED: {vehicles} vehicles", (10, 90),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        
            except Exception as e:
                print(f"Detection error: {e}")
        
        elif key == ord('o'):
            # Show optimization options
            print("\n⚡ What type of optimization?")
            print("1. Current traffic")
            print("2. Morning peak scenario")
            print("3. Evening rush hour")
            print("4. Custom input")
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Try different video sources
    sources = [
        # "rtsp://username:password@camera_ip:554/stream",  # Real IP camera
        "traffic_sample.mp4",  # Local video file
        0  # Webcam
    ]
    
    for source in sources:
        try:
            cctv_live_demo(source)
            break
        except:
            continue