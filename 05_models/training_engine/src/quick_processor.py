"""
quick_processor.py - Simple image to JSON converter
"""

import json
import os
from pathlib import Path

def simple_images_to_json(image_dir, output_file="simple_dataset.json"):
    """
    Simple function to create JSON from images
    
    Args:
        image_dir: Directory containing images
        output_file: Output JSON file name
    """
    
    dataset = {
        "info": {
            "description": "Simple Cambodia Traffic Dataset",
            "num_images": 0
        },
        "images": [],
        "categories": [
            {"id": 0, "name": "moto"},
            {"id": 1, "name": "tuktuk"},
            {"id": 2, "name": "bicycle"},
            {"id": 3, "name": "cart"},
            {"id": 4, "name": "car"}
        ]
    }
    
    # Get all image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(Path(image_dir).glob(f'*{ext}'))
    
    # Process each image
    for idx, img_path in enumerate(image_files):
        img_info = {
            "id": idx + 1,
            "file_name": img_path.name,
            "path": str(img_path.absolute()),
            "annotations": []  # You'll need to add labels manually or from label files
        }
        dataset["images"].append(img_info)
    
    dataset["info"]["num_images"] = len(dataset["images"])
    
    # Save to JSON
    with open(output_file, 'w') as f:
        json.dump(dataset, f, indent=2)
    
    print(f"Created {output_file} with {len(dataset['images'])} images")
    return dataset

# Run it
if __name__ == "__main__":
    simple_images_to_json("my_images", "my_dataset.json")