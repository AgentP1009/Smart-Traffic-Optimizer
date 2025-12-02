import cv2
import sys

def test_camera(camera_id=0):
    print(f"Testing camera {camera_id}...")
    
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        print(f"❌ Camera {camera_id} failed to open")
        return False
    
    print(f"✅ Camera {camera_id} opened successfully")
    
    # Try to read a frame
    ret, frame = cap.read()
    if not ret:
        print(f"❌ Camera {camera_id} opened but cannot read frames")
        cap.release()
        return False
    
    print(f"✅ Camera {camera_id} can read frames (shape: {frame.shape})")
    cap.release()
    return True

# Test different camera IDs
for cam_id in [0, 1, 2]:
    if test_camera(cam_id):
        print(f"🎯 Use camera ID: {cam_id}")
        break
else:
    print("❌ No working cameras found")