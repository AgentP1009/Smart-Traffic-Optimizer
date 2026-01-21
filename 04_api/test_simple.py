# test_simple.py
import requests
import os

def test_api():
    print("🧪 Testing Smart Traffic Optimizer API")
    print("=" * 50)
    
    # Test 1: Check API status
    print("\n1. Testing API status...")
    try:
        response = requests.get("http://127.0.0.1:8000/")
        data = response.json()
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📱 Message: {data['message']}")
        print(f"   🔧 Version: {data['version']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 2: Check detection endpoint info
    print("\n2. Checking detection endpoint info...")
    response = requests.get("http://127.0.0.1:8000/api/detect/")
    data = response.json()
    print(f"   ✅ Status: {response.status_code}")
    print(f"   📝 {data['message']}")
    print(f"   🚗 Supported: {', '.join(data['supported_vehicles'])}")
    
    # Test 3: Try POST with image
    print("\n3. Testing vehicle detection...")
    
    # Look for test images in common locations
    test_locations = [
        "test_traffic.jpg",
        "../test_images/traffic.jpg",
        "test.jpg",
        "../../test_images/traffic.jpg",
        "sample_traffic.jpg"
    ]
    
    image_found = None
    for img_path in test_locations:
        if os.path.exists(img_path):
            image_found = img_path
            break
    
    if image_found:
        print(f"   📁 Found test image: {image_found}")
        
        try:
            with open(image_found, 'rb') as img_file:
                files = {'image': img_file}
                response = requests.post("http://127.0.0.1:8000/api/detect/", files=files)
            
            print(f"   📤 POST Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success! Response keys: {list(result.keys())}")
                
                # Pretty print the response
                import json
                print("\n   📊 Response:")
                print(json.dumps(result, indent=2)[:500] + "..." if len(str(result)) > 500 else json.dumps(result, indent=2))
                
                # Extract vehicle counts if available
                if 'detections' in result:
                    print(f"\n   🚗 Total detections: {len(result['detections'])}")
                elif 'counts' in result:
                    total = sum(result['counts'].values())
                    print(f"\n   🚗 Total vehicles: {total}")
                    
            else:
                print(f"   ❌ Error response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ POST failed: {e}")
    else:
        print("   ⚠️ No test image found. Create 'test_traffic.jpg' or modify the script.")
        print("   To create a test image:")
        print("   1. Take a photo of traffic with your phone")
        print("   2. Save it as 'test_traffic.jpg' in this folder")
        print("   3. Run this test again")
    
    print("\n" + "=" * 50)
    print("Test completed! 🎉")

if __name__ == "__main__":
    test_api()