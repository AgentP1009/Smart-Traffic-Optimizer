import requests
import os

def test_upload():
    """Test file upload to your API"""
    url = 'http://localhost:8000/api/upload/'
    
    # Use an image from your project
    image_path = '../bus.jpg'  # Adjust path if needed
    
    if os.path.exists(image_path):
        with open(image_path, 'rb') as f:
            files = {'image': f}
            data = {
                'vehicle_type': 'bus',
                'location': 'Phnom Penh'
            }
            
            print("📤 Testing file upload...")
            response = requests.post(url, files=files, data=data)
            
            print(f"Status: {response.status_code}")
            print("Response:", response.json())
    else:
        print(f"❌ Image file not found: {image_path}")
        print("Available images in project:")
        # List available images
        for root, dirs, files in os.walk('..'):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    print(f"  - {os.path.join(root, file)}")

def test_detection():
    """Test vehicle detection"""
    url = 'http://localhost:8000/api/detect/'
    
    image_path = '../bus.jpg'
    
    if os.path.exists(image_path):
        with open(image_path, 'rb') as f:
            files = {'image': f}
            
            print("🔍 Testing vehicle detection...")
            response = requests.post(url, files=files)
            
            print(f"Status: {response.status_code}")
            print("Response:", response.json())

if __name__ == "__main__":
    test_upload()
    print("\n" + "="*50 + "\n")
    test_detection()