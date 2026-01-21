# test_detection.py
import requests
import json
import os

def test_api_detection():
    """Test the vehicle detection API with a sample image"""
    
    # API endpoint
    url = "http://127.0.0.1:8000/api/detect/"
    
    # Path to your test image
    # Try different paths based on where your images are stored
    test_image_paths = [
        "../test_images/traffic.jpg",
        "./test_images/traffic.jpg",
        "../../test_images/traffic.jpg",
        "traffic_test.jpg"
        "E:\Smart\Smart-Traffic-Optimizer\Smart-Traffic-Optimizer\test_image.jpg"
    ]
    
    # Find the first existing image
    image_path = None
    for path in test_image_paths:
        if os.path.exists(path):
            image_path = path
            print(f"📁 Found test image: {image_path}")
            break
    
    if not image_path:
        print("❌ No test image found. Creating a simple test...")
        
        # If you don't have images, we can test with a GET request first
        print("\nTesting GET request to check API status:")
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        print("\n⚠️ Please add a test image named 'E:\Smart\Smart-Traffic-Optimizer\Smart-Traffic-Optimizer\test_image.jpg' in this folder")
        print("Or modify the image_path in the script to point to your image.")
        return
    
    print(f"\n🚀 Testing POST request with image: {image_path}")
    
    try:
        # Send POST request with image
        with open(image_path, 'rb') as img_file:
            files = {'image': (os.path.basename(image_path), img_file, 'image/jpeg')}
            
            print(f"📤 Sending request to: {url}")
            response = requests.post(url, files=files)
        
        # Check response
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS! API Response:")
            print(json.dumps(result, indent=2))
            
            # Extract and display useful information
            print("\n📊 DETECTION SUMMARY:")
            
            if 'detections' in result:
                detections = result['detections']
                print(f"Total vehicles detected: {len(detections)}")
                
                # Count by vehicle type
                vehicle_counts = {}
                for detection in detections:
                    vehicle_type = detection.get('class', 'unknown')
                    confidence = detection.get('confidence', 0)
                    vehicle_counts[vehicle_type] = vehicle_counts.get(vehicle_type, 0) + 1
                
                print("\nVehicle Breakdown:")
                for vtype, count in vehicle_counts.items():
                    print(f"  {vtype}: {count}")
                    
            elif 'counts' in result:
                # If API returns counts directly
                print("Vehicle Counts:")
                for vtype, count in result['counts'].items():
                    print(f"  {vtype}: {count}")
                    
            elif 'message' in result:
                print(f"Message: {result['message']}")
                
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"Response text: {response.text}")
            
    except FileNotFoundError:
        print(f"❌ Image file not found: {image_path}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running!")
        print("Run: python manage.py runserver")
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")

def test_multiple_images():
    """Test with multiple images if available"""
    image_folder = "../test_images/"
    
    if os.path.exists(image_folder):
        image_files = [f for f in os.listdir(image_folder) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if image_files:
            print(f"\n🔍 Found {len(image_files)} test images")
            
            for i, img_file in enumerate(image_files[:3]):  # Test first 3
                img_path = os.path.join(image_folder, img_file)
                print(f"\n{'='*50}")
                print(f"Testing image {i+1}: {img_file}")
                
                try:
                    with open(img_path, 'rb') as img:
                        files = {'image': img}
                        response = requests.post("http://127.0.0.1:8000/api/detect/", files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if 'detections' in result:
                            count = len(result['detections'])
                            print(f"✅ Detected {count} vehicles")
                        elif 'counts' in result:
                            total = sum(result['counts'].values())
                            print(f"✅ Total vehicles: {total}")
                    else:
                        print(f"❌ Failed: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 SMART TRAFFIC OPTIMIZER - API TEST")
    print("=" * 50)
    
    # Test single image
    test_api_detection()
    
    # Optional: Test multiple images
    # test_multiple_images()
    
    print("\n" + "=" * 50)
    print("Test completed! 🎉")